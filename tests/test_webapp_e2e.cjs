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
    if (!bcEmpire.includes('Germania') && !bcEmpire.includes('Germany') && !bcEmpire.includes('Dütsch') && !bcEmpire.includes('Frankisch') && !bcEmpire.includes('Vrankisch')) {
      throw new Error(`Expected Germania / Dat Vrankische Imperi empire breadcrumb, got "${bcEmpire}"`);
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
    if (!secondEmpire.includes('Germania') && !secondEmpire.includes('Germany') && !secondEmpire.includes('Dütsch') && !secondEmpire.includes('Frankisch') && !secondEmpire.includes('Vrankisch')) {
      throw new Error(`Expected Germania / Dat Vrankische Imperi empire breadcrumb for Middelsachsen, got "${secondEmpire}"`);
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
    if (!polotskIpa.includes('[pɔ.ˈloː.tsɪç]')) {
      throw new Error(`Expected k_white_rus IPA "[pɔ.ˈloː.tsɪç]", got "${polotskIpa}"`);
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

    // Verify #barony-legend is separate from .map-stats-badge / #hover-info
    const isSeparateElement = await page.evaluate(() => {
      const legend = document.getElementById('barony-legend');
      const badge = document.querySelector('.map-stats-badge');
      return legend && badge && !badge.contains(legend) && !legend.contains(badge);
    });
    if (!isSeparateElement) {
      throw new Error('Expected #barony-legend to be completely separate from .map-stats-badge');
    }
    console.log('  Holding type legend verified as a separate floating component from hover-info badge.');

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

    // Test inspecting an unoccupied barony: name is blank, origin group hidden, only title key and hierarchy visible
    console.log('  Testing unoccupied barony inspection...');
    const hasUnoccupied = await page.evaluate(() => {
      const p = Array.from(document.querySelectorAll('#map svg path'))
        .find(el => el.getAttribute('fill') === '#424242');
      if (p) {
        p.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        return true;
      }
      return false;
    });
    if (hasUnoccupied) {
      await page.waitForTimeout(200);
      const drawerTitle = await page.locator('#drawer-tarr-name').innerText();
      if (drawerTitle.trim() !== '') {
        throw new Error(`Expected blank title name for unoccupied barony, got "${drawerTitle}"`);
      }
      const originHidden = await page.locator('#drawer-origin-group').evaluate(el => el.classList.contains('hidden'));
      if (!originHidden) {
        throw new Error('Expected #drawer-origin-group to be hidden for unoccupied barony');
      }
      const titleKey = await page.locator('#drawer-title-key').innerText();
      if (!titleKey || !titleKey.startsWith('b_')) {
        throw new Error(`Expected valid barony title key, got "${titleKey}"`);
      }
      const tierBadge = await page.locator('#drawer-tier-badge').innerText();
      if (!tierBadge.includes('UNOCCUPIED')) {
        throw new Error(`Expected UNOCCUPIED tier badge, got "${tierBadge}"`);
      }
      const topoHiddenUnocc = await page.locator('#drawer-toponymic-group').evaluate(el => el.classList.contains('hidden'));
      const rulerHiddenUnocc = await page.locator('#drawer-coinage-ruler-group').evaluate(el => el.classList.contains('hidden'));
      const ctxHiddenUnocc = await page.locator('#drawer-physical-context-group').evaluate(el => el.classList.contains('hidden'));
      if (!topoHiddenUnocc || !rulerHiddenUnocc || !ctxHiddenUnocc) {
        throw new Error('Expected toponymic, coinage ruler, and physical context groups to be hidden for unoccupied barony');
      }
      console.log(`  Unoccupied barony verified: key="${titleKey}", title name is blank, origin/toponymic/ruler/context groups hidden.`);
    }

    // Test 3 new barony culture views (Coinage, Substrate, Transmission) + occupied barony toponymic profile
    console.log('  Testing Barony view switcher (Coinage / Substrate / Transmission)...');
    const viewControlsVisible = await page.locator('#barony-view-controls').evaluate(el => !el.classList.contains('hidden'));
    if (!viewControlsVisible) {
      throw new Error('Expected #barony-view-controls to be visible in Barony tier');
    }

    for (const [viewKey, legendTitle] of [
      ['coinage_culture', 'Coinage:'],
      ['substrate_culture', 'Substrate:'],
      ['transmission_culture', 'Transmission:']
    ]) {
      await page.locator(`.barony-view-btn[data-view="${viewKey}"]`).click();
      await page.waitForFunction((expectedTitle) => {
        const legend = document.getElementById('barony-legend');
        return legend && legend.textContent.includes(expectedTitle);
      }, legendTitle, { timeout: 10000 });
      const viewFills = await page.evaluate(() => {
        const paths = Array.from(document.querySelectorAll('#map svg path'));
        return Array.from(new Set(paths.slice(0, 200).map(p => p.getAttribute('fill'))));
      });
      if (viewFills.length < 3) {
        throw new Error(`Expected diverse culture colors in ${viewKey} view, found ${viewFills.length}`);
      }
      console.log(`  ${viewKey} view active: ${viewFills.length} distinct sample colors, legend "${legendTitle}".`);
    }

    // Inspect an occupied barony via search (b_roma) and verify Toponymic Profile details
    await page.locator('.barony-view-btn[data-view="holding_type"]').click();
    await page.waitForFunction(() => {
      const legend = document.getElementById('barony-legend');
      return legend && legend.textContent.includes('Holdings:');
    }, { timeout: 5000 });

    const bSearch = page.locator('#title-search');
    await bSearch.fill('b_roma');
    await page.waitForSelector('#search-results .search-item', { timeout: 5000 });
    await page.locator('#search-results .search-item[data-key="b_roma"]').click();
    await page.waitForFunction(() => {
      return document.getElementById('drawer-title-key').innerText === 'b_roma' &&
             !document.getElementById('drawer-toponymic-group').classList.contains('hidden') &&
             !document.getElementById('drawer-coinage-ruler-group').classList.contains('hidden') &&
             !document.getElementById('drawer-physical-context-group').classList.contains('hidden');
    }, { timeout: 5000 });
    const coinageText = await page.locator('#drawer-coinage-culture').innerText();
    const substrateText = await page.locator('#drawer-substrate-culture').innerText();
    const transmissionText = await page.locator('#drawer-transmission-culture').innerText();
    if (!coinageText.includes('Italian') || !substrateText.includes('Italian') || !transmissionText.includes('Greek')) {
      throw new Error(`Unexpected b_roma toponymic profile: C="${coinageText}", S="${substrateText}", T="${transmissionText}"`);
    }
    const rulerName = await page.locator('#drawer-ruler-name').innerText();
    const ctxBuildings = await page.locator('#drawer-context-buildings').innerText();
    if (!rulerName.includes('Niccoló') || !ctxBuildings.includes('Curtain Walls')) {
      throw new Error(`Unexpected b_roma ruler/context: ruler="${rulerName}", bldgs="${ctxBuildings}"`);
    }
    console.log(`  Occupied barony b_roma profile verified: C=${coinageText}, S=${substrateText}, T=${transmissionText}, Ruler=${rulerName}.`);

    // Verify top bar audit badge updates and hides properly across barony categories (e.g. b_huoshan -> b_nimes)
    await bSearch.fill('b_huoshan');
    await page.waitForSelector('#search-results .search-item[data-key="b_huoshan"]', { timeout: 5000 });
    await page.locator('#search-results .search-item[data-key="b_huoshan"]').click();
    await page.waitForFunction(() => document.getElementById('drawer-title-key').innerText === 'b_huoshan', { timeout: 5000 });
    const huoshanBadgeVisible = await page.locator('#drawer-audit-badge').isVisible();
    const huoshanBadgeText = await page.locator('#drawer-audit-badge').textContent();
    if (!huoshanBadgeVisible || huoshanBadgeText.trim() !== 'Sinosphere Calque') {
      throw new Error(`Expected visible "Sinosphere Calque" badge on b_huoshan, got visible=${huoshanBadgeVisible}, text="${huoshanBadgeText}"`);
    }

    await bSearch.fill('b_nimes');
    await page.waitForSelector('#search-results .search-item[data-key="b_nimes"]', { timeout: 5000 });
    await page.locator('#search-results .search-item[data-key="b_nimes"]').click();
    await page.waitForFunction(() => document.getElementById('drawer-title-key').innerText === 'b_nimes', { timeout: 5000 });
    const nimesBadgeVisible = await page.locator('#drawer-audit-badge').isVisible();
    if (nimesBadgeVisible) {
      const staleText = await page.locator('#drawer-audit-badge').innerText();
      throw new Error(`Expected #drawer-audit-badge to be hidden on b_nimes, but it remained visible with text="${staleText}"`);
    }
    console.log('  Barony audit badge verified: visible "Sinosphere Calque" on b_huoshan, hidden on b_nimes.');

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
    const viewControlsHiddenInCounty = await page.locator('#barony-view-controls').evaluate(el => el.classList.contains('hidden'));
    if (!viewControlsHiddenInCounty) {
      throw new Error('Expected #barony-view-controls to be hidden in County tier');
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

    // 5.5 Test Imperial Linguistics Guide Modal & Hanzi Lexicon
    console.log('[6/8] Testing Imperial Linguistics & Toponymic Guide Modal...');
    const openGuideBtn = page.locator('#btn-open-linguistics');
    if (!(await openGuideBtn.isVisible())) {
      throw new Error('#btn-open-linguistics button is not visible');
    }
    await openGuideBtn.click();
    await page.waitForSelector('#linguistics-modal:not(.hidden)', { timeout: 3000 });
    console.log('  Linguistics modal opened successfully.');

    // Tab 1: Tarraconian Language & Phonotactics
    const tarrPaneActive = await page.locator('#tab-pane-tarraconian').evaluate(el => !el.classList.contains('hidden') && el.classList.contains('active'));
    if (!tarrPaneActive) {
      throw new Error('Expected #tab-pane-tarraconian to be active by default');
    }
    const tarrPaneText = await page.locator('#tab-pane-tarraconian').innerText();
    if (!tarrPaneText.includes('Sociolinguistic Overview') || !tarrPaneText.includes('reverse Frankish')) {
      throw new Error('Missing expected content in Tarraconian linguistics tab');
    }

    // Switch to Tab 2: Sinosphere Titles & Hanzi Calques
    console.log('  Testing tab switch to Sinosphere Titles & Hanzi Calques...');
    const sinoTabBtn = page.locator('.modal-tab-btn[data-tab="sinosphere"]');
    await sinoTabBtn.click();
    await page.waitForSelector('#tab-pane-sinosphere.active:not(.hidden)', { timeout: 3000 });
    const sinoPaneText = await page.locator('#tab-pane-sinosphere').innerText();
    if (!sinoPaneText.includes('Dual Toponymic Adoption Protocol') || !sinoPaneText.includes('1154 AD')) {
      throw new Error('Missing expected content in Sinosphere calque doctrine tab');
    }

    // Switch to Tab 3: Hanzi Calque Lexicon
    console.log('  Testing tab switch to Hanzi Calque Lexicon (641 Characters)...');
    const lexiconTabBtn = page.locator('.modal-tab-btn[data-tab="lexicon"]');
    await lexiconTabBtn.click();
    await page.waitForSelector('#tab-pane-lexicon.active:not(.hidden)', { timeout: 3000 });
    await page.waitForSelector('#lexicon-table-body tr td.lexicon-hanzi-cell', { timeout: 10000 });
    const initialKanjiCount = await page.locator('#lexicon-table-body tr').count();
    console.log(`  Initial Hanzi Lexicon rendered rows: ${initialKanjiCount}`);
    if (initialKanjiCount !== 641) {
      throw new Error(`Expected 641 Hanzi rows, found ${initialKanjiCount}`);
    }

    // Test Lexicon Search Filter
    console.log('  Testing Hanzi Lexicon search filter for "城"...');
    const lexiconSearch = page.locator('#lexicon-search-input');
    await lexiconSearch.fill('城');
    await page.waitForTimeout(300);
    const filteredKanjiCount = await page.locator('#lexicon-table-body tr').count();
    console.log(`  Filtered Hanzi rows for "城": ${filteredKanjiCount}`);
    if (filteredKanjiCount === 0 || filteredKanjiCount >= 641) {
      throw new Error(`Expected filtered count for "城" between 1 and 640, got ${filteredKanjiCount}`);
    }

    // Clear Lexicon Search
    const clearLexiconBtn = page.locator('#lexicon-search-clear');
    await clearLexiconBtn.click();
    await page.waitForTimeout(300);
    const restoredKanjiCount = await page.locator('#lexicon-table-body tr').count();
    if (restoredKanjiCount !== 641) {
      throw new Error(`Expected restored count 641 after clearing filter, got ${restoredKanjiCount}`);
    }

    // Close Modal
    console.log('  Closing Linguistics modal...');
    const closeGuideBtn = page.locator('#btn-close-linguistics');
    await closeGuideBtn.click();
    await page.waitForSelector('#linguistics-modal', { state: 'hidden', timeout: 3000 });
    console.log('  Linguistics modal closed successfully.');

    // 5.6 Test Sinosphere Hanzi Search & Drawer Card Integration
    console.log('  Testing Sinosphere title search by Hanzi "山城" (Yamashiro)...');
    await searchInput.fill('山城');
    await page.waitForSelector('#search-results .search-item[data-key="c_yamashiro"]', { timeout: 5000 });
    const yamashiroResult = page.locator('#search-results .search-item[data-key="c_yamashiro"]');
    const hanziBadgeText = await yamashiroResult.locator('.result-hanzi').innerText();
    console.log(`  Autocomplete Hanzi badge found: "${hanziBadgeText}"`);
    if (hanziBadgeText !== '山城') {
      throw new Error(`Expected .result-hanzi badge "山城", got "${hanziBadgeText}"`);
    }

    await yamashiroResult.click();
    await page.waitForSelector('#inspector-drawer.open', { timeout: 5000 });
    await page.waitForFunction(() => {
      return document.getElementById('drawer-title-key').innerText === 'c_yamashiro';
    }, { timeout: 5000 });

    const sinoGroupVisible = await page.locator('#drawer-sinosphere-group').evaluate(el => !el.classList.contains('hidden'));
    if (!sinoGroupVisible) {
      throw new Error('Expected #drawer-sinosphere-group to be visible for c_yamashiro');
    }

    const drawerHanzi = await page.locator('#drawer-sinosphere-hanzi').innerText();
    const drawerReading = await page.locator('#drawer-sinosphere-reading').innerText();
    const drawerSynthesis = await page.locator('#drawer-sinosphere-synthesis').innerText();
    console.log(`  Yamashiro Sinosphere Card: Hanzi="${drawerHanzi}", Reading="${drawerReading}", Synthesis="${drawerSynthesis}"`);
    if (drawerHanzi !== '山城') {
      throw new Error(`Expected drawer Hanzi "山城", got "${drawerHanzi}"`);
    }
    if (!drawerReading.includes('Yamashiro')) {
      throw new Error(`Expected reading to include "Yamashiro", got "${drawerReading}"`);
    }
    if (!drawerSynthesis.includes('Berchburch')) {
      throw new Error(`Expected synthesis to include "Berchburch", got "${drawerSynthesis}"`);
    }

    // Verify character breakdown pills
    const pillCount = await page.locator('#drawer-sinosphere-breakdown .sinosphere-char-pill').count();
    console.log(`  Yamashiro character pill count: ${pillCount}`);
    if (pillCount !== 2) {
      throw new Error(`Expected 2 character pills for 山城, got ${pillCount}`);
    }

    // Test that selecting a non-Sinosphere title hides the Sinosphere card
    console.log('  Testing that non-Sinosphere selection hides #drawer-sinosphere-group...');
    await searchInput.fill('c_middlesex');
    await page.waitForSelector('#search-results .search-item[data-key="c_middlesex"]', { timeout: 5000 });
    const midItem = page.locator('#search-results .search-item[data-key="c_middlesex"]');
    await midItem.click();
    await page.waitForFunction(() => {
      return document.getElementById('drawer-title-key').innerText === 'c_middlesex';
    }, { timeout: 5000 });

    const sinoGroupHiddenForMid = await page.locator('#drawer-sinosphere-group').evaluate(el => el.classList.contains('hidden'));
    if (!sinoGroupHiddenForMid) {
      throw new Error('Expected #drawer-sinosphere-group to be hidden for non-Sinosphere title c_middlesex');
    }
    console.log('  Non-Sinosphere reset verified: #drawer-sinosphere-group is hidden.');

    // 6. Test Mouse Movement & Zero Residual Highlighting
    console.log('[7/8] Testing mouse hover sweep across territories (verifying zero residual highlights)...');
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

    // 7. Test Paradox Disclaimer & Take Preview Screenshot
    console.log('[8/8] Verifying Paradox interactive fan notice and capturing preview...');
    const footerText = await page.locator('.footer-disclaimer').innerText();
    if (!footerText.includes('Paradox Interactive AB') || !footerText.includes('non-commercial')) {
      throw new Error(`Missing Paradox disclaimer in footer: "${footerText}"`);
    }

    const previewPath = path.join(DOCS_DIR, 'preview.png');
    await page.screenshot({ path: previewPath });
    console.log(`  Captured preview screenshot: ${previewPath}`);

    // Test GitHub Pages 404 Fallback Page
    console.log('  Testing GitHub Pages 404 page navigation...');
    await page.goto(`${baseUrl}/404.html`, { waitUntil: 'domcontentloaded' });
    const notFoundTitle = await page.title();
    if (!notFoundTitle.includes('404')) {
      throw new Error(`Expected 404 page title, got "${notFoundTitle}"`);
    }
    const returnLink = page.locator('a.btn-return');
    if (!(await returnLink.isVisible())) {
      throw new Error('Expected .btn-return link on 404 page');
    }
    await returnLink.click();
    await page.waitForSelector('#map', { timeout: 5000 });
    console.log('  404 return navigation verified.');

    // 8. Test Mobile Viewport Layout & Touch Interactions (390x844 iPhone)
    console.log('[9/9] Testing Mobile Viewport (iPhone 14 / 390x844)...');
    const mobileContext = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true
    });
    const mobilePage = await mobileContext.newPage();
    await mobilePage.goto(`${baseUrl}/index.html`, { waitUntil: 'domcontentloaded' });
    await mobilePage.waitForSelector('#loading-overlay', { state: 'detached', timeout: 20000 });

    // Verify zero horizontal overflow on mobile body
    const mobileScrollWidth = await mobilePage.evaluate(() => document.body.scrollWidth);
    console.log(`  Mobile body scrollWidth: ${mobileScrollWidth}px (viewport: 390px)`);
    if (mobileScrollWidth > 390) {
      throw new Error(`Mobile horizontal overflow detected: scrollWidth is ${mobileScrollWidth}px > 390px`);
    }

    // Verify header elements fit neatly in mobile viewport
    const headerFit = await mobilePage.evaluate(() => {
      const search = document.querySelector('.search-container').getBoundingClientRect();
      const tiers = document.querySelector('.tier-selector').getBoundingClientRect();
      const actions = document.querySelector('.header-actions').getBoundingClientRect();
      return {
        searchFits: search.right <= 390 && search.width >= 280,
        tiersFit: tiers.right <= 390,
        actionsFit: actions.right <= 390
      };
    });
    if (!headerFit.searchFits || !headerFit.tiersFit || !headerFit.actionsFit) {
      throw new Error(`Header layout overflowed mobile screen: ${JSON.stringify(headerFit)}`);
    }
    console.log('  Mobile header layout verified (zero overflow, full-width search & tier pills).');

    // Test Search & Bottom-Sheet Drawer on Mobile
    console.log('  Testing mobile search selection & bottom sheet drawer...');
    const mobileSearch = mobilePage.locator('#title-search');
    await mobileSearch.fill('Stûlwîtzenburch');
    await mobilePage.waitForSelector('#search-results .search-item', { timeout: 5000 });
    const mobileFirstResult = mobilePage.locator('#search-results .search-item').first();
    await mobileFirstResult.click();

    await mobilePage.waitForSelector('#inspector-drawer.open', { timeout: 5000 });
    await mobilePage.waitForTimeout(400); // Allow bottom-sheet CSS transition
    const mobileDrawerRect = await mobilePage.locator('#inspector-drawer').boundingBox();
    console.log(`  Mobile drawer bottom sheet: width=${mobileDrawerRect.width}px, y=${mobileDrawerRect.y}px`);
    if (mobileDrawerRect.width !== 390) {
      throw new Error(`Expected mobile drawer width 390px, got ${mobileDrawerRect.width}px`);
    }
    if (mobileDrawerRect.y < 100) {
      throw new Error(`Expected bottom-sheet drawer to leave top map visible, got y=${mobileDrawerRect.y}`);
    }

    // Close mobile drawer via close button
    const mobileDrawerClose = mobilePage.locator('#drawer-close');
    await mobileDrawerClose.click();
    await mobilePage.waitForSelector('#inspector-drawer:not(.open)', { timeout: 5000 });
    console.log('  Mobile drawer closed successfully.');

    // Test Mobile Linguistics Modal
    console.log('  Testing mobile Linguistics Guide modal...');
    const mobileOpenGuide = mobilePage.locator('#btn-open-linguistics');
    await mobileOpenGuide.click();
    await mobilePage.waitForSelector('#linguistics-modal:not(.hidden)', { timeout: 5000 });
    const mobileModalDialog = mobilePage.locator('.linguistics-modal-dialog');
    const mobileModalRect = await mobileModalDialog.boundingBox();
    console.log(`  Mobile modal dialog: width=${mobileModalRect.width}px, height=${mobileModalRect.height}px`);
    if (mobileModalRect.width > 390) {
      throw new Error(`Mobile modal width overflow: ${mobileModalRect.width}px > 390px`);
    }

    // Switch to Lexicon tab on mobile
    const mobileLexiconTab = mobilePage.locator('.modal-tab-btn[data-tab="lexicon"]');
    await mobileLexiconTab.click();
    await mobilePage.waitForSelector('#tab-pane-lexicon.active:not(.hidden)', { timeout: 5000 });
    await mobilePage.waitForSelector('#lexicon-table-body tr td.lexicon-hanzi-cell', { timeout: 10000 });

    const mobileCloseGuide = mobilePage.locator('#btn-close-linguistics');
    await mobileCloseGuide.click();
    await mobilePage.waitForSelector('#linguistics-modal', { state: 'hidden', timeout: 5000 });
    console.log('  Mobile modal closed successfully.');

    // Test Mobile Barony Tier Legend & Hover info separation
    console.log('  Testing mobile Barony tier holding legend separation...');
    const mobileBaronyBtn = mobilePage.locator('.tier-btn[data-tier="barony"]');
    await mobileBaronyBtn.click();
    await mobilePage.waitForSelector('#barony-legend:not(.hidden)', { timeout: 10000 });
    const mobileLegendVisible = await mobilePage.locator('#barony-legend').isVisible();
    if (!mobileLegendVisible) {
      throw new Error('Expected #barony-legend to be visible in mobile Barony tier');
    }
    const mobileSeparate = await mobilePage.evaluate(() => {
      const legend = document.getElementById('barony-legend');
      const badge = document.querySelector('.map-stats-badge');
      return legend && badge && !badge.contains(legend);
    });
    if (!mobileSeparate) {
      throw new Error('Expected #barony-legend to be separate from .map-stats-badge on mobile');
    }
    console.log('  Mobile Barony holding legend verified as separate from tap inspector badge.');

    await mobilePage.close();
    await mobileContext.close();

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
