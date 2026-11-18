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

    // Check breadcrumbs
    const bcKingdom = await page.locator('#bc-kingdom').innerText();
    console.log(`  Lineage Kingdom: ${bcKingdom}`);
    if (!bcKingdom.includes('Ungern') && !bcKingdom.includes('Hungary')) {
      throw new Error(`Expected Hungarian kingdom breadcrumb, got "${bcKingdom}"`);
    }

    // 4. Test De Jure Tier Switching
    console.log('[5/6] Testing De Jure tier switching...');
    const kingdomBtn = page.locator('.tier-btn[data-tier="kingdom"]');
    await kingdomBtn.click();
    if (!(await kingdomBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('Kingdom tier button failed to activate');
    }

    const empireBtn = page.locator('.tier-btn[data-tier="empire"]');
    await empireBtn.click();
    if (!(await empireBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('Empire tier button failed to activate');
    }

    const countyBtn = page.locator('.tier-btn[data-tier="county"]');
    await countyBtn.click();
    if (!(await countyBtn.evaluate(el => el.classList.contains('active')))) {
      throw new Error('County tier button failed to re-activate');
    }
    console.log('  Tier switching (Kingdom -> Empire -> County) validated.');

    // 5. Test Paradox Disclaimer & Take Preview Screenshot
    console.log('[6/6] Verifying Paradox interactive fan notice and capturing preview...');
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
