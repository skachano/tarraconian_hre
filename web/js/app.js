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
const baronyPropsMap = new Map();

// Sinosphere Hanzi & Calque datasets
let sinosphereCalques = null;
let sinosphereKanjiList = null;

// Search index: array of { key, name, tarr, tier, origin, empire, kingdom, duchy, feature, hanzi }
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
  map.on('click', () => {
    const searchDropdown = document.getElementById('search-results');
    if (searchDropdown && !searchDropdown.classList.contains('hidden')) {
      searchDropdown.classList.add('hidden');
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

    // Load Sinosphere Hanzi & Calque metadata
    try {
      const sinoRes = await fetch('data/sinosphere_hanzi_calques.json');
      if (sinoRes.ok) {
        sinosphereCalques = await sinoRes.json();
      }
    } catch (e) {
      console.warn('Could not load sinosphere_hanzi_calques.json:', e);
    }

    // Render primary layer
    renderActiveLayer();
    buildSearchIndex();

    const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    const hoverBadge = document.getElementById('hover-info');
    if (hoverBadge && isTouch) {
      hoverBadge.textContent = 'Tap a territory to inspect';
    }

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
    if (baroniesGeojson && baroniesGeojson.features) {
      for (const feat of baroniesGeojson.features) {
        if (feat.properties && feat.properties.barony) {
          baronyPropsMap.set(feat.properties.barony, feat.properties);
        }
      }
      indexBaroniesForSearch();
    }
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
  const legend = document.getElementById('barony-legend');
  if (legend) {
    legend.classList.toggle('hidden', currentTier !== 'barony');
  }
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
    const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    hoverBadge.innerHTML = isTouch ? 'Tap a territory to inspect' : 'Hover over a territory to inspect';
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
      const isUnoccupied = p.holding_type === 'unoccupied';
      if (isUnoccupied) {
        rankLabel = 'Holding (Unoccupied)';
        titleName = '';
      } else {
        const htName = p.holding_type_name || (p.holding_type ? p.holding_type.charAt(0).toUpperCase() + p.holding_type.slice(1) : '');
        rankLabel = htName ? `Holding (${htName})` : 'Holding';
        titleName = p.name || formatKey(p.barony);
      }
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

    if (tier === 'barony' && p.holding_type === 'unoccupied') {
      hoverBadge.innerHTML = `<strong>${rankLabel}:</strong> <span style="opacity:0.6;font-family:var(--font-mono)">(${titleKey})</span>`;
    } else {
      hoverBadge.innerHTML = `<strong>${rankLabel}:</strong> ${titleName} <span style="opacity:0.6;font-family:var(--font-mono)">(${titleKey})</span>`;
    }
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
      weight: isMulti ? 2.5 : 3.0,
      color: '#ffffff',
      opacity: 1.0
    });
    if (l.bringToFront) {
      l.bringToFront();
    }
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

  const originGroup = document.getElementById('drawer-origin-group');
  const isUnoccupiedBarony = tier === 'barony' && props.holding_type === 'unoccupied';

  // Tier info & Title Key
  if (tier === 'barony') {
    if (isUnoccupiedBarony) {
      badge.textContent = 'HOLDING · UNOCCUPIED';
    } else {
      const htName = props.holding_type_name || (props.holding_type ? props.holding_type.charAt(0).toUpperCase() + props.holding_type.slice(1) : '');
      badge.textContent = htName ? `HOLDING · ${htName.toUpperCase()}` : 'HOLDING';
    }
  } else {
    badge.textContent = tier.toUpperCase();
  }
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
    if (isUnoccupiedBarony) {
      tarrName.textContent = '';
      originName.textContent = '';
    } else {
      tarrName.textContent = props.name || formatKey(props.barony);
      originName.textContent = props.b_origin || props.name || formatKey(props.barony);
    }
    currentAnachronism = isUnoccupiedBarony ? '' : (props.b_anachronism || props.c_anachronism || '');
    currentIpa = isUnoccupiedBarony ? '' : (props.b_ipa || props.ipa || '');
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

  if (originGroup) {
    if (isUnoccupiedBarony) {
      originGroup.classList.add('hidden');
    } else {
      originGroup.classList.remove('hidden');
    }
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
  } else if (tier === 'barony') {
    if (props.b_tarr_hist && props.b_tarr_direct && props.b_tarr_hist !== props.b_tarr_direct) {
      histRes = props.b_tarr_hist;
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

  // Sinosphere Hanzi & Calque Analysis
  const sinoGroup = document.getElementById('drawer-sinosphere-group');
  const sinoHanziElem = document.getElementById('drawer-sinosphere-hanzi');
  const sinoReadingElem = document.getElementById('drawer-sinosphere-reading');
  const sinoStatusElem = document.getElementById('drawer-sinosphere-status');
  const sinoBreakdownElem = document.getElementById('drawer-sinosphere-breakdown');
  const sinoSynthesisElem = document.getElementById('drawer-sinosphere-synthesis');
  const sinoSubstrateElem = document.getElementById('drawer-sinosphere-substrate');

  let sinoEntry = sinosphereCalques ? sinosphereCalques[currentKey] : null;
  if (!sinoEntry) {
    const propHanzi = (tier === 'county' ? props.c_hanzi :
                       tier === 'duchy' ? (props.d_hanzi || props.hanzi) :
                       tier === 'kingdom' ? (props.k_hanzi || props.hanzi) :
                       tier === 'empire' ? (props.e_hanzi || props.hanzi) :
                       tier === 'barony' ? (props.b_hanzi || props.c_hanzi) : '');
    if (propHanzi) {
      sinoEntry = {
        hanzi: propHanzi,
        name: originName.textContent,
        tarr: tarrName.textContent,
        status: 'Sinosphere Title',
        characters: [],
        synthesis: props.c_calque || `Calqued root-for-root from CJK ${propHanzi} into Tarraconian High German.`
      };
    }
  }

  if (sinoGroup) {
    if (sinoEntry && sinoEntry.hanzi && !isUnoccupiedBarony) {
      sinoGroup.classList.remove('hidden');
      if (sinoHanziElem) sinoHanziElem.textContent = sinoEntry.hanzi;
      if (sinoReadingElem) sinoReadingElem.textContent = sinoEntry.name ? `(${sinoEntry.name})` : '';
      if (sinoStatusElem) {
        sinoStatusElem.textContent = sinoEntry.status.includes('Anachronism') ? 'Tier 3 Resolved' : 'Classical';
        sinoStatusElem.style.borderColor = sinoEntry.status.includes('Anachronism') ? 'rgba(184, 79, 24, 0.6)' : 'rgba(48, 105, 168, 0.5)';
        sinoStatusElem.style.color = sinoEntry.status.includes('Anachronism') ? '#f7a372' : '#8bbbee';
      }

      if (sinoBreakdownElem) {
        sinoBreakdownElem.innerHTML = '';
        if (sinoEntry.characters && sinoEntry.characters.length > 0) {
          for (const c of sinoEntry.characters) {
            const pill = document.createElement('div');
            pill.className = 'sinosphere-char-pill';
            const readings = c.pinyin ? `[${c.pinyin}]` : '';
            const mShort = (c.meaning || '').split('/')[0].trim();
            pill.innerHTML = `
              <div class="sinosphere-char-left">
                <span class="sinosphere-char-symbol">${c.char}</span>
                <span class="sinosphere-char-readings">${readings}</span>
                <span class="sinosphere-char-meaning">&ldquo;${mShort}&rdquo;</span>
              </div>
              <div class="sinosphere-char-right">&rarr; <strong>${c.morpheme || c.tarr_morpheme || '—'}</strong></div>
            `;
            sinoBreakdownElem.appendChild(pill);
          }
          sinoBreakdownElem.parentElement.classList.remove('hidden');
        } else {
          sinoBreakdownElem.parentElement.classList.add('hidden');
        }
      }

      if (sinoSynthesisElem) {
        sinoSynthesisElem.innerHTML = `<strong>Calque Synthesis:</strong> ${sinoEntry.synthesis || 'Calqued from Chinese logographic toponym.'}`;
      }

      if (sinoSubstrateElem) {
        if (sinoEntry.substrate || sinoEntry.justification) {
          sinoSubstrateElem.classList.remove('hidden');
          const subText = sinoEntry.substrate ? `<div><strong>Physical Substrate:</strong> ${sinoEntry.substrate}</div>` : '';
          const justText = sinoEntry.justification ? `<div><strong>Historical Resolution:</strong> ${sinoEntry.justification}</div>` : '';
          sinoSubstrateElem.innerHTML = subText + justText;
        } else {
          sinoSubstrateElem.classList.add('hidden');
          sinoSubstrateElem.innerHTML = '';
        }
      }
    } else {
      sinoGroup.classList.add('hidden');
    }
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

  // Render Procedural Title Symbol (Signa Imperii)
  const symbolCard = document.getElementById('drawer-symbol-card');
  if (symbolCard && window.TarraconianSymbols && !isUnoccupiedBarony) {
    window.TarraconianSymbols.renderSymbolToElement(
      symbolCard,
      currentKey,
      props,
      tier
    );
  } else if (symbolCard) {
    symbolCard.classList.add('hidden');
    symbolCard.innerHTML = '';
  }

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
      listElem.innerHTML = props.baronies.map(b => {
        let bName = formatKey(b);
        const bp = baronyPropsMap.get(b);
        if (bp) {
          if (bp.holding_type === 'unoccupied') {
            bName = `${formatKey(b)} [Unoccupied]`;
          } else if (bp.b_tarr || bp.name) {
            bName = bp.b_tarr || bp.name;
          }
        }
        return `<li class="barony-pill" data-key="${b}" data-tier="barony" style="cursor:pointer" title="Click to inspect ${bName}">${bName} <small style="opacity:0.6;font-family:var(--font-mono)">(${b})</small></li>`;
      }).join('');
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
  const symbolCard = document.getElementById('drawer-symbol-card');
  if (symbolCard) {
    symbolCard.classList.add('hidden');
    symbolCard.innerHTML = '';
  }
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
    const sino = sinosphereCalques ? sinosphereCalques[p.county] : null;
    const hanzi = (sino && sino.hanzi) ? sino.hanzi : (p.c_hanzi || '');
    searchIndex.push({
      key: p.county,
      tarr: p.tarr_hist || p.tarr_direct || p.tarr || '',
      origin: p.c_origin || formatKey(p.county),
      hanzi: hanzi,
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
      const e_sino = sinosphereCalques ? sinosphereCalques[e_k] : null;
      const e_hanzi = (e_sino && e_sino.hanzi) ? e_sino.hanzi : (e_data.hanzi || '');
      searchIndex.push({
        key: e_k,
        tarr: e_data.tarr || formatKey(e_k),
        origin: e_data.origin || formatKey(e_k),
        hanzi: e_hanzi,
        tier: 'empire',
        empire: e_data.tarr || formatKey(e_k),
        feature: null
      });

      for (const [k_k, k_data] of Object.entries(e_data.kingdoms || {})) {
        const k_sino = sinosphereCalques ? sinosphereCalques[k_k] : null;
        const k_hanzi = (k_sino && k_sino.hanzi) ? k_sino.hanzi : (k_data.hanzi || '');
        searchIndex.push({
          key: k_k,
          tarr: k_data.tarr || formatKey(k_k),
          origin: k_data.origin || formatKey(k_k),
          hanzi: k_hanzi,
          tier: 'kingdom',
          kingdom: k_data.tarr || formatKey(k_k),
          empire: e_data.tarr || formatKey(e_k),
          feature: null
        });

        for (const [d_k, d_data] of Object.entries(k_data.duchies || {})) {
          const d_sino = sinosphereCalques ? sinosphereCalques[d_k] : null;
          const d_hanzi = (d_sino && d_sino.hanzi) ? d_sino.hanzi : (d_data.hanzi || '');
          searchIndex.push({
            key: d_k,
            tarr: d_data.tarr || formatKey(d_k),
            origin: d_data.origin || formatKey(d_k),
            hanzi: d_hanzi,
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

  // 3. Index baronies if already loaded
  indexBaroniesForSearch();
}

function indexBaroniesForSearch() {
  if (!baroniesGeojson || !baroniesGeojson.features) return;
  // Prevent duplicate barony indexation
  if (searchIndex.some(item => item.tier === 'barony')) return;
  for (const feat of baroniesGeojson.features) {
    const p = feat.properties;
    if (p.holding_type !== 'unoccupied' && (p.b_tarr || p.name)) {
      searchIndex.push({
        key: p.barony,
        tarr: p.b_tarr || p.name,
        origin: p.b_origin || p.name,
        hanzi: '',
        tier: 'barony',
        county: p.c_tarr || formatKey(p.county),
        duchy: p.d_tarr || formatKey(p.duchy),
        kingdom: p.k_tarr || formatKey(p.kingdom),
        empire: p.e_tarr || formatKey(p.empire),
        feature: feat
      });
    }
  }
}

function handleSearch(query) {
  const dropdown = document.getElementById('search-results');
  const clearBtn = document.getElementById('search-clear');
  const queryRaw = query.trim();
  const queryLower = queryRaw.toLowerCase();

  if (!queryRaw) {
    dropdown.classList.add('hidden');
    dropdown.innerHTML = '';
    clearBtn.style.display = 'none';
    return;
  }

  clearBtn.style.display = 'block';

  // Filter top matches
  const matches = searchIndex.filter(item => {
    return (
      item.key.toLowerCase().includes(queryLower) ||
      item.tarr.toLowerCase().includes(queryLower) ||
      (item.origin && item.origin.toLowerCase().includes(queryLower)) ||
      (item.hanzi && item.hanzi.includes(queryRaw))
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
    const hanziBadge = m.hanzi ? `<span class="result-hanzi">${m.hanzi}</span>` : '';
    return `
      <div class="search-item" data-key="${m.key}" data-tier="${m.tier}">
        <div class="search-item-primary">${m.tarr || m.origin} ${hanziBadge} <span style="font-size:0.7rem;opacity:0.5;text-transform:uppercase">[${m.tier}]</span></div>
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
  const dragHandle = document.querySelector('.drawer-drag-handle');
  if (dragHandle) {
    dragHandle.addEventListener('click', closeInspector);
  }
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

  // Initialize Linguistics & Toponymic Guide Modal
  initLinguisticsModal();
}

// ---------------------------------------------------------------------------
// Linguistics & Toponymic Guide Modal
// ---------------------------------------------------------------------------
let activeLexiconCategory = 'all';
let lexiconSearchQuery = '';

function initLinguisticsModal() {
  const modal = document.getElementById('linguistics-modal');
  const openBtn = document.getElementById('btn-open-linguistics');
  const closeBtn = document.getElementById('btn-close-linguistics');
  if (!modal || !openBtn) return;

  function openModal() {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  openBtn.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
      closeModal();
    }
  });

  // Tab switching
  const tabBtns = modal.querySelectorAll('.modal-tab-btn');
  const tabPanes = {
    tarraconian: document.getElementById('tab-pane-tarraconian'),
    sinosphere: document.getElementById('tab-pane-sinosphere'),
    lexicon: document.getElementById('tab-pane-lexicon'),
    insignia: document.getElementById('tab-pane-insignia')
  };

  tabBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
      const targetTab = btn.getAttribute('data-tab');
      tabBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      Object.entries(tabPanes).forEach(([tabName, pane]) => {
        if (!pane) return;
        if (tabName === targetTab) {
          pane.classList.remove('hidden');
          pane.classList.add('active');
        } else {
          pane.classList.add('hidden');
          pane.classList.remove('active');
        }
      });

      if (targetTab === 'lexicon') {
        await ensureKanjiLexiconLoaded();
      } else if (targetTab === 'insignia') {
        renderInsigniaGallery();
      }
    });
  });

  // Setup Lexicon Controls
  const searchInput = document.getElementById('lexicon-search-input');
  const clearBtn = document.getElementById('lexicon-search-clear');
  const catFilterContainer = document.getElementById('lexicon-category-filters');

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      lexiconSearchQuery = e.target.value.trim().toLowerCase();
      if (clearBtn) clearBtn.style.display = lexiconSearchQuery ? 'block' : 'none';
      renderKanjiLexiconTable();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      lexiconSearchQuery = '';
      clearBtn.style.display = 'none';
      renderKanjiLexiconTable();
    });
  }

  if (catFilterContainer) {
    catFilterContainer.addEventListener('click', (e) => {
      const btn = e.target.closest('.lexicon-cat-btn');
      if (!btn) return;
      catFilterContainer.querySelectorAll('.lexicon-cat-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeLexiconCategory = btn.getAttribute('data-cat');
      renderKanjiLexiconTable();
    });
  }
}

async function ensureKanjiLexiconLoaded() {
  if (sinosphereKanjiList) {
    renderKanjiLexiconTable();
    return;
  }
  const tbody = document.getElementById('lexicon-table-body');
  if (tbody) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-dim)">Loading 641 Sinosphere characters...</td></tr>';

  try {
    const res = await fetch('data/sinosphere_kanji_tarraconian.json');
    if (res.ok) {
      sinosphereKanjiList = await res.json();
    }
  } catch (err) {
    console.error('Failed to load sinosphere_kanji_tarraconian.json:', err);
    if (tbody) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:#ff6b6b">Failed to load lexicon dataset.</td></tr>';
    return;
  }
  renderKanjiLexiconTable();
}

function renderKanjiLexiconTable() {
  if (!sinosphereKanjiList) return;
  const tbody = document.getElementById('lexicon-table-body');
  const countElem = document.getElementById('lexicon-match-count');
  if (!tbody) return;

  const q = lexiconSearchQuery;
  const cat = activeLexiconCategory;

  const filtered = sinosphereKanjiList.filter(item => {
    if (cat !== 'all' && String(item.cat_id) !== cat) {
      return false;
    }
    if (!q) return true;
    return (
      item.char.includes(q) ||
      (item.pinyin && item.pinyin.toLowerCase().includes(q)) ||
      (item.meaning && item.meaning.toLowerCase().includes(q)) ||
      (item.tarr_morpheme && item.tarr_morpheme.toLowerCase().includes(q)) ||
      (item.cat_name && item.cat_name.toLowerCase().includes(q)) ||
      (item.tarr_role && item.tarr_role.toLowerCase().includes(q)) ||
      (item.tarr_example && item.tarr_example.toLowerCase().includes(q))
    );
  });

  if (countElem) {
    countElem.textContent = `Showing ${filtered.length} of ${sinosphereKanjiList.length} characters`;
  }

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-dim)">No characters match your search criteria.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(item => {
    const readings = [
      item.pinyin ? `PY: ${item.pinyin}` : '',
      item.jp ? `JP: ${item.jp}` : '',
      item.kr ? `KR: ${item.kr}` : ''
    ].filter(Boolean).join('<br>');

    const exampleStr = item.tarr_example ? `<small style="opacity:0.8">${item.tarr_example}</small>` : (item.titles ? item.titles.slice(0, 2).join(', ') : '—');

    return `
      <tr>
        <td class="lexicon-hanzi-cell">${item.char}</td>
        <td><small style="font-family:var(--font-mono)">${readings}</small></td>
        <td><strong>${item.meaning}</strong><br><small style="color:var(--text-dim)">${item.cat_name}</small></td>
        <td class="lexicon-morpheme-cell">${item.tarr_morpheme || '—'}</td>
        <td class="lexicon-ipa-cell">${item.tarr_ipa || '—'}</td>
        <td><span style="font-size:0.75rem">${item.tarr_role || '—'}</span></td>
        <td>${exampleStr}</td>
      </tr>
    `;
  }).join('');
}

// ---------------------------------------------------------------------------
// Signa Imperii (Insignia & Title Symbol Gallery)
// ---------------------------------------------------------------------------
function renderInsigniaGallery() {
  const container = document.getElementById('insignia-gallery-grid');
  if (!container || container.children.length > 0) return;
  if (!window.TarraconianSymbols) return;

  const showcaseTitles = [
    { key: 'h_roman_empire', tier: 'empire', label: 'Dat Rômische Keiserrîch', subtitle: 'Restored Hegemony' },
    { key: 'k_france', tier: 'kingdom', label: 'Vrancrîch', subtitle: 'Regenat van Vrancrîch' },
    { key: 'k_east_francia', tier: 'kingdom', label: 'Dütschlant', subtitle: 'Regenat van Dütschlant' },
    { key: 'd_upper_lorraine', tier: 'duchy', label: 'Ober-Lôthringen', subtitle: 'Gubernat (Dynastic Cradle)' },
    { key: 'd_barcelona', tier: 'duchy', label: 'Barcelona', subtitle: 'Gubernat van Barcelona' },
    { key: 'c_tarragona', tier: 'county', label: 'Tarragôn', subtitle: 'Magistrat (Cultural Homeland)' },
    { key: 'c_roma', tier: 'county', label: 'Rôm (Roma)', subtitle: 'Imperial & Apostolic Capital' },
    { key: 'c_metz', tier: 'county', label: 'Metz', subtitle: 'Imperial Chancellery City' },
    { key: 'c_lviv', tier: 'county', label: 'Swenigorot (Lemberg)', subtitle: 'Resolved 10th-c. Gord' },
    { key: 'c_szekesfehervar', tier: 'county', label: 'Stûlwîtzenburch', subtitle: 'Coronation Seat of Hungary' },
    { key: 'c_nancy', tier: 'county', label: 'Lûnstat (Nancy)', subtitle: 'Resolved Antiquity Seat' },
    { key: 'c_byzantion', tier: 'county', label: 'Konstantinôpel (Bîsantz)', subtitle: 'Eastern Imperial Capital' },
    { key: 'c_jinzhou', tier: 'county', label: 'Goltberch (金州)', subtitle: 'Procedure 1 Sinitic Prefect' },
    { key: 'c_dongguan', tier: 'county', label: 'Ôsttor (東莞)', subtitle: 'Procedure 1 Maritime Gate' },
    { key: 'k_papal_state', tier: 'kingdom', label: 'Patrimonium Petri', subtitle: 'Papal Caesaropapist See' }
  ];

  container.innerHTML = showcaseTitles.map(s => {
    const sym = window.TarraconianSymbols.generateSymbol(s.key, { tarr: s.label }, s.tier);
    return `
      <div class="insignia-gallery-card" data-key="${s.key}" data-tier="${s.tier}" title="Click to inspect ${s.label} on map">
        <div class="insignia-card-graphic">
          ${sym.svgHtml}
        </div>
        <div class="insignia-card-title">${s.label}</div>
        <div class="insignia-card-meta">
          <span class="symbol-medium-badge">${sym.mediumLabel.split('(')[0].trim()}</span>
          <span class="tier-badge" style="font-size:0.6rem;padding:1px 6px;">${s.tier.toUpperCase()}</span>
        </div>
        <div class="insignia-card-blazon">&ldquo;${sym.blazonTarr}&rdquo;</div>
        <div class="insignia-card-legend"><code>${sym.legend}</code></div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.insignia-gallery-card').forEach(card => {
    card.addEventListener('click', () => {
      const key = card.getAttribute('data-key');
      const tier = card.getAttribute('data-tier');
      const modal = document.getElementById('linguistics-modal');
      if (modal) modal.classList.add('hidden');
      document.body.style.overflow = '';
      selectTitleByKey(key, tier);
    });
  });
}
