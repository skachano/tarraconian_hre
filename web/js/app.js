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

// Multi-feature selection and hover state
let selectedFeature = null;
let selectedLayers = [];
let selectedTitleKey = null;
let selectedTitleTier = null;

let hoveredLayers = [];
let hoveredTitleKey = null;

// Title to Leaflet layer lookup maps
const countyLayerMap = new Map();
const duchyLayersMap = new Map();
const kingdomLayersMap = new Map();
const empireLayersMap = new Map();
const baronyLayerMap = new Map();

// Search index: array of { key, name, tarr, tier, origin, empire, kingdom, duchy, feature }
let searchIndex = [];

// Fallback deterministic color generator
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
    if (hoveredLayers.length > 0 && e.originalEvent && e.originalEvent.target && e.originalEvent.target.tagName !== 'path') {
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
    setTimeout(() => overlay.remove(), 400);
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
      return props.e_color || stringToColor(props.empire, 60, 38);
    case 'kingdom':
      return props.k_color || stringToColor(props.kingdom, 55, 42);
    case 'duchy':
      return props.d_color || stringToColor(props.duchy, 50, 45);
    case 'county':
      return props.c_color || stringToColor(props.county, 45, 40);
    case 'barony':
      return props.b_color || stringToColor(props.barony, 40, 42);
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

function getLayersForTitle(tier, props) {
  if (!props) return [];
  if (tier === 'barony') {
    const l = baronyLayerMap.get(props.barony);
    return l ? [l] : [];
  }
  if (tier === 'county') {
    const l = countyLayerMap.get(props.county);
    return l ? [l] : [];
  }
  if (tier === 'duchy') {
    return duchyLayersMap.get(props.duchy) || [];
  }
  if (tier === 'kingdom') {
    return kingdomLayersMap.get(props.kingdom) || [];
  }
  if (tier === 'empire') {
    return empireLayersMap.get(props.empire) || [];
  }
  return [];
}

function getTitleKeyForTier(props, tier) {
  if (!props) return '';
  if (tier === 'barony') return props.barony || '';
  if (tier === 'county') return props.county || '';
  if (tier === 'duchy') return props.duchy || '';
  if (tier === 'kingdom') return props.kingdom || '';
  if (tier === 'empire') return props.empire || '';
  return props.county || '';
}

function renderCounties() {
  clearHover();
  if (countiesLayer) {
    if (!map.hasLayer(countiesLayer)) {
      countiesLayer.addTo(map);
    }
    countiesLayer.setStyle(countyStyle);
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

  // Build title maps for instant O(1) title lookup
  countyLayerMap.clear();
  duchyLayersMap.clear();
  kingdomLayersMap.clear();
  empireLayersMap.clear();

  countiesLayer.eachLayer(layer => {
    const p = layer.feature.properties;
    if (p.county) countyLayerMap.set(p.county, layer);
    if (p.duchy) {
      if (!duchyLayersMap.has(p.duchy)) duchyLayersMap.set(p.duchy, []);
      duchyLayersMap.get(p.duchy).push(layer);
    }
    if (p.kingdom) {
      if (!kingdomLayersMap.has(p.kingdom)) kingdomLayersMap.set(p.kingdom, []);
      kingdomLayersMap.get(p.kingdom).push(layer);
    }
    if (p.empire) {
      if (!empireLayersMap.has(p.empire)) empireLayersMap.set(p.empire, []);
      empireLayersMap.get(p.empire).push(layer);
    }
  });
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

    baronyLayerMap.clear();
    baroniesLayer.eachLayer(layer => {
      const p = layer.feature.properties;
      if (p.barony) baronyLayerMap.set(p.barony, layer);
    });
  }

  if (!map.hasLayer(baroniesLayer)) {
    baroniesLayer.addTo(map);
  }
  baroniesLayer.setStyle(baronyStyle);
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
  if (hoveredLayers.length > 0) {
    const selectedSet = new Set(selectedLayers);
    for (const l of hoveredLayers) {
      if (!selectedSet.has(l)) {
        resetLayerStyle(l);
      }
    }
    hoveredLayers = [];
  }
  hoveredTitleKey = null;
  const hoverBadge = document.getElementById('hover-info');
  if (hoverBadge) {
    hoverBadge.innerHTML = 'Hover over a territory to inspect';
  }
}

function onHover(layer, feature, tier = currentTier) {
  if (!layer || !feature) return;

  const titleKey = getTitleKeyForTier(feature.properties, tier);
  if (hoveredTitleKey === titleKey) return;

  clearHover();
  hoveredTitleKey = titleKey;

  const targetLayers = getLayersForTitle(tier, feature.properties);
  hoveredLayers = targetLayers;

  const selectedSet = new Set(selectedLayers);
  const isMulti = tier === 'empire' || tier === 'kingdom' || tier === 'duchy';
  for (const l of targetLayers) {
    if (!selectedSet.has(l)) {
      l.setStyle({
        weight: isMulti ? 2.0 : 2.5,
        color: '#f5d77f',
        fillOpacity: 0.85
      });
    }
  }

  // Update floating status badge
  const hoverBadge = document.getElementById('hover-info');
  if (hoverBadge) {
    const p = feature.properties;
    let titleName = '';
    let rankLabel = '';

    if (tier === 'barony') {
      rankLabel = 'Holding';
      titleName = p.name || formatKey(p.barony);
    } else if (tier === 'county') {
      rankLabel = 'County';
      titleName = p.tarr_hist || p.tarr_direct || p.tarr || formatKey(p.county);
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

    hoverBadge.innerHTML = `<strong>${rankLabel}:</strong> ${titleName} <span style="opacity:0.6;font-family:var(--font-mono)">(${titleKey})</span>`;
  }
}

function onHoverOut(layer, feature) {
  if (hoveredLayers.includes(layer)) {
    clearHover();
  } else if (!selectedLayers.includes(layer)) {
    resetLayerStyle(layer);
  }
}

function onSelect(layer, feature, tier = currentTier) {
  if (!feature) return;

  const titleKey = getTitleKeyForTier(feature.properties, tier);

  // If previous selection exists, reset all previous layers
  if (selectedLayers.length > 0) {
    for (const l of selectedLayers) {
      resetLayerStyle(l);
    }
    selectedLayers = [];
  }

  clearHover();

  selectedFeature = feature;
  selectedTitleKey = titleKey;
  selectedTitleTier = tier;

  // Retrieve all layers corresponding to this title tier
  const targetLayers = getLayersForTitle(tier, feature.properties);
  selectedLayers = targetLayers;

  const isMulti = tier === 'empire' || tier === 'kingdom' || tier === 'duchy';
  for (const l of targetLayers) {
    l.setStyle({
      weight: isMulti ? 2.0 : 3.0,
      color: '#ffffff',
      fillColor: '#993284',
      fillOpacity: 0.9
    });
  }

  openInspector(feature.properties, tier);
}

// ---------------------------------------------------------------------------
// Inspector Drawer
// ---------------------------------------------------------------------------
function openInspector(props, tier) {
  const drawer = document.getElementById('inspector-drawer');
  const badge = document.getElementById('drawer-tier-badge');
  const tarrName = document.getElementById('drawer-tarr-name');
  const originName = document.getElementById('drawer-origin-name');
  const titleKeyElem = document.getElementById('drawer-title-key');
  const histGroup = document.getElementById('drawer-hist-group');
  const histName = document.getElementById('drawer-hist-name');
  const baroniesSection = document.getElementById('drawer-baronies-section');
  const baroniesLabel = document.getElementById('drawer-baronies-label');
  const baroniesList = document.getElementById('drawer-baronies-list');

  // Breadcrumbs elements
  const bcEmpire = document.getElementById('bc-empire');
  const bcKingdom = document.getElementById('bc-kingdom');
  const bcDuchy = document.getElementById('bc-duchy');
  const bcCounty = document.getElementById('bc-county');

  // Tier info & Title Key
  badge.textContent = tier.toUpperCase();
  const currentKey = getTitleKeyForTier(props, tier);
  titleKeyElem.textContent = currentKey;

  // Title Names & Anachronism Analysis for active tier
  const countyTarr = props.tarr_hist || props.tarr_direct || props.c_tarr_hist || props.c_tarr_direct || props.tarr || props.c_tarr || '';
  let currentAnachronism = '';
  let currentIpa = '';

  if (tier === 'county') {
    tarrName.textContent = countyTarr || formatKey(props.county);
    originName.textContent = props.c_origin || formatKey(props.county);
    currentAnachronism = props.c_anachronism || '';
    currentIpa = props.c_ipa || props.ipa || '';
  } else if (tier === 'barony') {
    tarrName.textContent = props.name || formatKey(props.barony);
    originName.textContent = props.b_origin || props.name || formatKey(props.barony);
    currentAnachronism = props.b_anachronism || props.c_anachronism || '';
    currentIpa = props.b_ipa || props.ipa || '';
  } else if (tier === 'duchy') {
    tarrName.textContent = props.d_tarr || formatKey(props.duchy);
    originName.textContent = props.d_origin || formatKey(props.duchy);
    currentAnachronism = props.d_anachronism || '';
    currentIpa = props.d_ipa || props.ipa || '';
  } else if (tier === 'kingdom') {
    tarrName.textContent = props.k_tarr || formatKey(props.kingdom);
    originName.textContent = props.k_origin || formatKey(props.kingdom);
    currentAnachronism = props.k_anachronism || '';
    currentIpa = props.k_ipa || props.ipa || '';
  } else if (tier === 'empire') {
    tarrName.textContent = props.e_tarr || formatKey(props.empire);
    originName.textContent = props.e_origin || formatKey(props.empire);
    currentAnachronism = props.e_anachronism || '';
    currentIpa = props.e_ipa || props.ipa || '';
  }

  const anachNote = document.getElementById('drawer-anachronism-note');
  if (anachNote) {
    if (currentAnachronism) {
      anachNote.innerHTML = `<strong>ℹ️ Anachronistic Title Analysis:</strong> ${currentAnachronism}`;
      anachNote.classList.remove('hidden');
    } else {
      anachNote.classList.add('hidden');
      anachNote.innerHTML = '';
    }
  }

  const ipaGroup = document.getElementById('drawer-ipa-group');
  const ipaVal = document.getElementById('drawer-ipa');
  if (ipaGroup && ipaVal) {
    if (currentIpa) {
      ipaVal.textContent = currentIpa;
      ipaGroup.classList.remove('hidden');
    } else {
      ipaGroup.classList.add('hidden');
      ipaVal.textContent = '—';
    }
  }

  // Historical resolution (if applicable)
  let histRes = '';
  if (tier === 'county') {
    if (props.tarr_hist && props.tarr_direct && props.tarr_hist !== props.tarr_direct) {
      histRes = props.tarr_hist;
    }
  } else if (tier === 'duchy') {
    if (props.d_tarr_hist && props.d_tarr_direct && props.d_tarr_hist !== props.d_tarr_direct) {
      histRes = props.d_tarr_hist;
    }
  } else if (tier === 'kingdom') {
    if (props.k_tarr_hist && props.k_tarr_direct && props.k_tarr_hist !== props.k_tarr_direct) {
      histRes = props.k_tarr_hist;
    }
  } else if (tier === 'empire') {
    if (props.e_tarr_hist && props.e_tarr_direct && props.e_tarr_hist !== props.e_tarr_direct) {
      histRes = props.e_tarr_hist;
    }
  }

  if (histRes) {
    histGroup.classList.remove('hidden');
    histName.textContent = histRes;
  } else {
    histGroup.classList.add('hidden');
    histName.textContent = '—';
  }

  // Breadcrumbs
  bcEmpire.textContent = props.e_tarr || formatKey(props.empire);
  bcKingdom.textContent = props.k_tarr || formatKey(props.kingdom);
  bcDuchy.textContent = props.d_tarr || formatKey(props.duchy);
  bcCounty.textContent = countyTarr || formatKey(props.county);

  // Active breadcrumb style
  document.querySelectorAll('.bc-item').forEach(el => el.classList.remove('active'));
  const activeBc = document.getElementById(`bc-${tier}`);
  if (activeBc) activeBc.classList.add('active');

  // Breadcrumb interactive click-to-select
  bcEmpire.onclick = () => selectTitleByKey(props.empire, 'empire');
  bcKingdom.onclick = () => selectTitleByKey(props.kingdom, 'kingdom');
  bcDuchy.onclick = () => selectTitleByKey(props.duchy, 'duchy');
  bcCounty.onclick = () => selectTitleByKey(props.county, 'county');

  // Constituent Titles list in drawer
  renderConstituentTitles(props, tier, baroniesSection, baroniesLabel, baroniesList);

  drawer.classList.add('open');
}

function renderConstituentTitles(props, tier, section, label, listElem) {
  if (tier === 'empire') {
    const empData = titleTree ? titleTree[props.empire] : null;
    const kingdoms = empData ? Object.entries(empData.kingdoms || {}) : [];
    if (kingdoms.length > 0) {
      section.classList.remove('hidden');
      label.textContent = `Constituent Kingdoms (${kingdoms.length})`;
      listElem.innerHTML = kingdoms.map(([k_k, k_data]) => {
        const name = k_data.tarr || formatKey(k_k);
        return `<li class="barony-pill" data-key="${k_k}" data-tier="kingdom" style="cursor:pointer" title="Click to inspect ${name}">${name} <small style="opacity:0.6;font-family:var(--font-mono)">(${k_k})</small></li>`;
      }).join('');
      attachPillHandlers(listElem);
    } else {
      section.classList.add('hidden');
      listElem.innerHTML = '';
    }
  } else if (tier === 'kingdom') {
    const empData = titleTree ? titleTree[props.empire] : null;
    const kData = empData && empData.kingdoms ? empData.kingdoms[props.kingdom] : null;
    const duchies = kData ? Object.entries(kData.duchies || {}) : [];
    if (duchies.length > 0) {
      section.classList.remove('hidden');
      label.textContent = `Constituent Duchies (${duchies.length})`;
      listElem.innerHTML = duchies.map(([d_k, d_data]) => {
        const name = d_data.tarr || formatKey(d_k);
        return `<li class="barony-pill" data-key="${d_k}" data-tier="duchy" style="cursor:pointer" title="Click to inspect ${name}">${name} <small style="opacity:0.6;font-family:var(--font-mono)">(${d_k})</small></li>`;
      }).join('');
      attachPillHandlers(listElem);
    } else {
      section.classList.add('hidden');
      listElem.innerHTML = '';
    }
  } else if (tier === 'duchy') {
    const empData = titleTree ? titleTree[props.empire] : null;
    const kData = empData && empData.kingdoms ? empData.kingdoms[props.kingdom] : null;
    const dData = kData && kData.duchies ? kData.duchies[props.duchy] : null;
    const counties = dData ? Object.entries(dData.counties || {}) : [];
    if (counties.length > 0) {
      section.classList.remove('hidden');
      label.textContent = `Constituent Counties (${counties.length})`;
      listElem.innerHTML = counties.map(([c_k, c_data]) => {
        const name = c_data.tarr || c_data.tarr_hist || c_data.tarr_direct || formatKey(c_k);
        return `<li class="barony-pill" data-key="${c_k}" data-tier="county" style="cursor:pointer" title="Click to inspect ${name}">${name} <small style="opacity:0.6;font-family:var(--font-mono)">(${c_k})</small></li>`;
      }).join('');
      attachPillHandlers(listElem);
    } else {
      section.classList.add('hidden');
      listElem.innerHTML = '';
    }
  } else if (tier === 'county') {
    if (props.baronies && props.baronies.length > 0) {
      section.classList.remove('hidden');
      label.textContent = `Constituent Holdings (Baronies)`;
      listElem.innerHTML = props.baronies.map(b => `<li class="barony-pill" data-key="${b}" data-tier="barony" style="cursor:pointer">${b}</li>`).join('');
      attachPillHandlers(listElem);
    } else {
      section.classList.add('hidden');
      listElem.innerHTML = '';
    }
  } else {
    section.classList.add('hidden');
    listElem.innerHTML = '';
  }
}

function attachPillHandlers(listElem) {
  listElem.querySelectorAll('.barony-pill[data-key]').forEach(pill => {
    pill.addEventListener('click', () => {
      const key = pill.getAttribute('data-key');
      const targetTier = pill.getAttribute('data-tier');
      selectTitleByKey(key, targetTier);
    });
  });
}

async function selectTitleByKey(titleKey, tier) {
  if (!titleKey) return;

  if (tier === 'barony') {
    document.querySelectorAll('.tier-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tier') === 'barony');
    });
    currentTier = 'barony';
    renderActiveLayer();
    await ensureBaroniesLoaded();
    const bLayer = baronyLayerMap.get(titleKey);
    if (bLayer) {
      onSelect(bLayer, bLayer.feature, 'barony');
      map.fitBounds(bLayer.getBounds(), { padding: [60, 60] });
    }
    return;
  }

  if (!countiesLayer) return;

  // Find a representative county feature carrying this title key
  const matchLayer = countiesLayer.getLayers().find(l => {
    const p = l.feature.properties;
    return (tier === 'empire' && p.empire === titleKey) ||
           (tier === 'kingdom' && p.kingdom === titleKey) ||
           (tier === 'duchy' && p.duchy === titleKey) ||
           (tier === 'county' && p.county === titleKey);
  });

  if (matchLayer) {
    // If target tier is different from current, switch tier
    if (tier !== currentTier) {
      document.querySelectorAll('.tier-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tier') === tier);
      });
      currentTier = tier;
      renderActiveLayer();
    }

    onSelect(matchLayer, matchLayer.feature, tier);

    // Zoom to title bounds
    if (selectedLayers.length > 0) {
      const group = L.featureGroup(selectedLayers);
      map.fitBounds(group.getBounds(), { padding: [60, 60] });
    }
  }
}

function closeInspector() {
  document.getElementById('inspector-drawer').classList.remove('open');
  if (selectedLayers.length > 0) {
    for (const l of selectedLayers) {
      resetLayerStyle(l);
    }
    selectedLayers = [];
  }
  selectedFeature = null;
  selectedTitleKey = null;
  selectedTitleTier = null;
  clearHover();
}

// ---------------------------------------------------------------------------
// Search & Quick Jump Index
// ---------------------------------------------------------------------------
function buildSearchIndex() {
  searchIndex = [];
  if (!countiesGeojson) return;

  // 1. Index all counties
  for (const feat of countiesGeojson.features) {
    const p = feat.properties;
    searchIndex.push({
      key: p.county,
      tarr: p.tarr_hist || p.tarr_direct || p.tarr || '',
      origin: p.c_origin || formatKey(p.county),
      tier: 'county',
      duchy: p.d_tarr || formatKey(p.duchy),
      kingdom: p.k_tarr || formatKey(p.kingdom),
      empire: p.e_tarr || formatKey(p.empire),
      feature: feat
    });
  }

  // 2. Index higher-tier titles from titleTree for search
  if (titleTree) {
    for (const [e_k, e_data] of Object.entries(titleTree)) {
      searchIndex.push({
        key: e_k,
        tarr: e_data.tarr || formatKey(e_k),
        origin: e_data.origin || formatKey(e_k),
        tier: 'empire',
        empire: e_data.tarr || formatKey(e_k),
        feature: null
      });

      for (const [k_k, k_data] of Object.entries(e_data.kingdoms || {})) {
        searchIndex.push({
          key: k_k,
          tarr: k_data.tarr || formatKey(k_k),
          origin: k_data.origin || formatKey(k_k),
          tier: 'kingdom',
          kingdom: k_data.tarr || formatKey(k_k),
          empire: e_data.tarr || formatKey(e_k),
          feature: null
        });

        for (const [d_k, d_data] of Object.entries(k_data.duchies || {})) {
          searchIndex.push({
            key: d_k,
            tarr: d_data.tarr || formatKey(d_k),
            origin: d_data.origin || formatKey(d_k),
            tier: 'duchy',
            duchy: d_data.tarr || formatKey(d_k),
            kingdom: k_data.tarr || formatKey(k_k),
            empire: e_data.tarr || formatKey(e_k),
            feature: null
          });
        }
      }
    }
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
      (item.origin && item.origin.toLowerCase().includes(query))
    );
  }).slice(0, 10);

  if (matches.length === 0) {
    dropdown.innerHTML = '<div class="search-item"><span style="color:var(--text-dim)">No titles found</span></div>';
    dropdown.classList.remove('hidden');
    return;
  }

  dropdown.innerHTML = matches.map(m => {
    let subline = '';
    if (m.tier === 'empire') {
      subline = `Empire`;
    } else if (m.tier === 'kingdom') {
      subline = `Kingdom &bull; ${m.empire}`;
    } else if (m.tier === 'duchy') {
      subline = `Duchy &bull; ${m.kingdom} (${m.empire})`;
    } else {
      subline = `${m.kingdom} (${m.empire})`;
    }
    const originLabel = m.origin && m.origin !== m.tarr ? ` &bull; <em>${m.origin}</em>` : '';
    return `
      <div class="search-item" data-key="${m.key}" data-tier="${m.tier}">
        <div class="search-item-primary">${m.tarr || m.origin} <span style="font-size:0.7rem;opacity:0.5;text-transform:uppercase">[${m.tier}]</span></div>
        <div class="search-item-secondary">
          <code>${m.key}</code>${originLabel} &bull; <span>${subline}</span>
        </div>
      </div>
    `;
  }).join('');

  dropdown.classList.remove('hidden');

  dropdown.querySelectorAll('.search-item').forEach(el => {
    el.addEventListener('click', () => {
      const key = el.getAttribute('data-key');
      const tier = el.getAttribute('data-tier') || 'county';
      selectTitleByKey(key, tier);
      dropdown.classList.add('hidden');
    });
  });
}

// ---------------------------------------------------------------------------
// Event Listeners
// ---------------------------------------------------------------------------
function setupEventListeners() {
  // Tier pills
  document.querySelectorAll('.tier-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTier = btn.getAttribute('data-tier');
      renderActiveLayer();

      if (selectedFeature) {
        if (currentTier === 'barony') {
          await ensureBaroniesLoaded();
          let baronyKey = selectedFeature.properties.barony;
          if (!baronyKey && selectedFeature.properties.baronies && selectedFeature.properties.baronies.length > 0) {
            baronyKey = selectedFeature.properties.baronies[0];
          }
          if (baronyKey && baronyLayerMap.has(baronyKey)) {
            const bLayer = baronyLayerMap.get(baronyKey);
            onSelect(bLayer, bLayer.feature, 'barony');
          } else {
            closeInspector();
          }
        } else {
          // If previous selection was a barony, retrieve its county feature
          let feat = selectedFeature;
          if (feat.properties.barony && feat.properties.county && countyLayerMap.has(feat.properties.county)) {
            feat = countyLayerMap.get(feat.properties.county).feature;
          }
          onSelect(null, feat, currentTier);
        }
      }
    });
  });

  // Drawer close & zoom
  document.getElementById('drawer-close').addEventListener('click', closeInspector);
  document.getElementById('drawer-zoom-btn').addEventListener('click', () => {
    if (selectedLayers.length > 0) {
      const group = L.featureGroup(selectedLayers);
      map.fitBounds(group.getBounds(), { padding: [60, 60] });
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
  });

  // Keyboard escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeInspector();
      document.getElementById('search-results').classList.add('hidden');
    }
  });
}
