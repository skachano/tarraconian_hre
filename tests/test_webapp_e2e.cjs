/**
 * test_webapp_e2e.cjs
 *
 * End-to-End browser test for the Tarraconian Atlas web application.
 * Uses Playwright to verify map rendering, search interaction, drawer inspection,
 * tier switching, and paradox fan disclaimer in a headless browser.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const DOCS_DIR = path.resolve(__dirname, '..', 'docs');
const SELECTED_STROKE_COLOR = '#ffffff';

const MIME_TYPES = {
  '.html': 'text/html; charset=UTF-8',
  '.css': 'text/css; charset=UTF-8',
  '.js': 'application/javascript; charset=UTF-8',
  '.json': 'application/json; charset=UTF-8',
  '.geojson': 'application/geo+json; charset=UTF-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
};

// 1. Simple zero-dependency HTTP static server
function createStaticServer(rootDir) {
  return http.createServer((req, res) => {
    let reqPath = decodeURI(req.url.split('?')[0]);
    if (reqPath === '/' || reqPath === '') reqPath = '/index.html';
    const filePath = path.join(rootDir, reqPath);

    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end(`404 Not Found: ${reqPath}`);
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
}

async function runE2ETests() {
  console.log('--- Starting Tarraconian Atlas E2E Tests ---');
  const server = createStaticServer(DOCS_DIR);

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  const baseUrl = `http://127.0.0.1:${port}`;
  console.log(`[1/6] Static server running on ${baseUrl}`);

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  // Listen to browser console and error messages
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.error(`[Browser Console Error]: ${msg.text()}`);
    }
  });
  page.on('pageerror', err => {
    console.error(`[Browser Page Error]: ${err.message}`);
  });

  try {
    // 1. Page Load
    console.log('[2/6] Navigating to index.html...');
    await page.goto(`${baseUrl}/index.html`, { waitUntil: 'domcontentloaded' });
    const title = await page.title();
    console.log(`  Page Title: "${title}"`);
    if (!title.includes('Tarraconian Atlas') || !title.includes('Dat Rômische Keiserrîch')) {
      throw new Error(`Unexpected page title: "${title}"`);
    }

    // 2. Wait for GeoJSON loading and overlay removal
    console.log('[3/6] Waiting for cartography data to load...');
    await page.waitForSelector('#loading-overlay', { state: 'detached', timeout: 20000 });
    console.log('  Data loaded and loading overlay removed successfully.');

    // Verify map canvas and SVG render layer
    await page.waitForSelector('#map .leaflet-pane svg path', { state: 'attached', timeout: 10000 });
    const pathCount = await page.locator('#map .leaflet-pane svg path').count();
    console.log(`  Rendered SVG vector paths count: ${pathCount}`);
    if (pathCount < 100) {
      throw new Error(`Expected at least 100 vector paths, found ${pathCount}`);
    }

    // 3. Search Autocomplete & Selection
    console.log('[4/6] Testing search autocomplete for "Stûlwîtzenburch"...');
    const searchInput = page.locator('#title-search');
    await searchInput.fill('Stûlwîtzenburch');

    await page.waitForSelector('#search-results .search-item', { timeout: 5000 });
    const firstResult = page.locator('#search-results .search-item').first();
    const resultText = await firstResult.innerText();
    console.log(`  Autocomplete top result: ${resultText.replace(/\n/g, ' ')}`);
    if (!resultText.includes('Stûlwîtzenburch') || !resultText.includes('c_szekesfehervar')) {
      throw new Error(`Unexpected search result: ${resultText}`);
    }

    // Click result to trigger selection and open drawer
    await firstResult.click();

    // Verify Inspector Drawer
    await page.waitForSelector('#inspector-drawer.open', { timeout: 5000 });
    const tarrName = await page.locator('#drawer-tarr-name').innerText();
    const titleKey = await page.locator('#drawer-title-key').innerText();
    const tierBadge = await page.locator('#drawer-tier-badge').innerText();
    const originName = await page.locator('#drawer-origin-name').innerText();

    console.log(`  Drawer inspected: [${tierBadge}] ${tarrName} (${titleKey}) -> Origin: "${originName}"`);
    if (tarrName !== 'Stûlwîtzenburch') {
      throw new Error(`Expected drawer tarr name "Stûlwîtzenburch", got "${tarrName}"`);
    }
    if (titleKey !== 'c_szekesfehervar') {
      throw new Error(`Expected title key "c_szekesfehervar", got "${titleKey}"`);
    }
    if (tierBadge.toUpperCase() !== 'COUNTY') {
      throw new Error(`Expected tier badge "COUNTY", got "${tierBadge}"`);
    }
    if (originName !== 'Székesfehérvár') {
      throw new Error(`Expected drawer origin name "Székesfehérvár", got "${originName}"`);
    }

    const szAnachHidden = await page.locator('#drawer-anachronism-note').evaluate(el => el.classList.contains('hidden'));
    if (!szAnachHidden) {
      throw new Error('Expected #drawer-anachronism-note to be hidden for authentic pre-1059 title Székesfehérvár');
    }

    // Check breadcrumbs for first title (Stûlwîtzenburch)
    const bcEmpire = await page.locator('#bc-empire').innerText();
    const bcKingdom = await page.locator('#bc-kingdom').innerText();
    console.log(`  Lineage: Empire="${bcEmpire}", Kingdom="${bcKingdom}"`);
    if (!bcEmpire.includes('Germania') && !bcEmpire.includes('Germany')) {
      throw new Error(`Expected Germania empire breadcrumb, got "${bcEmpire}"`);
    }
    if (!bcKingdom.includes('Ungern') && !bcKingdom.includes('Hungary')) {
      throw new Error(`Expected Hungarian kingdom breadcrumb, got "${bcKingdom}"`);
    }

    // Verify exactly 1 title boundary is highlighted
    const initialSelectedCount = await page.evaluate((selStroke) => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === selStroke).length;
    }, SELECTED_STROKE_COLOR);
    if (initialSelectedCount !== 1) {
      throw new Error(`Expected exactly 1 selected territory boundary, found ${initialSelectedCount}`);
    }

    // Verify that NO paths have a highlight fill color (fill highlight removed altogether)
    const hasHighlightFill = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .some(p => p.getAttribute('fill') === '#ffffff' || p.getAttribute('fill') === '#d3d3d3' || p.getAttribute('fill') === '#993284');
    });
    if (hasHighlightFill) {
      throw new Error('Detected unexpected highlight fill; fill highlight should be removed altogether');
    }

    // Now select a SECOND title (Middelsachsen / c_middlesex) and verify previous selection is reset
    console.log('  Testing sequential selection: selecting second title "Middelsachsen"...');
    await searchInput.fill('Middelsachsen');
    await page.waitForSelector('#search-results .search-item[data-key]', { timeout: 5000 });
    const middlesexResult = page.locator('#search-results .search-item[data-key]').first();
    await middlesexResult.click();

    await page.waitForFunction(() => {
      return document.getElementById('drawer-title-key').innerText === 'c_middlesex';
    }, { timeout: 5000 });

    const secondSelectedCount = await page.evaluate((selStroke) => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === selStroke).length;
    }, SELECTED_STROKE_COLOR);
    console.log(`  Selected territories count after second click: ${secondSelectedCount}`);
    if (secondSelectedCount !== 1) {
      throw new Error(`Residual selection detected! Expected exactly 1 selected territory, got ${secondSelectedCount}`);
    }

    const secondKingdom = await page.locator('#bc-kingdom').innerText();
    const secondEmpire = await page.locator('#bc-empire').innerText();
    const secondOrigin = await page.locator('#drawer-origin-name').innerText();
    console.log(`  Middelsachsen Lineage: Empire="${secondEmpire}", Kingdom="${secondKingdom}", Origin="${secondOrigin}"`);
    if (secondOrigin !== 'Middle Seaxe') {
      throw new Error(`Expected drawer origin name "Middle Seaxe", got "${secondOrigin}"`);
    }
    if (!secondEmpire.includes('Germania') && !secondEmpire.includes('Germany')) {
      throw new Error(`Expected Germania empire breadcrumb for Middelsachsen, got "${secondEmpire}"`);
    }
    if (!secondKingdom.includes('Engellant') && !secondKingdom.includes('England')) {
      throw new Error(`Expected English kingdom breadcrumb, got "${secondKingdom}"`);
    }

    const midAnachHidden = await page.locator('#drawer-anachronism-note').evaluate(el => el.classList.contains('hidden'));
    if (!midAnachHidden) {
      throw new Error('Expected #drawer-anachronism-note to be hidden for authentic pre-1059 title Middle Seaxe');
    }

    // Now select an ANACHRONISTIC title (München / c_munchen) and verify historical analysis block
    console.log('  Testing anachronistic title inspection: selecting "München" / "c_munchen"...');
    await searchInput.fill('c_munchen');
    await page.waitForSelector('#search-results .search-item[data-key]', { timeout: 5000 });
    const munchenResult = page.locator('#search-results .search-item[data-key="c_munchen"]').first();
    await munchenResult.click();

    await page.waitForFunction(() => {
      return document.getElementById('drawer-title-key').innerText === 'c_munchen';
    }, { timeout: 5000 });

    const munchenOrigin = await page.locator('#drawer-origin-name').innerText();
    console.log(`  München Origin displayed: "${munchenOrigin}"`);
    if (!munchenOrigin.includes('Freising') || !munchenOrigin.includes('München')) {
      throw new Error(`Expected München origin to include "Freising" and "München", got "${munchenOrigin}"`);
    }

    const munchenTitle = await page.locator('#drawer-tarr-name').innerText();
    console.log(`  München Drawer title name: "${munchenTitle}"`);
    if (munchenTitle !== 'Vrîsing') {
      throw new Error(`Expected drawer title name to be historical name "Vrîsing", got "${munchenTitle}"`);
    }

    const munchenAnachVisible = await page.locator('#drawer-anachronism-note').evaluate(el => !el.classList.contains('hidden'));
    if (!munchenAnachVisible) {
      throw new Error('Expected #drawer-anachronism-note to be visible for anachronistic title c_munchen');
    }

    const anachText = await page.locator('#drawer-anachronism-note').innerText();
    console.log(`  München Anachronism note: "${anachText}"`);
    if (!anachText.includes('1158') || !anachText.includes('Henry the Lion')) {
      throw new Error(`Expected anachronism analysis to mention 1158 foundation and Henry the Lion, got "${anachText}"`);
    }
    if (!anachText.includes('ℹ️') || anachText.includes('⚠️')) {
      throw new Error(`Expected anachronism note to have info icon ℹ️ instead of ⚠️, got "${anachText}"`);
    }

    const histGroupVisible = await page.locator('#drawer-hist-group').evaluate(el => !el.classList.contains('hidden'));
    if (!histGroupVisible) {
      throw new Error('Expected #drawer-hist-group to be visible for c_munchen');
    }
    const histLabel = await page.locator('#drawer-hist-group label').innerText();
    if (!histLabel.toUpperCase().includes('HISTORICAL RESOLUTION') || histLabel.includes('1059')) {
      throw new Error(`Expected label "Historical Resolution" without "1059", got "${histLabel}"`);
    }
    const histText = await page.locator('#drawer-hist-name').innerText();
    if (histText.includes('(Direct:') || !histText.includes('Vrîsing')) {
      throw new Error(`Expected historical resolution to be "Vrîsing" without (Direct: ...), got "${histText}"`);
    }

    // Test c_cleves for IPA pronunciation and historical resolution
    console.log('  Testing IPA pronunciation and historical naming on c_cleves...');
    await searchInput.fill('c_cleves');
    await page.waitForSelector('#search-results .search-item[data-key="c_cleves"]', { timeout: 5000 });
    const clevesResult = page.locator('#search-results .search-item[data-key="c_cleves"]').first();
    await clevesResult.click();
    await page.waitForFunction(() => {
      return document.getElementById('drawer-title-key').innerText === 'c_cleves';
    }, { timeout: 5000 });

    const clevesTitle = await page.locator('#drawer-tarr-name').innerText();
    if (clevesTitle !== 'Xanten') {
      throw new Error(`Expected c_cleves title name to be "Xanten", got "${clevesTitle}"`);
    }

    const ipaVisible = await page.locator('#drawer-ipa-group').evaluate(el => !el.classList.contains('hidden'));
    if (!ipaVisible) {
      throw new Error('Expected #drawer-ipa-group to be visible for c_cleves');
    }
    const ipaText = await page.locator('#drawer-ipa').innerText();
    if (!ipaText.includes('[ˈkleː.və]')) {
      throw new Error(`Expected IPA "[ˈkleː.və]", got "${ipaText}"`);
    }

    const titleBox = await page.locator('#drawer-tarr-name').boundingBox();
    const ipaBox = await page.locator('#drawer-ipa-group').boundingBox();
    if (titleBox && ipaBox && ipaBox.y <= titleBox.y) {
      throw new Error(`Expected #drawer-ipa-group to be below #drawer-tarr-name: titleY=${titleBox.y}, ipaY=${ipaBox.y}`);
    }

    const clevesHistText = await page.locator('#drawer-hist-name').innerText();
    if (clevesHistText.includes('(Direct:') || !clevesHistText.includes('Xanten')) {
      throw new Error(`Expected historical resolution "Xanten" without "(Direct: ...)", got "${clevesHistText}"`);
    }

    // Re-select Middlesex so that switching to Kingdom tier tests k_england
    console.log('  Re-selecting Middlesex for De Jure tier tests...');
    await searchInput.fill('c_middlesex');
    await page.waitForSelector('#search-results .search-item[data-key="c_middlesex"]', { timeout: 5000 });
    const midRes = page.locator('#search-results .search-item[data-key="c_middlesex"]').first();
    await midRes.click();
    await page.waitForFunction(() => {
      return document.getElementById('drawer-title-key').innerText === 'c_middlesex';
    }, { timeout: 5000 });

    // 4. Test De Jure Tier Switching & High-Tier Title Selection
    console.log('[5/7] Testing De Jure tier title selection (Kingdom, Duchy, Empire) & constituent navigation...');
    const kingdomBtn = page.locator('.tier-btn[data-tier="kingdom"]');
    const duchyBtn = page.locator('.tier-btn[data-tier="duchy"]');
    const empireBtn = page.locator('.tier-btn[data-tier="empire"]');
    const countyBtn = page.locator('.tier-btn[data-tier="county"]');
    const baronyBtn = page.locator('.tier-btn[data-tier="barony"]');

    // Currently Middlesex (c_middlesex) is selected. Switch to Kingdom mode:
    console.log('  Switching to Kingdom tier while Middlesex is selected...');
    await kingdomBtn.click();
    if (!(await kingdomBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('Kingdom tier button failed to activate');
    }

    // Verify Kingdom title selection: entire Kingdom of England selected
    await page.waitForFunction(() => {
      return document.getElementById('drawer-tier-badge').innerText === 'KINGDOM' &&
             document.getElementById('drawer-title-key').innerText === 'k_england';
    }, { timeout: 5000 });

    const kingdomOrigin = await page.locator('#drawer-origin-name').innerText();
    console.log(`  Kingdom of England origin: "${kingdomOrigin}"`);
    if (kingdomOrigin !== 'England') {
      throw new Error(`Expected drawer origin name "England" for k_england, got "${kingdomOrigin}"`);
    }

    const kingdomSelectedCount = await page.evaluate((selStroke) => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === selStroke).length;
    }, SELECTED_STROKE_COLOR);
    console.log(`  Selected counties for Kingdom of England: ${kingdomSelectedCount}`);
    if (kingdomSelectedCount <= 1) {
      throw new Error(`Expected whole kingdom selection (>1 counties), got ${kingdomSelectedCount}`);
    }

    // Verify constituent duchies list in drawer
    const constituentLabel = await page.locator('#drawer-baronies-label').innerText();
    console.log(`  Drawer constituent label: "${constituentLabel}"`);
    if (!constituentLabel.toUpperCase().includes('CONSTITUENT DUCHIES')) {
      throw new Error(`Expected "Constituent Duchies" label, got "${constituentLabel}"`);
    }

    // Click constituent duchy pill (e.g. Bedford / Ôstsachsen: d_bedford)
    console.log('  Clicking constituent duchy pill "d_bedford"...');
    const bedfordPill = page.locator('.barony-pill[data-key="d_bedford"]');
    await bedfordPill.click();

    await page.waitForFunction(() => {
      return document.getElementById('drawer-tier-badge').innerText === 'DUCHY' &&
             document.getElementById('drawer-title-key').innerText === 'd_bedford';
    }, { timeout: 5000 });

    const duchyOrigin = await page.locator('#drawer-origin-name').innerText();
    console.log(`  Duchy of Bedford origin: "${duchyOrigin}"`);
    if (duchyOrigin !== 'East Seaxe') {
      throw new Error(`Expected drawer origin name "East Seaxe" for d_bedford, got "${duchyOrigin}"`);
    }

    if (!(await duchyBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('Duchy tier button failed to activate on duchy pill click');
    }

    const duchySelectedCount = await page.evaluate((selStroke) => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === selStroke).length;
    }, SELECTED_STROKE_COLOR);
    console.log(`  Selected counties for Duchy of Bedford: ${duchySelectedCount}`);
    if (duchySelectedCount <= 1 || duchySelectedCount >= kingdomSelectedCount) {
      throw new Error(`Expected duchy county count between 2 and ${kingdomSelectedCount}, got ${duchySelectedCount}`);
    }

    // Click constituent county pill (c_middlesex)
    console.log('  Clicking constituent county pill "c_middlesex"...');
    const middlesexPill = page.locator('.barony-pill[data-key="c_middlesex"]');
    await middlesexPill.click();

    await page.waitForFunction(() => {
      return document.getElementById('drawer-tier-badge').innerText === 'COUNTY' &&
             document.getElementById('drawer-title-key').innerText === 'c_middlesex';
    }, { timeout: 5000 });

    if (!(await countyBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('County tier button failed to activate on county pill click');
    }

    const countySelectedCount = await page.evaluate((selStroke) => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === selStroke).length;
    }, SELECTED_STROKE_COLOR);
    console.log(`  Selected counties for County of Middlesex: ${countySelectedCount}`);
    if (countySelectedCount !== 1) {
      throw new Error(`Expected exactly 1 selected county, got ${countySelectedCount}`);
    }

    // Test Empire breadcrumb navigation
    console.log('  Clicking Empire breadcrumb (Germania)...');
    const empireBc = page.locator('#bc-empire');
    await empireBc.click();

    await page.waitForFunction(() => {
      return document.getElementById('drawer-tier-badge').innerText === 'EMPIRE' &&
             document.getElementById('drawer-title-key').innerText === 'e_germany';
    }, { timeout: 5000 });

    const empireOrigin = await page.locator('#drawer-origin-name').innerText();
    console.log(`  Empire of Germania origin: "${empireOrigin}"`);
    if (empireOrigin !== 'Germania') {
      throw new Error(`Expected drawer origin name "Germania" for e_germany, got "${empireOrigin}"`);
    }

    if (!(await empireBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('Empire tier button failed to activate on empire breadcrumb click');
    }

    const empireSelectedCount = await page.evaluate((selStroke) => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === selStroke).length;
    }, SELECTED_STROKE_COLOR);
    console.log(`  Selected counties for Empire of Germania: ${empireSelectedCount}`);
    if (empireSelectedCount <= kingdomSelectedCount) {
      throw new Error(`Expected empire county count > ${kingdomSelectedCount}, got ${empireSelectedCount}`);
    }

    // Test Zoom button
    const zoomBtn = page.locator('#drawer-zoom-btn');
    await zoomBtn.click();
    console.log('  Drawer zoom button clicked successfully.');

    // Test sequential selection in Kingdom tier: search for Kingdom of France
    console.log('  Testing sequential title selection in Kingdom tier (searching k_france)...');
    await kingdomBtn.click();
    await searchInput.fill('k_france');
    await page.waitForSelector('#search-results .search-item[data-key="k_france"]', { timeout: 5000 });
    const franceItem = page.locator('#search-results .search-item[data-key="k_france"]');
    await franceItem.click();

    await page.waitForFunction(() => {
      return document.getElementById('drawer-tier-badge').innerText === 'KINGDOM' &&
             document.getElementById('drawer-title-key').innerText === 'k_france';
    }, { timeout: 5000 });

    const franceIpa = await page.locator('#drawer-ipa').innerText();
    console.log(`  Kingdom of France IPA: "${franceIpa}"`);
    if (!franceIpa.includes('[ˈvraŋk.riːç]')) {
      throw new Error(`Expected Kingdom of France IPA "[ˈvraŋk.riːç]", got "${franceIpa}"`);
    }

    const franceSelectedCount = await page.evaluate((selStroke) => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === selStroke).length;
    }, SELECTED_STROKE_COLOR);
    console.log(`  Selected counties for Kingdom of France: ${franceSelectedCount}`);
    if (franceSelectedCount <= 1 || franceSelectedCount === empireSelectedCount) {
      throw new Error(`Unexpected selection count for France: ${franceSelectedCount}`);
    }

    // Test Kingdom of Polotia (k_white_rus) resolved to historical name Polôtzich
    console.log('  Testing Kingdom of Polotia (k_white_rus) resolved to historical name "Polôtzich"...');
    await searchInput.fill('k_white_rus');
    await page.waitForSelector('#search-results .search-item[data-key="k_white_rus"]', { timeout: 5000 });
    const polotskItem = page.locator('#search-results .search-item[data-key="k_white_rus"]');
    await polotskItem.click();

    await page.waitForFunction(() => {
      return document.getElementById('drawer-tier-badge').innerText === 'KINGDOM' &&
             document.getElementById('drawer-title-key').innerText === 'k_white_rus';
    }, { timeout: 5000 });

    const polotskTitle = await page.locator('#drawer-tarr-name').innerText();
    console.log(`  k_white_rus title displayed: "${polotskTitle}"`);
    if (polotskTitle !== 'Polôtzich') {
      throw new Error(`Expected k_white_rus title to be "Polôtzich", got "${polotskTitle}"`);
    }

    const polotskIpa = await page.locator('#drawer-ipa').innerText();
    if (!polotskIpa.includes('[ˈpɔ.lɔtsk]')) {
      throw new Error(`Expected k_white_rus IPA "[ˈpɔ.lɔtsk]", got "${polotskIpa}"`);
    }

    const polotskHist = await page.locator('#drawer-hist-name').innerText();
    if (polotskHist !== 'Polôtzich') {
      throw new Error(`Expected historical resolution "Polôtzich", got "${polotskHist}"`);
    }

    // Test search autocomplete by historical origin name ("Bernicia" -> c_northumberland)
    console.log('  Testing search autocomplete by title name origin ("Bernicia")...');
    await countyBtn.click();
    await searchInput.fill('Bernicia');
    await page.waitForSelector('#search-results .search-item[data-key="c_northumberland"]', { timeout: 5000 });
    const berniciaItem = page.locator('#search-results .search-item[data-key="c_northumberland"]');
    await berniciaItem.click();

    await page.waitForFunction(() => {
      return document.getElementById('drawer-title-key').innerText === 'c_northumberland' &&
             document.getElementById('drawer-origin-name').innerText === 'Bernicia';
    }, { timeout: 5000 });
    console.log('  Search by origin name ("Bernicia") matched c_northumberland successfully.');

    // Switch to Barony (lazy-loads 11,297 baronies)
    console.log('  Switching to Barony tier...');
    await baronyBtn.click();
    await page.waitForFunction(() => {
      return document.querySelectorAll('#map svg path').length === 11297;
    }, { timeout: 10000 });
    console.log('  Barony tier active: 11,297 holding polygons loaded.');

    const legendVisibleInBarony = await page.locator('#barony-legend').evaluate(el => !el.classList.contains('hidden'));
    if (!legendVisibleInBarony) {
      throw new Error('Expected #barony-legend to be visible in Barony tier');
    }

    const baronyFills = await page.evaluate(() => {
      const paths = Array.from(document.querySelectorAll('#map svg path'));
      const fills = new Set(paths.slice(0, 100).map(p => p.getAttribute('fill')));
      return Array.from(fills);
    });
    console.log(`  Sample barony holding fill colors: ${baronyFills.join(', ')}`);
    const expectedBaronyColors = ['#ab3348', '#3069a8', '#3b824a', '#424242'];
    const matchedColors = expectedBaronyColors.filter(c => baronyFills.includes(c));
    if (matchedColors.length < 2) {
      throw new Error(`Expected barony holding colors among sample, found only: ${matchedColors.join(', ')}`);
    }

    // Switch back to County tier (must restore 3,476 county polygons)
    console.log('  Switching from Barony back to County tier...');
    await countyBtn.click();
    await page.waitForFunction(() => {
      return document.querySelectorAll('#map svg path').length === 3476;
    }, { timeout: 5000 });
    console.log('  Restored County tier: 3,476 county polygons loaded.');

    const legendHiddenInCounty = await page.locator('#barony-legend').evaluate(el => el.classList.contains('hidden'));
    if (!legendHiddenInCounty) {
      throw new Error('Expected #barony-legend to be hidden in County tier');
    }

    // Verify non-empty hex fill colors from map coloring
    const sampleFills = await page.evaluate(() => {
      const paths = Array.from(document.querySelectorAll('#map svg path'));
      return paths.slice(0, 10).map(p => p.getAttribute('fill'));
    });
    console.log(`  Sample territory fill colors: ${sampleFills.slice(0, 5).join(', ')}`);
    for (const f of sampleFills) {
      if (!f || !f.startsWith('#')) {
        throw new Error(`Expected valid hex fill color, got "${f}"`);
      }
    }

    // 5. Test Mouse Movement & Zero Residual Highlighting
    console.log('[6/7] Testing mouse hover sweep across territories (verifying zero residual highlights)...');
    // Close drawer to test clean canvas sweep
    const closeBtn = page.locator('#drawer-close');
    if (await closeBtn.isVisible()) {
      await closeBtn.click();
    }

    const closedSelectedCount = await page.evaluate((selStroke) => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === selStroke).length;
    }, SELECTED_STROKE_COLOR);
    if (closedSelectedCount !== 0) {
      throw new Error(`Expected 0 selected territories after drawer close, found ${closedSelectedCount}`);
    }

    // Sweep across map coordinates
    for (let x = 300; x <= 800; x += 25) {
      const y = 400 + Math.sin(x / 40) * 80;
      await page.mouse.move(x, y);
      const highlightedCount = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('#map svg path'))
          .filter(p => p.getAttribute('stroke') === '#f5d77f').length;
      });
      if (highlightedCount > 1) {
        throw new Error(`Residual highlight detected! ${highlightedCount} paths highlighted simultaneously at (${x}, ${y})`);
      }
    }

    // Move cursor away off map to header
    await page.mouse.move(200, 20);
    await page.waitForTimeout(200);
    const residualCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('stroke') === '#f5d77f').length;
    });
    if (residualCount > 0) {
      throw new Error(`Residual highlight remained after moving off territory: ${residualCount} paths`);
    }
    console.log('  Mouse movement sweep verified: exactly 0 residual highlights.');

    // 6. Test Paradox Disclaimer & Take Preview Screenshot
    console.log('[7/7] Verifying Paradox interactive fan notice and capturing preview...');
    const footerText = await page.locator('.footer-disclaimer').innerText();
    if (!footerText.includes('Paradox Interactive AB') || !footerText.includes('non-commercial')) {
      throw new Error(`Missing Paradox disclaimer in footer: "${footerText}"`);
    }

    const previewPath = path.join(DOCS_DIR, 'preview.png');
    await page.screenshot({ path: previewPath });
    console.log(`  Captured preview screenshot: ${previewPath}`);

    console.log('\n========================================');
    console.log('✅ ALL E2E WEB APPLICATION TESTS PASSED!');
    console.log('========================================');
  } finally {
    await browser.close();
    server.close();
  }
}

runE2ETests().catch(err => {
  console.error('\n❌ E2E TEST FAILED:', err);
  process.exit(1);
});
