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

    console.log(`  Drawer inspected: [${tierBadge}] ${tarrName} (${titleKey})`);
    if (tarrName !== 'Stûlwîtzenburch') {
      throw new Error(`Expected drawer tarr name "Stûlwîtzenburch", got "${tarrName}"`);
    }
    if (titleKey !== 'c_szekesfehervar') {
      throw new Error(`Expected title key "c_szekesfehervar", got "${titleKey}"`);
    }
    if (tierBadge.toUpperCase() !== 'COUNTY') {
      throw new Error(`Expected tier badge "COUNTY", got "${tierBadge}"`);
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

    // Verify exactly 1 title is selected
    const initialSelectedCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('fill') === '#993284').length;
    });
    if (initialSelectedCount !== 1) {
      throw new Error(`Expected exactly 1 selected territory, found ${initialSelectedCount}`);
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

    const secondSelectedCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('fill') === '#993284').length;
    });
    console.log(`  Selected territories count after second click: ${secondSelectedCount}`);
    if (secondSelectedCount !== 1) {
      throw new Error(`Residual selection detected! Expected exactly 1 selected territory, got ${secondSelectedCount}`);
    }

    const secondKingdom = await page.locator('#bc-kingdom').innerText();
    const secondEmpire = await page.locator('#bc-empire').innerText();
    console.log(`  Middelsachsen Lineage: Empire="${secondEmpire}", Kingdom="${secondKingdom}"`);
    if (!secondEmpire.includes('Germania') && !secondEmpire.includes('Germany')) {
      throw new Error(`Expected Germania empire breadcrumb for Middelsachsen, got "${secondEmpire}"`);
    }
    if (!secondKingdom.includes('Engellant') && !secondKingdom.includes('England')) {
      throw new Error(`Expected English kingdom breadcrumb, got "${secondKingdom}"`);
    }

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

    const kingdomSelectedCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('fill') === '#993284').length;
    });
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

    if (!(await duchyBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('Duchy tier button failed to activate on duchy pill click');
    }

    const duchySelectedCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('fill') === '#993284').length;
    });
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

    const countySelectedCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('fill') === '#993284').length;
    });
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

    if (!(await empireBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('Empire tier button failed to activate on empire breadcrumb click');
    }

    const empireSelectedCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('fill') === '#993284').length;
    });
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

    const franceSelectedCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('fill') === '#993284').length;
    });
    console.log(`  Selected counties for Kingdom of France: ${franceSelectedCount}`);
    if (franceSelectedCount <= 1 || franceSelectedCount === empireSelectedCount) {
      throw new Error(`Unexpected selection count for France: ${franceSelectedCount}`);
    }

    // Switch to Barony (lazy-loads 11,297 baronies)
    console.log('  Switching to Barony tier...');
    await baronyBtn.click();
    await page.waitForFunction(() => {
      return document.querySelectorAll('#map svg path').length === 11297;
    }, { timeout: 10000 });
    console.log('  Barony tier active: 11,297 holding polygons loaded.');

    // Switch back to County tier (must restore 3,476 county polygons)
    console.log('  Switching from Barony back to County tier...');
    await countyBtn.click();
    await page.waitForFunction(() => {
      return document.querySelectorAll('#map svg path').length === 3476;
    }, { timeout: 5000 });
    console.log('  Restored County tier: 3,476 county polygons loaded.');

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

    const closedSelectedCount = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('#map svg path'))
        .filter(p => p.getAttribute('fill') === '#993284').length;
    });
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

    // Move cursor away to ocean / corner
    await page.mouse.move(20, 100);
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
