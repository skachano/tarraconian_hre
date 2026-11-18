/**
 * Tarraconian Atlas — Interactive Cartography Application
 * Uses Leaflet with L.CRS.Simple for flat CK3 9216x4608 coordinates.
 */

// State
let map = null;
let currentTier = 'county';
let countiesGeojson = null;
let baroniesGeojson = null;
let titleTree = null;
let countiesLayer = null;
let baroniesLayer = null;
let selectedFeature = null;
let selectedLayer = null;
let hoveredLayer = null;

// Search index: array of { key, name, tarr, tier, bounds, layer }
let searchIndex = [];

// Deterministic color generator using a hash of string keys
function stringToColor(str, saturation = 55, lightness = 42) {
  if (!str) return '#333333';
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
    hash = hash & hash;
  }
  const h = Math.abs(hash) % 360;
  return `hsl(${h}, ${saturation}%, ${lightness}%)`;
}

// Format title string (e.g. c_szekesfehervar -> Szekesfehervar)
function formatKey(key) {
  if (!key) return '';
  return key.replace(/^[a-z]_/, '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
  initMap();
  setupEventListeners();
  await loadData();
});

function initMap() {
  const mapBounds = [[0, 0], [4608, 9216]];

  map = L.map('map', {
    crs: L.CRS.Simple,
    minZoom: -3,
    maxZoom: 2,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    attributionControl: false,
    maxBounds: [[-600, -600], [5208, 9816]],
    maxBoundsViscosity: 0.8
  });

  map.fitBounds(mapBounds);

  // Zoom to Europe/Mediterranean by default
  map.setView([2304, 4608], -2);

  // Clear any residual hover when leaving the canvas or moving over background ocean
  map.on('mouseout', clearHover);
  map.getContainer().addEventListener('mouseleave', clearHover);
  map.on('mousemove', (e) => {
    if (hoveredLayer && e.originalEvent && e.originalEvent.target && e.originalEvent.target.tagName !== 'path') {
      clearHover();
    }
  });
}

// ---------------------------------------------------------------------------
// Data Loading
// ---------------------------------------------------------------------------
async function loadData() {
  const overlay = document.getElementById('loading-overlay');
  const loadingText = document.getElementById('loading-text');

  try {
    loadingText.textContent = 'Loading title hierarchy index...';
    const treeRes = await fetch('data/ck3_title_tree.json');
    titleTree = await treeRes.json();

    loadingText.textContent = 'Loading county geography (3,476 territories)...';
    const countiesRes = await fetch('data/ck3_counties.geojson');
    countiesGeojson = await countiesRes.json();

    // Render primary layer
    renderActiveLayer();
    buildSearchIndex();

    overlay.classList.add('fade-out');
    setTimeout(() => overlay.remove(), 400);
  } catch (err) {
    console.error('Error loading map data:', err);
    loadingText.innerHTML = `<span style="color:#ff6b6b">Failed to load map data.</span><br><small>${err.message}</small>`;
  }
}

// Lazy-load baronies GeoJSON when requested
async function ensureBaroniesLoaded() {
  if (baroniesGeojson) return;
  const overlay = document.getElementById('loading-overlay') || createMiniOverlay();
  overlay.classList.remove('fade-out');
  const text = document.getElementById('loading-text');
  if (text) text.textContent = 'Loading holding polygons (11,297 baronies)...';

  try {
    const res = await fetch('data/ck3_baronies.geojson');
    baroniesGeojson = await res.json();
  } catch (err) {
    console.error('Failed to load baronies:', err);
  } finally {
    overlay.classList.add('fade-out');
  }
}

function createMiniOverlay() {
  const div = document.createElement('div');
  div.id = 'loading-overlay';
  div.className = 'loading-overlay';
  div.innerHTML = '<div class="loading-spinner"></div><p id="loading-text">Loading...</p>';
  document.querySelector('.app-main').appendChild(div);
  return div;
}

// ---------------------------------------------------------------------------
// Layer Rendering & Styling
// ---------------------------------------------------------------------------
function getFeatureColor(props, tier) {
  switch (tier) {
    case 'empire':
      return stringToColor(props.empire, 60, 38);
    case 'kingdom':
      return stringToColor(props.kingdom, 55, 42);
    case 'duchy':
      return stringToColor(props.duchy, 50, 45);
    case 'county':
      return stringToColor(props.county, 45, 40);
    case 'barony':
      return stringToColor(props.barony, 40, 42);
    default:
      return '#3d3832';
  }
}

function countyStyle(feature) {
  const p = feature.properties;
  return {
    fillColor: getFeatureColor(p, currentTier),
    fillOpacity: 0.65,
    color: '#0d0b09',
    weight: currentTier === 'county' ? 0.8 : 1.2,
    opacity: 0.9
  };
}

function baronyStyle(feature) {
  const p = feature.properties;
  return {
    fillColor: getFeatureColor(p, 'barony'),
    fillOpacity: 0.7,
    color: '#1a1614',
    weight: 0.5,
    opacity: 0.8
  };
}

function renderActiveLayer() {
  clearHover();
  if (currentTier === 'barony') {
    if (countiesLayer) map.removeLayer(countiesLayer);
    renderBaronies();
  } else {
    if (baroniesLayer) map.removeLayer(baroniesLayer);
    renderCounties();
  }
}

function renderCounties() {
  clearHover();
  if (countiesLayer) {
    countiesLayer.setStyle(countyStyle);
    if (selectedLayer) {
      selectedLayer.setStyle({
        weight: 3,
        color: '#ffffff',
        fillColor: '#993284',
        fillOpacity: 0.9
      });
    }
    return;
  }

  countiesLayer = L.geoJSON(countiesGeojson, {
    style: countyStyle,
    onEachFeature: (feature, layer) => {
      layer.on({
        mouseover: () => onHover(layer, feature),
        mouseout: () => onHoverOut(layer, feature),
        click: () => onSelect(layer, feature, currentTier)
      });
    }
  }).addTo(map);
}

async function renderBaronies() {
  clearHover();
  await ensureBaroniesLoaded();
  if (!baroniesGeojson) return;

  if (!baroniesLayer) {
    baroniesLayer = L.geoJSON(baroniesGeojson, {
      style: baronyStyle,
      onEachFeature: (feature, layer) => {
        layer.on({
          mouseover: () => onHover(layer, feature, 'barony'),
          mouseout: () => onHoverOut(layer, feature),
          click: () => onSelect(layer, feature, 'barony')
        });
      }
    });
  }

  baroniesLayer.addTo(map);
}

// ---------------------------------------------------------------------------
// Interaction Handlers (Hover, Click, Inspect)
// ---------------------------------------------------------------------------
function resetLayerStyle(layer) {
  if (!layer) return;
  if (currentTier === 'barony' && baroniesLayer) {
    baroniesLayer.resetStyle(layer);
  } else if (countiesLayer) {
    countiesLayer.resetStyle(layer);
  }
}

function clearHover() {
  if (hoveredLayer) {
    if (hoveredLayer !== selectedLayer) {
      resetLayerStyle(hoveredLayer);
    }
    hoveredLayer = null;
  }
  const hoverBadge = document.getElementById('hover-info');
  if (hoverBadge) {
    hoverBadge.innerHTML = 'Hover over a territory to inspect';
  }
}

function onHover(layer, feature, tier = currentTier) {
  if (!layer) return;

  // Immediately clear previous hover if moving between adjacent territories
  if (hoveredLayer && hoveredLayer !== layer) {
    if (hoveredLayer !== selectedLayer) {
      resetLayerStyle(hoveredLayer);
    }
  }
  hoveredLayer = layer;

  // Highlight only if this is not the actively selected inspection target
  if (layer !== selectedLayer) {
    layer.setStyle({
      weight: 2.5,
      color: '#f5d77f',
      fillOpacity: 0.85
    });
  }
  // Note: We intentionally avoid layer.bringToFront() here because DOM re-ordering
  // drops mouseout events and creates residual highlighting across SVG vector geometries.

  // Update floating status badge
  const hoverBadge = document.getElementById('hover-info');
  const p = feature.properties;
  let titleName = '';
  let rankLabel = '';

  if (tier === 'barony') {
    rankLabel = 'Holding';
    titleName = p.name || formatKey(p.barony);
  } else if (tier === 'county') {
    rankLabel = 'County';
    titleName = p.tarr_hist || p.tarr_direct || formatKey(p.county);
  } else if (tier === 'duchy') {
    rankLabel = 'Duchy';
    titleName = p.d_tarr || formatKey(p.duchy);
  } else if (tier === 'kingdom') {
    rankLabel = 'Kingdom';
    titleName = p.k_tarr || formatKey(p.kingdom);
  } else if (tier === 'empire') {
    rankLabel = 'Empire';
    titleName = p.e_tarr || formatKey(p.empire);
  }

  hoverBadge.innerHTML = `<strong>${rankLabel}:</strong> ${titleName} <span style="opacity:0.6;font-family:var(--font-mono)">(${p[tier] || p.county || ''})</span>`;
}

function onHoverOut(layer, feature) {
  if (layer === hoveredLayer) {
    clearHover();
  } else if (layer !== selectedLayer) {
    resetLayerStyle(layer);
  }
}

function onSelect(layer, feature, tier = currentTier) {
  if (!layer) return;

  // If a different layer was previously selected, restore its default style
  if (selectedLayer && selectedLayer !== layer) {
    resetLayerStyle(selectedLayer);
  }

  // Clear hover state
  if (hoveredLayer && hoveredLayer !== layer && hoveredLayer !== selectedLayer) {
    resetLayerStyle(hoveredLayer);
  }
  hoveredLayer = null;

  selectedFeature = feature;
  selectedLayer = layer;

  layer.setStyle({
    weight: 3,
    color: '#ffffff',
    fillColor: '#993284',
    fillOpacity: 0.9
  });

  openInspector(feature.properties, tier);
}

// ---------------------------------------------------------------------------
// Inspector Drawer
// ---------------------------------------------------------------------------
function openInspector(props, tier) {
  const drawer = document.getElementById('inspector-drawer');
  const badge = document.getElementById('drawer-tier-badge');
  const tarrName = document.getElementById('drawer-tarr-name');
  const canonicalName = document.getElementById('drawer-canonical-name');
  const titleKey = document.getElementById('drawer-title-key');
  const histGroup = document.getElementById('drawer-hist-group');
  const histName = document.getElementById('drawer-hist-name');
  const baroniesSection = document.getElementById('drawer-baronies-section');
  const baroniesList = document.getElementById('drawer-baronies-list');

  // Breadcrumbs elements
  const bcEmpire = document.getElementById('bc-empire');
  const bcKingdom = document.getElementById('bc-kingdom');
  const bcDuchy = document.getElementById('bc-duchy');
  const bcCounty = document.getElementById('bc-county');

  // Tier info
  badge.textContent = tier.toUpperCase();
  titleKey.textContent = props[tier] || props.county || props.barony || '';

  // Names
  const countyTarr = props.tarr_hist || props.tarr_direct || props.c_tarr_hist || props.c_tarr_direct || '';
  if (tier === 'county') {
    tarrName.textContent = countyTarr || formatKey(props.county);
    canonicalName.textContent = formatKey(props.county);
  } else if (tier === 'barony') {
    tarrName.textContent = props.name || formatKey(props.barony);
    canonicalName.textContent = props.name || formatKey(props.barony);
  } else if (tier === 'duchy') {
    tarrName.textContent = props.d_tarr || formatKey(props.duchy);
    canonicalName.textContent = formatKey(props.duchy);
  } else if (tier === 'kingdom') {
    tarrName.textContent = props.k_tarr || formatKey(props.kingdom);
    canonicalName.textContent = formatKey(props.kingdom);
  } else if (tier === 'empire') {
    tarrName.textContent = props.e_tarr || formatKey(props.empire);
    canonicalName.textContent = formatKey(props.empire);
  }

  // Historical resolution (if applicable and distinct)
  if (props.tarr_hist && props.tarr_direct && props.tarr_hist !== props.tarr_direct) {
    histGroup.classList.remove('hidden');
    histName.textContent = `${props.tarr_hist} (Direct: ${props.tarr_direct})`;
  } else {
    histGroup.classList.add('hidden');
  }

  // Breadcrumbs
  bcEmpire.textContent = props.e_tarr || formatKey(props.empire);
  bcKingdom.textContent = props.k_tarr || formatKey(props.kingdom);
  bcDuchy.textContent = props.d_tarr || formatKey(props.duchy);
  bcCounty.textContent = countyTarr || formatKey(props.county);

  // Baronies list
  if (props.baronies && props.baronies.length > 0) {
    baroniesSection.classList.remove('hidden');
    baroniesList.innerHTML = props.baronies.map(b => `<li class="barony-pill">${b}</li>`).join('');
  } else {
    baroniesSection.classList.add('hidden');
    baroniesList.innerHTML = '';
  }

  drawer.classList.add('open');
}

function closeInspector() {
  document.getElementById('inspector-drawer').classList.remove('open');
  if (selectedLayer) {
    const prev = selectedLayer;
    selectedLayer = null;
    selectedFeature = null;
    resetLayerStyle(prev);
  }
  clearHover();
}

// ---------------------------------------------------------------------------
// Search & Quick Jump Index
// ---------------------------------------------------------------------------
function buildSearchIndex() {
  searchIndex = [];
  if (!countiesGeojson) return;

  for (const feat of countiesGeojson.features) {
    const p = feat.properties;
    const entry = {
      key: p.county,
      tarr: p.tarr_hist || p.tarr_direct || '',
      canonical: formatKey(p.county),
      duchy: p.d_tarr || formatKey(p.duchy),
      kingdom: p.k_tarr || formatKey(p.kingdom),
      empire: p.e_tarr || formatKey(p.empire),
      feature: feat
    };
    searchIndex.push(entry);
  }
}

function handleSearch(query) {
  const dropdown = document.getElementById('search-results');
  const clearBtn = document.getElementById('search-clear');
  query = query.trim().toLowerCase();

  if (!query) {
    dropdown.classList.add('hidden');
    dropdown.innerHTML = '';
    clearBtn.style.display = 'none';
    return;
  }

  clearBtn.style.display = 'block';

  // Filter top matches
  const matches = searchIndex.filter(item => {
    return (
      item.key.toLowerCase().includes(query) ||
      item.tarr.toLowerCase().includes(query) ||
      item.canonical.toLowerCase().includes(query)
    );
  }).slice(0, 10);

  if (matches.length === 0) {
    dropdown.innerHTML = '<div class="search-item"><span style="color:var(--text-dim)">No titles found</span></div>';
    dropdown.classList.remove('hidden');
    return;
  }

  dropdown.innerHTML = matches.map(m => `
    <div class="search-item" data-key="${m.key}">
      <div class="search-item-primary">${m.tarr || m.canonical}</div>
      <div class="search-item-secondary">
        <code>${m.key}</code> &bull; <span>${m.kingdom} (${m.empire})</span>
      </div>
    </div>
  `).join('');

  dropdown.classList.remove('hidden');

  dropdown.querySelectorAll('.search-item').forEach(el => {
    el.addEventListener('click', () => {
      const key = el.getAttribute('data-key');
      jumpToTitle(key);
      dropdown.classList.add('hidden');
    });
  });
}

function jumpToTitle(countyKey) {
  if (!countiesLayer) return;
  const targetLayer = countiesLayer.getLayers().find(l => l.feature && l.feature.properties.county === countyKey);
  if (targetLayer) {
    const bounds = targetLayer.getBounds();
    map.fitBounds(bounds, { maxZoom: 0, padding: [60, 60] });
    onSelect(targetLayer, targetLayer.feature, 'county');
  }
}

// ---------------------------------------------------------------------------
// Event Listeners
// ---------------------------------------------------------------------------
function setupEventListeners() {
  // Tier pills
  document.querySelectorAll('.tier-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTier = btn.getAttribute('data-tier');
      renderActiveLayer();
      if (selectedFeature) {
        openInspector(selectedFeature.properties, currentTier);
      }
    });
  });

  // Drawer close & zoom
  document.getElementById('drawer-close').addEventListener('click', closeInspector);
  document.getElementById('drawer-zoom-btn').addEventListener('click', () => {
    if (selectedLayer) {
      map.fitBounds(selectedLayer.getBounds(), { padding: [80, 80] });
    }
  });

  // Search input
  const searchInput = document.getElementById('title-search');
  searchInput.addEventListener('input', (e) => handleSearch(e.target.value));
  searchInput.addEventListener('focus', (e) => {
    if (e.target.value) handleSearch(e.target.value);
  });

  document.getElementById('search-clear').addEventListener('click', () => {
    searchInput.value = '';
    handleSearch('');
    searchInput.focus();
  });

  // Close search dropdown on click outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-container')) {
      document.getElementById('search-results').classList.add('hidden');
    }
  });
}
