/**
 * Tarraconian Atlas — Procedural Title Symbol Generator (Signa Imperii)
 * ---------------------------------------------------------------------
 * Generates rank-differentiated, historically authentic title symbols
 * based on the 1194 Roman Empire Chancellery doctrines:
 *
 * 1. Physical Media Silhouettes by Rank:
 *    - Empire:    Imperial Vexillum (Fringed silk banner on crossbar with cords & finials)
 *    - Kingdom:   Carolingian/Catalan Three-Tailed Gonfanon (Amtsvanen)
 *    - Duchy:     Late-Roman Notitia Command Shield (Scutum with metallic rim & boss)
 *    - County:    Circular Chancellery Bulla / Municipal Seal (Lead/Wax with legend)
 *                 OR Sinosphere Vermilion Chop (Guóxī) for Procedure 1 counties
 *    - Ecc.:      Pointed Mandorla (Vesica Piscis) for Archdioceses and Patriarchal Sees
 *    - Barony:    Civic Holding Badge
 *
 * 2. Deterministic Derivation Engine:
 *    - Canting toponymic morphemes (-burch, -berch, -brücke, -vort, -stat, etc.)
 *    - Colour prefixes (Wîtz-, Rôt-, Swartz-, Golt-, Grûn-, Blâ-)
 *    - Antiquity & historical resolutions (Rome, Metz, Swenigorot, Lûnstat, Olbîe, etc.)
 *    - Sinosphere Kanji Matrix & Procedure 1 Hanzi calques
 *    - In-save warbanners & seals of investiture
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.TarraconianSymbols = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {

  // =========================================================================
  // 1. Imperial Tincture Palette & Gradients
  // =========================================================================
  const PALETTE = {
    or: '#d4af37',            // Imperial Gold
    or_bright: '#f5d77f',     // Highlight Gold
    argent: '#f4f1ea',        // Silver / White
    argent_dim: '#dcd8cf',    // Silver Shadow
    gules: '#9e1b1b',         // Imperial Crimson / Red
    gules_dark: '#731313',    // Deep Crimson
    sable: '#1c1c1c',         // Chancellery Black
    sable_light: '#2d2d2d',   // Warm Charcoal
    azure: '#1e4d8c',         // Imperial Azure
    azure_light: '#316ab3',   // Cerulean Highlight
    vert: '#2d6a4f',          // Rhenish Green
    purpure: '#5a1846',       // Porphyry Purple (Eastern Roman)
    vermilion: '#c8281e',     // Cinnabar Seal Ink
    vermilion_dark: '#8e160e',// Aged Cinnabar
    lead: '#4a4e54',          // Antique Seal Lead
    lead_dark: '#2d3034',     // Shadow Lead
    brass: '#b8972e',         // Finial Brass
    wood: '#4a2e18'           // Lance Wood
  };

  // =========================================================================
  // 2. Vector Charge Library (24 Path Builders)
  // =========================================================================
  const CHARGES = {
    // Double-headed Imperial Eagle (Rome / HRE)
    eagle_double: (color = PALETTE.sable, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-100, -100)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.5">
        <!-- Body & Tail -->
        <path d="M 94 85 C 92 120 90 145 100 168 C 110 145 108 120 106 85 Z" />
        <path d="M 88 155 L 75 185 L 100 178 L 125 185 L 112 155 Z" />
        <!-- Left Wing -->
        <path d="M 90 95 C 60 70 35 75 22 95 C 28 115 48 135 75 140 C 60 130 40 115 35 100 C 45 88 68 85 88 102 Z" />
        <path d="M 28 92 C 15 110 25 130 50 148 C 35 135 22 120 22 105 Z" opacity="0.9" />
        <!-- Right Wing -->
        <path d="M 110 95 C 140 70 165 75 178 95 C 172 115 152 135 125 140 C 140 130 160 115 165 100 C 155 88 132 85 112 102 Z" />
        <path d="M 172 92 C 185 110 175 130 150 148 C 165 135 178 120 178 105 Z" opacity="0.9" />
        <!-- Left Head & Neck -->
        <path d="M 94 90 C 85 80 75 75 75 60 C 75 52 82 48 85 46 C 78 48 70 54 70 62 C 70 72 82 82 92 92 Z" />
        <polygon points="72,55 58,58 72,62" fill="${PALETTE.or}" stroke="${PALETTE.sable}" stroke-width="1" />
        <circle cx="80" cy="54" r="2" fill="${PALETTE.or}" />
        <!-- Right Head & Neck -->
        <path d="M 106 90 C 115 80 125 75 125 60 C 125 52 118 48 115 46 C 122 48 130 54 130 62 C 130 72 118 82 108 92 Z" />
        <polygon points="128,55 142,58 128,62" fill="${PALETTE.or}" stroke="${PALETTE.sable}" stroke-width="1" />
        <circle cx="120" cy="54" r="2" fill="${PALETTE.or}" />
        <!-- Twin Halos -->
        <circle cx="78" cy="56" r="14" fill="none" stroke="${PALETTE.or}" stroke-width="2" />
        <circle cx="122" cy="56" r="14" fill="none" stroke="${PALETTE.or}" stroke-width="2" />
        <!-- Talons -->
        <path d="M 78 150 L 65 165 M 78 152 L 72 168 M 82 152 L 82 170" stroke="${PALETTE.or}" stroke-width="3" stroke-linecap="round" />
        <path d="M 122 150 L 135 165 M 122 152 L 128 168 M 118 152 L 118 170" stroke="${PALETTE.or}" stroke-width="3" stroke-linecap="round" />
      </g>
    `,

    // Lorraine Alerion (spread eaglet without beak or claws)
    alerion: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -40)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 40 18 C 34 26 30 35 34 50 C 37 60 40 68 40 72 C 40 68 43 60 46 50 C 50 35 46 26 40 18 Z" />
        <path d="M 35 32 C 22 22 12 25 6 34 C 10 44 20 54 32 56 C 24 50 16 42 14 36 C 18 30 28 29 35 36 Z" />
        <path d="M 45 32 C 58 22 68 25 74 34 C 70 44 60 54 48 56 C 56 50 64 42 66 36 C 62 30 52 29 45 36 Z" />
        <path d="M 33 65 L 25 75 L 40 71 L 55 75 L 47 65 Z" />
      </g>
    `,

    // Triple-towered Crenellated Castrum / Fortress
    castrum: (color = PALETTE.argent, scale = 1, cx = 110, cy = 115, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-60, -55)" fill="${color}" stroke="${accent}" stroke-width="2" stroke-linejoin="round">
        <!-- Main Wall Base -->
        <rect x="15" y="45" width="90" height="50" rx="1" />
        <!-- Wall Crenellations -->
        <rect x="23" y="38" width="10" height="7" />
        <rect x="41" y="38" width="10" height="7" />
        <rect x="69" y="38" width="10" height="7" />
        <rect x="87" y="38" width="10" height="7" />
        <!-- Left Flanking Tower -->
        <rect x="10" y="20" width="22" height="65" />
        <polygon points="8,20 12,12 30,12 34,20" />
        <rect x="11" y="10" width="5" height="5" />
        <rect x="19" y="10" width="5" height="5" />
        <rect x="27" y="10" width="5" height="5" />
        <rect x="18" y="30" width="6" height="12" rx="2" fill="${accent}" />
        <!-- Right Flanking Tower -->
        <rect x="88" y="20" width="22" height="65" />
        <polygon points="86,20 90,12 108,12 112,20" />
        <rect x="89" y="10" width="5" height="5" />
        <rect x="97" y="10" width="5" height="5" />
        <rect x="105" y="10" width="5" height="5" />
        <rect x="96" y="30" width="6" height="12" rx="2" fill="${accent}" />
        <!-- Central Great Donjon Tower -->
        <rect x="45" y="8" width="30" height="60" />
        <polygon points="42,8 47,0 73,0 78,8" />
        <rect x="46" y="-3" width="6" height="5" />
        <rect x="57" y="-3" width="6" height="5" />
        <rect x="68" y="-3" width="6" height="5" />
        <rect x="56" y="18" width="8" height="15" rx="3" fill="${accent}" />
        <!-- Portcullis & Gateway Arch -->
        <path d="M 48 95 L 48 65 Q 60 55 72 65 L 72 95 Z" fill="${accent}" />
        <line x1="54" y1="65" x2="54" y2="95" stroke="${color}" stroke-width="1.5" />
        <line x1="60" y1="60" x2="60" y2="95" stroke="${color}" stroke-width="1.5" />
        <line x1="66" y1="65" x2="66" y2="95" stroke="${color}" stroke-width="1.5" />
        <line x1="48" y1="75" x2="72" y2="75" stroke="${color}" stroke-width="1.5" />
        <line x1="48" y1="85" x2="72" y2="85" stroke="${color}" stroke-width="1.5" />
      </g>
    `,

    // Classical Roman City Gate / Triumphal Arch
    roman_gate: (color = PALETTE.argent, scale = 1, cx = 110, cy = 115, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-50, -50)" fill="${color}" stroke="${accent}" stroke-width="2" stroke-linejoin="round">
        <!-- Entablature / Pediment -->
        <polygon points="0,22 50,2 100,22" />
        <rect x="5" y="22" width="90" height="10" />
        <!-- Pillars -->
        <rect x="8" y="32" width="22" height="62" />
        <rect x="70" y="32" width="22" height="62" />
        <rect x="5" y="90" width="28" height="8" />
        <rect x="67" y="90" width="28" height="8" />
        <!-- Archway -->
        <path d="M 30 94 L 30 60 Q 50 40 70 60 L 70 94 Z" fill="${accent}" />
        <!-- Keystone -->
        <polygon points="46,40 54,40 52,48 48,48" fill="${PALETTE.or}" stroke="${accent}" stroke-width="1" />
      </g>
    `,

    // Triple Mountain (Dreiberg)
    mount_triple: (color = PALETTE.vert, scale = 1, cx = 110, cy = 135, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-60, -35)" fill="${color}" stroke="${accent}" stroke-width="2">
        <path d="M 0 35 C 10 15 30 15 40 35 Z" />
        <path d="M 80 35 C 90 15 110 15 120 35 Z" />
        <path d="M 30 35 C 45 5 75 5 90 35 Z" />
      </g>
    `,

    // Stone Arch Bridge
    bridge: (color = PALETTE.argent, scale = 1, cx = 110, cy = 120, accent = PALETTE.sable, field = null) => {
      const waterColor = (field === 'azure' || color === PALETTE.azure) ? PALETTE.argent : PALETTE.azure;
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-60, -25)" fill="${color}" stroke="${accent}" stroke-width="2">
        <rect x="5" y="0" width="110" height="12" rx="2" />
        <path d="M 5 12 L 5 40 L 22 40 Q 38 18 54 40 L 66 40 Q 82 18 98 40 L 115 40 L 115 12 Z" />
        <!-- Water below bridge -->
        <path d="M 5 44 C 20 40 35 48 50 44 C 65 40 80 48 95 44 C 105 42 112 45 115 44" fill="none" stroke="${waterColor}" stroke-width="3" stroke-linecap="round" />
      </g>
    `;
    },

    // Wavy Water Bars (Hydronyms / Maritime)
    waves: (color = PALETTE.azure, scale = 1, cx = 110, cy = 130, field = null) => {
      const waveColor = (field === 'azure' || color === PALETTE.argent || color === PALETTE.or) ? (color !== PALETTE.azure ? color : PALETTE.argent) : (color || PALETTE.azure);
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-65, -20)" fill="none" stroke="${waveColor}" stroke-width="4" stroke-linecap="round">
        <path d="M 0 0 C 18 -8 28 8 45 0 C 62 -8 72 8 90 0 C 108 -8 118 8 130 0" />
        <path d="M 0 16 C 18 8 28 24 45 16 C 62 8 72 24 90 16 C 108 8 118 24 130 16" />
        <path d="M 0 32 C 18 24 28 40 45 32 C 62 24 72 40 90 32 C 108 24 118 40 130 32" opacity="0.75" />
      </g>
    `;
    },

    // Ringing Bell (Swenigorot canting charge)
    bell: (color = PALETTE.or, scale = 1, cx = 110, cy = 80, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-30, -35)" fill="${color}" stroke="${accent}" stroke-width="2" stroke-linejoin="round">
        <rect x="24" y="0" width="12" height="8" rx="2" fill="${accent}" />
        <path d="M 30 8 C 22 10 16 22 14 36 C 12 48 6 52 4 56 L 56 56 C 54 52 48 48 46 36 C 44 22 38 10 30 8 Z" />
        <circle cx="30" cy="62" r="5" fill="${PALETTE.brass}" stroke="${accent}" stroke-width="1.5" />
      </g>
    `,

    // St. Peter's Crossed Keys (Rome / Papal / Bishopric)
    keys_st_peter: (colorOr = PALETTE.or, scale = 1, cx = 110, cy = 110, colorArg = PALETTE.argent, field = null) => {
      const isMetal = (field === 'or' || field === 'argent' || colorOr === PALETTE.sable || colorOr === PALETTE.azure);
      const k1 = isMetal ? ((field === 'or' || colorOr === PALETTE.sable) ? PALETTE.sable : PALETTE.azure) : colorOr;
      const k2 = isMetal ? ((field === 'argent' || colorArg === PALETTE.azure) ? PALETTE.azure : PALETTE.gules) : colorArg;
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-45, -45)" stroke="${PALETTE.sable}" stroke-width="1.5" stroke-linecap="round">
        <!-- Gold Key (Dexter) -->
        <g fill="${k1}">
          <line x1="12" y1="78" x2="78" y2="12" stroke="${k1}" stroke-width="5" />
          <line x1="12" y1="78" x2="78" y2="12" stroke="${PALETTE.sable}" stroke-width="1.5" />
          <circle cx="16" cy="74" r="12" stroke-width="2" />
          <circle cx="16" cy="74" r="5" fill="${PALETTE.sable}" />
          <!-- Wards -->
          <path d="M 72 18 L 84 30 L 78 36 L 73 31 L 70 34 L 65 29 Z" />
        </g>
        <!-- Silver Key (Sinister) -->
        <g fill="${k2}">
          <line x1="78" y1="78" x2="12" y2="12" stroke="${k2}" stroke-width="5" />
          <line x1="78" y1="78" x2="12" y2="12" stroke="${PALETTE.sable}" stroke-width="1.5" />
          <circle cx="74" cy="74" r="12" stroke-width="2" />
          <circle cx="74" cy="74" r="5" fill="${PALETTE.sable}" />
          <!-- Wards -->
          <path d="M 18 18 L 6 30 L 12 36 L 17 31 L 20 34 L 25 29 Z" />
        </g>
      </g>
    `;
    },

    // Archiepiscopal / Metropolitan Crozier (Prince-Bishoprics)
    crozier: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-25, -60)" fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round">
        <line x1="25" y1="35" x2="25" y2="115" stroke="${PALETTE.brass}" stroke-width="5" />
        <line x1="25" y1="35" x2="25" y2="115" stroke="${accent}" stroke-width="1.5" />
        <!-- Volute spiral -->
        <path d="M 25 35 C 25 15 45 5 45 25 C 45 35 35 42 28 35 C 24 30 28 24 32 26" fill="none" stroke="${color}" stroke-width="4.5" />
        <circle cx="25" cy="40" r="5" fill="${color}" stroke="${accent}" stroke-width="1.5" />
      </g>
    `,

    // Patriarchal Cross (Two horizontal bars)
    cross_patriarchal: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-30, -50)" fill="${color}" stroke="${accent}" stroke-width="2">
        <rect x="25" y="0" width="10" height="100" rx="1" />
        <rect x="10" y="20" width="40" height="9" rx="1" />
        <rect x="0" y="45" width="60" height="11" rx="1" />
      </g>
    `,

    // Byzantine Tetragrammatic Cross with 4 Firesteels (B)
    cross_byzantine: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-50, -50)" fill="${color}" stroke="${accent}" stroke-width="1.5">
        <!-- Main Cross -->
        <rect x="44" y="5" width="12" height="90" rx="1" />
        <rect x="5" y="44" width="90" height="12" rx="1" />
        <!-- Four Betas / Firesteels -->
        <!-- Q1 (top right) -->
        <path d="M 64 20 L 78 20 C 84 20 86 26 80 29 C 86 32 84 38 78 38 L 64 38 Z M 70 24 L 75 24 C 77 24 77 27 75 27 L 70 27 Z M 70 31 L 75 31 C 77 31 77 34 75 34 L 70 34 Z" />
        <!-- Q2 (top left) -->
        <path d="M 36 20 L 22 20 C 16 20 14 26 20 29 C 14 32 16 38 22 38 L 36 38 Z M 30 24 L 25 24 C 23 24 23 27 25 27 L 30 27 Z M 30 31 L 25 31 C 23 31 23 34 25 34 L 30 34 Z" />
        <!-- Q3 (bottom left) -->
        <path d="M 36 62 L 22 62 C 16 62 14 68 20 71 C 14 74 16 80 22 80 L 36 80 Z M 30 66 L 25 66 C 23 66 23 69 25 69 L 30 69 Z M 30 73 L 25 73 C 23 73 23 76 25 76 L 30 76 Z" />
        <!-- Q4 (bottom right) -->
        <path d="M 64 62 L 78 62 C 84 62 86 68 80 71 C 86 74 84 80 78 80 L 64 80 Z M 70 66 L 75 66 C 77 66 77 69 75 69 L 70 69 Z M 70 73 L 75 73 C 77 73 77 76 75 76 L 70 76 Z" />
      </g>
    `,

    // Chestnut Tree (Kestenholz / Châtenois canting)
    tree_chestnut: (color = PALETTE.vert, scale = 1, cx = 110, cy = 115, trunk = PALETTE.wood, field = null) => {
      const crownColor = (field === 'vert' || color === PALETTE.or || color === PALETTE.argent) ? (color !== PALETTE.vert ? color : PALETTE.or) : (color || PALETTE.vert);
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-45, -55)" stroke="${PALETTE.sable}" stroke-width="1.8">
        <!-- Trunk & Roots -->
        <path d="M 40 50 L 38 85 L 20 98 M 42 85 L 45 98 M 52 85 L 70 98 L 50 50 Z" fill="${trunk}" />
        <!-- Foliage Crown (3 lobes) -->
        <path d="M 20 55 C 5 45 5 25 25 20 C 25 5 65 5 65 20 C 85 25 85 45 70 55 C 80 70 55 75 45 65 C 35 75 10 70 20 55 Z" fill="${crownColor}" />
      </g>
    `;
    },

    // Heraldic Lion Rampant
    lion_rampant: (color = PALETTE.gules, scale = 1, cx = 110, cy = 115, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -50)" fill="${color}" stroke="${accent}" stroke-width="1.5">
        <path d="M 38 10 C 44 8 50 14 46 20 C 52 20 56 24 50 28 L 56 32 L 48 34 C 54 42 58 46 64 42 L 60 48 L 48 44 C 44 54 42 66 48 76 L 62 74 L 64 80 L 46 84 C 42 92 36 98 25 98 L 22 92 C 30 90 34 84 34 76 C 26 76 22 70 20 62 C 28 64 34 58 34 50 C 24 50 20 44 18 36 L 24 36 C 28 42 34 38 34 30 C 30 30 26 26 28 20 C 34 24 38 18 38 10 Z" />
        <!-- Claws & Tongue -->
        <path d="M 50 24 L 58 24" stroke="${PALETTE.gules}" stroke-width="1.5" />
        <!-- Curving Tail -->
        <path d="M 36 78 C 22 70 12 50 16 35 C 18 25 10 20 8 30 C 6 45 15 65 28 84 Z" fill="${color}" />
      </g>
    `,

    // Medieval Maritime Cog / Galley
    ship: (color = PALETTE.wood, scale = 1, cx = 110, cy = 120, sail = null, field = null) => {
      const isMetal = (field === 'or' || field === 'argent' || color === PALETTE.sable || color === PALETTE.azure || color === PALETTE.gules || color === PALETTE.vert || color === PALETTE.purpure);
      const hullColor = (color && color !== PALETTE.wood) ? color : ((field === 'sable') ? PALETTE.or : PALETTE.wood);
      const sailColor = isMetal ? ((color && color !== PALETTE.argent && color !== PALETTE.or) ? color : PALETTE.azure) : (sail || PALETTE.argent);
      const waveColor = (field === 'azure') ? (isMetal ? PALETTE.sable : PALETTE.argent) : PALETTE.azure;
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-50, -45)" stroke="${PALETTE.sable}" stroke-width="1.8" stroke-linejoin="round">
        <!-- Hull -->
        <path d="M 5 45 C 15 68 85 68 95 45 L 85 45 L 75 52 L 25 52 L 15 45 Z" fill="${hullColor}" />
        <!-- Mast & Cross -->
        <line x1="50" y1="10" x2="50" y2="52" stroke="${hullColor}" stroke-width="4" />
        <polygon points="50,6 58,10 50,14" fill="${isMetal ? PALETTE.azure : PALETTE.gules}" stroke="${PALETTE.sable}" stroke-width="1" />
        <!-- Full Billowing Square Sail -->
        <path d="M 28 16 Q 50 12 72 16 Q 80 32 72 44 Q 50 40 28 44 Q 20 32 28 16 Z" fill="${sailColor}" />
        <!-- Waves below -->
        <path d="M 0 65 Q 12 60 25 65 Q 37 70 50 65 Q 62 60 75 65 Q 87 70 100 65" fill="none" stroke="${waveColor}" stroke-width="3" stroke-linecap="round" />
      </g>
    `;
    },

    // Imperial Crown
    crown: (color = PALETTE.or, scale = 1, cx = 110, cy = 60, jewels = PALETTE.gules) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -25)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.5">
        <rect x="5" y="28" width="70" height="12" rx="2" />
        <circle cx="15" cy="34" r="2.5" fill="${jewels}" stroke="none" />
        <circle cx="40" cy="34" r="3" fill="${PALETTE.azure}" stroke="none" />
        <circle cx="65" cy="34" r="2.5" fill="${jewels}" stroke="none" />
        <!-- Crown Spikes / Arches -->
        <path d="M 5 28 L 10 12 L 22 24 L 40 4 L 58 24 L 70 12 L 75 28 Z" />
        <circle cx="10" cy="10" r="2.5" fill="${PALETTE.argent}" />
        <circle cx="40" cy="2" r="3.5" fill="${PALETTE.argent}" />
        <circle cx="70" cy="10" r="2.5" fill="${PALETTE.argent}" />
      </g>
    `,

    // Sinosphere Dragon
    dragon: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-50, -50)" fill="none" stroke="${color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
        <!-- Serpentine S-Body -->
        <path d="M 20 30 Q 35 15 50 30 Q 65 45 80 30 Q 90 20 85 45 Q 80 65 55 60 Q 30 55 25 75 Q 20 90 40 90 Q 60 90 75 80" />
        <!-- Dragon Head -->
        <path d="M 20 30 L 10 25 L 14 35 L 8 40 L 22 42 Z" fill="${color}" stroke="${accent}" stroke-width="1.5" />
        <line x1="12" y1="24" x2="4" y2="15" stroke="${PALETTE.vermilion}" stroke-width="2" />
        <!-- Claws -->
        <path d="M 42 32 L 35 42 M 72 38 L 78 50 M 35 62 L 25 70" stroke="${color}" stroke-width="2.5" />
      </g>
    `,

    // Crossed Chivalric Broadswords
    sword_crossed: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110, hilt = PALETTE.or) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -40)" stroke="${PALETTE.sable}" stroke-width="1.2">
        <!-- Sword 1 (dexter to sinister) -->
        <line x1="12" y1="68" x2="68" y2="12" stroke="${color}" stroke-width="3.5" stroke-linecap="round" />
        <polygon points="68,12 65,18 70,15" fill="${color}" />
        <line x1="18" y1="62" x2="26" y2="70" stroke="${hilt}" stroke-width="3" stroke-linecap="round" />
        <circle cx="12" cy="68" r="3" fill="${hilt}" />
        <!-- Sword 2 (sinister to dexter) -->
        <line x1="68" y1="68" x2="12" y2="12" stroke="${color}" stroke-width="3.5" stroke-linecap="round" />
        <polygon points="12,12 18,15 15,18" fill="${color}" />
        <line x1="62" y1="62" x2="54" y2="70" stroke="${hilt}" stroke-width="3" stroke-linecap="round" />
        <circle cx="68" cy="68" r="3" fill="${hilt}" />
      </g>
    `,

    // Frankish / Nordic Battleaxe
    battleaxe: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110, shaft = PALETTE.wood) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -45)" stroke="${PALETTE.sable}" stroke-width="1.2">
        <line x1="35" y1="10" x2="35" y2="80" stroke="${shaft}" stroke-width="5" stroke-linecap="round" />
        <path d="M 35 18 C 52 14, 65 22, 65 38 C 65 52, 48 58, 35 52 Z" fill="${color}" />
        <path d="M 35 22 L 24 26 L 24 44 L 35 48 Z" fill="${color}" />
        <polygon points="35,10 32,5 38,5" fill="${color}" />
      </g>
    `,

    // Chivalric Lance / Spear with Pennon
    spear: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110, shaft = PALETTE.wood, field = null) => {
      const pennonColor = (field === 'gules' || color === PALETTE.or) ? PALETTE.or : PALETTE.gules;
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -45)" stroke="${PALETTE.sable}" stroke-width="1.2">
        <line x1="35" y1="15" x2="35" y2="80" stroke="${shaft}" stroke-width="4" stroke-linecap="round" />
        <path d="M 35 3 C 28 12, 30 22, 35 25 C 40 22, 42 12, 35 3 Z" fill="${color}" />
        <line x1="35" y1="5" x2="35" y2="24" stroke="${PALETTE.sable}" stroke-width="0.8" />
        <polygon points="35,26 55,32 35,40" fill="${pennonColor}" />
      </g>
    `;
    },

    // Recurve Bow & Nocked Arrow
    bow_and_arrow: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, stringColor = PALETTE.argent, field = null) => {
      const tipColor = (field === 'argent' || field === 'or' || color === PALETTE.sable) ? PALETTE.sable : PALETTE.argent;
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -40)" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 20 15 C 38 25, 45 40, 45 40 C 45 40, 38 55, 20 65" fill="none" stroke="${color}" stroke-width="4.5" stroke-linecap="round" />
        <line x1="20" y1="15" x2="20" y2="65" stroke="${stringColor}" stroke-width="1" />
        <line x1="12" y1="40" x2="62" y2="40" stroke="${color}" stroke-width="2.5" />
        <polygon points="62,40 54,36 56,40 54,44" fill="${color}" />
        <polygon points="12,40 18,36 15,40 18,44" fill="${tipColor}" />
      </g>
    `;
    },

    // Heraldic Inescutcheon
    shield_escutcheon: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110, border = PALETTE.or) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -40)" stroke="${PALETTE.sable}" stroke-width="1.5">
        <path d="M 12 12 L 58 12 L 58 45 C 58 64, 35 74, 35 74 C 35 74, 12 64, 12 45 Z" fill="${color}" />
        <path d="M 16 16 L 54 16 L 54 44 C 54 60, 35 68, 35 68 C 35 68, 16 60, 16 44 Z" fill="none" stroke="${border}" stroke-width="2" />
      </g>
    `,

    // Standing Stag Attired
    stag_attired: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, antlers = PALETTE.or) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -45)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2" stroke-linejoin="round">
        <path d="M 28 42 C 32 38, 48 38, 54 44 C 56 50, 56 60, 53 62 L 54 78 L 50 78 L 48 64 L 38 64 L 38 78 L 34 78 L 33 60 C 27 58, 25 50, 28 42 Z" />
        <path d="M 30 44 L 28 26 C 26 24, 22 24, 20 25 L 18 28 L 24 30 L 26 36 L 28 44 Z" />
        <path d="M 26 24 C 24 16, 18 10, 14 8 M 20 14 C 16 14, 14 16, 14 16 M 22 18 C 18 19, 16 22, 16 22 M 27 24 C 30 16, 36 10, 40 8 M 32 14 C 36 14, 38 16, 38 16 M 31 18 C 35 19, 37 22, 37 22" fill="none" stroke="${antlers}" stroke-width="2" stroke-linecap="round" />
      </g>
    `,

    // Bear Rampant
    bear_rampant: (color = PALETTE.sable, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -45)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2" stroke-linejoin="round">
        <path d="M 45 80 L 52 80 L 50 64 C 55 58, 56 46, 52 38 L 58 30 L 54 28 L 46 34 C 42 32, 36 30, 30 26 C 26 24, 22 25, 20 28 C 18 32, 22 36, 26 36 L 22 42 L 26 44 L 32 38 C 36 44, 36 54, 32 60 L 32 80 L 38 80 L 38 66 C 40 68, 43 68, 45 66 Z" />
        <circle cx="28" cy="28" r="2.5" fill="${color}" />
      </g>
    `,

    // Galloping Steed / Horse Courant
    horse_courant: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-45, -35)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2" stroke-linejoin="round">
        <path d="M 22 28 C 24 22, 28 16, 32 18 C 36 20, 38 26, 44 26 C 54 26, 62 30, 68 34 L 80 26 L 82 28 L 74 38 C 72 44, 68 48, 62 48 L 72 58 L 68 60 L 56 48 C 48 50, 38 48, 34 44 L 24 58 L 20 56 L 26 42 C 22 38, 18 34, 12 32 L 14 26 C 18 28, 20 28, 22 28 Z" />
        <path d="M 70 34 C 76 38, 80 46, 82 54" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round" />
      </g>
    `,

    // Wolf Statant
    wolf_statant: (color = PALETTE.sable, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-45, -35)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 24 26 L 14 28 L 18 32 C 20 34, 24 38, 28 38 L 26 58 L 30 58 L 34 42 L 52 42 L 52 58 L 56 58 L 58 40 C 64 38, 68 32, 70 28 L 74 44 L 78 44 L 72 24 C 66 22, 58 26, 50 26 C 42 26, 34 22, 28 22 Z" />
        <polygon points="26,22 24,16 28,20" />
      </g>
    `,

    // Twin Heraldic Fish Haurient
    fish_twin: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -40)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 22 15 C 14 28, 14 48, 22 62 L 16 68 L 22 64 L 28 68 L 22 62 C 30 48, 30 28, 22 15 Z" />
        <circle cx="22" cy="22" r="2" fill="${PALETTE.sable}" />
        <path d="M 48 15 C 40 28, 40 48, 48 62 L 42 68 L 48 64 L 54 68 L 48 62 C 56 48, 56 28, 48 15 Z" />
        <circle cx="48" cy="22" r="2" fill="${PALETTE.sable}" />
      </g>
    `,

    // Hunting Falcon on Perch
    falcon_perched: (color = PALETTE.sable, scale = 1, cx = 110, cy = 110, perch = PALETTE.wood) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -45)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <line x1="10" y1="68" x2="60" y2="68" stroke="${perch}" stroke-width="4" stroke-linecap="round" />
        <path d="M 32 20 C 30 15, 36 12, 40 14 C 44 16, 44 22, 42 26 C 46 32, 48 42, 44 58 L 40 76 L 36 76 L 36 60 C 30 56, 26 48, 26 38 C 26 30, 28 24, 32 20 Z" />
        <polygon points="40,16 46,18 41,20" fill="${PALETTE.or}" />
        <circle cx="36" cy="18" r="1.8" fill="${PALETTE.or}" />
      </g>
    `,

    // Seeded Heraldic Rose
    rose_seeded: (color = PALETTE.gules, scale = 1, cx = 110, cy = 110, seeds = PALETTE.or, field = null) => {
      const sepalsColor = (field === 'vert') ? PALETTE.or : PALETTE.vert;
      const seedsColor = (field === 'or' || color === PALETTE.or) ? PALETTE.gules : (seeds || PALETTE.or);
      const petalColor = (color === PALETTE.argent || color === PALETTE.or) ? color : ((field === 'gules') ? PALETTE.argent : PALETTE.gules);
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -40)" stroke="${PALETTE.sable}" stroke-width="1.2">
        <polygon points="40,8 35,24 45,24" fill="${sepalsColor}" />
        <polygon points="70,30 55,35 62,45" fill="${sepalsColor}" />
        <polygon points="58,70 48,56 40,64" fill="${sepalsColor}" />
        <polygon points="22,70 32,56 40,64" fill="${sepalsColor}" />
        <polygon points="10,30 25,35 18,45" fill="${sepalsColor}" />
        <circle cx="40" cy="24" r="14" fill="${petalColor}" />
        <circle cx="55" cy="35" r="14" fill="${petalColor}" />
        <circle cx="49" cy="53" r="14" fill="${petalColor}" />
        <circle cx="31" cy="53" r="14" fill="${petalColor}" />
        <circle cx="25" cy="35" r="14" fill="${petalColor}" />
        <circle cx="40" cy="40" r="8" fill="${seedsColor}" />
      </g>
    `;
    },

    // Royal Fleur-de-lis
    fleur_de_lis: (color = PALETTE.or, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -45)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 40 10 C 35 22, 34 35, 40 50 C 46 35, 45 22, 40 10 Z" />
        <path d="M 37 36 C 24 30, 14 36, 12 45 C 15 54, 25 56, 35 50 C 32 54, 26 62, 20 66 L 35 60 C 36 56, 37 46, 37 36 Z" />
        <path d="M 43 36 C 56 30, 66 36, 68 45 C 65 54, 55 56, 45 50 C 48 54, 54 62, 60 66 L 45 60 C 44 56, 43 46, 43 36 Z" />
        <rect x="28" y="48" width="24" height="5" rx="1.5" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        <path d="M 34 53 C 34 65, 40 72, 40 72 C 40 72, 46 65, 46 53 Z" />
      </g>
    `,

    // Wheatsheaf Garb
    wheatsheaf_garb: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, band = PALETTE.gules, field = null) => {
      const bandColor = (field === 'gules') ? PALETTE.azure : (band || PALETTE.gules);
      const garbColor = (color === PALETTE.sable || color === PALETTE.argent) ? color : ((field === 'or') ? PALETTE.vert : (color || PALETTE.or));
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -45)" fill="${garbColor}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 35 45 C 24 35, 12 25, 15 15 C 22 20, 30 32, 35 45 Z" />
        <path d="M 35 45 C 30 30, 28 18, 35 10 C 42 18, 40 30, 35 45 Z" />
        <path d="M 35 45 C 46 35, 58 25, 55 15 C 48 20, 40 32, 35 45 Z" />
        <path d="M 35 52 L 20 74 L 50 74 Z" />
        <rect x="22" y="44" width="26" height="8" rx="2" fill="${bandColor}" stroke="${PALETTE.sable}" stroke-width="1.2" />
      </g>
    `;
    },

    // Oak Branch with Acorns
    oak_branch: (color = PALETTE.vert, scale = 1, cx = 110, cy = 110, acorn = PALETTE.or, field = null) => {
      const leafColor = (field === 'vert' || color === PALETTE.or || color === PALETTE.argent) ? (color !== PALETTE.vert ? color : PALETTE.or) : (color || PALETTE.vert);
      const acornColor = (field === 'or' || color === PALETTE.or) ? PALETTE.gules : (acorn || PALETTE.or);
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -40)" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 35 70 C 35 60, 20 55, 24 45 C 18 42, 18 32, 25 28 C 22 22, 28 15, 35 10 C 42 15, 48 22, 45 28 C 52 32, 52 42, 46 45 C 50 55, 35 60, 35 70 Z" fill="${leafColor}" />
        <line x1="35" y1="18" x2="35" y2="65" stroke="${PALETTE.sable}" stroke-width="1" />
        <rect x="18" y="48" width="8" height="6" rx="2" fill="${PALETTE.wood}" />
        <path d="M 19 54 C 19 60, 25 60, 25 54 Z" fill="${acornColor}" />
        <rect x="44" y="48" width="8" height="6" rx="2" fill="${PALETTE.wood}" />
        <path d="M 45 54 C 45 60, 51 60, 51 54 Z" fill="${acornColor}" />
      </g>
    `;
    },

    // Cluster of Grapes with Vine Leaf
    grape_cluster: (color = PALETTE.purpure, scale = 1, cx = 110, cy = 110, leaf = PALETTE.vert, field = null) => {
      const leafColor = (field === 'vert') ? PALETTE.or : (leaf || PALETTE.vert);
      const grapeColor = (field === 'purpure' || color === PALETTE.or || color === PALETTE.argent) ? (color !== PALETTE.purpure ? color : PALETTE.or) : (color || PALETTE.purpure);
      return `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -40)" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 35 10 Q 30 18 35 25" fill="none" stroke="${PALETTE.wood}" stroke-width="3" />
        <polygon points="35,18 20,12 25,24" fill="${leafColor}" />
        <polygon points="35,18 50,12 45,24" fill="${leafColor}" />
        <circle cx="27" cy="30" r="5" fill="${grapeColor}" />
        <circle cx="35" cy="30" r="5" fill="${grapeColor}" />
        <circle cx="43" cy="30" r="5" fill="${grapeColor}" />
        <circle cx="23" cy="38" r="5" fill="${grapeColor}" />
        <circle cx="31" cy="38" r="5" fill="${grapeColor}" />
        <circle cx="39" cy="38" r="5" fill="${grapeColor}" />
        <circle cx="47" cy="38" r="5" fill="${grapeColor}" />
        <circle cx="27" cy="46" r="5" fill="${grapeColor}" />
        <circle cx="35" cy="46" r="5" fill="${grapeColor}" />
        <circle cx="43" cy="46" r="5" fill="${grapeColor}" />
        <circle cx="31" cy="54" r="5" fill="${grapeColor}" />
        <circle cx="39" cy="54" r="5" fill="${grapeColor}" />
        <circle cx="35" cy="62" r="5" fill="${grapeColor}" />
      </g>
    `;
    },

    // Radiant Sun with 16 Rays
    sun_radiant: (color = PALETTE.or, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -40)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        ${[0, 45, 90, 135, 180, 225, 270, 315].map(deg => `
          <polygon points="40,15 37,28 43,28" transform="rotate(${deg} 40 40)" />
          <path d="M 38 28 Q 44 20 40 12 Q 36 20 42 28" transform="rotate(${deg + 22.5} 40 40)" />
        `).join('')}
        <circle cx="40" cy="40" r="14" fill="${color}" />
      </g>
    `,

    // Six-pointed Star / Mullet
    star_six_pointed: (color = PALETTE.or, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -40)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <polygon points="40,12 47,28 64,28 50,38 56,54 40,44 24,54 30,38 16,28 33,28" />
      </g>
    `,

    // Crescent Moon
    crescent_moon: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -35)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <path d="M 35 10 C 50 10, 60 22, 60 35 C 60 48, 50 60, 35 60 C 45 52, 48 42, 48 35 C 48 28, 45 18, 35 10 Z" />
      </g>
    `,

    // Six-spoked Cart / Mill Wheel
    wheel_spoked: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-40, -40)" stroke="${PALETTE.sable}" stroke-width="1.5">
        <circle cx="40" cy="40" r="28" fill="${color}" />
        <circle cx="40" cy="40" r="22" fill="none" stroke="${PALETTE.sable}" stroke-width="1.5" />
        ${[0, 60, 120, 180, 240, 300].map(deg => `
          <line x1="40" y1="40" x2="${(40 + 22 * Math.cos(deg * Math.PI / 180)).toFixed(1)}" y2="${(40 + 22 * Math.sin(deg * Math.PI / 180)).toFixed(1)}" stroke="${PALETTE.sable}" stroke-width="2.5" />
        `).join('')}
        <circle cx="40" cy="40" r="7" fill="${color}" />
        <circle cx="40" cy="40" r="3" fill="${PALETTE.sable}" />
      </g>
    `,

    // Maritime Anchor
    anchor: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110, stock = PALETTE.wood) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -45)" stroke="${PALETTE.sable}" stroke-width="1.5">
        <rect x="15" y="24" width="40" height="6" rx="2" fill="${stock}" />
        <line x1="35" y1="14" x2="35" y2="70" stroke="${color}" stroke-width="5" stroke-linecap="round" />
        <circle cx="35" cy="14" r="6" fill="none" stroke="${color}" stroke-width="3" />
        <path d="M 12 50 C 18 76, 52 76, 58 50" fill="none" stroke="${color}" stroke-width="5" stroke-linecap="round" />
        <polygon points="12,50 6,56 16,56" fill="${color}" />
        <polygon points="58,50 54,56 64,56" fill="${color}" />
      </g>
    `,

    // Classical Roman Column
    column_roman: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-35, -45)" fill="${color}" stroke="${PALETTE.sable}" stroke-width="1.2">
        <rect x="18" y="14" width="34" height="6" rx="1.5" />
        <polygon points="16,14 54,14 48,22 22,22" />
        <rect x="24" y="22" width="22" height="46" />
        <line x1="28" y1="23" x2="28" y2="67" stroke="${PALETTE.sable}" stroke-width="0.8" />
        <line x1="32" y1="23" x2="32" y2="67" stroke="${PALETTE.sable}" stroke-width="0.8" />
        <line x1="36" y1="23" x2="36" y2="67" stroke="${PALETTE.sable}" stroke-width="0.8" />
        <line x1="40" y1="23" x2="40" y2="67" stroke="${PALETTE.sable}" stroke-width="0.8" />
        <polygon points="22,68 48,68 52,74 18,74" />
        <rect x="16" y="74" width="38" height="6" rx="1" />
      </g>
    `

  };

  // =========================================================================
  // 3. Heraldic Tincture & Charge Dictionaries & Morphological Patterns
  // =========================================================================
  const TINCTURES = {
    or: { key: 'or', tarr: 'Golt', tarrAdj: 'gülden', en: 'Or', enAdj: 'Or', hex: PALETTE.or },
    argent: { key: 'argent', tarr: 'Silber', tarrAdj: 'silbern', en: 'Argent', enAdj: 'Argent', hex: PALETTE.argent },
    gules: { key: 'gules', tarr: 'Keiser-Rôt', tarrAdj: 'rôt', en: 'Gules', enAdj: 'Gules', hex: PALETTE.gules },
    sable: { key: 'sable', tarr: 'Swartz', tarrAdj: 'swartz', en: 'Sable', enAdj: 'Sable', hex: PALETTE.sable },
    azure: { key: 'azure', tarr: 'Lâsûr', tarrAdj: 'blou', en: 'Azure', enAdj: 'Azure', hex: PALETTE.azure },
    vert: { key: 'vert', tarr: 'Grûne', tarrAdj: 'grûne', en: 'Vert', enAdj: 'Vert', hex: PALETTE.vert },
    purpure: { key: 'purpure', tarr: 'Purper', tarrAdj: 'purpern', en: 'Purpure', enAdj: 'Purpure', hex: PALETTE.purpure },
    vermilion: { key: 'vermilion', tarr: 'Zinôber-Rôt', tarrAdj: 'zinôber-rôt', en: 'Vermilion', enAdj: 'Vermilion', hex: PALETTE.vermilion }
  };

  const CHARGE_BLAZONS = {
    eagle_double: { tarrNoun: 'doppelter Adler', enNoun: 'double-headed eagle', enArticle: 'a' },
    alerion: { tarrNoun: 'Alerion', enNoun: 'alerion', enArticle: 'an' },
    castrum: { tarrNoun: 'Burch mit drîn Türmen', enNoun: 'triple-towered castrum', enArticle: 'a' },
    roman_gate: { tarrNoun: 'römisches Stat-Tôr', enNoun: 'Roman city gate', enArticle: 'a' },
    mount_triple: { tarrNoun: 'Dreiberch', enNoun: 'triple mount', enArticle: 'a' },
    bridge: { tarrNoun: 'steinene Brücke', enNoun: 'stone bridge', enArticle: 'a' },
    waves: { tarrNoun: 'Meereswâgen', enNoun: 'waves in base', enArticle: '' },
    bell: { tarrNoun: 'Glocke', enNoun: 'bell', enArticle: 'a' },
    keys_st_peter: { tarrNoun: 'Slüttele van Zant Peter', enNoun: 'keys of St. Peter in saltire', enArticle: 'the' },
    crozier: { tarrNoun: 'Bischofsstap', enNoun: 'crozier', enArticle: 'a' },
    cross_patriarchal: { tarrNoun: 'Patriarchenkrütz', enNoun: 'patriarchal cross', enArticle: 'a' },
    cross_byzantine: { tarrNoun: 'bîsantinisch Krütz belegt mit vîr Füristeinen', enNoun: 'cross between four firesteels', enArticle: 'a' },
    tree_chestnut: { tarrNoun: 'Kestenboum', enNoun: 'chestnut tree', enArticle: 'a' },
    lion_rampant: { tarrNoun: 'klimmender Lôwe', enNoun: 'lion rampant', enArticle: 'a' },
    ship: { tarrNoun: 'Kogge', enNoun: 'lymphad under sail', enArticle: 'a' },
    crown: { tarrNoun: 'Keiserkrône', enNoun: 'imperial crown', enArticle: 'an' },
    dragon: { tarrNoun: 'Drache', enNoun: 'dragon', enArticle: 'a' },
    sword_crossed: { tarrNoun: 'gekrütztes Swert', tarrPlural: 'gekrützte Swerter', enNoun: 'swords in saltire', enPlural: 'swords in saltire', enArticle: '' },
    battleaxe: { tarrNoun: 'Strîtbîle', tarrPlural: 'Strîtbîlen', enNoun: 'battleaxe', enPlural: 'battleaxes', enArticle: 'a' },
    spear: { tarrNoun: 'Spêr', tarrPlural: 'Spêre', enNoun: 'spear with pennon', enPlural: 'spears with pennons', enArticle: 'a' },
    bow_and_arrow: { tarrNoun: 'Boge mit Pfiil', tarrPlural: 'Bogen mit Pfiilen', enNoun: 'bow and arrow', enPlural: 'bows and arrows', enArticle: 'a' },
    shield_escutcheon: { tarrNoun: 'Schiltelîn', tarrPlural: 'Schiltelîne', enNoun: 'inescutcheon', enPlural: 'inescutcheons', enArticle: 'an' },
    stag_attired: { tarrNoun: 'stehender Hirz', tarrPlural: 'stehende Hirze', enNoun: 'stag attired', enPlural: 'stags attired', enArticle: 'a' },
    bear_rampant: { tarrNoun: 'klimmender Bêr', tarrPlural: 'klimmende Bêren', enNoun: 'bear rampant', enPlural: 'bears rampant', enArticle: 'a' },
    horse_courant: { tarrNoun: 'lopendes Ros', tarrPlural: 'lopende Rosse', enNoun: 'horse courant', enPlural: 'horses courant', enArticle: 'a' },
    wolf_statant: { tarrNoun: 'stehender Wolf', tarrPlural: 'stehende Wolfe', enNoun: 'wolf statant', enPlural: 'wolves statant', enArticle: 'a' },
    fish_twin: { tarrNoun: 'zwên aufsteigende Vische', tarrPlural: 'Vische', enNoun: 'two fish haurient', enPlural: 'fish haurient', enArticle: '' },
    falcon_perched: { tarrNoun: 'sitzender Valke', tarrPlural: 'sitzende Valken', enNoun: 'falcon perched', enPlural: 'falcons perched', enArticle: 'a' },
    rose_seeded: { tarrNoun: 'gekernde Rôse', tarrPlural: 'gekernde Rôsen', enNoun: 'heraldic rose', enPlural: 'heraldic roses', enArticle: 'a' },
    fleur_de_lis: { tarrNoun: 'Lilje', tarrPlural: 'Liljen', enNoun: 'fleur-de-lis', enPlural: 'fleurs-de-lis', enArticle: 'a' },
    wheatsheaf_garb: { tarrNoun: 'Kornbouche', tarrPlural: 'Kornbouchen', enNoun: 'wheat garb', enPlural: 'wheat garbs', enArticle: 'a' },
    oak_branch: { tarrNoun: 'Eikentwîch mit Eicheln', tarrPlural: 'Eikentwîge', enNoun: 'oak branch with acorns', enPlural: 'oak branches', enArticle: 'an' },
    grape_cluster: { tarrNoun: 'Wîntrûbe mit Blat', tarrPlural: 'Wîntrûben', enNoun: 'cluster of grapes', enPlural: 'clusters of grapes', enArticle: 'a' },
    sun_radiant: { tarrNoun: 'strâlende Sunne', tarrPlural: 'strâlende Sunnen', enNoun: 'sun radiant', enPlural: 'suns radiant', enArticle: 'a' },
    star_six_pointed: { tarrNoun: 'sechsspitziger Stern', tarrPlural: 'sechsspitzige Sterne', enNoun: 'six-pointed mullet', enPlural: 'six-pointed mullets', enArticle: 'a' },
    crescent_moon: { tarrNoun: 'Mânschîn', tarrPlural: 'Mânschîne', enNoun: 'crescent moon', enPlural: 'crescent moons', enArticle: 'a' },
    wheel_spoked: { tarrNoun: 'speichertes Rad', tarrPlural: 'speicherte Reder', enNoun: 'spoked wheel', enPlural: 'spoked wheels', enArticle: 'a' },
    anchor: { tarrNoun: 'Anker', tarrPlural: 'Ankere', enNoun: 'anchor', enPlural: 'anchors', enArticle: 'an' },
    column_roman: { tarrNoun: 'rômische Sûle', tarrPlural: 'rômische Sûlen', enNoun: 'Roman column', enPlural: 'Roman columns', enArticle: 'a' }
  };

  const ORDINARY_BLAZONS = {
    solid: { key: 'solid', tarr: 'Einfach', en: 'Solid' },
    per_pale: { key: 'per_pale', tarr: 'Gespalten', en: 'Party per pale' },
    per_fess: { key: 'per_fess', tarr: 'Geteilt', en: 'Party per fess' },
    per_bend: { key: 'per_bend', tarr: 'Schräggeteilt', en: 'Party per bend' },
    per_bend_sinister: { key: 'per_bend_sinister', tarr: 'Links-schräggeteilt', en: 'Party per bend sinister' },
    quarterly: { key: 'quarterly', tarr: 'Geviert', en: 'Quarterly' },
    per_saltire: { key: 'per_saltire', tarr: 'Schräggeviert', en: 'Party per saltire' },
    fess: { key: 'fess', tarr: 'Balken', en: 'Fess' },
    pale: { key: 'pale', tarr: 'Pfahl', en: 'Pale' },
    bend: { key: 'bend', tarr: 'Schrägbalken', en: 'Bend' },
    bend_sinister: { key: 'bend_sinister', tarr: 'Schräglinksbalken', en: 'Bend sinister' },
    chevron: { key: 'chevron', tarr: 'Sparren', en: 'Chevron' },
    cross: { key: 'cross', tarr: 'Krütz', en: 'Cross' },
    saltire: { key: 'saltire', tarr: 'Andreaskrütz', en: 'Saltire' },
    chief: { key: 'chief', tarr: 'Schildhaupt', en: 'Chief' },
    bordure: { key: 'bordure', tarr: 'Bordüre', en: 'Bordure' },
    barry: { key: 'barry', tarr: 'Gestreift', en: 'Barry' },
    chequy: { key: 'chequy', tarr: 'Geschacht', en: 'Chequy' },
    pales: { key: 'pales', tarr: 'Gepfählt', en: 'Paly' },
    pales_undy: { key: 'pales_undy', tarr: 'Wellengepfählt', en: 'Paly undy' }
  };


  const CANONICAL_HERALDRY = {"k_papal_state":["gules","solid","keys_st_peter","or",1,"or"],"k_orthodox":["azure","solid","castrum","or",1,"argent"],"k_fashion":["purpure","solid","castrum","or",1,"or"],"d_iconoclast":["azure","solid","castrum","or",1,"argent"],"k_danelaw":["gules","solid","castrum","or",1,"argent"],"k_daneland":["gules","solid","castrum","or",1,"argent"],"d_sunni":["argent","solid","castrum","azure",1,"sable"],"d_shiite":["sable","solid","castrum","or",1,"argent"],"d_imami":["vert","solid","castrum","or",1,"argent"],"d_ismaili":["sable","solid","castrum","or",1,"argent"],"d_nizari":["vert","solid","castrum","or",1,"argent"],"d_zayidi":["vert","solid","castrum","or",1,"or"],"d_masmudi":["argent","per_bend","castrum","azure",1,"gules"],"d_muwalladi":["argent","solid","castrum","azure",1,"or"],"e_golden_horde":["argent","solid","castrum","azure",1,"gules"],"e_ilkhanate":["or","solid","castrum","sable",1,"gules"],"e_chagatai":["argent","solid","castrum","azure",1,"or"],"e_red_horde":["gules","solid","castrum","or",1,"or"],"e_white_horde":["argent","solid","castrum","azure",1,"sable"],"e_aarlud_khanate":["argent","solid","bow_and_arrow","sable",1,"sable"],"e_togskol_khanate":["gules","solid","bow_and_arrow","or",1,"or"],"e_baruun_khanate":["azure","solid","bow_and_arrow","argent",1,"argent"],"e_great_yuan":["argent","solid","castrum","azure",1,"azure"],"e_blue_horde":["azure","solid","bow_and_arrow","argent",1,"or"],"e_omnod_dalai_khanate":["vert","solid","bow_and_arrow","argent",1,"argent"],"e_uyghur_khanate":["azure","solid","bow_and_arrow","argent",1,"argent"],"e_kirghiz_khanate":["gules","solid","bow_and_arrow","or",1,"or"],"e_mongol_empire":["azure","solid","castrum","or",1,"argent"],"e_great_liao":["azure","solid","castrum","or",1,"argent"],"e_kara_khitai":["sable","chevron","chevron","or",1,"or"],"e_jin":["vert","solid","castrum","or",1,"gules"],"e_timurids":["sable","solid","castrum","or",1,"gules"],"k_bosporan_kingdom":["gules","solid","alerion","or",1,"argent"],"k_naiman":["sable","chevron","bow_and_arrow","or",1,"or"],"k_sakya_trizin":["gules","solid","rose_seeded","or",1,"argent"],"k_guiyi":["gules","solid","rose_seeded","or",1,"sable"],"k_switzerland":["gules","solid","cross","argent",1,"argent"],"k_austria":["gules","solid","eagle_double","or",1,"argent"],"k_carantania":["argent","solid","crown","azure",1,"azure"],"e_outremer":["or","solid","cross","gules",1,"gules"],"k_toledo":["azure","solid","cross","or",1,"or"],"d_jomsvikings":["argent","solid","castrum","azure",1,"gules"],"e_latin_empire":["gules","solid","cross","or",1,"or"],"e_slavia":["argent","solid","crown","azure",2,"azure"],"e_armenia":["or","solid","lion_rampant","gules",1,"gules"],"e_viet":["or","solid","castrum","sable",1,"gules"],"e_majapahit":["gules","solid","castrum","or",1,"argent"],"e_ruucuu":["argent","solid","castrum","azure",1,"azure"],"e_north_sea":["or","solid","waves","azure",1,"azure"],"e_carthage":["purpure","solid","bow_and_arrow","argent",1,"argent"],"k_pechenegs":["gules","chevron","horse_courant","argent",1,"argent"],"k_carthage":["gules","solid","castrum","or",1,"argent"],"k_tripolitania":["gules","solid","castrum","or",1,"argent"],"k_mauretania":["gules","per_fess","castrum","or",1,"argent"],"k_carthago_nova":["gules","solid","castrum","or",1,"argent"],"d_zaragoza":["gules","solid","lion_rampant","or",1,"or"],"d_amalfi":["azure","solid","cross","argent",1,"argent"],"e_hre":["or","solid","bend","gules",1,"gules"],"k_hansa":["argent","solid","eagle_double","sable",1,"gules"],"e_britannia":["argent","solid","dragon","gules",1,"gules"],"k_england":["gules","solid","lion_rampant","or",3,"or"],"d_bedford":["gules","solid","castrum","or",1,"or"],"c_middlesex":["argent","solid","cross","gules",1,"gules"],"c_essex":["or","chequy","castrum","sable",1,"gules"],"b_dunmow":["or","solid","castrum","sable",1,"gules"],"c_bedford":["or","solid","castrum","sable",1,"gules"],"b_luton":["gules","solid","cross","or",3,"or"],"c_hertfordshire":["or","solid","chevron","gules",1,"gules"],"b_saint_albans":["azure","solid","castrum","or",1,"or"],"c_buckinghamshire":["gules","solid","lion_rampant","argent",3,"argent"],"b_aylesbury":["azure","solid","cross","argent",1,"argent"],"b_newport":["or","solid","fess","gules",1,"gules"],"b_wycombe":["or","solid","castrum","sable",1,"gules"],"d_northumberland":["purpure","solid","castrum","or",1,"or"],"c_northumberland":["or","solid","castrum","sable",1,"gules"],"c_durham":["azure","solid","cross","or",1,"argent"],"c_cumberland":["or","solid","fess","gules",1,"azure"],"d_lancaster":["argent","per_pale","cross","gules",1,"gules"],"c_lancashire":["argent","solid","castrum","azure",1,"gules"],"c_westmorland":["gules","solid","castrum","or",1,"argent"],"b_appleby":["or","solid","fess","gules",1,"azure"],"c_cheshire":["azure","solid","wheatsheaf_garb","or",1,"argent"],"c_derby":["or","solid","castrum","sable",1,"gules"],"c_north_riding":["azure","solid","fess","or",1,"or"],"b_scarborough":["argent","solid","fess","gules",1,"vert"],"c_west_riding":["gules","solid","castrum","or",1,"or"],"c_lincolnshire":["or","solid","lion_rampant","purpure",1,"purpure"],"d_norfolk":["gules","solid","cross","argent",1,"argent"],"c_norfolk":["argent","solid","cross","gules",1,"gules"],"c_suffolk":["sable","solid","cross","or",1,"or"],"c_cambridgeshire":["or","solid","lion_rampant","sable",1,"sable"],"d_hereford":["azure","solid","castrum","or",1,"or"],"c_warwickshire":["or","solid","bend","sable",1,"azure"],"c_leicestershire":["argent","solid","castrum","azure",1,"gules"],"c_nottinghamshire":["gules","solid","lion_rampant","argent",1,"argent"],"b_newark":["vert","solid","bow_and_arrow","or",1,"argent"],"c_staffordshire":["or","solid","chevron","gules",1,"gules"],"c_worcestershire":["argent","solid","castrum","azure",1,"gules"],"c_huntingdonshire":["or","solid","castrum","sable",1,"gules"],"c_northamptonshire":["argent","solid","lion_rampant","azure",1,"gules"],"c_shropshire":["or","solid","bend","azure",1,"azure"],"d_gloucester":["sable","solid","alerion","or",1,"or"],"c_gloucestershire":["gules","solid","castrum","or",1,"or"],"c_wiltshire":["azure","solid","dragon","or",1,"or"],"c_oxfordshire":["gules","chequy","star_six_pointed","argent",1,"or"],"c_berkshire":["argent","per_pale","fess","gules",1,"gules"],"b_newbury":["argent","solid","castrum","azure",1,"sable"],"c_kent":["gules","solid","castrum","or",1,"argent"],"b_canterbury":["azure","solid","castrum","or",1,"argent"],"c_surrey":["or","solid","castrum","sable",1,"azure"],"c_sussex":["gules","solid","lion_rampant","or",1,"or"],"b_hastings":["or","solid","castrum","sable",1,"gules"],"d_somerset":["gules","solid","dragon","or",1,"or"],"c_hampton":["or","solid","fess","gules",1,"gules"],"b_southampton":["argent","solid","castrum","azure",1,"gules"],"c_isle_of_wight":["or","solid","lion_rampant","azure",1,"azure"],"c_dorset":["gules","solid","dragon","or",1,"or"],"c_somerset":["or","solid","dragon","gules",1,"argent"],"d_cornwall":["sable","solid","crown","or",1,"argent"],"c_devon":["or","solid","lion_rampant","azure",1,"azure"],"b_okehampton":["or","solid","castrum","sable",1,"gules"],"c_cornwall":["sable","solid","castrum","or",1,"or"],"b_tintagel":["sable","solid","cross","argent",1,"argent"],"k_wales":["or","solid","lion_rampant","gules",2,"gules"],"d_gwynedd":["argent","solid","dragon","gules",1,"gules"],"c_cardiganshire":["sable","solid","lion_rampant","or",1,"argent"],"c_merioneth":["azure","solid","castrum","or",1,"argent"],"c_caernarfonshire":["vert","solid","alerion","or",3,"argent"],"c_anglesey":["gules","solid","chevron","or",1,"or"],"b_holyhead":["argent","per_fess","castrum","azure",1,"vert"],"c_denbighshire":["argent","chequy","lion_rampant","sable",1,"azure"],"b_wrexham":["sable","solid","cross","argent",1,"argent"],"d_powys":["or","solid","lion_rampant","gules",1,"gules"],"c_maldwyn":["argent","solid","lion_rampant","sable",1,"azure"],"b_newtown":["or","solid","lion_rampant","gules",1,"gules"],"c_sir_faesyfed":["gules","chequy","lion_rampant","or",2,"argent"],"b_llandrindod":["gules","solid","lion_rampant","or",1,"argent"],"b_rhayader":["argent","solid","castrum","azure",1,"azure"],"b_wigmore":["or","solid","castrum","sable",1,"azure"],"b_clifford":["or","solid","bend","gules",1,"azure"],"d_deheubarth":["gules","solid","lion_rampant","or",1,"or"],"c_carmarthenshire":["azure","solid","lion_rampant","or",1,"argent"],"c_pembrokeshire":["or","per_pale","lion_rampant","gules",1,"vert"],"b_st_davids":["sable","solid","cross","or",1,"or"],"c_glamorgan":["gules","solid","chevron","argent",1,"argent"],"c_monmouthshire":["azure","per_pale","fleur_de_lis","or",3,"argent"],"c_brecknockshire":["sable","solid","chevron","argent",1,"argent"],"k_scotland":["or","bordure","lion_rampant","gules",1,"gules"],"d_albany":["azure","solid","castrum","or",1,"argent"],"c_gowrie":["or","solid","castrum","sable",1,"gules"],"c_fife":["or","solid","lion_rampant","gules",1,"argent"],"c_strathearn":["or","solid","chevron","gules",1,"gules"],"c_atholl":["or","solid","castrum","sable",1,"sable"],"b_dunkeld":["or","solid","lion_rampant","gules",1,"gules"],"c_angus":["argent","solid","lion_rampant","gules",1,"gules"],"b_mar":["azure","solid","bend","or",1,"or"],"c_mearns":["argent","solid","pale","azure",1,"gules"],"d_the_isles":["gules","solid","castrum","or",1,"argent"],"c_isle_of_man":["gules","solid","castrum","or",1,"argent"],"b_ramsey":["argent","solid","lion_rampant","gules",1,"azure"],"d_galloway":["azure","solid","crown","argent",1,"argent"],"c_lennox":["argent","solid","castrum","azure",1,"gules"],"b_meneith":["or","solid","castrum","sable",1,"gules"],"c_galloway":["azure","solid","lion_rampant","argent",1,"argent"],"c_carrick":["argent","solid","chevron","gules",1,"gules"],"c_ayrshire":["or","solid","fess","azure",1,"argent"],"c_annandale":["or","solid","fess","gules",1,"gules"],"c_outer_hebrides":["azure","solid","castrum","argent",1,"argent"],"d_lothian":["gules","solid","lion_rampant","argent",1,"argent"],"c_lothian":["argent","solid","castrum","sable",1,"sable"],"b_penicuick":["argent","solid","cross","sable",1,"sable"],"c_dunbar":["gules","solid","lion_rampant","argent",1,"argent"],"c_teviotdale":["argent","solid","castrum","azure",1,"gules"],"c_linlithgowshire":["argent","solid","castrum","azure",1,"gules"],"c_lanarkshire":["argent","solid","star_six_pointed","azure",3,"azure"],"b_cadyou":["gules","solid","castrum","or",1,"argent"],"d_moray":["azure","solid","star_six_pointed","argent",3,"argent"],"c_moray":["azure","solid","star_six_pointed","argent",3,"argent"],"c_ross":["gules","solid","lion_rampant","argent",3,"argent"],"c_buchan":["azure","solid","wheatsheaf_garb","or",3,"or"],"c_sutherland":["gules","solid","star_six_pointed","or",3,"or"],"c_caithness":["gules","solid","ship","or",1,"or"],"c_inverness":["gules","solid","wheatsheaf_garb","or",3,"or"],"k_ireland":["azure","solid","castrum","or",1,"or"],"d_meath":["azure","solid","crown","or",3,"or"],"b_kildare":["argent","solid","castrum","azure",1,"gules"],"c_athlone":["argent","solid","castrum","azure",1,"gules"],"d_ulster":["or","solid","cross","gules",1,"gules"],"c_ulster":["or","solid","fess","gules",1,"gules"],"c_oriel":["vert","solid","castrum","or",1,"argent"],"c_ailech":["argent","solid","castrum","azure",1,"gules"],"d_connacht":["argent","solid","oak_branch","vert",1,"vert"],"c_connacht":["argent","solid","eagle_double","sable",1,"azure"],"c_breifne":["or","solid","lion_rampant","sable",2,"sable"],"d_leinster":["gules","solid","lion_rampant","argent",1,"argent"],"c_leinster":["gules","solid","lion_rampant","argent",1,"argent"],"c_ossory":["sable","solid","castrum","or",1,"argent"],"d_munster":["argent","solid","lion_rampant","gules",3,"gules"],"c_thomond":["gules","per_pale","castrum","or",1,"or"],"c_ormond":["or","solid","castrum","sable",1,"azure"],"c_desmond":["argent","solid","stag_attired","gules",1,"gules"],"k_cornwall":["sable","solid","crown","or",3,"or"],"k_mann_the_isles":["gules","solid","waves","or",1,"argent"],"k_cumbria":["argent","solid","crown","azure",1,"azure"],"d_cumbria":["gules","solid","fess","or",1,"azure"],"e_germany":["or","solid","eagle_double","sable",1,"sable"],"k_saxony":["sable","solid","castrum","or",1,"argent"],"d_angria":["argent","solid","castrum","azure",1,"gules"],"c_minden":["gules","solid","keys_st_peter","argent",1,"argent"],"c_lippe":["argent","solid","castrum","azure",1,"gules"],"c_bremen":["gules","solid","keys_st_peter","argent",1,"argent"],"c_wolpe":["azure","solid","castrum","or",1,"argent"],"c_hannover":["gules","solid","castrum","or",1,"or"],"c_hildesheim":["or","solid","castrum","sable",1,"gules"],"c_oldenburg":["or","solid","castrum","sable",1,"gules"],"d_westfalen":["gules","solid","horse_courant","argent",1,"argent"],"c_osnabruck":["argent","solid","wheel_spoked","gules",1,"gules"],"c_tecklenburg":["argent","solid","castrum","azure",1,"gules"],"c_munster":["or","solid","fess","gules",1,"gules"],"c_waldeck":["or","solid","star_six_pointed","sable",1,"sable"],"c_paderborn":["gules","solid","cross","or",1,"or"],"d_ostfalen":["or","solid","castrum","sable",1,"gules"],"c_luneburg":["or","solid","lion_rampant","azure",1,"azure"],"c_brunswick":["gules","solid","castrum","or",1,"or"],"c_hamburg":["gules","solid","castrum","argent",1,"argent"],"c_dannenberg":["or","solid","lion_rampant","azure",1,"azure"],"c_stendal":["argent","per_pale","alerion","gules",1,"gules"],"d_holstein":["gules","solid","castrum","or",1,"argent"],"c_lubeck":["or","solid","eagle_double","sable",1,"argent"],"c_stade":["azure","solid","keys_st_peter","argent",1,"argent"],"c_ditmarschen":["gules","solid","castrum","or",1,"argent"],"k_frisia":["azure","bend","rose_seeded","argent",2,"argent"],"d_holland":["or","solid","crown","gules",1,"gules"],"c_holland":["or","solid","lion_rampant","gules",1,"gules"],"c_westfriesland":["azure","solid","lion_rampant","or",2,"or"],"c_zeeland":["gules","chief","lion_rampant","or",1,"or"],"d_gelre":["azure","solid","crown","or",1,"or"],"c_guelders":["or","solid","castrum","sable",1,"gules"],"c_arnhem":["azure","solid","eagle_double","argent",1,"argent"],"c_zutphen":["argent","solid","cross","gules",1,"gules"],"d_utrecht":["gules","solid","cross","argent",1,"argent"],"c_nedersticht":["argent","solid","bend","azure",1,"gules"],"c_oversticht":["azure","solid","cross","argent",1,"argent"],"c_groningen":["argent","solid","fess","vert",1,"vert"],"d_frisia":["azure","solid","lion_rampant","or",2,"or"],"c_dokkum":["azure","solid","crescent_moon","argent",3,"argent"],"c_ostfriesland":["sable","solid","alerion","or",1,"or"],"c_frisia":["azure","solid","castrum","or",1,"or"],"k_lotharingia":["or","bend","alerion","sable",3,"gules"],"d_luxembourg":["argent","solid","crown","gules",1,"azure"],"c_luxembourg":["argent","solid","crown","gules",1,"azure"],"b_vianden":["gules","solid","castrum","or",1,"argent"],"c_bouillon":["gules","solid","fess","argent",1,"argent"],"b_chiny":["gules","solid","cross","or",3,"or"],"c_liege":["gules","solid","spear","or",1,"or"],"c_namur":["or","solid","lion_rampant","sable",1,"sable"],"d_brabant":["sable","solid","lion_rampant","or",1,"or"],"c_brabant":["or","solid","pale","gules",1,"gules"],"b_brussels":["gules","solid","castrum","or",1,"or"],"c_antwerpen":["or","solid","castrum","sable",1,"sable"],"b_breda":["gules","solid","castrum","or",1,"argent"],"c_hainaut":["or","solid","chevron","sable",1,"sable"],"c_cambray":["argent","solid","lion_rampant","gules",3,"gules"],"d_julich":["or","solid","crown","sable",1,"sable"],"c_aachen":["or","solid","alerion","sable",1,"sable"],"c_cleves":["gules","solid","castrum","or",1,"argent"],"c_maastricht":["gules","solid","star_six_pointed","argent",1,"argent"],"d_upper_lorraine":["or","solid","bend","gules",1,"gules"],"c_trier":["argent","solid","cross","gules",1,"gules"],"c_nancy":["gules","solid","cross","argent",3,"argent"],"b_blankenberg":["gules","solid","castrum","or",1,"argent"],"b_salm":["argent","solid","castrum","azure",1,"gules"],"c_metz":["argent","per_pale","cross","gules",1,"gules"],"c_saarbrucken":["azure","solid","crown","argent",1,"argent"],"c_puttlingen":["or","solid","pale","gules",1,"gules"],"c_neufchateau":["or","solid","bend","gules",1,"gules"],"b_vaudemont":["argent","solid","castrum","azure",1,"sable"],"d_lower_lorraine":["argent","solid","crown","gules",1,"gules"],"c_cologne":["argent","solid","cross","sable",1,"sable"],"c_dortmund":["or","solid","castrum","sable",1,"azure"],"b_dortmund":["argent","solid","alerion","sable",1,"sable"],"c_arnsberg":["gules","solid","alerion","argent",1,"argent"],"c_mark":["or","solid","fess","gules",1,"gules"],"c_koblenz":["argent","solid","castrum","azure",1,"gules"],"b_sponhem":["argent","solid","castrum","azure",1,"gules"],"c_bergh":["argent","solid","castrum","azure",1,"gules"],"c_sayn":["or","solid","lion_rampant","gules",1,"gules"],"d_bar":["azure","solid","cross","or",3,"or"],"c_bar":["azure","solid","castrum","or",1,"or"],"c_briey":["or","solid","pale","sable",1,"sable"],"c_vaucouleurs":["azure","chief","lion_rampant","argent",1,"or"],"b_toul":["argent","solid","castrum","azure",1,"gules"],"k_bavaria":["argent","chequy","castrum","azure",1,"azure"],"d_bavaria":["argent","solid","bend","azure",1,"azure"],"c_regensburg":["gules","solid","bend","argent",1,"argent"],"c_munchen":["azure","solid","lion_rampant","argent",1,"or"],"c_eschenlohe":["argent","per_pale","fess","azure",1,"sable"],"c_rothenburg":["argent","solid","mount_triple","azure",1,"gules"],"c_geisenhausen":["gules","solid","castrum","or",1,"argent"],"c_frontenhausen":["gules","solid","bend","argent",1,"argent"],"c_falkenstein":["azure","solid","mount_triple","or",1,"or"],"c_ingolstadt":["argent","solid","castrum","azure",1,"sable"],"c_passau":["argent","solid","wolf_statant","gules",1,"gules"],"d_nordgau":["azure","solid","crown","or",3,"or"],"c_eichstadt":["gules","solid","castrum","or",1,"argent"],"b_hirschberg":["or","solid","mount_triple","vert",1,"sable"],"c_leuchtenburg":["argent","solid","fess","azure",1,"azure"],"c_parsberg":["sable","solid","castrum","or",1,"argent"],"c_hohenburg":["gules","solid","castrum","or",1,"argent"],"d_salzburg":["or","solid","lion_rampant","sable",1,"sable"],"c_salzburg":["argent","solid","castrum","azure",1,"sable"],"c_berchtesgaden":["gules","solid","keys_st_peter","or",1,"argent"],"b_kitzbuhel":["argent","solid","mount_triple","sable",1,"sable"],"c_linz":["gules","per_fess","fess","argent",1,"argent"],"b_steyr":["vert","solid","castrum","or",1,"argent"],"c_schaumberg":["azure","solid","castrum","or",1,"argent"],"b_strasswalchen":["argent","solid","bend","azure",1,"gules"],"d_augsburg":["gules","solid","oak_branch","or",1,"argent"],"c_augsburg":["gules","solid","castrum","or",1,"argent"],"c_alpsee":["gules","solid","castrum","or",1,"argent"],"c_kempten":["gules","solid","fess","or",1,"azure"],"c_ravensburg":["argent","solid","castrum","azure",1,"azure"],"b_bregenz":["argent","solid","castrum","azure",1,"sable"],"c_burgau":["argent","solid","bend","azure",1,"gules"],"d_steyermark":["vert","solid","castrum","or",1,"argent"],"c_graz":["argent","solid","castrum","azure",1,"vert"],"c_pitten":["argent","solid","dragon","gules",1,"gules"],"c_murzzuschlag":["or","solid","castrum","sable",1,"sable"],"d_osterreich":["gules","solid","fess","argent",1,"argent"],"c_vienna":["sable","solid","alerion","or",1,"or"],"c_hohenau":["azure","solid","alerion","or",3,"or"],"c_sankt_polten":["sable","solid","castrum","or",1,"argent"],"b_sankt_polten":["argent","solid","wolf_statant","gules",1,"gules"],"c_freistadt":["sable","per_pale","alerion","or",1,"or"],"c_amstetten":["sable","solid","fess","argent",1,"argent"],"c_krems":["or","solid","castrum","sable",1,"sable"],"b_horn":["azure","solid","castrum","or",1,"argent"],"d_tyrol":["argent","solid","alerion","gules",1,"gules"],"c_innsbruck":["azure","solid","alerion","argent",1,"argent"],"c_brixen":["argent","solid","alerion","gules",1,"gules"],"c_lienz":["azure","solid","castrum","or",1,"or"],"d_carinthia":["argent","solid","castrum","azure",1,"sable"],"c_karnten":["or","solid","lion_rampant","sable",3,"sable"],"c_kammersberg":["argent","solid","bend","sable",1,"sable"],"c_knittelfeld":["gules","solid","castrum","or",1,"argent"],"c_villach":["azure","solid","lion_rampant","or",1,"or"],"d_krain":["argent","solid","alerion","azure",1,"azure"],"c_kranj":["argent","solid","alerion","azure",1,"azure"],"c_ljubljana":["azure","solid","star_six_pointed","or",3,"or"],"k_east_francia":["or","solid","alerion","sable",1,"sable"],"d_west_franconia":["sable","solid","crown","or",1,"or"],"c_frankfurt":["gules","solid","alerion","argent",1,"argent"],"b_hanau":["or","solid","chevron","sable",1,"gules"],"c_mainz":["gules","solid","wheel_spoked","argent",1,"argent"],"b_katzenelnbogen":["or","solid","lion_rampant","gules",1,"gules"],"b_boppard":["argent","solid","lion_rampant","sable",1,"sable"],"c_klingenberg":["azure","solid","castrum","or",1,"argent"],"c_erbach":["argent","solid","fess","gules",1,"gules"],"c_worms":["azure","solid","keys_st_peter","argent",1,"argent"],"c_speyer":["azure","solid","cross","argent",1,"argent"],"c_vaihingen":["argent","solid","mount_triple","azure",1,"gules"],"c_durne":["azure","solid","castrum","or",1,"argent"],"c_kaiserslautern":["gules","solid","lion_rampant","or",3,"or"],"b_kreusnach":["or","solid","castrum","sable",1,"azure"],"b_veldenz":["argent","solid","lion_rampant","azure",1,"azure"],"d_east_franconia":["argent","solid","castrum","azure",1,"gules"],"c_wurzburg":["argent","solid","castrum","azure",1,"gules"],"c_ansbach":["gules","solid","castrum","or",1,"argent"],"c_coburg":["or","solid","castrum","sable",1,"sable"],"c_hohenlohe":["argent","solid","lion_rampant","sable",2,"sable"],"c_nurnberg":["or","solid","lion_rampant","sable",1,"sable"],"c_bamberg":["or","solid","lion_rampant","sable",1,"sable"],"b_casel":["argent","solid","castrum","azure",1,"gules"],"c_nordlingen":["or","solid","castrum","sable",1,"gules"],"c_wiltberg":["or","solid","castrum","sable",1,"sable"],"b_schweinfurt":["azure","solid","alerion","argent",1,"argent"],"b_henneberg":["or","solid","mount_triple","vert",1,"sable"],"d_hesse":["argent","solid","crown","azure",1,"gules"],"c_kassel":["argent","solid","lion_rampant","azure",1,"gules"],"c_fulda":["argent","solid","cross","sable",1,"sable"],"c_nassau":["azure","solid","lion_rampant","or",1,"or"],"b_solms":["or","solid","lion_rampant","azure",1,"azure"],"c_marburg":["or","solid","star_six_pointed","sable",2,"sable"],"d_currezia":["argent","solid","castrum","azure",1,"sable"],"c_grisons":["sable","solid","castrum","or",1,"argent"],"c_sankt_gallen":["or","solid","bear_rampant","sable",1,"sable"],"b_konstanz":["argent","solid","cross","sable",1,"sable"],"c_zurich":["argent","solid","bend","azure",1,"azure"],"b_basel":["argent","solid","castrum","azure",1,"gules"],"d_alsace":["gules","solid","bend","argent",1,"argent"],"c_strassburg":["argent","solid","bend","gules",1,"gules"],"c_breisgau":["or","solid","alerion","gules",1,"gules"],"c_colmar":["argent","solid","castrum","azure",1,"sable"],"c_sundgau":["gules","solid","castrum","or",1,"or"],"d_swabia":["or","solid","castrum","sable",1,"sable"],"c_ulm":["argent","solid","castrum","azure",1,"sable"],"b_helfenstein":["gules","solid","mount_triple","or",1,"argent"],"c_grunningen":["vert","solid","lion_rampant","argent",1,"argent"],"b_sigmaringen":["azure","solid","mount_triple","argent",1,"or"],"c_wurttemberg":["or","solid","castrum","sable",1,"sable"],"b_tubingen":["or","solid","castrum","sable",1,"gules"],"b_teck":["or","solid","bend","sable",1,"sable"],"c_baden":["or","solid","bend","gules",1,"gules"],"b_calw":["or","solid","mount_triple","azure",1,"gules"],"c_zollern":["argent","solid","castrum","azure",1,"sable"],"b_vehringen":["or","solid","castrum","sable",1,"gules"],"c_hohenberg":["gules","solid","castrum","or",1,"argent"],"c_furstenberg":["or","solid","castrum","sable",1,"azure"],"b_nellenburg":["or","solid","castrum","sable",1,"azure"],"d_anhalt":["or","solid","castrum","sable",1,"sable"],"c_dessau":["or","solid","castrum","sable",1,"gules"],"c_halberstadt":["argent","solid","castrum","azure",1,"gules"],"c_magdeburg":["gules","per_pale","alerion","argent",1,"argent"],"c_blankenburg":["gules","solid","fess","argent",1,"argent"],"c_mansfeld":["argent","solid","castrum","azure",1,"gules"],"c_mersenburg":["or","solid","cross","sable",1,"sable"],"d_thuringia":["argent","solid","crown","gules",1,"gules"],"c_schmalkalden":["azure","solid","lion_rampant","argent",1,"argent"],"c_gottingen":["argent","solid","lion_rampant","gules",1,"gules"],"c_gleichenstein":["gules","solid","castrum","or",1,"argent"],"c_orlamunde":["or","solid","lion_rampant","sable",1,"sable"],"c_lobdaburg":["gules","solid","bend","argent",1,"argent"],"e_illyria":["gules","solid","alerion","or",1,"argent"],"e_macedonia":["azure","solid","star_six_pointed","or",1,"argent"],"e_anatolia":["argent","solid","cross","gules",3,"or"],"e_oriens":["argent","chief","cross","sable",3,"sable"],"e_aegyptus":["gules","solid","column_roman","or",1,"or"],"e_africa":["sable","solid","cross","argent",1,"azure"],"e_byzantium":["gules","solid","cross","or",1,"or"],"k_saruhan":["sable","solid","crescent_moon","or",1,"or"],"k_trinacria":["or","solid","alerion","sable",2,"argent"],"k_tekke":["argent","solid","star_six_pointed","gules",1,"gules"],"k_trebizond":["gules","solid","eagle_double","or",1,"or"],"k_ottoman":["gules","solid","crescent_moon","or",1,"or"],"k_rum":["argent","solid","eagle_double","azure",1,"azure"],"k_mentese":["azure","solid","star_six_pointed","argent",1,"argent"],"k_karaman":["argent","solid","star_six_pointed","azure",1,"azure"],"k_germiyan":["gules","solid","castrum","or",1,"or"],"k_eretnid":["gules","solid","castrum","or",1,"or"],"k_aydin":["gules","solid","castrum","or",1,"sable"],"k_candar":["argent","solid","star_six_pointed","gules",1,"gules"],"k_thessalonika":["gules","solid","cross","argent",1,"argent"],"d_thrace":["purpure","solid","castrum","or",1,"argent"],"d_strymon":["or","solid","cross","sable",1,"sable"],"c_mosynopolis":["gules","solid","cross","or",1,"or"],"d_aegean_islands":["argent","solid","bend","azure",1,"azure"],"c_naxos":["or","solid","castrum","sable",1,"sable"],"c_abydos":["gules","solid","castrum","or",1,"argent"],"c_lesbos":["argent","per_fess","castrum","azure",1,"gules"],"c_chios":["gules","solid","fleur_de_lis","or",1,"argent"],"d_thessalonika":["or","solid","castrum","sable",1,"gules"],"d_thessaly":["argent","solid","castrum","azure",1,"gules"],"k_epirus":["sable","solid","alerion","or",3,"or"],"d_epirus":["azure","solid","cross","argent",1,"argent"],"c_epeiros":["argent","solid","castrum","sable",1,"azure"],"d_dyrrachion":["sable","solid","lion_rampant","or",3,"or"],"d_cephalonia":["azure","solid","cross","argent",1,"argent"],"k_hellas":["argent","solid","cross","gules",3,"gules"],"d_athens":["argent","solid","castrum","azure",1,"gules"],"d_achaia":["or","solid","cross","sable",1,"sable"],"c_achaia":["azure","solid","lion_rampant","or",3,"or"],"c_messenia":["azure","solid","lion_rampant","or",1,"or"],"k_krete":["gules","solid","ship","or",1,"or"],"d_krete":["gules","solid","castrum","or",1,"argent"],"c_chandax":["azure","solid","castrum","or",1,"argent"],"k_croatia":["gules","chequy","shield_escutcheon","argent",1,"argent"],"d_dalmatia":["gules","solid","lion_rampant","argent",3,"argent"],"d_croatia":["gules","per_fess","star_six_pointed","argent",1,"or"],"d_slavonia":["argent","solid","castrum","azure",1,"gules"],"d_bosna":["gules","solid","bend","argent",1,"argent"],"d_usora":["argent","solid","castrum","azure",1,"gules"],"d_ragusa":["argent","solid","castrum","azure",1,"gules"],"k_serbia":["gules","solid","eagle_double","argent",1,"argent"],"d_rashka":["argent","solid","eagle_double","gules",1,"gules"],"c_rashka":["azure","solid","horse_courant","argent",3,"argent"],"d_macva":["argent","solid","castrum","azure",1,"gules"],"d_duklja":["gules","solid","bend","or",1,"or"],"k_bosnia":["azure","solid","bend","argent",1,"argent"],"k_albania":["gules","solid","eagle_double","or",1,"argent"],"k_bulgaria":["gules","solid","lion_rampant","or",1,"or"],"d_vidin":["azure","solid","castrum","or",1,"argent"],"c_vidin":["gules","solid","cross","argent",1,"argent"],"d_turnovo":["or","solid","lion_rampant","purpure",3,"purpure"],"c_nikopolis":["gules","solid","crown","or",1,"argent"],"d_dobrudja":["or","solid","cross","gules",1,"gules"],"d_bulgaria":["sable","solid","lion_rampant","or",3,"or"],"d_philippopolis":["argent","solid","crescent_moon","gules",1,"gules"],"c_philippopolis":["argent","solid","castrum","azure",1,"azure"],"c_adrianopolis":["azure","solid","fleur_de_lis","or",3,"argent"],"k_cyprus":["argent","solid","crown","gules",1,"gules"],"d_cyprus":["azure","solid","crescent_moon","or",1,"or"],"k_nikaea":["gules","solid","eagle_double","or",1,"or"],"d_opsikion":["or","solid","cross","gules",1,"gules"],"c_nikaea":["azure","solid","bend","argent",1,"argent"],"d_ephese":["or","solid","castrum","sable",1,"azure"],"d_thracesia":["argent","solid","chevron","gules",1,"gules"],"d_optimatoi":["azure","solid","cross","argent",3,"argent"],"d_bucellaria":["argent","solid","castrum","azure",1,"azure"],"k_anatolia":["azure","solid","cross","argent",1,"argent"],"d_cilicia":["or","solid","lion_rampant","gules",1,"gules"],"c_seleucia":["argent","solid","lion_rampant","gules",1,"gules"],"d_cibyrrhaeot":["sable","solid","lion_rampant","or",1,"or"],"d_anatolia":["argent","solid","cross","vert",3,"vert"],"d_cappadocia":["sable","solid","fess","or",1,"or"],"d_charsianon":["gules","solid","castrum","or",1,"argent"],"k_pontus":["argent","solid","ship","azure",1,"azure"],"d_paphlagonia":["gules","solid","star_six_pointed","argent",3,"argent"],"d_armeniac":["or","solid","castrum","sable",1,"sable"],"d_sebasteia":["gules","solid","castrum","or",1,"argent"],"d_chaldia":["or","solid","castrum","sable",1,"vert"],"k_armenia":["or","solid","lion_rampant","gules",1,"gules"],"d_mesopotamia":["gules","solid","lion_rampant","argent",1,"argent"],"d_vaspurakan":["gules","solid","castrum","or",1,"argent"],"k_georgia":["argent","solid","cross","gules",1,"gules"],"c_abkhazia":["gules","solid","castrum","or",1,"argent"],"c_guria":["argent","solid","stag_attired","azure",1,"azure"],"d_georgia":["gules","solid","lion_rampant","argent",2,"argent"],"c_kakheti":["argent","solid","fleur_de_lis","gules",1,"vert"],"k_sicily":["or","per_saltire","alerion","sable",1,"gules"],"d_sicily":["argent","solid","alerion","sable",1,"sable"],"c_palermo":["gules","solid","alerion","or",1,"or"],"c_messina":["gules","solid","cross","or",1,"or"],"c_siracusa":["vert","solid","castrum","or",1,"or"],"c_agrigento":["argent","solid","castrum","azure",1,"azure"],"c_malta":["azure","solid","alerion","argent",1,"argent"],"d_benevento":["gules","chequy","castrum","or",1,"argent"],"c_benevento":["gules","solid","star_six_pointed","or",1,"or"],"c_foggia":["or","per_bend_sinister","bend","sable",1,"gules"],"d_capua":["gules","solid","cross","or",1,"or"],"c_capua":["gules","solid","crown","or",1,"or"],"c_napoli":["or","solid","fess","sable",1,"gules"],"d_apulia":["argent","solid","castrum","azure",1,"azure"],"c_apulia":["azure","solid","bend","argent",1,"argent"],"c_bari":["argent","solid","castrum","azure",1,"gules"],"c_lecce":["argent","solid","castrum","azure",1,"azure"],"d_salerno":["argent","solid","bend","gules",1,"gules"],"c_salerno":["argent","solid","bend","gules",1,"gules"],"c_camarda":["argent","solid","fess","gules",1,"gules"],"d_calabria":["argent","solid","cross","sable",1,"sable"],"c_reggio_calabria":["or","solid","bend","sable",1,"gules"],"c_cosenza":["gules","solid","cross","argent",1,"argent"],"c_rossano":["sable","solid","castrum","or",1,"argent"],"k_venice":["gules","chief","lion_rampant","or",1,"or"],"d_venice":["azure","solid","lion_rampant","or",1,"or"],"c_venezia":["argent","solid","lion_rampant","gules",1,"gules"],"c_veneto":["argent","solid","lion_rampant","gules",1,"gules"],"k_armenian_principality":["or","solid","crown","gules",1,"gules"],"k_old_armenia":["or","solid","crown","gules",1,"gules"],"e_italy":["gules","per_pale","eagle_double","or",1,"or"],"k_genoa":["argent","solid","cross","gules",1,"gules"],"k_pisa":["gules","solid","cross","argent",1,"argent"],"k_naples":["azure","solid","fleur_de_lis","or",3,"or"],"k_italy":["argent","per_pale","cross","gules",1,"azure"],"d_friuli":["azure","solid","crown","or",1,"or"],"c_aquileia":["azure","solid","alerion","or",1,"or"],"c_friuli":["vert","solid","castrum","or",1,"or"],"c_gorz":["azure","per_bend_sinister","lion_rampant","or",1,"or"],"d_verona":["azure","solid","cross","or",1,"or"],"c_verona":["azure","solid","cross","or",1,"or"],"c_treviso":["sable","solid","castrum","or",1,"argent"],"c_padua":["argent","solid","castrum","azure",1,"gules"],"c_polesine":["sable","solid","castrum","or",1,"argent"],"d_piedmonte":["gules","per_pale","castrum","argent",1,"argent"],"c_monferrato":["argent","solid","castrum","azure",1,"gules"],"c_turin":["argent","solid","castrum","gules",1,"gules"],"c_novara":["gules","solid","cross","argent",1,"argent"],"c_cuneo":["argent","solid","castrum","azure",1,"azure"],"b_saluzzo":["argent","solid","castrum","azure",1,"azure"],"d_lombardia":["argent","solid","cross","gules",1,"gules"],"c_lombardia":["argent","solid","castrum","azure",1,"azure"],"c_brescia":["argent","solid","lion_rampant","azure",1,"azure"],"c_como":["argent","solid","bend","gules",1,"gules"],"c_trent":["argent","solid","alerion","sable",1,"sable"],"c_pavia":["gules","solid","castrum","or",1,"azure"],"c_cremona":["gules","solid","castrum","or",1,"argent"],"c_parma":["or","solid","cross","azure",1,"azure"],"c_tortona":["gules","solid","lion_rampant","argent",1,"argent"],"d_genoa":["argent","solid","cross","gules",1,"gules"],"c_genoa":["gules","solid","castrum","argent",1,"argent"],"b_monaco":["argent","solid","castrum","azure",1,"gules"],"c_luni":["argent","solid","castrum","gules",1,"gules"],"d_emilia":["azure","solid","crown","argent",1,"argent"],"c_modena":["azure","solid","alerion","argent",1,"argent"],"b_canossa":["gules","solid","castrum","or",1,"argent"],"c_mantua":["gules","solid","castrum","or",1,"or"],"d_pisa":["argent","per_pale","cross","azure",1,"gules"],"c_pisa":["gules","per_pale","eagle_double","or",1,"or"],"b_piombino":["argent","solid","castrum","azure",1,"gules"],"d_toscana":["gules","solid","castrum","or",1,"argent"],"c_firenze":["argent","solid","fleur_de_lis","gules",1,"gules"],"c_lucca":["argent","solid","fess","azure",1,"gules"],"c_arezzo":["argent","solid","horse_courant","sable",1,"sable"],"c_siena":["argent","solid","fess","azure",1,"sable"],"c_orbetello":["or","solid","lion_rampant","gules",1,"gules"],"d_istria":["azure","solid","castrum","or",1,"or"],"k_sardinia":["vert","per_pale","eagle_double","argent",1,"or"],"d_corsica":["or","solid","castrum","sable",1,"sable"],"c_ajaccio":["gules","solid","castrum","or",1,"vert"],"c_bastia":["argent","solid","castrum","azure",1,"sable"],"c_vecchio":["argent","solid","castrum","sable",1,"sable"],"d_sardinia":["argent","solid","cross","gules",1,"gules"],"c_cagliari":["or","solid","horse_courant","sable",1,"sable"],"c_arborea":["argent","solid","oak_branch","azure",1,"azure"],"c_gallura":["argent","solid","castrum","azure",1,"sable"],"c_logudoro":["gules","solid","castrum","argent",1,"argent"],"c_tortoli":["gules","solid","castrum","or",1,"argent"],"k_romagna":["azure","per_pale","cross","or",1,"argent"],"d_romagna":["azure","solid","eagle_double","argent",1,"argent"],"c_ravenna":["or","solid","alerion","gules",1,"gules"],"c_bologna":["argent","solid","castrum","azure",1,"sable"],"c_ferrara":["sable","solid","fess","or",1,"argent"],"c_casentino":["argent","solid","lion_rampant","gules",1,"gules"],"d_ancona":["gules","solid","cross","or",1,"or"],"c_ancona":["gules","solid","cross","or",1,"or"],"c_urbino":["azure","solid","bend","argent",1,"or"],"c_fermo":["gules","solid","cross","argent",1,"argent"],"d_spoleto":["argent","solid","castrum","azure",1,"gules"],"c_spoleto":["argent","solid","castrum","azure",1,"sable"],"c_orvieto":["azure","solid","bend","or",1,"or"],"b_perugia":["gules","solid","dragon","argent",1,"argent"],"c_teramo":["gules","solid","bend","argent",1,"argent"],"c_lanciano":["gules","solid","bend","argent",1,"argent"],"c_abruzzi":["azure","solid","bend","or",1,"or"],"d_latium":["gules","chequy","crown","or",1,"or"],"c_roma":["gules","solid","cross","or",1,"or"],"b_vaticano":["gules","solid","keys_st_peter","or",1,"argent"],"c_viterbo":["argent","solid","dragon","gules",1,"gules"],"c_tivoli":["gules","chequy","crown","or",1,"or"],"k_sapmi":["argent","solid","sun_radiant","azure",1,"azure"],"d_aarjetje":["argent","solid","bear_rampant","gules",1,"gules"],"d_duortnoseatnu":["gules","solid","pale","or",1,"or"],"k_finland":["gules","solid","sword_crossed","argent",1,"argent"],"d_finland":["gules","solid","sword_crossed","or",1,"or"],"d_savo":["sable","solid","bow_and_arrow","or",1,"argent"],"d_pohjanmaa":["or","solid","bear_rampant","sable",1,"sable"],"d_karelia":["gules","solid","bear_rampant","or",1,"sable"],"e_wendish_empire":["sable","solid","dragon","argent",1,"argent"],"k_pomerania":["argent","solid","dragon","gules",1,"gules"],"d_pommerania":["argent","solid","dragon","gules",1,"gules"],"d_nordmark":["azure","solid","dragon","or",1,"or"],"c_mecklenburg":["or","solid","crown","sable",1,"sable"],"c_wolgast":["or","solid","dragon","sable",1,"sable"],"c_rugen":["argent","solid","lion_rampant","sable",1,"sable"],"c_rostock":["azure","solid","dragon","or",1,"or"],"c_werle":["or","solid","castrum","sable",1,"sable"],"d_pomerelia":["or","solid","dragon","sable",1,"sable"],"c_danzig":["gules","solid","cross","argent",2,"argent"],"c_slupsk":["argent","solid","dragon","gules",1,"azure"],"d_ostmark":["argent","solid","crown","gules",1,"gules"],"c_brandenburg":["argent","solid","alerion","gules",1,"gules"],"c_ruppin":["gules","solid","alerion","argent",1,"argent"],"c_berlin":["argent","solid","bear_rampant","sable",1,"sable"],"c_havelberg":["azure","solid","cross","argent",1,"argent"],"k_lithuania":["gules","solid","horse_courant","argent",1,"argent"],"d_lithuanians":["gules","solid","castrum","or",1,"or"],"d_prussia":["argent","solid","alerion","sable",1,"sable"],"d_courland":["azure","solid","stag_attired","argent",1,"argent"],"d_samogitia":["gules","solid","bear_rampant","or",1,"sable"],"d_latgalians":["gules","solid","dragon","argent",1,"argent"],"c_talava":["argent","solid","dragon","vert",1,"vert"],"k_esthonia":["or","solid","star_six_pointed","gules",3,"azure"],"d_esthonia":["or","solid","castrum","sable",1,"azure"],"c_osel":["azure","solid","ship","argent",1,"argent"],"d_livonia":["argent","solid","cross","sable",1,"sable"],"k_livonia":["argent","solid","crown","gules",2,"azure"],"e_west_slavia":["gules","solid","alerion","argent",1,"argent"],"k_moravia":["gules","chequy","cross","argent",1,"argent"],"k_poland":["gules","solid","alerion","argent",1,"argent"],"d_lesser_poland":["gules","solid","alerion","argent",1,"argent"],"c_krakowska":["gules","solid","fess","argent",1,"argent"],"c_sacz":["gules","solid","star_six_pointed","or",3,"or"],"c_sandomierska":["gules","solid","star_six_pointed","or",3,"argent"],"c_stezycka":["gules","solid","stag_attired","argent",3,"argent"],"c_lubelska":["gules","solid","stag_attired","argent",1,"argent"],"d_wielkopolska":["gules","solid","alerion","argent",1,"argent"],"c_kaliska":["argent","solid","crown","azure",1,"gules"],"c_lubusz":["or","solid","ship","sable",1,"sable"],"d_mazovia":["gules","solid","alerion","argent",1,"argent"],"c_plocka":["gules","solid","alerion","or",1,"sable"],"c_czerska":["argent","solid","dragon","vert",1,"vert"],"c_lomzynska":["gules","solid","stag_attired","or",1,"or"],"d_upper_silesia":["azure","solid","alerion","or",1,"gules"],"c_opole":["azure","solid","alerion","or",1,"or"],"c_brzeg":["or","solid","alerion","sable",1,"sable"],"c_nysa":["gules","solid","alerion","argent",1,"argent"],"c_cieszyn":["azure","solid","crown","or",1,"or"],"c_ratibor":["azure","solid","alerion","or",1,"or"],"c_bethen":["azure","solid","alerion","or",1,"or"],"d_lower_silesia":["or","solid","alerion","sable",1,"sable"],"c_breslau":["gules","solid","fleur_de_lis","or",3,"or"],"c_schweibus":["gules","solid","dragon","argent",1,"argent"],"c_legnica":["or","per_pale","alerion","sable",1,"sable"],"d_kuyavia":["or","per_pale","lion_rampant","sable",1,"sable"],"c_kujawy":["or","per_pale","lion_rampant","gules",1,"gules"],"c_leczycka":["argent","per_pale","lion_rampant","gules",1,"gules"],"c_sieradzka":["or","per_pale","lion_rampant","gules",1,"gules"],"k_bohemia":["gules","solid","lion_rampant","argent",1,"argent"],"d_bohemia":["argent","solid","alerion","gules",3,"gules"],"c_praha":["sable","solid","fess","or",1,"or"],"c_litomerice":["or","solid","castrum","sable",1,"sable"],"c_plzen":["gules","solid","castrum","or",1,"argent"],"b_stribro":["or","solid","castrum","sable",1,"sable"],"c_doudleby":["argent","solid","castrum","azure",1,"gules"],"b_krumlov":["argent","solid","castrum","azure",1,"vert"],"b_chynov":["or","solid","castrum","sable",1,"sable"],"c_boleslav":["gules","solid","lion_rampant","argent",1,"argent"],"c_hradec":["gules","solid","bend","or",1,"or"],"c_caslav":["gules","solid","castrum","or",1,"argent"],"d_moravia":["azure","chequy","crown","argent",1,"argent"],"c_olomouc":["argent","solid","fess","gules",2,"gules"],"c_opava":["argent","solid","castrum","azure",1,"gules"],"c_brno":["gules","solid","castrum","or",1,"argent"],"c_znojmo":["azure","chequy","crown","argent",1,"argent"],"k_galicia-volhynia":["azure","solid","lion_rampant","or",1,"or"],"d_volhynia":["gules","solid","cross","argent",1,"argent"],"d_halych":["argent","solid","falcon_perched","sable",1,"sable"],"d_cherven_cities":["azure","per_pale","lion_rampant","or",1,"or"],"k_sorbia":["gules","solid","battleaxe","argent",1,"argent"],"d_meissen":["or","solid","crown","sable",1,"sable"],"c_meissen":["or","solid","lion_rampant","sable",1,"sable"],"c_dresden":["sable","per_pale","pale","or",1,"or"],"c_wolkenstein":["argent","solid","bend","azure",1,"gules"],"c_osterland":["gules","per_fess","bend","or",1,"argent"],"c_naumburg":["or","solid","castrum","sable",1,"gules"],"c_vogtland":["sable","solid","lion_rampant","or",1,"or"],"c_cottbus":["argent","solid","castrum","azure",1,"gules"],"c_gorlitz":["argent","solid","lion_rampant","gules",1,"gules"],"d_lausitz":["argent","solid","castrum","azure",1,"gules"],"c_juterbog":["argent","solid","fess","azure",1,"gules"],"c_wittenberg":["azure","solid","crown","or",1,"or"],"c_brene":["argent","solid","castrum","azure",1,"gules"],"b_torgau":["sable","solid","castrum","or",1,"argent"],"c_spreewald":["or","solid","castrum","sable",1,"azure"],"c_naumberg":["gules","solid","castrum","argent",1,"or"],"e_russia":["gules","solid","spear","or",1,"or"],"k_ruthenia":["gules","solid","spear","or",1,"or"],"d_turov":["gules","solid","bow_and_arrow","or",1,"or"],"d_chernigov":["sable","solid","cross","argent",1,"azure"],"c_chernigov":["argent","solid","eagle_double","sable",1,"sable"],"k_novgorod":["argent","solid","bear_rampant","sable",1,"sable"],"d_novgorod":["azure","solid","spear","or",1,"or"],"d_luki":["gules","solid","bow_and_arrow","or",3,"or"],"k_white_rus":["gules","solid","cross_patriarchal","or",1,"or"],"d_grodno":["sable","solid","bear_rampant","argent",1,"argent"],"d_pinsk":["argent","solid","bow_and_arrow","gules",1,"gules"],"d_polotsk":["gules","solid","castrum","or",1,"argent"],"c_polotsk":["argent","solid","castrum","azure",1,"gules"],"d_smolensk":["gules","solid","bear_rampant","argent",1,"argent"],"c_smolensk":["gules","solid","bear_rampant","argent",1,"argent"],"k_opolye":["azure","solid","alerion","or",1,"or"],"d_opolye":["gules","solid","crown","or",1,"or"],"c_yaroslavl":["or","solid","bear_rampant","sable",1,"sable"],"c_vladimir":["gules","solid","lion_rampant","or",1,"or"],"d_ryazan":["gules","solid","horse_courant","argent",1,"argent"],"c_ryazan":["gules","solid","horse_courant","argent",1,"argent"],"d_nizhny_novgorod":["argent","solid","stag_attired","gules",1,"gules"],"k_bjarmaland":["gules","solid","bear_rampant","or",1,"or"],"e_caspian-pontic_steppe":["sable","solid","horse_courant","argent",1,"argent"],"k_pontic_steppe":["gules","solid","bow_and_arrow","argent",1,"argent"],"d_crimea":["gules","solid","castrum","or",1,"or"],"k_caucasus":["vert","solid","fess","argent",1,"gules"],"c_derbent":["vert","solid","castrum","argent",1,"argent"],"k_caspian_steppe":["azure","solid","star_six_pointed","or",1,"or"],"k_magyar":["argent","solid","castrum","azure",1,"gules"],"e_volga-ural":["or","solid","dragon","sable",1,"sable"],"k_volga_bulgaria":["or","solid","dragon","gules",1,"gules"],"k_mordvinia":["argent","solid","cross","gules",1,"gules"],"k_permia":["gules","solid","bear_rampant","argent",1,"argent"],"k_bashkiria":["argent","solid","horse_courant","azure",1,"or"],"e_siberia":["azure","solid","bear_rampant","argent",1,"argent"],"k_yugra":["vert","solid","stag_attired","or",1,"or"],"k_sibir":["argent","solid","bear_rampant","azure",1,"azure"],"k_ob":["azure","solid","fish_twin","argent",1,"argent"],"e_mongolia":["azure","solid","bow_and_arrow","or",1,"or"],"k_otuken":["azure","solid","crescent_moon","argent",1,"or"],"d_ogrash":["gules","chevron","bow_and_arrow","argent",1,"argent"],"c_ulaanbaatar":["azure","solid","bow_and_arrow","argent",1,"argent"],"c_khentii":["or","chevron","bow_and_arrow","sable",1,"sable"],"d_ovorkhangai":["or","chevron","chevron","sable",1,"sable"],"k_tuva":["sable","solid","horse_courant","or",1,"or"],"k_khakassia":["azure","solid","sun_radiant","argent",1,"gules"],"d_khakass_hollow":["vert","chevron","crescent_moon","or",2,"argent"],"k_buryatia":["azure","solid","horse_courant","argent",2,"argent"],"k_angara":["gules","solid","bow_and_arrow","or",3,"or"],"e_tartaria":["or","solid","horse_courant","sable",2,"sable"],"k_zhetysu":["gules","chevron","chevron","or",1,"or"],"c_emil":["sable","chevron","chevron","or",1,"or"],"k_cuman":["azure","solid","bow_and_arrow","or",1,"or"],"k_kipchak":["vert","solid","horse_courant","or",1,"or"],"k_dzungaria":["azure","solid","castrum","or",1,"gules"],"k_khotan":["sable","solid","horse_courant","argent",1,"argent"],"k_oghuz_il":["azure","solid","horse_courant","or",1,"or"],"k_syr_darya":["or","chevron","chevron","gules",1,"gules"],"k_transoxiana":["sable","solid","alerion","or",1,"or"],"d_soghd":["vert","solid","sun_radiant","or",1,"argent"],"c_bukhara":["or","solid","castrum","sable",1,"vert"],"e_bactria":["argent","solid","castrum","azure",1,"gules"],"e_persia":["vert","solid","lion_rampant","or",1,"or"],"k_persia":["vert","solid","sun_radiant","or",1,"or"],"d_isfahan":["gules","solid","castrum","or",1,"argent"],"c_bam":["or","solid","dragon","azure",1,"azure"],"d_fars":["argent","solid","bow_and_arrow","azure",1,"azure"],"d_kermanshah":["gules","solid","castrum","or",1,"argent"],"c_kermanshah":["gules","solid","castrum","or",1,"argent"],"k_khorasan":["sable","solid","sun_radiant","or",1,"or"],"d_ghur":["vert","solid","castrum","or",1,"gules"],"c_ghur":["or","solid","castrum","gules",1,"gules"],"d_balkh":["gules","per_bend","bow_and_arrow","or",1,"or"],"c_balkh":["sable","solid","lion_rampant","or",1,"gules"],"k_daylam":["vert","solid","mount_triple","or",1,"or"],"b_alamut":["gules","solid","castrum","or",1,"argent"],"c_mazandaran":["gules","solid","star_six_pointed","or",1,"purpure"],"c_baduspan":["azure","solid","bow_and_arrow","or",1,"or"],"k_makran":["vert","solid","anchor","or",1,"or"],"k_kabulistan":["or","solid","horse_courant","gules",1,"gules"],"k_mesopotamia":["sable","solid","lion_rampant","argent",1,"argent"],"d_samarra":["sable","solid","castrum","or",1,"argent"],"c_samarra":["sable","solid","castrum","or",1,"argent"],"d_baghdad":["argent","solid","bow_and_arrow","sable",1,"sable"],"c_baghdad":["argent","solid","bow_and_arrow","sable",1,"sable"],"k_jazira":["vert","solid","star_six_pointed","or",1,"or"],"c_harran":["argent","solid","castrum","azure",1,"azure"],"e_carpathia":["gules","solid","cross_patriarchal","argent",1,"argent"],"k_dacia":["gules","solid","dragon","or",1,"or"],"d_transylvanian_alps":["azure","solid","alerion","argent",1,"sable"],"d_muntenia":["or","solid","castrum","sable",1,"vert"],"d_oltenia":["or","solid","castrum","sable",1,"gules"],"k_moldavia":["gules","solid","stag_attired","or",1,"or"],"d_bukovina":["azure","solid","star_six_pointed","or",1,"sable"],"c_suceava":["argent","solid","crescent_moon","azure",1,"sable"],"d_moldova":["gules","solid","star_six_pointed","or",1,"or"],"k_hungary":["gules","solid","cross_patriarchal","argent",1,"argent"],"d_visegrad":["azure","solid","crown","or",1,"or"],"c_szekesfehervar":["azure","solid","lion_rampant","or",1,"or"],"d_somogy":["gules","solid","fess","argent",1,"argent"],"c_baranya":["gules","solid","fess","or",1,"azure"],"d_nyitra":["gules","solid","cross_patriarchal","argent",1,"argent"],"d_ungvar":["or","solid","bear_rampant","gules",1,"gules"],"c_abauj":["gules","per_pale","eagle_double","argent",1,"argent"],"d_transcarpathia":["gules","solid","cross","or",1,"sable"],"c_marmaros":["gules","solid","castrum","or",1,"sable"],"d_transylvania":["argent","per_pale","alerion","azure",1,"azure"],"d_bihar":["gules","solid","castrum","or",1,"argent"],"d_temes":["azure","solid","lion_rampant","or",1,"or"],"d_bacs":["argent","solid","castrum","azure",1,"gules"],"d_gyor":["gules","solid","castrum","or",1,"argent"],"c_gyor":["azure","solid","fleur_de_lis","or",1,"or"],"d_syrmia":["azure","solid","crown","or",3,"or"],"c_szerem":["gules","solid","castrum","or",1,"argent"],"e_france":["azure","solid","fleur_de_lis","or",3,"or"],"k_france":["azure","solid","fleur_de_lis","or",3,"or"],"d_valois":["gules","solid","fleur_de_lis","or",3,"azure"],"c_ile_de_france":["azure","solid","castrum","or",1,"or"],"b_saint_denis":["argent","solid","cross","gules",1,"gules"],"b_versailles":["azure","solid","lion_rampant","argent",1,"or"],"b_montlhery":["or","solid","cross","gules",1,"gules"],"c_brie_francaise":["argent","solid","castrum","azure",1,"gules"],"b_bray":["argent","solid","battleaxe","gules",2,"gules"],"b_nemours":["or","solid","castrum","sable",1,"azure"],"c_vermandois":["or","solid","castrum","sable",1,"azure"],"b_roucy":["or","solid","lion_rampant","azure",1,"azure"],"c_valois":["gules","solid","wheatsheaf_garb","or",3,"or"],"b_crepy":["gules","solid","fleur_de_lis","or",3,"or"],"b_coucy":["argent","solid","castrum","azure",1,"azure"],"c_amiens":["gules","solid","castrum","or",1,"or"],"b_corbie":["argent","solid","crown","gules",1,"gules"],"b_peronne":["or","chief","lion_rampant","sable",1,"gules"],"c_beaumont":["azure","solid","lion_rampant","or",1,"or"],"b_beauvais":["argent","solid","cross","sable",1,"sable"],"b_montfort":["gules","solid","lion_rampant","argent",1,"argent"],"c_clermont":["gules","solid","wheatsheaf_garb","or",3,"or"],"b_noyon":["or","solid","fess","azure",1,"azure"],"d_berry":["gules","solid","fleur_de_lis","or",3,"azure"],"c_berry":["argent","solid","fess","gules",1,"gules"],"c_tourraine":["or","solid","alerion","azure",3,"azure"],"b_loches":["or","solid","fess","gules",1,"gules"],"c_blois":["azure","solid","bend","argent",1,"argent"],"c_issoudun":["azure","solid","wheatsheaf_garb","or",3,"or"],"d_anjou":["azure","solid","fleur_de_lis","or",3,"or"],"c_anjou":["azure","solid","lion_rampant","or",3,"or"],"c_saumur":["gules","solid","castrum","or",1,"or"],"c_maine":["or","solid","chevron","sable",1,"gules"],"c_sable":["or","solid","alerion","azure",1,"azure"],"b_mayenne":["or","solid","castrum","sable",1,"gules"],"b_laval":["or","solid","cross","gules",1,"gules"],"d_normandy":["gules","solid","castrum","or",1,"or"],"c_rouen":["gules","solid","castrum","or",1,"or"],"b_gisors":["or","solid","cross","gules",1,"gules"],"c_evreux":["argent","solid","castrum","azure",1,"gules"],"b_vernon":["or","solid","castrum","sable",1,"azure"],"c_bayeux":["gules","solid","lion_rampant","or",2,"or"],"c_avranches":["azure","solid","wolf_statant","argent",1,"argent"],"c_alencon":["or","solid","bend","azure",1,"azure"],"c_lisieux":["sable","solid","castrum","or",1,"or"],"c_eu":["azure","solid","lion_rampant","or",1,"or"],"b_aumale":["or","solid","bend","azure",1,"azure"],"d_orleans":["azure","solid","fleur_de_lis","or",3,"or"],"c_orleans":["argent","solid","alerion","gules",3,"gules"],"b_beaugency":["or","solid","fess","gules",1,"azure"],"c_montargis":["argent","solid","lion_rampant","gules",1,"gules"],"b_coutenay":["or","solid","castrum","sable",1,"gules"],"c_vendome":["gules","chief","crown","or",1,"argent"],"b_chateaudun":["argent","solid","castrum","azure",1,"sable"],"c_chartres":["or","solid","fess","sable",1,"sable"],"b_dreux":["or","solid","castrum","sable",1,"azure"],"b_perche":["argent","solid","chevron","gules",1,"gules"],"c_sancerre":["azure","solid","cross","or",3,"argent"],"b_sully_sur_loire":["azure","solid","lion_rampant","or",1,"or"],"d_champagne":["azure","solid","bend","argent",1,"argent"],"c_reims":["azure","solid","fleur_de_lis","or",3,"or"],"c_troyes":["azure","solid","castrum","or",1,"argent"],"c_coulommiers":["gules","solid","castrum","or",1,"or"],"c_meaux":["gules","solid","lion_rampant","or",1,"or"],"c_chalons":["gules","solid","castrum","or",1,"or"],"b_saint_dizier":["gules","solid","castrum","or",1,"or"],"c_rethel":["gules","solid","castrum","or",1,"or"],"b_grandpre":["or","solid","castrum","sable",1,"gules"],"c_sens":["or","solid","alerion","gules",1,"gules"],"d_burgundy":["azure","solid","castrum","or",1,"or"],"c_dijon":["azure","solid","lion_rampant","or",3,"or"],"b_gray":["gules","solid","bend","or",1,"or"],"c_chalon":["gules","solid","bend","or",1,"or"],"b_citeaux":["gules","solid","sword_crossed","or",1,"or"],"c_auxerre":["or","solid","castrum","sable",1,"gules"],"b_donzy":["argent","solid","castrum","azure",1,"gules"],"c_tonnerrois":["azure","solid","bend","or",1,"or"],"b_montbard":["gules","solid","castrum","or",1,"argent"],"c_avalois":["azure","solid","bend","or",1,"or"],"c_macon":["argent","solid","chevron","azure",1,"gules"],"b_semur_en_brionnais":["argent","solid","bend","azure",1,"gules"],"c_nevers":["azure","solid","lion_rampant","or",1,"or"],"c_langres":["azure","solid","fleur_de_lis","or",3,"or"],"d_flanders":["or","solid","lion_rampant","sable",1,"sable"],"c_brugge":["argent","solid","crown","azure",1,"gules"],"b_gent":["sable","solid","castrum","or",1,"argent"],"b_roeselare":["argent","solid","castrum","azure",1,"sable"],"c_yperen":["gules","solid","castrum","or",1,"argent"],"c_guines":["or","solid","castrum","sable",1,"azure"],"b_saint_omer":["azure","solid","fess","or",1,"or"],"c_lille":["gules","solid","castrum","or",1,"or"],"b_lille":["gules","solid","fleur_de_lis","argent",1,"argent"],"c_boulogne":["or","solid","castrum","sable",1,"gules"],"k_aquitaine":["gules","solid","crown","or",1,"or"],"d_gascogne":["argent","solid","lion_rampant","gules",1,"gules"],"c_bordeaux":["or","solid","castrum","sable",1,"argent"],"b_fronsac":["gules","solid","pale","or",1,"or"],"c_labourd":["or","solid","lion_rampant","gules",1,"gules"],"c_albret":["gules","solid","castrum","or",1,"argent"],"b_tartas":["gules","solid","castrum","or",1,"or"],"c_marsan":["gules","solid","castrum","or",1,"argent"],"b_gabardan":["argent","solid","lion_rampant","sable",3,"sable"],"c_agenais":["or","solid","bend","sable",1,"gules"],"d_aquitaine":["gules","solid","lion_rampant","or",1,"or"],"c_angouleme":["or","solid","castrum","sable",1,"gules"],"b_cognac":["or","solid","castrum","sable",1,"azure"],"c_perigord":["gules","solid","lion_rampant","or",3,"or"],"c_limousin":["or","solid","lion_rampant","azure",3,"azure"],"b_ventadour":["or","solid","castrum","sable",1,"gules"],"b_turenne":["or","solid","bend","gules",1,"gules"],"c_saintonge":["or","solid","lion_rampant","gules",1,"gules"],"b_jonzac":["gules","solid","castrum","or",1,"or"],"b_royan":["gules","solid","lion_rampant","or",1,"or"],"c_aunis":["gules","solid","pale","or",1,"argent"],"d_toulouse":["gules","solid","cross","or",1,"or"],"c_toulouse":["gules","solid","cross","or",1,"or"],"c_quercy":["gules","solid","lion_rampant","argent",1,"argent"],"c_gevaudan":["gules","solid","wheatsheaf_garb","or",1,"argent"],"c_rouergue":["gules","solid","lion_rampant","or",1,"or"],"c_millau":["or","solid","pale","gules",1,"gules"],"d_languedoc":["or","per_pale","cross","sable",1,"gules"],"c_albi":["gules","solid","castrum","or",1,"argent"],"c_uses":["gules","solid","castrum","or",1,"argent"],"c_montpellier":["argent","solid","castrum","azure",1,"azure"],"c_carcassonne":["gules","solid","star_six_pointed","or",1,"or"],"b_narbonne":["gules","solid","castrum","or",1,"or"],"c_beziers":["argent","solid","castrum","azure",1,"sable"],"c_foix":["gules","solid","castrum","or",1,"argent"],"d_armagnac":["argent","solid","crown","gules",1,"gules"],"c_armagnac":["argent","solid","lion_rampant","gules",1,"gules"],"c_bigorre":["or","solid","lion_rampant","gules",2,"gules"],"c_bearn":["or","solid","castrum","sable",1,"gules"],"c_comminges":["argent","solid","cross","gules",1,"azure"],"b_astarac":["or","solid","castrum","sable",1,"gules"],"d_poitou":["argent","solid","lion_rampant","gules",1,"gules"],"c_poitiers":["argent","solid","lion_rampant","gules",1,"gules"],"b_chatellerault":["argent","solid","lion_rampant","gules",1,"gules"],"c_lusignan":["gules","solid","castrum","or",1,"argent"],"c_montaigu":["or","solid","castrum","sable",1,"gules"],"c_thouars":["or","solid","fleur_de_lis","azure",3,"argent"],"b_parthenay":["argent","solid","bend","gules",1,"azure"],"d_auvergne":["or","solid","castrum","sable",1,"gules"],"c_auvergne":["or","solid","castrum","sable",1,"gules"],"c_clermont_sur_allier":["or","solid","castrum","sable",1,"azure"],"b_la_tour":["gules","solid","castrum","argent",1,"argent"],"b_mercaeur":["argent","solid","castrum","azure",1,"azure"],"c_thiers":["or","solid","lion_rampant","gules",1,"gules"],"c_velay":["argent","solid","castrum","azure",1,"gules"],"d_bourbon":["azure","solid","fleur_de_lis","or",3,"gules"],"c_bourbon":["or","solid","lion_rampant","gules",1,"gules"],"c_bellac":["or","solid","lion_rampant","gules",3,"gules"],"b_la_tremouille":["or","solid","chevron","gules",1,"gules"],"c_jaligny":["or","solid","castrum","sable",1,"gules"],"c_la_marche":["argent","solid","lion_rampant","gules",3,"azure"],"k_brittany":["argent","chequy","fleur_de_lis","sable",1,"sable"],"d_brittany":["or","solid","castrum","sable",1,"azure"],"c_vannes":["gules","solid","castrum","or",1,"or"],"b_rohan":["gules","solid","castrum","or",1,"or"],"c_nantes":["gules","solid","crescent_moon","argent",3,"argent"],"b_rais":["or","solid","cross","sable",1,"sable"],"b_chateaubriant":["gules","solid","fleur_de_lis","or",3,"or"],"c_cornouaille":["argent","solid","crescent_moon","gules",1,"gules"],"c_french_leon":["or","solid","lion_rampant","sable",1,"argent"],"c_penthievre":["gules","solid","castrum","or",1,"or"],"c_rennes":["gules","solid","castrum","or",1,"argent"],"k_burgundy":["or","barry","bordure","azure",1,"gules"],"d_provence":["or","solid","castrum","sable",1,"gules"],"c_venaissin":["or","solid","castrum","sable",1,"azure"],"b_arles":["gules","solid","star_six_pointed","argent",1,"argent"],"b_orange":["or","solid","castrum","sable",1,"azure"],"b_avignon":["gules","solid","keys_st_peter","or",3,"or"],"c_provence":["gules","solid","pale","or",1,"or"],"b_castellane":["gules","solid","castrum","or",1,"or"],"b_marseille":["argent","solid","cross","azure",1,"azure"],"c_nice":["argent","solid","alerion","gules",1,"gules"],"c_forcalquier":["or","solid","cross","gules",1,"gules"],"b_apt":["or","solid","wolf_statant","azure",1,"azure"],"b_embrun":["gules","solid","cross","argent",1,"argent"],"d_savoie":["argent","solid","alerion","sable",1,"gules"],"c_savoie":["gules","solid","cross","argent",1,"argent"],"c_aosta":["sable","solid","lion_rampant","argent",1,"argent"],"c_geneva":["azure","solid","castrum","or",1,"argent"],"b_faucigny":["or","solid","castrum","sable",1,"gules"],"c_canavese":["gules","solid","alerion","argent",1,"argent"],"b_ivrea":["gules","solid","alerion","argent",1,"argent"],"d_dauphine":["or","solid","castrum","sable",1,"azure"],"c_lyon":["gules","solid","lion_rampant","argent",1,"argent"],"b_villars":["or","solid","bend","sable",1,"gules"],"b_beaujeu":["or","solid","lion_rampant","sable",1,"sable"],"c_forez":["gules","solid","castrum","or",1,"or"],"b_roanne":["or","solid","lion_rampant","sable",1,"sable"],"c_viviers":["azure","solid","fleur_de_lis","or",3,"or"],"b_annonay":["or","solid","castrum","sable",1,"azure"],"c_viennois":["gules","solid","castrum","or",1,"or"],"c_valentinois":["azure","solid","castrum","or",1,"or"],"b_monteil":["or","solid","bend","azure",1,"azure"],"b_die":["gules","solid","castrum","or",1,"or"],"d_upper_burgundy":["gules","solid","crown","argent",1,"argent"],"c_besancon":["gules","solid","alerion","argent",1,"argent"],"b_vesoul":["or","solid","bend","gules",1,"gules"],"c_bresse":["or","solid","bend","azure",1,"azure"],"c_dole":["gules","solid","alerion","or",1,"or"],"b_salins":["or","solid","bend","gules",1,"gules"],"d_transjurania":["or","per_pale","eagle_double","sable",1,"sable"],"c_bern":["gules","solid","bend","or",1,"or"],"b_lausanne":["argent","solid","castrum","azure",1,"gules"],"c_aargau":["argent","solid","fess","gules",1,"gules"],"b_lucerne":["azure","solid","castrum","or",1,"argent"],"c_neuchatel":["gules","solid","chevron","argent",1,"argent"],"e_spain":["gules","solid","castrum","or",3,"or"],"k_andalusia":["argent","solid","castrum","azure",1,"vert"],"d_cordoba":["argent","solid","crown","gules",1,"azure"],"c_cordoba":["argent","solid","sun_radiant","azure",1,"azure"],"d_granada":["argent","solid","castrum","azure",1,"or"],"c_granada":["argent","solid","sun_radiant","azure",1,"azure"],"c_almeria":["argent","solid","sun_radiant","azure",1,"azure"],"d_toledo":["azure","solid","cross","or",1,"or"],"c_cuenca":["gules","solid","star_six_pointed","argent",1,"argent"],"k_badajoz":["vert","solid","lion_rampant","argent",1,"argent"],"d_beja":["or","solid","castrum","gules",1,"gules"],"c_lisboa":["or","solid","waves","vert",1,"argent"],"c_alcacer_do_sal":["argent","solid","castrum","azure",1,"gules"],"d_badajoz":["azure","solid","crown","argent",1,"argent"],"c_badajoz":["azure","solid","crown","argent",1,"argent"],"c_caceres":["gules","per_pale","castrum","or",1,"argent"],"d_algarve":["argent","solid","castrum","azure",1,"sable"],"k_valencia":["or","per_pale","pale","gules",1,"gules"],"d_valencia":["vert","solid","bend","argent",1,"or"],"c_valencia":["or","solid","pale","gules",1,"gules"],"c_castellon":["or","solid","castrum","sable",1,"gules"],"c_denia":["or","solid","bend","sable",1,"sable"],"d_mallorca":["or","solid","bend","azure",1,"gules"],"d_murcia":["gules","solid","crown","or",3,"or"],"k_castille":["gules","solid","castrum","or",1,"or"],"d_castilla":["gules","solid","castrum","or",3,"or"],"d_cantabria":["argent","solid","cross","gules",1,"gules"],"k_aragon":["or","pales","pale","gules",1,"gules"],"d_aragon":["azure","solid","cross","argent",1,"argent"],"c_zaragoza":["gules","solid","crown","or",1,"argent"],"c_albarracin":["or","solid","cross","gules",1,"gules"],"c_alto_aragon":["or","solid","cross","gules",1,"gules"],"c_calatayud":["gules","solid","crescent_moon","argent",1,"argent"],"d_barcelona":["or","solid","castrum","sable",1,"gules"],"c_barcelona":["or","pales","pale","gules",1,"gules"],"b_manresa":["gules","solid","castrum","or",1,"or"],"c_urgell":["or","solid","castrum","sable",1,"sable"],"c_puigcerda":["argent","solid","cross","gules",2,"azure"],"c_girona":["or","solid","castrum","sable",1,"gules"],"c_rossello":["or","solid","pale","gules",1,"gules"],"c_tarragona":["or","pales","waves","azure",1,"gules"],"k_navarra":["gules","solid","cross","or",1,"or"],"d_navarra":["gules","solid","cross","or",1,"or"],"c_navarra":["or","solid","alerion","sable",1,"argent"],"c_najera":["argent","solid","sun_radiant","azure",1,"or"],"c_tudela":["or","solid","cross","sable",1,"sable"],"k_asturias":["azure","solid","cross","or",1,"or"],"k_leon":["argent","solid","lion_rampant","purpure",1,"purpure"],"d_leon":["argent","solid","lion_rampant","purpure",1,"purpure"],"c_leon":["argent","solid","lion_rampant","purpure",1,"purpure"],"c_zamora":["vert","solid","castrum","or",1,"argent"],"d_asturias":["azure","solid","cross","or",1,"or"],"c_asturias_de_oviedo":["azure","solid","cross","or",1,"or"],"k_spanish_galicia":["azure","solid","cross_patriarchal","or",1,"or"],"d_galicia":["azure","solid","castrum","or",1,"or"],"c_coruna":["argent","solid","bend","azure",1,"azure"],"c_santiago":["gules","solid","castrum","or",1,"or"],"c_astorga":["gules","solid","cross","or",1,"or"],"k_portugal":["argent","solid","cross","azure",1,"azure"],"d_porto":["argent","solid","cross","azure",1,"azure"],"c_porto":["argent","solid","cross","azure",1,"azure"],"c_braganza":["gules","solid","castrum","or",1,"argent"],"d_coimbra":["gules","solid","fleur_de_lis","argent",1,"argent"],"c_castelo_branco":["gules","solid","castrum","argent",1,"argent"],"e_maghreb":["argent","solid","crescent_moon","azure",1,"azure"],"k_maghreb":["gules","solid","crescent_moon","or",1,"or"],"c_fes":["azure","solid","castrum","argent",1,"argent"],"k_canarias":["argent","solid","lion_rampant","sable",1,"azure"],"k_tahert":["sable","solid","star_six_pointed","argent",1,"argent"],"c_figuig":["vert","chief","crescent_moon","argent",1,"argent"],"d_bejaia":["gules","solid","castrum","or",1,"argent"],"k_africa":["or","solid","lion_rampant","azure",1,"azure"],"c_jafara":["gules","solid","star_six_pointed","or",1,"vert"],"k_anbiya":["vert","solid","star_six_pointed","or",3,"or"],"k_sahara":["or","solid","sun_radiant","sable",1,"gules"],"e_arabia":["or","solid","alerion","sable",1,"argent"],"k_israel":["argent","solid","castrum","azure",1,"azure"],"k_arabia":["sable","solid","crescent_moon","argent",1,"argent"],"c_al_jawf":["sable","chequy","castrum","or",1,"or"],"c_al_aqabah":["azure","solid","lion_rampant","argent",1,"gules"],"k_yemen":["gules","solid","alerion","or",1,"or"],"c_mahra":["argent","solid","castrum","azure",1,"azure"],"c_dhofar":["azure","solid","castrum","argent",1,"argent"],"k_egypt":["gules","solid","crescent_moon","argent",1,"argent"],"d_alexandria":["azure","solid","ship","or",1,"or"],"c_alexandria":["azure","solid","lion_rampant","or",1,"or"],"d_cairo":["argent","solid","castrum","gules",1,"azure"],"c_cairo":["azure","solid","castrum","argent",1,"argent"],"c_farama":["gules","solid","castrum","or",1,"argent"],"k_jerusalem":["argent","solid","cross","azure",1,"or"],"c_kerak":["or","per_fess","castrum","sable",1,"gules"],"d_palestine":["or","solid","alerion","sable",1,"argent"],"c_ghazza":["gules","solid","bend","argent",1,"argent"],"c_acre":["gules","per_pale","castrum","or",1,"or"],"k_syria":["gules","solid","cross","or",3,"or"],"c_edessa":["gules","solid","castrum","or",1,"or"],"c_aintab":["azure","solid","castrum","or",1,"or"],"c_hama":["argent","per_pale","star_six_pointed","azure",1,"sable"],"d_antioch":["or","solid","cross","gules",1,"gules"],"c_alexandretta":["argent","solid","lion_rampant","sable",1,"sable"],"d_lebanon":["gules","solid","cross","or",1,"or"],"c_tripoli":["gules","solid","cross","or",1,"or"],"c_sukhna":["sable","solid","crescent_moon","or",1,"argent"],"c_qaryatan":["gules","solid","castrum","or",1,"vert"],"e_abyssinia":["or","solid","lion_rampant","sable",1,"sable"],"k_abyssinia":["or","solid","star_six_pointed","sable",1,"sable"],"d_gojjam":["vert","solid","bend","or",1,"argent"],"k_nubia":["argent","solid","cross_patriarchal","gules",1,"gules"],"d_makuria":["argent","solid","castrum","azure",1,"sable"],"c_atbara":["vert","solid","alerion","argent",1,"sable"],"c_alodia":["gules","per_fess","castrum","or",1,"or"],"k_blemmyia":["sable","solid","cross","argent",3,"argent"],"k_damot":["vert","solid","cross_patriarchal","or",1,"or"],"k_adal":["argent","solid","crescent_moon","gules",1,"gules"],"e_azania":["gules","solid","crescent_moon","argent",1,"or"],"k_ajuraan":["gules","solid","star_six_pointed","argent",1,"or"],"k_bale":["vert","solid","spear","argent",1,"argent"],"k_zanj":["or","solid","crescent_moon","vert",3,"sable"],"d_pate":["argent","per_pale","crescent_moon","azure",1,"gules"],"c_lamu":["vert","solid","crescent_moon","argent",1,"argent"],"d_mombasa":["argent","solid","waves","azure",1,"azure"],"c_mombasa":["argent","solid","waves","azure",1,"azure"],"c_malindi":["azure","solid","oak_branch","argent",1,"argent"],"d_zanzibar":["gules","solid","crescent_moon","or",1,"or"],"c_mrima":["azure","solid","waves","argent",1,"argent"],"e_kanem_bornu":["argent","solid","oak_branch","vert",1,"gules"],"k_kanem":["argent","solid","castrum","azure",1,"gules"],"k_sao":["gules","solid","oak_branch","or",1,"or"],"k_hausaland":["gules","solid","horse_courant","or",1,"or"],"c_daura":["argent","solid","castrum","azure",1,"vert"],"k_darfur":["sable","solid","spear","or",1,"or"],"e_mali":["gules","solid","sun_radiant","or",1,"or"],"k_songhay":["gules","solid","spear","argent",1,"argent"],"k_gurma":["sable","solid","horse_courant","or",1,"or"],"k_ghana":["or","solid","spear","sable",1,"sable"],"k_mali":["or","solid","sun_radiant","sable",1,"sable"],"c_bambuk":["azure","solid","castrum","or",1,"argent"],"k_takrur":["azure","solid","spear","or",1,"or"],"k_jenne":["azure","solid","cross","argent",1,"sable"],"k_kaabu":["sable","solid","spear","argent",1,"argent"],"e_guinea":["or","solid","castrum","sable",1,"sable"],"k_guinea":["or","solid","tree_chestnut","sable",1,"sable"],"k_kong":["gules","solid","anchor","or",1,"or"],"k_akan":["gules","solid","castrum","or",1,"vert"],"k_gur":["sable","solid","cross","or",1,"or"],"k_borgu":["vert","solid","spear","or",1,"or"],"k_yorubaland":["vert","solid","crown","or",1,"or"],"k_igbo-benue":["azure","solid","bell","or",1,"or"],"e_rajastan":["vert","solid","sun_radiant","or",1,"or"],"k_sindh":["argent","solid","horse_courant","azure",1,"azure"],"k_punjab":["argent","solid","lion_rampant","azure",1,"azure"],"k_delhi":["vert","solid","crescent_moon","or",1,"or"],"k_gujarat":["vert","solid","lion_rampant","or",1,"or"],"k_rajputana":["gules","solid","sun_radiant","argent",1,"argent"],"c_ajayameru":["vert","per_pale","castrum","or",1,"argent"],"k_malwa":["or","solid","wheel_spoked","sable",1,"sable"],"k_kosala":["argent","solid","bow_and_arrow","azure",1,"azure"],"k_himalaya":["azure","solid","mount_triple","argent",3,"argent"],"k_kashmir":["gules","solid","mount_triple","or",1,"or"],"e_bengal":["argent","solid","lion_rampant","gules",1,"gules"],"k_bengal":["vert","solid","rose_seeded","or",1,"or"],"k_kamarupa":["azure","solid","dragon","argent",1,"argent"],"k_bihar":["azure","solid","rose_seeded","or",1,"or"],"k_gondwana":["sable","solid","star_six_pointed","or",1,"or"],"k_orissa":["argent","solid","wheel_spoked","gules",1,"gules"],"e_deccan":["gules","solid","rose_seeded","or",1,"or"],"k_bene_israel":["gules","solid","castrum","or",1,"or"],"k_maharastra":["gules","solid","sword_crossed","or",2,"or"],"k_karnata":["or","solid","crescent_moon","sable",1,"sable"],"k_tamilakam":["gules","solid","fish_twin","or",1,"or"],"k_andhra":["or","solid","sun_radiant","gules",1,"gules"],"k_telingana":["gules","solid","wheel_spoked","or",1,"or"],"k_lanka":["sable","solid","lion_rampant","or",1,"or"],"e_tibet":["sable","solid","lion_rampant","or",1,"or"],"k_u":["azure","solid","wheel_spoked","argent",1,"argent"],"k_tsang":["gules","solid","wheel_spoked","argent",1,"argent"],"k_kham":["sable","solid","mount_triple","argent",1,"argent"],"k_amdo":["azure","solid","mount_triple","or",1,"or"],"k_gyalrong":["argent","solid","mount_triple","azure",1,"azure"],"k_guge":["gules","solid","wheel_spoked","or",1,"argent"],"k_maryul":["purpure","solid","mount_triple","argent",1,"argent"],"k_lhomon":["or","solid","dragon","vert",1,"vert"],"e_andong":["vert","solid","castrum","or",1,"gules"],"k_balhae":["azure","solid","horse_courant","argent",1,"argent"],"e_amur":["sable","solid","star_six_pointed","or",3,"or"],"e_srivijaya":["gules","solid","rose_seeded","or",1,"argent"],"d_JAV_mataram":["gules","solid","castrum","or",1,"argent"],"d_laamp_sabbah":["gules","solid","castrum","or",1,"argent"],"d_laamp_wake":["or","solid","lion_rampant","sable",1,"sable"],"d_laamp_el_cid":["vert","per_pale","bend","argent",1,"argent"],"d_laamp_crispin":["argent","solid","castrum","azure",1,"gules"],"d_laamp_suleyman":["azure","solid","alerion","argent",1,"argent"],"d_laamp_wallada":["argent","solid","castrum","azure",1,"azure"],"d_laamp_kizil_buga":["azure","solid","castrum","or",1,"argent"],"d_laamp_andronikos_komnenos":["or","solid","castrum","sable",1,"sable"],"d_laamp_raoul":["azure","solid","lion_rampant","or",1,"or"],"k_adiukru":["argent","solid","cross","vert",1,"vert"],"k_toro":["argent","solid","star_six_pointed","sable",1,"sable"],"k_winideheim":["sable","solid","lion_rampant","argent",1,"argent"],"e_japan":["gules","solid","castrum","or",1,"argent"],"k_chrysanthemum_throne":["gules","solid","castrum","or",1,"argent"],"c_nf_fujiwara_ashikaga":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_hamuro":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_hidesato":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_jimyoin":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_kajuji":["purpure","solid","oak_branch","argent",1,"argent"],"c_nf_fujiwara_kanin":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_koichijo":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_kujo":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_matsudono":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_michitsuna":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_mikohida":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_nakamikado":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_nakamura":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_namba":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_oinomikado":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_ononomiya":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_oshu":["or","solid","castrum","sable",1,"argent"],"c_nf_fujiwara_rokujo":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_saionji":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_saito":["gules","solid","castrum","or",1,"argent"],"c_nf_fujiwara_sanjo":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_sesonji":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_shijo":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_takaie":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_tokudaiji":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_utsunomiya":["purpure","solid","castrum","or",1,"argent"],"c_nf_fujiwara_yoshiyo":["purpure","solid","castrum","or",1,"argent"],"c_nf_minamoto_inoue":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_kawachi":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_kazan":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_kiso":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_mitsumasa":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_murakami":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_sanjo":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_sasaki":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_seiwa":["argent","solid","castrum","azure",1,"azure"],"c_nf_minamoto_uda":["gules","solid","castrum","or",1,"argent"],"c_nf_minamoto_yozei":["argent","solid","castrum","azure",1,"azure"],"c_nf_taira_hitachi":["argent","solid","castrum","azure",1,"azure"],"c_nf_taira_iwaki":["argent","solid","castrum","azure",1,"azure"],"c_nf_taira_kamakura":["argent","solid","castrum","azure",1,"azure"],"c_nf_taira_takamune":["argent","solid","castrum","azure",1,"azure"],"c_nf_ki_hosomi":["azure","solid","castrum","or",1,"argent"],"c_nf_ki_miyatsuko":["azure","solid","castrum","or",1,"argent"],"c_nf_ikeda":["argent","solid","castrum","azure",1,"azure"],"c_nf_ito":["vert","solid","castrum","or",1,"argent"],"c_nf_kikuchi":["sable","solid","castrum","or",1,"argent"],"c_nf_kimotsuki":["argent","solid","castrum","azure",1,"azure"],"c_nf_koremune":["argent","solid","castrum","azure",1,"azure"],"c_nf_kudo":["or","solid","castrum","sable",1,"argent"],"c_nf_matsura":["sable","solid","castrum","or",1,"argent"],"c_nf_otsuki":["gules","solid","castrum","or",1,"argent"],"c_nf_suzuki":["sable","solid","castrum","or",1,"argent"],"c_nf_tachibana_tokai":["gules","solid","castrum","or",1,"argent"],"c_nf_yokoyama":["vert","solid","cross","argent",1,"argent"],"c_nf_xia_liang":["sable","solid","castrum","or",1,"argent"],"e_zhongyuan":["or","solid","castrum","sable",1,"gules"],"k_henan":["or","solid","castrum","sable",1,"argent"],"d_dongji":["argent","solid","castrum","azure",1,"or"],"d_biansong":["or","solid","castrum","sable",1,"argent"],"d_shanguo":["or","solid","castrum","sable",1,"argent"],"d_zhenghua":["or","solid","castrum","sable",1,"argent"],"d_chenxu":["argent","solid","castrum","azure",1,"or"],"k_qingxu":["gules","solid","castrum","or",1,"sable"],"d_ziqing":["gules","solid","castrum","or",1,"sable"],"d_yanhai":["gules","solid","castrum","or",1,"sable"],"d_xusi":["sable","solid","castrum","or",1,"gules"],"d_yuncao":["sable","solid","castrum","or",1,"gules"],"k_hebei":["or","solid","fess","azure",1,"azure"],"d_weibo":["or","solid","castrum","sable",1,"azure"],"d_xingming":["azure","solid","fish_twin","or",1,"or"],"d_chengde":["or","solid","castrum","sable",1,"azure"],"d_cangjing":["azure","solid","castrum","or",1,"or"],"d_heyang":["azure","solid","castrum","or",1,"or"],"k_hedong":["or","solid","fish_twin","gules",1,"gules"],"d_hedong":["gules","solid","fish_twin","or",1,"or"],"d_yanmen":["or","solid","castrum","sable",1,"gules"],"d_hezhong":["or","solid","castrum","sable",1,"sable"],"d_zelu":["gules","solid","castrum","or",1,"or"],"k_youji":["gules","solid","castrum","or",1,"argent"],"d_youzhou":["gules","solid","castrum","or",1,"argent"],"d_yideng":["argent","solid","castrum","azure",1,"gules"],"d_yingmo":["gules","solid","castrum","or",1,"argent"],"k_daibei":["sable","solid","castrum","or",1,"or"],"d_yunshuo":["sable","solid","castrum","or",1,"or"],"d_sanggan":["sable","solid","castrum","or",1,"or"],"d_xinan":["or","solid","castrum","sable",1,"sable"],"e_yongliang":["argent","solid","castrum","azure",1,"sable"],"k_guannei":["argent","solid","castrum","azure",1,"sable"],"d_yongxing":["argent","solid","castrum","azure",1,"sable"],"d_fengxiang":["sable","solid","castrum","or",1,"argent"],"d_jinshang":["sable","solid","castrum","or",1,"argent"],"d_binning":["argent","solid","castrum","azure",1,"sable"],"d_fufang":["sable","solid","castrum","or",1,"argent"],"d_jingyuan":["argent","solid","castrum","azure",1,"sable"],"d_qincheng":["argent","solid","castrum","azure",1,"sable"],"d_xingfeng":["sable","solid","castrum","or",1,"argent"],"k_hexi":["gules","solid","roman_gate","or",1,"or"],"d_hexi":["argent","solid","castrum","azure",1,"gules"],"d_longyou":["gules","solid","castrum","or",1,"argent"],"d_gansu":["gules","solid","castrum","or",1,"argent"],"d_guasha":["argent","solid","castrum","azure",1,"gules"],"k_xia":["sable","solid","castrum","or",1,"argent"],"d_shuofang":["gules","solid","castrum","or",1,"sable"],"d_xiasui":["sable","solid","castrum","or",1,"gules"],"d_tiande":["gules","solid","castrum","or",1,"sable"],"d_langshan":["sable","solid","castrum","or",1,"gules"],"d_xiutu":["gules","solid","castrum","or",1,"sable"],"d_juyan":["sable","solid","castrum","or",1,"gules"],"e_jingyang":["gules","solid","castrum","or",1,"purpure"],"k_jiangdong":["gules","solid","waves","or",1,"azure"],"d_jiangdong":["gules","solid","castrum","or",1,"azure"],"d_xuanshe":["azure","solid","castrum","or",1,"gules"],"k_liangzhe":["purpure","solid","castrum","or",1,"argent"],"d_zhexi":["argent","solid","castrum","azure",1,"purpure"],"d_zhedong":["purpure","solid","castrum","or",1,"argent"],"k_fujian":["azure","solid","ship","argent",1,"argent"],"d_weiwu":["azure","solid","castrum","or",1,"argent"],"d_pinghai":["argent","solid","castrum","azure",1,"azure"],"c_zhangzhou":["sable","solid","castrum","or",1,"azure"],"d_jianning":["azure","solid","castrum","or",1,"argent"],"k_huainan":["purpure","solid","waves","or",1,"azure"],"d_huainan":["purpure","solid","castrum","or",1,"azure"],"c_yangzhou":["purpure","solid","castrum","or",1,"azure"],"d_huaixi":["azure","solid","castrum","or",1,"purpure"],"k_jiangxi":["purpure","solid","castrum","or",1,"or"],"d_jiangxi":["or","solid","castrum","sable",1,"purpure"],"d_dingjiang":["or","solid","castrum","sable",1,"purpure"],"d_zhaoxin":["purpure","solid","castrum","or",1,"or"],"k_shannan":["gules","solid","column_roman","or",1,"or"],"d_xiangdeng":["or","solid","castrum","sable",1,"gules"],"d_jingnan":["gules","solid","castrum","or",1,"or"],"d_eyue":["gules","solid","castrum","or",1,"or"],"k_hunan":["gules","solid","tree_chestnut","or",1,"or"],"d_hunan":["gules","solid","castrum","or",1,"or"],"d_lingling":["gules","solid","castrum","or",1,"or"],"e_liangyi":["azure","solid","castrum","or",1,"argent"],"k_xichuan":["azure","solid","castrum","or",1,"sable"],"d_xichuan":["sable","solid","castrum","or",1,"azure"],"d_qiongnan":["azure","solid","castrum","or",1,"or"],"c_meizhou":["vert","solid","castrum","or",1,"or"],"k_xingyuan":["azure","solid","castrum","or",1,"argent"],"d_xingyuan":["azure","solid","castrum","or",1,"argent"],"d_lilang":["azure","solid","castrum","or",1,"argent"],"d_baqu":["argent","solid","castrum","azure",1,"azure"],"k_dongchuan":["azure","solid","mount_triple","argent",1,"argent"],"d_dongchuan":["argent","solid","castrum","azure",1,"azure"],"d_wuxin":["azure","solid","castrum","or",1,"argent"],"k_kuizhou":["sable","solid","castrum","or",1,"azure"],"d_kuizhong":["sable","solid","castrum","or",1,"vert"],"d_qianzhong":["azure","solid","castrum","or",1,"sable"],"d_wuxi":["sable","solid","castrum","or",1,"azure"],"k_qianzhong":["azure","solid","tree_chestnut","or",1,"or"],"d_luodian":["azure","solid","castrum","or",1,"argent"],"d_luoshi":["azure","solid","castrum","or",1,"vert"],"d_shimen":["vert","solid","castrum","or",1,"argent"],"d_zangke":["vert","solid","castrum","or",1,"azure"],"d_xiyuan":["argent","solid","castrum","azure",1,"azure"],"k_dali":["argent","solid","dragon","azure",1,"azure"],"d_dali":["argent","solid","castrum","azure",1,"or"],"d_jianchuan":["argent","solid","castrum","azure",1,"or"],"d_huichuan":["argent","solid","castrum","azure",1,"azure"],"d_yinsheng":["azure","solid","castrum","or",1,"argent"],"d_tuodong":["azure","solid","castrum","or",1,"argent"],"d_tonghai":["argent","solid","castrum","azure",1,"or"],"e_lingnan":["vert","solid","castrum","or",1,"azure"],"k_lingnan":["vert","solid","battleaxe","argent",1,"argent"],"d_lingnan":["vert","solid","castrum","or",1,"argent"],"d_huixun":["argent","solid","castrum","azure",1,"vert"],"d_gaoliang":["vert","solid","castrum","or",1,"argent"],"d_qiongguan":["vert","solid","castrum","or",1,"argent"],"k_lingxi":["vert","solid","castrum","or",1,"sable"],"d_guiguan":["vert","solid","castrum","or",1,"sable"],"d_jingjiang":["sable","solid","castrum","or",1,"vert"],"d_rongguan":["vert","solid","castrum","or",1,"sable"],"d_yongguan":["sable","solid","castrum","or",1,"vert"],"k_viet":["azure","solid","castrum","or",1,"vert"],"d_hai_dong":["azure","solid","castrum","or",1,"vert"],"d_nghe_an":["vert","solid","castrum","or",1,"azure"],"d_lam_tay":["vert","solid","castrum","or",1,"azure"],"d_thang_long":["azure","solid","castrum","or",1,"argent"],"e_minister_chancellor":["azure","solid","castrum","or",1,"argent"],"e_minister_censor":["purpure","solid","castrum","or",1,"argent"],"e_minister_grand_marshal":["gules","solid","castrum","or",1,"argent"],"e_minister_of_personnel":["argent","solid","castrum","azure",1,"azure"],"e_minister_of_revenue":["vert","solid","castrum","or",1,"argent"],"e_minister_of_rites":["argent","solid","castrum","azure",1,"sable"],"e_minister_of_war":["argent","solid","castrum","azure",1,"gules"],"e_minister_of_justice":["argent","solid","castrum","azure",1,"sable"],"e_minister_of_works":["argent","solid","castrum","azure",1,"vert"],"e_suvarnabhumi":["or","solid","sun_radiant","gules",1,"gules"],"k_pagan":["gules","solid","castrum","or",1,"azure"],"d_pagan":["azure","solid","castrum","or",1,"gules"],"d_ramannadesa":["or","solid","castrum","sable",1,"gules"],"d_yongchang":["gules","solid","castrum","or",1,"vert"],"d_haripunjaya":["gules","solid","castrum","or",1,"or"],"k_siam":["gules","solid","castrum","or",1,"argent"],"e_brunei":["or","solid","castrum","sable",1,"sable"],"k_brunei":["or","solid","castrum","sable",1,"sable"],"e_kambuja":["azure","solid","castrum","or",1,"gules"],"k_funan":["or","solid","dragon","sable",1,"sable"],"d_angkor":["gules","solid","castrum","or",1,"azure"],"c_nf_wang_738b_6":["gules","solid","castrum","or",1,"argent"],"c_nf_su_82CF":["azure","solid","castrum","or",1,"or"],"c_nf_qin_79E6_4":["vert","solid","castrum","or",1,"or"],"c_nf_new_noble_dynasty":["sable","solid","castrum","or",1,"argent"],"e_goryeo":["or","solid","castrum","sable",1,"vert"],"k_goguryeo":["azure","solid","falcon_perched","argent",1,"argent"],"k_silla":["azure","solid","crown","argent",1,"argent"],"k_baekje":["or","solid","stag_attired","sable",1,"sable"],"d_tamna":["gules","solid","castrum","or",1,"argent"],"k_yongson_throne":["gules","solid","castrum","or",1,"azure"],"e_nusantara":["gules","solid","ship","or",1,"argent"],"d_BOR_kutai":["or","solid","crescent_moon","gules",1,"argent"],"k_ruucuu":["argent","solid","cross","azure",1,"azure"],"d_ruucuu":["argent","solid","wolf_statant","azure",1,"azure"],"d_cd_ostia":["azure","per_fess","anchor","or",1,"or"],"d_cd_porto":["azure","per_fess","ship","or",1,"argent"],"d_cd_velletri":["gules","per_fess","castrum","argent",1,"argent"],"d_cd_frascati":["azure","solid","cross","argent",1,"or"],"d_cd_albano":["azure","solid","mount_triple","argent",1,"argent"],"d_cd_palestrina":["gules","solid","crown","or",1,"argent"],"d_cd_sabina":["azure","solid","star_six_pointed","or",1,"or"],"d_cd_san_ciriaco":["argent","solid","lion_rampant","gules",1,"gules"],"d_cd_san_lorenzo":["gules","solid","cross","argent",1,"or"],"d_cd_santa_cecilia":["azure","solid","star_six_pointed","argent",1,"or"],"d_cd_santa_balbina":["gules","solid","cross","argent",1,"argent"],"d_cd_san_pietro":["gules","solid","keys_st_peter","or",1,"or"],"d_cd_santa_anastasia":["argent","solid","cross","gules",1,"gules"],"d_cd_damaso":["gules","solid","crown","argent",1,"or"],"d_cd_santa_rufina":["argent","solid","waves","azure",1,"azure"],"d_cd_santa_sabina":["vert","solid","cross","argent",1,"argent"],"d_cd_santa_maria":["azure","solid","ship","argent",1,"argent"],"d_cd_santa_prassede":["gules","solid","oak_branch","argent",1,"or"],"d_cd_santi_cosma_e_damiano":["vert","solid","cross","argent",2,"argent"],"d_cd_san_stefano":["gules","solid","oak_branch","or",1,"or"],"d_cd_san_clemente":["azure","solid","anchor","argent",1,"argent"],"d_cd_santi_silvestro_e_martino":["azure","solid","crown","argent",1,"or"],"d_cd_santi_nereo_ed_achilleo":["gules","solid","cross","argent",1,"argent"],"d_cd_san_eustachio":["azure","solid","stag_attired","or",1,"or"],"d_cd_santa_maria_nuova":["azure","solid","star_six_pointed","argent",1,"argent"],"d_cd_san_teodoro":["gules","solid","dragon","or",1,"or"],"d_cd_san_adriano":["sable","solid","sword_crossed","or",1,"or"],"d_cd_san_marcello":["gules","solid","cross_patriarchal","argent",1,"argent"],"d_cd_san_vitale":["gules","solid","oak_branch","argent",1,"argent"],"d_cd_san_angelo":["azure","solid","sword_crossed","or",1,"or"],"d_cd_santa_croce":["argent","solid","cross","gules",1,"gules"],"d_cd_portico_octaviae":["gules","solid","cross","or",1,"argent"],"d_cd_san_crisogono":["or","solid","cross","gules",1,"gules"],"d_cd_san_giorgio":["argent","solid","cross","azure",1,"gules"],"d_cd_cosmedin":["azure","solid","star_six_pointed","argent",1,"argent"],"d_cd_san_marco":["gules","solid","lion_rampant","or",1,"or"],"d_cd_santi_apostoli":["azure","solid","keys_st_peter","or",1,"or"],"d_cd_santa_pudenziana":["azure","solid","oak_branch","argent",1,"argent"],"d_cd_san_eusebio":["vert","solid","cross","argent",1,"or"],"d_cd_santi_sergio_e_bacco":["vert","solid","cross","argent",1,"argent"],"d_cd_san_nicola":["azure","solid","cross","argent",1,"or"],"d_cd_santi_giovanni_e_paolo":["gules","solid","cross","argent",1,"argent"],"d_et_toledo":["gules","solid","cross","argent",1,"or"],"d_et_santiago":["azure","per_pale","star_six_pointed","or",1,"argent"],"d_et_tarragona":["gules","solid","castrum","or",1,"argent"],"d_et_sevilla":["gules","per_pale","cross","argent",1,"or"],"d_et_braga":["azure","per_pale","star_six_pointed","argent",1,"argent"],"d_et_merida":["gules","solid","cross","argent",1,"or"],"d_et_tingitana":["azure","solid","cross","or",1,"argent"],"d_et_york":["gules","solid","cross","argent",1,"argent"],"d_et_tuam":["vert","solid","cross","or",1,"or"],"d_et_dublin":["azure","solid","castrum","argent",3,"argent"],"d_et_cashel":["vert","solid","mount_triple","or",1,"argent"],"d_et_armagh":["argent","solid","castrum","azure",1,"gules"],"d_et_canterbury":["azure","solid","cross","argent",3,"argent"],"d_et_rouen":["gules","solid","cross","argent",1,"or"],"d_et_reims":["azure","solid","cross_patriarchal","or",1,"or"],"d_et_sens":["azure","solid","cross_patriarchal","or",1,"or"],"d_et_tours":["azure","per_pale","sword_crossed","argent",1,"argent"],"d_et_bourges":["azure","solid","fleur_de_lis","or",3,"or"],"d_et_bordeaux":["azure","solid","ship","argent",1,"argent"],"d_et_lyon":["gules","solid","cross_patriarchal","or",1,"or"],"d_et_tarentaise":["gules","solid","cross","argent",1,"argent"],"d_et_vienne":["or","solid","cross","azure",1,"azure"],"d_et_eauze":["azure","solid","cross","argent",1,"or"],"d_et_auch":["azure","solid","cross","argent",1,"or"],"d_et_narbonne":["argent","solid","cross","gules",1,"gules"],"d_et_besancon":["or","solid","cross_patriarchal","sable",1,"sable"],"d_et_arles":["or","solid","cross","gules",1,"gules"],"d_et_aix":["or","solid","cross","gules",1,"gules"],"d_et_embrun":["vert","solid","mount_triple","argent",1,"or"],"d_et_milano":["argent","solid","cross","gules",1,"gules"],"d_et_genoa":["argent","solid","cross","gules",1,"gules"],"d_et_cagliari":["argent","solid","cross","gules",1,"gules"],"d_et_torres":["or","solid","cross","gules",1,"gules"],"d_et_oristano":["argent","solid","cross","gules",1,"vert"],"d_et_reggio_calabria":["gules","per_fess","cross","argent",1,"or"],"d_et_cosenza":["vert","solid","mount_triple","argent",1,"argent"],"d_et_messina":["azure","solid","cross","argent",1,"argent"],"d_et_palermo":["gules","solid","cross","argent",1,"or"],"d_et_santa_severina":["vert","solid","oak_branch","argent",1,"argent"],"d_et_ravenna":["or","solid","alerion","gules",1,"gules"],"d_et_roma":["argent","solid","keys_st_peter","azure",1,"or"],"d_et_pisa":["gules","solid","cross","argent",1,"argent"],"d_et_capua":["gules","solid","cross","argent",1,"or"],"d_et_napoli":["or","solid","horse_courant","sable",1,"gules"],"d_et_salerno":["vert","solid","cross","argent",1,"or"],"d_et_benevento":["gules","solid","cross_patriarchal","argent",1,"or"],"d_et_bari":["sable","solid","castrum","or",1,"or"],"d_et_trani":["azure","per_fess","cross","or",1,"argent"],"d_et_brindisi":["gules","solid","cross","or",1,"argent"],"d_et_aquileia":["azure","solid","alerion","or",1,"or"],"d_et_esztergom":["gules","solid","cross_patriarchal","or",1,"argent"],"d_et_kalocsa":["gules","solid","cross_patriarchal","argent",1,"argent"],"d_et_split":["gules","per_pale","cross","or",1,"or"],"d_et_ohrid":["sable","solid","cross","or",1,"or"],"d_et_ragusa":["gules","solid","cross","or",1,"argent"],"d_et_salzburg":["or","solid","lion_rampant","sable",1,"sable"],"d_et_trier":["argent","solid","cross","gules",1,"gules"],"d_et_gniezno":["gules","solid","alerion","argent",1,"argent"],"d_et_mainz":["gules","solid","wheel_spoked","argent",1,"argent"],"d_et_magdeburg":["gules","per_fess","castrum","or",1,"argent"],"d_et_cologne":["argent","solid","cross","sable",1,"sable"],"d_et_hamburg":["gules","solid","castrum","argent",1,"argent"],"d_et_lund":["gules","solid","cross","argent",1,"argent"],"d_et_uppsala":["gules","solid","cross","or",1,"or"],"d_et_nidaros":["gules","solid","lion_rampant","argent",1,"or"],"d_et_kyiv":["azure","solid","cross","argent",1,"or"],"d_et_constantinople":["or","solid","alerion","sable",1,"sable"],"d_et_jerusalem":["argent","solid","cross","azure",1,"or"],"d_et_antioch":["gules","solid","cross_patriarchal","argent",1,"or"],"d_et_cyprus":["argent","solid","crown","gules",1,"azure"],"d_et_georgia":["argent","solid","cross","gules",1,"gules"],"d_et_kartli":["gules","solid","cross","argent",1,"argent"],"d_et_armenia":["gules","solid","cross","or",1,"or"],"d_et_seleucia_ctesiphon":["azure","solid","anchor","argent",1,"argent"],"d_et_tyre":["argent","solid","cross","gules",1,"azure"],"d_et_alexandria":["azure","solid","lion_rampant","or",1,"or"],"d_et_axum":["vert","per_pale","cross","argent",1,"or"],"d_et_africa":["azure","solid","oak_branch","or",1,"or"],"d_arc":["sable","solid","lion_rampant","argent",1,"argent"],"e_scandinavia_norse":["argent","solid","castrum","azure",1,"gules"],"d_viken_norse":["or","solid","castrum","sable",1,"gules"],"c_sudurland_norse":["gules","solid","dragon","argent",1,"argent"],"c_faereyar_norse":["azure","solid","ship","or",1,"or"],"c_vestisland":["vert","solid","castrum","or",1,"sable"],"d_northern_isles":["azure","solid","ship","or",1,"or"],"c_orkney":["azure","solid","ship","or",1,"or"],"c_shetland":["azure","solid","waves","argent",1,"or"],"c_faereyar":["azure","solid","castrum","or",1,"argent"],"c_sudurland":["gules","solid","wheel_spoked","argent",1,"argent"],"d_western_isles":["or","solid","ship","sable",3,"sable"],"c_inner_hebrides":["or","solid","alerion","gules",1,"gules"],"c_argyll":["sable","solid","castrum","or",1,"or"],"c_austisland":["or","solid","castrum","sable",1,"azure"],"c_nordrland":["sable","solid","star_six_pointed","or",1,"or"],"d_iceland":["or","solid","lion_rampant","gules",1,"gules"],"c_dublin":["or","solid","ship","sable",1,"sable"],"c_east_riding":["argent","solid","cross","gules",1,"gules"],"d_york":["or","solid","crown","gules",1,"gules"],"c_harjadalen":["gules","solid","castrum","or",1,"or"],"d_bergslagen":["gules","solid","battleaxe","argent",1,"argent"],"d_halogaland":["gules","solid","dragon","or",1,"or"],"c_vastmanland":["argent","solid","dragon","sable",1,"sable"],"c_dalarna":["azure","solid","crown","or",1,"or"],"c_bothin":["or","solid","wheel_spoked","gules",3,"argent"],"d_norrland":["azure","solid","stag_attired","argent",1,"argent"],"c_medelpad":["argent","solid","castrum","azure",1,"azure"],"c_angermanland":["argent","solid","castrum","azure",1,"azure"],"d_gotland":["gules","solid","castrum","or",1,"argent"],"c_gutland":["gules","solid","castrum","or",1,"argent"],"d_sjaelland":["or","solid","dragon","azure",1,"gules"],"c_lolland_falster":["azure","solid","oak_branch","argent",1,"gules"],"c_fyn":["argent","solid","fleur_de_lis","gules",1,"gules"],"d_skane":["gules","solid","castrum","or",1,"or"],"d_vestlandi":["gules","solid","crown","or",1,"or"],"c_halland":["argent","solid","lion_rampant","azure",1,"gules"],"c_skane":["argent","solid","castrum","azure",1,"gules"],"c_bornholm":["azure","solid","dragon","or",1,"argent"],"c_vingulmork":["sable","solid","castrum","or",1,"azure"],"c_agdeside":["argent","solid","castrum","azure",1,"or"],"d_jamtland":["gules","solid","lion_rampant","or",1,"or"],"c_helgum":["argent","solid","castrum","azure",1,"azure"],"c_vastvag":["gules","solid","dragon","or",1,"or"],"d_agder":["vert","solid","oak_branch","or",1,"or"],"c_nedenes":["azure","solid","star_six_pointed","argent",3,"argent"],"d_vastergotland":["sable","per_bend","lion_rampant","or",1,"or"],"c_norwegian_more":["gules","solid","castrum","or",1,"or"],"c_jamtfir":["gules","solid","cross","argent",1,"argent"],"c_morarna":["vert","solid","castrum","or",1,"gules"],"d_jylland":["or","solid","castrum","sable",1,"azure"],"c_viborg":["argent","solid","castrum","azure",1,"azure"],"c_aalborg":["argent","solid","castrum","azure",1,"azure"],"c_ringkobing":["argent","solid","bend","azure",1,"azure"],"c_aarhus":["or","solid","castrum","sable",1,"gules"],"k_sweden":["azure","solid","crown","or",3,"or"],"c_skara":["azure","solid","cross","or",1,"argent"],"c_namdalfylki":["gules","solid","alerion","argent",3,"azure"],"k_denmark":["or","solid","lion_rampant","azure",3,"gules"],"d_slesvig":["or","solid","castrum","sable",1,"azure"],"c_sjaelland":["sable","solid","castrum","or",1,"or"],"d_trandalog":["or","solid","cross","gules",1,"gules"],"c_vorbasse":["argent","solid","castrum","azure",1,"gules"],"c_ribe":["argent","solid","castrum","gules",1,"gules"],"c_sogn":["sable","solid","castrum","argent",1,"or"],"c_hordalandi":["argent","solid","castrum","azure",1,"azure"],"c_halsingland":["sable","solid","castrum","or",1,"or"],"c_rogalandi":["argent","solid","bend","azure",1,"azure"],"d_smaland":["or","solid","lion_rampant","gules",1,"gules"],"c_more":["or","solid","castrum","sable",1,"azure"],"c_sevede":["vert","solid","castrum","or",1,"sable"],"c_oland":["azure","solid","stag_attired","or",1,"argent"],"c_blekinge":["argent","solid","crown","sable",1,"azure"],"c_finnveden":["gules","solid","castrum","or",1,"argent"],"c_njudung":["or","solid","castrum","sable",1,"gules"],"c_varend":["gules","solid","castrum","or",1,"or"],"d_dalir":["or","solid","castrum","sable",1,"sable"],"c_gudbrandsdalir":["sable","solid","castrum","or",1,"argent"],"c_eystridalir":["argent","solid","castrum","azure",1,"azure"],"c_gauldala":["sable","solid","castrum","or",1,"or"],"c_telemark":["sable","solid","star_six_pointed","argent",3,"azure"],"c_firdafylki":["azure","solid","castrum","or",1,"or"],"k_norway":["gules","solid","battleaxe","or",1,"or"],"c_vestfold":["vert","solid","castrum","or",1,"gules"],"c_dal":["argent","solid","castrum","azure",1,"gules"],"c_raniriki":["or","solid","star_six_pointed","gules",1,"gules"],"c_trandheim":["or","solid","castrum","sable",1,"argent"],"c_ostergotland":["gules","per_bend","lion_rampant","or",1,"argent"],"d_ostergotland":["gules","solid","dragon","or",1,"or"],"c_kinda":["argent","solid","star_six_pointed","azure",3,"azure"],"c_narke":["gules","solid","castrum","or",1,"or"],"d_viken":["or","solid","bear_rampant","sable",1,"sable"],"c_hedmork":["sable","solid","castrum","or",1,"or"],"c_dalabergslagen":["azure","solid","castrum","or",1,"argent"],"d_svealand":["azure","solid","crown","or",3,"or"],"c_upland":["gules","solid","castrum","or",1,"or"],"c_gastrikland":["argent","solid","castrum","azure",1,"gules"],"c_sodermannaland":["or","solid","dragon","sable",1,"sable"],"c_aland":["azure","solid","stag_attired","or",1,"or"],"c_nordmark":["argent","solid","bear_rampant","azure",1,"azure"],"c_slesvig":["or","solid","lion_rampant","azure",2,"azure"],"c_vastergotland":["azure","per_bend","lion_rampant","or",1,"argent"],"c_varmland":["argent","solid","star_six_pointed","azure",3,"azure"],"e_scandinavia":["gules","solid","crown","or",3,"or"],"e_hre_roman":["gules","solid","crown","or",2,"or"],"d_canterbury":["gules","solid","horse_courant","argent",1,"argent"],"c_hereford":["gules","per_bend_sinister","bend","or",1,"or"],"c_byzantion":["gules","solid","cross","or",1,"or"],"h_roman_empire":["or","solid","eagle_double","sable",1,"sable"],"e_turan":["azure","solid","wolf_statant","or",1,"or"],"x_script_7238":["or","solid","cross","sable",1,"sable"],"x_script_6717":["or","solid","alerion","gules",1,"gules"],"k_tanjungnagara":["azure","solid","anchor","or",1,"or"],"k_azuma":["argent","solid","sun_radiant","gules",1,"gules"],"k_maluku":["vert","solid","ship","or",1,"or"],"x_script_2942":["or","solid","cross_patriarchal","sable",1,"sable"],"k_amur":["azure","solid","fish_twin","argent",2,"argent"],"k_aynumosir":["sable","solid","bear_rampant","argent",1,"argent"],"k_khitan":["azure","solid","falcon_perched","or",1,"or"],"k_luzhen":["vert","solid","oak_branch","or",1,"or"],"k_raole":["or","solid","oak_branch","sable",1,"sable"],"k_gobi":["or","solid","horse_courant","sable",1,"sable"],"x_script_4359":["gules","solid","cross","or",2,"or"],"x_script_4774":["azure","solid","cross","or",1,"or"],"x_script_6373":["argent","solid","cross","gules",2,"gules"],"k_qara_dala":["vert","solid","horse_courant","argent",1,"argent"],"x_script_5503":["azure","solid","bow_and_arrow","argent",1,"argent"],"x_script_3965":["or","solid","alerion","sable",2,"sable"],"x_script_4328":["argent","solid","lion_rampant","gules",2,"gules"],"k_hitakami":["vert","solid","tree_chestnut","or",1,"or"],"k_tsukushi":["azure","solid","waves","argent",1,"argent"],"k_yamato":["gules","solid","sun_radiant","or",1,"or"],"k_champa":["or","solid","rose_seeded","gules",1,"gules"],"k_chenla":["or","solid","castrum","gules",1,"gules"],"k_naimania":["gules","solid","bow_and_arrow","or",1,"or"],"k_shiwei":["azure","solid","stag_attired","argent",1,"argent"],"k_kabisay-an":["azure","solid","ship","or",1,"or"],"k_liuqiu":["azure","solid","sun_radiant","or",1,"or"],"k_lusung":["gules","solid","star_six_pointed","or",3,"or"],"k_sulawesi":["or","solid","anchor","sable",1,"sable"],"k_hujung_medini":["gules","solid","sword_crossed","or",1,"or"],"k_malayadvipa":["or","solid","ship","gules",1,"gules"],"k_yavakadvipa":["gules","solid","rose_seeded","or",1,"or"],"k_dvaravati":["or","solid","wheel_spoked","gules",1,"gules"],"k_saryarka":["vert","solid","bow_and_arrow","or",1,"or"]};

  const CANONICAL_SINOSPHERE_HANZI = {
    e_zhongyuan: '中原',
    e_liangyi: '梁益',
    e_jingyang: '荆扬',
    e_yongliang: '雍凉',
    e_lingnan: '岭南',
    e_goryeo: '三韩',
    e_japan: '日本',
    e_andong: '安东',
    e_amur: '阿穆尔'
  };

  function formatBlazon(fieldKey, chargeKey, chargeColorHex, ordinaryKey = 'solid', chargeCount = 1, ordColorHex = null) {
    const fieldTinc = TINCTURES[fieldKey] || TINCTURES.gules;
    let chargeTincKey = 'argent';
    if (typeof chargeColorHex === 'string' && TINCTURES[chargeColorHex]) chargeTincKey = chargeColorHex;
    else if (chargeColorHex === PALETTE.or) chargeTincKey = 'or';
    else if (chargeColorHex === PALETTE.sable) chargeTincKey = 'sable';
    else if (chargeColorHex === PALETTE.gules) chargeTincKey = 'gules';
    else if (chargeColorHex === PALETTE.azure) chargeTincKey = 'azure';
    else if (chargeColorHex === PALETTE.vert) chargeTincKey = 'vert';
    else if (chargeColorHex === PALETTE.purpure) chargeTincKey = 'purpure';
    const chargeTinc = TINCTURES[chargeTincKey] || TINCTURES.argent;

    let ordTincKey = 'argent';
    if (typeof ordColorHex === 'string' && TINCTURES[ordColorHex]) ordTincKey = ordColorHex;
    else if (ordColorHex === PALETTE.or) ordTincKey = 'or';
    else if (ordColorHex === PALETTE.sable) ordTincKey = 'sable';
    else if (ordColorHex === PALETTE.gules) ordTincKey = 'gules';
    else if (ordColorHex === PALETTE.azure) ordTincKey = 'azure';
    else if (ordColorHex === PALETTE.vert) ordTincKey = 'vert';
    else if (ordColorHex === PALETTE.purpure) ordTincKey = 'purpure';
    const ordTinc = TINCTURES[ordTincKey] || TINCTURES.argent;

    const chargeMeta = CHARGE_BLAZONS[chargeKey] || {
      tarrNoun: 'Emblem',
      tarrPlural: 'Embleme',
      enNoun: (chargeKey || 'charge').replace(/_/g, ' '),
      enPlural: ((chargeKey || 'charge') + 's').replace(/_/g, ' '),
      enArticle: 'a'
    };

    let chargeTextTarr = '';
    let chargeTextEn = '';
    const adj = chargeTinc.tarrAdj;
    const plAdj = adj.endsWith('er') ? adj.slice(0, -2) + 'e' : (adj.endsWith('en') ? adj : adj + 'e');

    if (chargeKey === 'waves') {
      if (chargeCount === 2) {
        chargeTextTarr = `zwô Meereswâgen van ${chargeTinc.tarr}`;
        chargeTextEn = `two waves ${chargeTinc.en}`;
      } else if (chargeCount >= 3) {
        chargeTextTarr = `drî Meereswâgen van ${chargeTinc.tarr}`;
        chargeTextEn = `three waves ${chargeTinc.en}`;
      } else {
        chargeTextTarr = `Meereswâgen van ${chargeTinc.tarr}`;
        chargeTextEn = `waves ${chargeTinc.en}`;
      }
    } else if (chargeKey === 'keys_st_peter') {
      chargeTextTarr = `zwên gekrützte Slüttele van Zant Peter van Golt und Silber`;
      chargeTextEn = `two keys in saltire of St. Peter Or and Argent`;
    } else if (chargeCount === 2) {
      chargeTextTarr = `zwên ${plAdj} ${chargeMeta.tarrPlural || chargeMeta.tarrNoun}`;
      chargeTextEn = `two ${chargeMeta.enPlural || chargeMeta.enNoun} in pale ${chargeTinc.en}`;
    } else if (chargeCount >= 3) {
      chargeTextTarr = `drî ${plAdj} ${chargeMeta.tarrPlural || chargeMeta.tarrNoun}`;
      chargeTextEn = `three ${chargeMeta.enPlural || chargeMeta.enNoun} ${chargeTinc.en}`;
    } else {
      chargeTextTarr = `ein ${adj} ${chargeMeta.tarrNoun}`;
      const art = chargeMeta.enArticle ? `${chargeMeta.enArticle} ` : '';
      chargeTextEn = `${art}${chargeMeta.enNoun} ${chargeTinc.en}`;
    }

    let blazonTarr = '';
    let blazonEn = '';

    if (!ordinaryKey || ordinaryKey === 'solid') {
      blazonTarr = `In ${fieldTinc.tarr} ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'per_pale') {
      blazonTarr = `Gespalten van ${fieldTinc.tarr} und ${ordTinc.tarr}, belegt mit ${chargeTextTarr}`;
      blazonEn = `Party per pale ${fieldTinc.en} and ${ordTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'per_fess') {
      blazonTarr = `Geteilt van ${fieldTinc.tarr} und ${ordTinc.tarr}, belegt mit ${chargeTextTarr}`;
      blazonEn = `Party per fess ${fieldTinc.en} and ${ordTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'per_bend') {
      blazonTarr = `Schräggeteilt van ${fieldTinc.tarr} und ${ordTinc.tarr}, belegt mit ${chargeTextTarr}`;
      blazonEn = `Party per bend ${fieldTinc.en} and ${ordTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'per_bend_sinister') {
      blazonTarr = `Links-schräggeteilt van ${fieldTinc.tarr} und ${ordTinc.tarr}, belegt mit ${chargeTextTarr}`;
      blazonEn = `Party per bend sinister ${fieldTinc.en} and ${ordTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'quarterly') {
      blazonTarr = `Geviert van ${fieldTinc.tarr} und ${ordTinc.tarr}, belegt mit ${chargeTextTarr}`;
      blazonEn = `Quarterly ${fieldTinc.en} and ${ordTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'per_saltire') {
      blazonTarr = `Schräggeviert van ${fieldTinc.tarr} und ${ordTinc.tarr}, belegt mit ${chargeTextTarr}`;
      blazonEn = `Party per saltire ${fieldTinc.en} and ${ordTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'fess') {
      blazonTarr = `In ${fieldTinc.tarr} ein ${ordTinc.tarrAdj} Balken begleitet van ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, a fess ${ordTinc.en} accompanied by ${chargeTextEn}`;
    } else if (ordinaryKey === 'pale') {
      blazonTarr = `In ${fieldTinc.tarr} ein ${ordTinc.tarrAdj} Pfahl belegt mit ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, a pale ${ordTinc.en} charged with ${chargeTextEn}`;
    } else if (ordinaryKey === 'bend') {
      blazonTarr = `In ${fieldTinc.tarr} ein ${ordTinc.tarrAdj} Schrägbalken belegt mit ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, on a bend ${ordTinc.en} ${chargeTextEn}`;
    } else if (ordinaryKey === 'bend_sinister') {
      blazonTarr = `In ${fieldTinc.tarr} ein ${ordTinc.tarrAdj} Schräglinksbalken belegt mit ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, on a bend sinister ${ordTinc.en} ${chargeTextEn}`;
    } else if (ordinaryKey === 'chevron') {
      blazonTarr = `In ${fieldTinc.tarr} ein ${ordTinc.tarrAdj} Sparren begleitet van ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, a chevron ${ordTinc.en} between ${chargeTextEn}`;
    } else if (ordinaryKey === 'cross') {
      blazonTarr = `In ${fieldTinc.tarr} ein ${ordTinc.tarrAdj} Krütz belegt mit ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, a cross ${ordTinc.en} charged with ${chargeTextEn}`;
    } else if (ordinaryKey === 'saltire') {
      blazonTarr = `In ${fieldTinc.tarr} ein ${ordTinc.tarrAdj} Andreaskrütz belegt mit ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, a saltire ${ordTinc.en} charged with ${chargeTextEn}`;
    } else if (ordinaryKey === 'chief') {
      blazonTarr = `In ${fieldTinc.tarr} ein ${ordTinc.tarrAdj} Schildhoubet, im Schilt ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, a chief ${ordTinc.en}, in the field ${chargeTextEn}`;
    } else if (ordinaryKey === 'bordure') {
      blazonTarr = `In ${fieldTinc.tarr} innerhalb eines ${ordTinc.tarrAdj.endsWith('er') ? ordTinc.tarrAdj.slice(0, -2) + 'en' : ordTinc.tarrAdj + 'en'} Bordes ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, within a bordure ${ordTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'barry') {
      blazonTarr = `Sechsmâl geteilt van ${fieldTinc.tarr} und ${ordTinc.tarr}, belegt mit ${chargeTextTarr}`;
      blazonEn = `Barry of six ${fieldTinc.en} and ${ordTinc.en}, ${chargeTextEn}`;
    } else if (ordinaryKey === 'chequy') {
      blazonTarr = `Geschacht van ${fieldTinc.tarr} und ${ordTinc.tarr}, belegt mit ${chargeTextTarr}`;
      blazonEn = `Chequy ${fieldTinc.en} and ${ordTinc.en}, ${chargeTextEn}`;
    } else {
      blazonTarr = `In ${fieldTinc.tarr} ${chargeTextTarr}`;
      blazonEn = `${fieldTinc.en}, ${chargeTextEn}`;
    }

    return { blazonTarr, blazonEn };
  }

  // Multilingual Toponymic Tincture Morpheme Patterns
  const TINCTURE_PATTERNS = {
    vert: new RegExp(
      '(?:' +
      'gr[uûü]n[a-z]*|' +
      '\\bzelen[a-z]*\\b|\\bseleng[oô]r[a-z]*\\b|' +
      '\\bz[oö]ld[a-z]*\\b|' +
      '\\b(?:al[-_]?)?akhdar\\b|\\b(?:al[-_]?)?kh?adra\\b(?!mawt)|' +
      '\\byashil[a-z]*\\b|\\bye[sş]il[a-z]*\\b|' +
      '\\bchlor[a-z]*\\b|' +
      '\\bglas\\b|buglas|' +
      '\\bvert\\b|\\bverde[a-z]*\\b|\\bvirid[a-z]*\\b|' +
      '\\bgreen[a-z]*\\b|' +
      '\\bl[uü]se\\b|\\blv\\b|\\bverdant\\b' +
      ')',
      'i'
    ),
    azure: new RegExp(
      '(?:' +
      '\\bblou[a-z]*\\b|k[oô]lblou[a-z]*|z[iî]blou[a-z]*|' +
      '\\bbl[aâ]u[a-z]*\\b|\\bblâ(?!n)[a-z]*\\b|' +
      '\\bl[aâ]s[uû]r[a-z]*\\b|' +
      '\\bazur[a-z]*\\b|\\bazzurr[a-z]*\\b|\\bazure\\b|' +
      '\\bk[eé]k[a-z]*\\b|' +
      '\\bsin[yi][a-z]*\\b|' +
      '\\bplav[a-z]*\\b|' +
      '\\b(?:al[-_]?)?azraq\\b|\\bzarqa\\b|' +
      '\\bg[oö]k[a-z]*\\b|' +
      '\\bkyan[a-z]*\\b|\\bcyano[a-z]*\\b|' +
      '\\bbleu[a-z]*\\b|\\bblue[a-z]*\\b|' +
      '\\bcaerul[a-z]*\\b|' +
      '\\bgorm\\b|' +
      '\\bqing[a-z]*\\b|' +
      '\\bcang(?:zhou|jing)\\b' +
      ')',
      'i'
    ),
    argent: new RegExp('(?:w[îi]tz[a-z]*|weiss[a-z]*|blank[a-z]*|\\balba\\b|\\balbus\\b|\\bfeh[eé]r[a-z]*|\\bb[eé]l[a-z]*|\\bblanc\\b|\\bbianco\\b|\\babyad\\b)', 'i'),
    gules: new RegExp('(?:r[oô]t[a-z]*|\\bv[oö]r[oö]s[a-z]*|\\bpiros[a-z]*|\\brouge\\b|\\brosso\\b|\\bahmar\\b|\\bcz?erven[a-z]*|\\bkrasn[a-z]*|\\bred\\b)', 'i'),
    sable: new RegExp('(?:swartz[a-z]*|schwarz[a-z]*|\\bcz?ern[a-z]*|\\bfekete[a-z]*|\\bnoir\\b|\\bnero\\b|\\baswad\\b|\\bqara\\b|\\bblack\\b)', 'i'),
    or: new RegExp('(?:golt[a-z]*|gold[a-z]*|g[uü]ld[a-z]*|\\barany[a-z]*|\\bzlat[a-z]*|\\baur[a-z]*|\\bchrys[a-z]*|\\bdhahab\\b|\\baltyn\\b)', 'i')
  };

  // =========================================================================
  // 4. Deterministic Hash, Chronological Horizons & Canting Analyzer
  // =========================================================================
  function hashString(str) {
    let hash = 5381;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) + hash) + str.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash);
  }

  const HORIZON_0_TITLES = new Set([
    'h_roman_empire', 'e_hre', 'c_roma', 'd_latium', 'k_romagna', 'k_papal_state',
    'c_byzantion', 'e_byzantium', 'c_tarragona', 'c_barcelona', 'd_barcelona',
    'c_metz', 'd_upper_lorraine', 'k_lotharingia', 'c_aachen', 'c_trier', 'c_cologne',
    'c_paris', 'c_alexandria', 'c_antioch', 'c_jerusalem', 'c_lviv', 'c_szekesfehervar'
  ]);

  const HORIZON_1_EMPIRES = new Set(['e_germany', 'e_france']);
  const HORIZON_1_KINGDOMS = new Set([
    'k_germany', 'k_lotharingia', 'k_bavaria', 'k_italy', 'k_burgundy',
    'k_francia', 'k_aquitaine', 'k_east_francia', 'k_west_francia'
  ]);

  const HORIZON_2_EMPIRES = new Set(['e_britannia', 'e_carpathia']);
  const HORIZON_2_KINGDOMS = new Set([
    'k_england', 'k_bohemia', 'k_poland', 'k_denmark', 'k_croatia',
    'k_sicily', 'k_hungary', 'k_aragon', 'k_navarra', 'k_castille', 'k_valencia'
  ]);

  const HORIZON_3_EMPIRES = new Set([
    'e_scandinavia', 'e_russia', 'e_west_slavia', 'e_wendish_empire',
    'e_anatolia', 'e_macedonia', 'e_illyria', 'e_maghreb', 'e_africa',
    'e_aegyptus', 'e_oriens'
  ]);

  function getChronologicalHorizon(key, props, tier) {
    const k = (key || '').toLowerCase();
    if (HORIZON_0_TITLES.has(k)) return 0;
    const emp = props.empire || props.e_key || '';
    const kng = props.kingdom || props.k_key || '';
    if (HORIZON_1_EMPIRES.has(emp) || HORIZON_1_KINGDOMS.has(kng)) return 1;
    if (HORIZON_2_EMPIRES.has(emp) || HORIZON_2_KINGDOMS.has(kng)) return 2;
    if (HORIZON_3_EMPIRES.has(emp)) return 3;
    return 4;
  }

  function analyzeTitle(titleKey, props = {}, tier = 'county') {
    const key = (titleKey || '').toLowerCase();

    let tarrName = '';
    let origName = '';
    let anachNote = '';
    let calque = '';
    let hanzi = '';

    if (tier === 'empire') {
      tarrName = props.e_tarr_hist || props.e_tarr_direct || props.e_tarr || props.tarr || '';
      origName = props.e_origin || props.origin || '';
      anachNote = props.e_anachronism || props.anachronism || '';
      calque = props.e_calque || props.calque || '';
      hanzi = props.e_hanzi || props.hanzi || '';
    } else if (tier === 'kingdom') {
      tarrName = props.k_tarr_hist || props.k_tarr_direct || props.k_tarr || props.tarr || '';
      origName = props.k_origin || props.origin || '';
      anachNote = props.k_anachronism || props.anachronism || '';
      calque = props.k_calque || props.calque || '';
      hanzi = props.k_hanzi || props.hanzi || '';
    } else if (tier === 'duchy') {
      tarrName = props.d_tarr_hist || props.d_tarr_direct || props.d_tarr || props.tarr || '';
      origName = props.d_origin || props.origin || '';
      anachNote = props.d_anachronism || props.anachronism || '';
      calque = props.d_calque || props.calque || '';
      hanzi = props.d_hanzi || props.hanzi || '';
    } else if (tier === 'barony') {
      tarrName = props.name || props.b_tarr || props.tarr || '';
      origName = props.b_origin || props.origin || props.name || '';
      anachNote = props.b_anachronism || props.anachronism || '';
      calque = props.b_calque || props.calque || '';
      hanzi = props.b_hanzi || props.c_hanzi || '';
    } else {
      // County tier (default)
      tarrName = props.tarr_hist || props.tarr_direct || props.c_tarr_hist || props.c_tarr_direct || props.tarr || props.c_tarr || '';
      origName = props.c_origin || props.origin || '';
      anachNote = props.c_anachronism || props.anachronism || '';
      calque = props.c_calque || props.calque || '';
      hanzi = props.c_hanzi || props.hanzi || '';
    }

    if (!hanzi && CANONICAL_SINOSPHERE_HANZI[key]) {
      hanzi = CANONICAL_SINOSPHERE_HANZI[key];
    }

    tarrName = (tarrName || key).toLowerCase();
    origName = (origName || '').toLowerCase();
    anachNote = (anachNote || '').toLowerCase();

    const combinedText = [
      key,
      tarrName,
      origName,
      anachNote,
      calque
    ].join(' ');

    const h = hashString(key || tarrName);

    // 1. Detect High Historical / Canonical Titles First
    if (key === 'h_roman_empire' || key === 'e_hre') {
      return {
        medium: 'vexillum',
        field: 'gules',
        ordinary: 'solid',
        charges: ['eagle_double', 'crown'],
        chargeCount: 1,
        chargeColor: PALETTE.sable,
        blazonTarr: 'In Keiser-Rôt ein gekrônter doppelter Adler van Swartz mit guldenen Nimben und SPQR-Schilt',
        blazonEn: 'Gules, a double-headed eagle Sable crowned and nimbed Or bearing an inescutcheon Argent inscribed SPQR',
        legend: '+ SENATVS • POPVLVSQVE • ROMANVS •',
        source: 'Imperial Restored Hegemony (COA 56131)'
      };
    }

    if (key === 'c_roma' || key === 'd_latium' || key === 'k_romagna' || key === 'k_papal_state') {
      return {
        medium: tier === 'county' ? 'bulla_seal' : 'vesica_seal',
        field: 'gules',
        ordinary: 'solid',
        charges: ['keys_st_peter'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Keiser-Rôt zwên gekrützte Slüttele van Zant Peter van Golt und Silber',
        blazonEn: 'Gules, two keys in saltire of St. Peter Or and Argent',
        legend: '+ SIGILLVM • VRBIS • ROMAE • CAPVT • MVNDI',
        source: 'Patrimonium Sancti Petri (COA 6)'
      };
    }

    if (key === 'c_tarragona' || key === 'c_barcelona' || key === 'd_barcelona') {
      const isWavy = key.includes('tarragona');
      return {
        medium: tier === 'county' ? 'bulla_seal' : 'notitia_scutum',
        field: 'or',
        ordinary: isWavy ? 'pales_undy' : 'pales',
        charges: [],
        chargeCount: 0,
        chargeColor: PALETTE.gules,
        blazonTarr: isWavy ? 'In Golt vîr wâgende Pâle van Keiser-Rôt' : 'In Golt vîr Pâle van Keiser-Rôt',
        blazonEn: isWavy ? 'Or, four pales undy Gules' : 'Or, four pales Gules',
        legend: isWavy ? '+ S. MAGISTRATVS • TARRACONENSIS •' : '+ S. MAGISTRATVS • BARCINONENSIS •',
        source: isWavy ? 'Historical Attestation (COA 1205)' : 'Historical Attestation (COA 1198)'
      };
    }

    if (key === 'c_metz' || key === 'd_upper_lorraine' || key === 'k_lotharingia') {
      const isMetz = key === 'c_metz';
      return {
        medium: tier === 'county' ? 'bulla_seal' : (tier === 'duchy' ? 'notitia_scutum' : 'gonfanon'),
        field: isMetz ? 'per_pale' : 'or',
        ordinary: isMetz ? 'per_pale' : 'bend',
        charges: isMetz ? [] : ['alerion'],
        chargeCount: isMetz ? 0 : 3,
        chargeColor: isMetz ? PALETTE.argent : PALETTE.argent,
        blazonTarr: isMetz ? 'Gespalten van Silber und Swartz' : 'In Golt ein rôter Schrägbalken belegt mit drîn silbern Alerions',
        blazonEn: isMetz ? 'Party per pale Argent and Sable' : 'Or, on a bend Gules three alerions Argent',
        legend: isMetz ? '+ S. MAGISTRATVS • METENSIS •' : '+ S. DVCATVS • LOTHORINGIAE •',
        source: isMetz ? 'Historical Civic Arms (COA 286)' : 'House Kestenholz Origin (COA 281)'
      };
    }

    if (key === 'c_lviv' || tarrName.includes('swenigorot') || anachNote.includes('zvenyhorod')) {
      return {
        medium: 'bulla_seal',
        field: 'azure',
        ordinary: 'solid',
        charges: ['castrum', 'bell'],
        chargeCount: 2,
        chargeColor: PALETTE.argent,
        blazonTarr: 'In Lâsûr ein silbern Burch mit drîn Türmen unter einer goldenen Glocke',
        blazonEn: 'Azure, a triple-towered castrum Argent beneath a bell Or',
        legend: '+ S. MAGISTRATVS • SWENIGOROTENSIS •',
        source: 'Procedure 2 Resolution (10th-c. Zvenyhorod)'
      };
    }

    if (key === 'c_szekesfehervar' || tarrName.includes('stûlwîtzenburch')) {
      return {
        medium: 'bulla_seal',
        field: 'gules',
        ordinary: 'solid',
        charges: ['castrum', 'crown'],
        chargeCount: 2,
        chargeColor: PALETTE.argent,
        blazonTarr: 'In Keiser-Rôt ein wîtze dreitürmige Burch, darüber ein kûninclicher Stûl van Golt',
        blazonEn: 'Gules, a triple-towered castrum Argent surmounted by a royal throne Or',
        legend: '+ S. MAGISTRATVS • ALBAEREGALENSIS •',
        source: 'Procedure 2 Resolution (Stûlwîtzenburch)'
      };
    }

    if (key === 'c_byzantion' || key === 'e_byzantium' || tarrName.includes('konstantinôpel') || tarrName.includes('bîsantz')) {
      return {
        medium: tier === 'empire' ? 'vexillum' : 'notitia_scutum',
        field: 'gules',
        ordinary: 'cross_byzantine',
        charges: ['cross_byzantine'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Keiser-Rôt ein gulden Krütz begleitet van vîr Füristeinen',
        blazonEn: 'Gules, a cross between four firesteels Or',
        legend: '+ BASILEIA • ROMAION • CONSTANTINOPOLIS •',
        source: 'Historical Attestation (COA 442)'
      };
    }

    // 2. Procedure 1: Sinospheric Titles (Hanzi Preserved)
    if (hanzi || key.startsWith('c_chi_') || key.startsWith('c_jap_') || props.c_hanzi || CANONICAL_SINOSPHERE_HANZI[key]) {
      if (!hanzi && CANONICAL_SINOSPHERE_HANZI[key]) {
        hanzi = CANONICAL_SINOSPHERE_HANZI[key];
      }
      const charStr = hanzi ? (hanzi.length <= 2 ? hanzi : hanzi.substring(0, 2)) : '城';
      let calqueCharge = 'mount_triple';
      let fieldColor = 'vermilion';

      // Detect Azure / Hydronymic Sinosphere titles
      if (TINCTURE_PATTERNS.azure.test(combinedText) || tarrName.includes('flutz') || tarrName.includes('wazzer') || origName.includes('he') || origName.includes('jiang')) {
        calqueCharge = 'waves';
        fieldColor = 'azure';
      } else if (TINCTURE_PATTERNS.vert.test(combinedText) || origName.includes('zhu') || tarrName.includes('bambûs')) {
        calqueCharge = 'tree_chestnut';
        fieldColor = 'vert';
      } else if (tarrName.includes('drak') || origName.includes('long')) {
        calqueCharge = 'dragon';
      } else if (tarrName.includes('tor') || tarrName.includes('port') || origName.includes('men') || origName.includes('guan')) {
        calqueCharge = 'roman_gate';
      } else if (tarrName.includes('burch') || origName.includes('cheng') || origName.includes('zhou')) {
        calqueCharge = 'castrum';
      }

      const fieldTinc = TINCTURES[fieldColor] || TINCTURES.vermilion;
      const chargeMeta = CHARGE_BLAZONS[calqueCharge] || { tarrNoun: 'golden Emblem', enNoun: 'emblem', enArticle: 'an' };

      let sinoMedium = 'sinosphere_chop';
      if (tier === 'empire') sinoMedium = 'vexillum';
      else if (tier === 'kingdom') sinoMedium = 'gonfanon';
      else if (tier === 'duchy') sinoMedium = 'notitia_scutum';
      else if (tier === 'county') sinoMedium = 'sinosphere_chop';
      else if (tier === 'barony') sinoMedium = 'civic_badge';

      return {
        medium: sinoMedium,
        field: fieldColor,
        ordinary: 'solid',
        charges: [calqueCharge],
        chargeCount: 1,
        hanzi: hanzi || '州',
        hanziChar: charStr,
        chargeColor: PALETTE.or,
        blazonTarr: `In ${fieldTinc.tarr} das Siegel-Schriftzeichen ${charStr} begleitet van einem goldenen ${chargeMeta.tarrNoun}`,
        blazonEn: `${fieldTinc.en}, the seal-script glyph ${charStr} accompanied by ${chargeMeta.enArticle ? chargeMeta.enArticle + ' ' : ''}${chargeMeta.enNoun} Or`,
        legend: `${(props.tarr_hist || props.tarr || tarrName || key).toUpperCase()} • ${charStr}之印`,
        source: 'Procedure 1 Sinosphere Continuity Protocol'
      };
    }

    // 3. Authentic Canonical In-Save Heraldry Database
    if (typeof CANONICAL_HERALDRY !== 'undefined' && CANONICAL_HERALDRY[key]) {
      const [cField, cOrd, cCharge, cChargeColor, cCount, cOrdColor] = CANONICAL_HERALDRY[key];
      const fieldKey = cField || 'gules';
      const ordKey = cOrd || 'solid';
      const chargeKey = cCharge || 'castrum';
      const chargeColorHex = PALETTE[cChargeColor] || PALETTE.or;
      const ordColorHex = PALETTE[cOrdColor] || PALETTE.argent;
      const count = cCount || 1;

      let chosenMedium = 'bulla_seal';
      if (tier === 'empire') chosenMedium = 'vexillum';
      else if (tier === 'kingdom') chosenMedium = 'gonfanon';
      else if (tier === 'duchy') chosenMedium = 'notitia_scutum';
      else if (tier === 'county') chosenMedium = 'bulla_seal';
      else if (tier === 'barony') chosenMedium = 'civic_badge';

      const blazon = formatBlazon(fieldKey, chargeKey, chargeColorHex, ordKey, count, ordColorHex);

      const latinized = (props.tarr_hist || props.tarr || key)
        .replace(/^[a-z]_/, '')
        .replace(/[^a-zA-Z]/g, '')
        .toUpperCase();

      return {
        medium: chosenMedium,
        field: fieldKey,
        ordinary: ordKey,
        ordinaryColor: cOrdColor || (fieldKey === 'or' ? 'gules' : 'azure'),
        charges: Array(count).fill(chargeKey),
        chargeCount: count,
        chargeColor: chargeColorHex,
        blazonTarr: blazon.blazonTarr,
        blazonEn: blazon.blazonEn,
        legend: `+ S. MAGISTRATVS • ${latinized}ENSIS •`,
        source: 'Historical Attestation (In-Save COA)'
      };
    }

    // 4. Canting Morpheme Toponymic Derivation Engine
    const horizon = getChronologicalHorizon(key, props, tier);

    let detectedField = 'gules';
    let detectedCharge = 'castrum';
    let detectedOrdinary = 'solid';
    let chargeCount = 1;

    // Color detection across multilingual stems
    if (TINCTURE_PATTERNS.argent.test(combinedText)) {
      detectedField = 'argent';
    } else if (TINCTURE_PATTERNS.gules.test(combinedText)) {
      detectedField = 'gules';
    } else if (TINCTURE_PATTERNS.sable.test(combinedText)) {
      detectedField = 'sable';
    } else if (TINCTURE_PATTERNS.or.test(combinedText)) {
      detectedField = 'or';
    } else if (TINCTURE_PATTERNS.vert.test(combinedText)) {
      detectedField = 'vert';
    } else if (TINCTURE_PATTERNS.azure.test(combinedText)) {
      detectedField = 'azure';
    } else {
      // Deterministic field pick based on region / hash
      const fields = ['gules', 'azure', 'or', 'argent', 'vert', 'sable'];
      detectedField = fields[h % fields.length];
    }

    // Ordinary / Partition selection based on Chronological Horizon & Tier
    // Titles that became administrative earlier (Horizon 0 & 1) get simpler designs (predominantly solid field).
    // Titles integrated later (Horizon 2, 3, 4) get geometric ordinaries, partitions, and bordures.
    if (horizon <= 1) {
      const earlyOrdinaries = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'fess', 'pale', 'per_pale', 'per_fess'];
      detectedOrdinary = earlyOrdinaries[(h >> 2) % earlyOrdinaries.length];
    } else if (horizon === 2) {
      const midOrdinaries = ['solid', 'solid', 'fess', 'pale', 'bend', 'chevron', 'cross', 'per_bend', 'per_fess', 'barry'];
      detectedOrdinary = midOrdinaries[(h >> 2) % midOrdinaries.length];
    } else if (horizon === 3) {
      const lateOrdinaries = ['solid', 'fess', 'bend', 'bend_sinister', 'chevron', 'cross', 'saltire', 'quarterly', 'per_saltire', 'chief', 'bordure', 'barry'];
      detectedOrdinary = lateOrdinaries[(h >> 2) % lateOrdinaries.length];
    } else {
      const frontierOrdinaries = ['fess', 'bend', 'chevron', 'cross', 'saltire', 'quarterly', 'per_saltire', 'chequy', 'bordure', 'chief', 'barry', 'solid'];
      detectedOrdinary = frontierOrdinaries[(h >> 2) % frontierOrdinaries.length];
    }

    // Baronies cadency differencing: use bordure or solid to avoid collision with superior duchy/county
    if (tier === 'barony' && (detectedOrdinary === 'cross' || detectedOrdinary === 'saltire' || detectedOrdinary === 'quarterly') && (h % 3 === 0)) {
      detectedOrdinary = 'bordure';
    }

    // Architectural, natural, and expanded toponymic charges
    if (tarrName.includes('burch') || tarrName.includes('kastel') || tarrName.includes('wâr') || tarrName.includes('grad') || origName.includes('burg') || origName.includes('castr')) {
      detectedCharge = 'castrum';
    } else if (tarrName.includes('stat') || tarrName.includes('polis') || origName.includes('gorod') || origName.includes('ville') || origName.includes('civitas')) {
      detectedCharge = 'roman_gate';
    } else if (tarrName.includes('berch') || tarrName.includes('stein') || tarrName.includes('vêls') || tarrName.includes('gôre') || origName.includes('mont') || origName.includes('hegy') || origName.includes('gora')) {
      detectedCharge = 'mount_triple';
    } else if (tarrName.includes('brücke') || origName.includes('bridge') || origName.includes('puente') || origName.includes('ponte')) {
      detectedCharge = 'bridge';
    } else if (tarrName.includes('vort') || tarrName.includes('flutz') || tarrName.includes('flôz') || tarrName.includes('wazzer') || tarrName.includes('münde') || tarrName.includes('sê') || origName.includes('ford') || origName.includes('water')) {
      detectedCharge = 'waves';
    } else if (tarrName.includes('kîrch') || tarrName.includes('münster') || tarrName.includes('dom') || tarrName.startsWith('zant-') || origName.startsWith('st-') || origName.startsWith('saint')) {
      detectedCharge = 'cross_patriarchal';
    } else if (tarrName.includes('wald') || tarrName.includes('holt') || tarrName.includes('holz') || origName.includes('wood') || origName.includes('forest')) {
      detectedCharge = 'tree_chestnut';
    } else if (tarrName.includes('hâven') || tarrName.includes('port') || tarrName.includes('insel') || origName.includes('havn') || origName.includes('sea') || origName.includes('island')) {
      detectedCharge = 'ship';
    } else if (tarrName.includes('lôwe') || origName.includes('lion') || origName.includes('león')) {
      detectedCharge = 'lion_rampant';
    } else if (tarrName.includes('swert') || tarrName.includes('klinge') || origName.includes('sword') || origName.includes('blade')) {
      detectedCharge = 'sword_crossed';
    } else if (tarrName.includes('rôse') || tarrName.includes('rosen') || origName.includes('rose')) {
      detectedCharge = 'rose_seeded';
    } else if (tarrName.includes('rad') || tarrName.includes('rade') || origName.includes('wheel') || origName.includes('rad')) {
      detectedCharge = 'wheel_spoked';
    } else if (tarrName.includes('hirz') || tarrName.includes('hart') || origName.includes('stag') || origName.includes('hart') || origName.includes('cervo')) {
      detectedCharge = 'stag_attired';
    } else if (tarrName.includes('bêr') || tarrName.includes('bern') || origName.includes('bear') || origName.includes('orso') || origName.includes('medved')) {
      detectedCharge = 'bear_rampant';
    } else if (tarrName.includes('ros') || tarrName.includes('pfert') || origName.includes('horse') || origName.includes('cheval') || origName.includes('cavallo')) {
      detectedCharge = 'horse_courant';
    } else if (tarrName.includes('stern') || origName.includes('star') || origName.includes('stella')) {
      detectedCharge = 'star_six_pointed';
    } else if (tarrName.includes('sunne') || origName.includes('sun') || origName.includes('sole')) {
      detectedCharge = 'sun_radiant';
    } else if (tarrName.includes('mâne') || origName.includes('moon') || origName.includes('lune')) {
      detectedCharge = 'crescent_moon';
    } else if (tarrName.includes('korn') || tarrName.includes('weiz') || origName.includes('wheat') || origName.includes('grain')) {
      detectedCharge = 'wheatsheaf_garb';
    } else if (tarrName.includes('lilje') || origName.includes('lily') || origName.includes('lis')) {
      detectedCharge = 'fleur_de_lis';
    } else if (tarrName.includes('eik') || tarrName.includes('eich') || origName.includes('oak') || origName.includes('quercia')) {
      detectedCharge = 'oak_branch';
    } else if (tarrName.includes('wîn') || tarrName.includes('rebe') || tarrName.includes('trûbe') || origName.includes('wine') || origName.includes('grape')) {
      detectedCharge = 'grape_cluster';
    } else if (tarrName.includes('anker') || origName.includes('anchor') || origName.includes('ancora')) {
      detectedCharge = 'anchor';
    } else if (tarrName.includes('bîle') || tarrName.includes('axt') || origName.includes('axe') || origName.includes('hache')) {
      detectedCharge = 'battleaxe';
    } else if (tarrName.includes('visch') || origName.includes('fish') || origName.includes('poisson') || origName.includes('pesce')) {
      detectedCharge = 'fish_twin';
    } else if (tarrName.includes('valke') || origName.includes('falcon') || origName.includes('faucon')) {
      detectedCharge = 'falcon_perched';
    } else {
      // Tier-aware expanded charge pool fallback
      if (tier === 'empire') {
        const empirePool = ['eagle_double', 'crown', 'lion_rampant', 'sun_radiant', 'sword_crossed', 'fleur_de_lis', 'dragon'];
        detectedCharge = empirePool[(h >> 4) % empirePool.length];
      } else if (tier === 'kingdom') {
        const kingdomPool = ['crown', 'lion_rampant', 'sword_crossed', 'fleur_de_lis', 'horse_courant', 'bear_rampant', 'stag_attired', 'sun_radiant', 'battleaxe', 'ship'];
        detectedCharge = kingdomPool[(h >> 4) % kingdomPool.length];
      } else if (tier === 'barony') {
        const baronyPool = ['wheel_spoked', 'wheatsheaf_garb', 'rose_seeded', 'star_six_pointed', 'oak_branch', 'anchor', 'fish_twin', 'roman_gate', 'castrum', 'grape_cluster'];
        detectedCharge = baronyPool[(h >> 4) % baronyPool.length];
      } else {
        const generalPool = [
          'castrum', 'roman_gate', 'mount_triple', 'ship', 'tree_chestnut',
          'lion_rampant', 'waves', 'crown', 'sword_crossed', 'battleaxe',
          'stag_attired', 'wolf_statant', 'bear_rampant', 'horse_courant',
          'falcon_perched', 'fish_twin', 'rose_seeded', 'fleur_de_lis',
          'wheatsheaf_garb', 'oak_branch', 'sun_radiant', 'star_six_pointed',
          'crescent_moon', 'wheel_spoked', 'anchor'
        ];
        detectedCharge = generalPool[(h >> 4) % generalPool.length];
      }
    }

    // Multi-Charge Disambiguation:
    // Earlier chronological horizons (Horizon 0 and 1) have preference for simpler designs (count = 1).
    // Later horizons and newly integrated marches feature 2 or 3 charges.
    if (horizon <= 1 || tier === 'empire') {
      chargeCount = 1;
    } else if (horizon === 2) {
      chargeCount = (h % 4 !== 0) ? 1 : 2;
    } else if (horizon === 3) {
      const counts3 = [1, 2, 3, 1, 3];
      chargeCount = counts3[(h >> 5) % counts3.length];
    } else {
      const counts4 = [1, 2, 3, 3, 2, 3];
      chargeCount = counts4[(h >> 5) % counts4.length];
    }

    // Certain architectural or large solitary charges look best single
    if (detectedCharge === 'castrum' || detectedCharge === 'roman_gate' || detectedCharge === 'bridge' || detectedCharge === 'sun_radiant' || detectedCharge === 'eagle_double') {
      chargeCount = 1;
    }

    // Select suitable contrast charge color
    const chargeColor = (detectedField === 'argent' || detectedField === 'or') ? PALETTE.sable : PALETTE.argent;
    const ordinaryColorHex = (detectedField === 'argent' || detectedField === 'or') ? (detectedField === 'or' ? PALETTE.gules : PALETTE.azure) : PALETTE.argent;
    const ordinaryColor = (detectedField === 'argent' || detectedField === 'or') ? (detectedField === 'or' ? 'gules' : 'azure') : 'argent';

    // Physical medium based on de jure tier
    let chosenMedium = 'bulla_seal';
    if (tier === 'empire') chosenMedium = 'vexillum';
    else if (tier === 'kingdom') chosenMedium = 'gonfanon';
    else if (tier === 'duchy') chosenMedium = 'notitia_scutum';
    else if (tier === 'county') chosenMedium = 'bulla_seal';
    else if (tier === 'barony') chosenMedium = 'civic_badge';

    const latinized = (props.tarr_hist || props.tarr || key)
      .replace(/^[a-z]_/, '')
      .replace(/[^a-zA-Z]/g, '')
      .toUpperCase();

    const blazon = formatBlazon(detectedField, detectedCharge, chargeColor, detectedOrdinary, chargeCount, ordinaryColorHex);

    return {
      medium: chosenMedium,
      field: detectedField,
      ordinary: detectedOrdinary,
      ordinaryColor: ordinaryColor,
      charges: Array(chargeCount).fill(detectedCharge),
      chargeCount: chargeCount,
      chargeColor: chargeColor,
      blazonTarr: blazon.blazonTarr,
      blazonEn: blazon.blazonEn,
      legend: `+ S. MAGISTRATVS • ${latinized}ENSIS •`,
      source: 'Chancellery Toponymic & Morpheme Calque'
    };
  }

  // =========================================================================
  // 4. SVG Medium Frame Renderers & Unique ID Generator
  // =========================================================================

  let symbolUidCounter = 0;
  function getUniqueId(prefix = 'sym') {
    symbolUidCounter += 1;
    return `${prefix}_${symbolUidCounter}_${Math.random().toString(36).substring(2, 7)}`;
  }

  function renderField(def, width, height, clipId) {
    const fColor = PALETTE[def.field] || PALETTE.gules;
    const fColor2 = PALETTE[def.ordinaryColor] || (def.field === 'argent' || def.field === 'or' ? PALETTE.gules : PALETTE.argent);
    const clipAttr = clipId ? `clip-path="url(#${clipId})"` : '';
    const ord = def.ordinary || 'solid';

    if (ord === 'pales' || ord === 'pales_undy') {
      const isUndy = ord === 'pales_undy';
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${PALETTE.or}" />
          ${[0, 1, 2, 3].map(i => {
            const x = (width / 8) * (2 * i + 1);
            const w = width / 8;
            if (isUndy) {
              return `<path d="M ${x} 0 Q ${x - 8} ${height * 0.25} ${x} ${height * 0.5} Q ${x + 8} ${height * 0.75} ${x} ${height} L ${x + w} ${height} Q ${x + w + 8} ${height * 0.75} ${x + w} ${height * 0.5} Q ${x + w - 8} ${height * 0.25} ${x + w} 0 Z" fill="${PALETTE.gules}" />`;
            }
            return `<rect x="${x}" y="0" width="${w}" height="${height}" fill="${PALETTE.gules}" />`;
          }).join('')}
        </g>
      `;
    }

    if (ord === 'per_pale') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width / 2}" height="${height}" fill="${fColor}" />
          <rect x="${width / 2}" y="0" width="${width / 2}" height="${height}" fill="${fColor2}" />
        </g>
      `;
    }

    if (ord === 'per_fess') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height / 2}" fill="${fColor}" />
          <rect x="0" y="${height / 2}" width="${width}" height="${height / 2}" fill="${fColor2}" />
        </g>
      `;
    }

    if (ord === 'per_bend') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <polygon points="0,0 ${width},${height} 0,${height}" fill="${fColor2}" />
        </g>
      `;
    }

    if (ord === 'per_bend_sinister') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <polygon points="${width},0 ${width},${height} 0,${height}" fill="${fColor2}" />
        </g>
      `;
    }

    if (ord === 'quarterly') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <rect x="${width / 2}" y="0" width="${width / 2}" height="${height / 2}" fill="${fColor2}" />
          <rect x="0" y="${height / 2}" width="${width / 2}" height="${height / 2}" fill="${fColor2}" />
        </g>
      `;
    }

    if (ord === 'per_saltire') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <polygon points="0,0 ${width / 2},${height / 2} 0,${height}" fill="${fColor2}" />
          <polygon points="${width},0 ${width / 2},${height / 2} ${width},${height}" fill="${fColor2}" />
        </g>
      `;
    }

    if (ord === 'fess') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <rect x="0" y="${height * 0.35}" width="${width}" height="${height * 0.30}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'pale') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <rect x="${width * 0.35}" y="0" width="${width * 0.30}" height="${height}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'bend') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <polygon points="0,0 ${width * 0.35},0 ${width},${height * 0.65} ${width},${height} ${width * 0.65},${height} 0,${height * 0.35}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'bend_sinister') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <polygon points="${width},0 ${width * 0.65},0 0,${height * 0.65} 0,${height} ${width * 0.35},${height} ${width},${height * 0.35}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'chevron') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <polygon points="0,${height * 0.8} ${width / 2},${height * 0.32} ${width},${height * 0.8} ${width},${height * 0.6} ${width / 2},${height * 0.12} 0,${height * 0.6}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'cross') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <rect x="0" y="${height * 0.38}" width="${width}" height="${height * 0.24}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
          <rect x="${width * 0.38}" y="0" width="${width * 0.24}" height="${height}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'saltire') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <polygon points="0,0 ${width * 0.20},0 ${width},${height * 0.80} ${width},${height} ${width * 0.80},${height} 0,${height * 0.20}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
          <polygon points="${width},0 ${width * 0.80},0 0,${height * 0.80} 0,${height} ${width * 0.20},${height} ${width},${height * 0.20}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'chief') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <rect x="0" y="0" width="${width}" height="${height * 0.30}" fill="${fColor2}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'bordure') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor2}" />
          <rect x="${width * 0.12}" y="${height * 0.12}" width="${width * 0.76}" height="${height * 0.76}" fill="${fColor}" stroke="${PALETTE.sable}" stroke-width="1.2" />
        </g>
      `;
    }

    if (ord === 'barry') {
      return `
        <g ${clipAttr}>
          ${[0, 1, 2, 3, 4, 5].map(i => `<rect x="0" y="${(i * height) / 6}" width="${width}" height="${height / 6 + 0.5}" fill="${i % 2 === 0 ? fColor : fColor2}" />`).join('')}
        </g>
      `;
    }

    if (ord === 'chequy') {
      return `
        <g ${clipAttr}>
          ${Array.from({ length: 16 }).map((_, i) => {
            const row = Math.floor(i / 4), col = i % 4;
            return `<rect x="${(col * width) / 4}" y="${(row * height) / 4}" width="${width / 4 + 0.5}" height="${height / 4 + 0.5}" fill="${(row + col) % 2 === 0 ? fColor : fColor2}" />`;
          }).join('')}
        </g>
      `;
    }

    return `<rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" ${clipAttr} />`;
  }

  function renderMultiCharges(def, cx, cy, baseScale) {
    if (!def.charges || def.charges.length === 0) return '';
    const color = def.chargeColor || PALETTE.or;
    const count = def.chargeCount || def.charges.length || 1;

    // Handle composite charges (e.g. Székesfehérvár or Lviv)
    if (def.charges.length > 1 && def.charges[0] !== def.charges[1]) {
      const sc1 = baseScale * 0.60;
      const sc2 = baseScale * 0.48;
      const c1 = def.charges[0];
      const c2 = def.charges[1];
      return `
        ${CHARGES[c1] ? CHARGES[c1](color, sc1, cx, cy + 14) : ''}
        ${CHARGES[c2] ? CHARGES[c2](color, sc2, cx, cy - 28) : ''}
      `;
    }

    const c = def.charges[0];
    const builder = CHARGES[c];
    if (!builder) return '';

    if (count === 2) {
      const dy = Math.round(baseScale * 38);
      const sc = baseScale * 0.62;
      return `
        ${builder(color, sc, cx, cy - dy)}
        ${builder(color, sc, cx, cy + dy)}
      `;
    } else if (count >= 3) {
      const dx = Math.round(baseScale * 38);
      const dy = Math.round(baseScale * 25);
      const sc = baseScale * 0.50;
      return `
        ${builder(color, sc, cx - dx, cy - dy)}
        ${builder(color, sc, cx + dx, cy - dy)}
        ${builder(color, sc, cx, cy + Math.round(dy * 1.15))}
      `;
    }

    return builder(color, baseScale, cx, cy);
  }

  // --- A. Imperial Vexillum (Empire Tier) ---
  function renderVexillum(def) {
    const W = 220, H = 270;
    const bannerX = 35, bannerY = 42, bannerW = 150, bannerH = 185;
    const uid = getUniqueId('vex');
    const fColor = PALETTE[def.field] || PALETTE.gules;
    const hanziText = def.hanziChar || (def.hanzi ? (def.hanzi.length <= 2 ? def.hanzi : def.hanzi.substring(0, 2)) : '');
    const hanziColor = (def.field === 'or' || def.field === 'argent') ? PALETTE.sable : (def.chargeColor || PALETTE.or);
    const hanziStroke = hanziColor === PALETTE.sable ? 'none' : PALETTE.sable;

    return `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" class="tarr-symbol-svg" aria-label="${def.blazonEn}">
        <defs>
          <clipPath id="${uid}_clip">
            <rect x="${bannerX}" y="${bannerY}" width="${bannerW}" height="${bannerH}" rx="2" />
          </clipPath>
        </defs>

        <!-- Hanging Cords & Tassels -->
        <path d="M 40 40 Q 110 5 180 40" fill="none" stroke="${PALETTE.brass}" stroke-width="3" stroke-linecap="round" />
        <circle cx="110" cy="18" r="6" fill="${PALETTE.or}" stroke="${PALETTE.sable}" stroke-width="1.5" />
        <line x1="30" y1="42" x2="25" y2="90" stroke="${PALETTE.brass}" stroke-width="2" />
        <circle cx="25" cy="93" r="4" fill="${PALETTE.or}" />
        <line x1="190" y1="42" x2="195" y2="90" stroke="${PALETTE.brass}" stroke-width="2" />
        <circle cx="195" cy="93" r="4" fill="${PALETTE.or}" />

        <!-- Banner Cloth Drop Shadow -->
        <rect x="${bannerX + 2}" y="${bannerY + 4}" width="${bannerW}" height="${bannerH + 12}" rx="3" fill="rgba(0,0,0,0.3)" />

        <!-- Banner Cloth Body -->
        <g>
          <!-- Base Field Color Rect -->
          <rect x="${bannerX}" y="${bannerY}" width="${bannerW}" height="${bannerH}" fill="${fColor}" stroke="${PALETTE.sable}" stroke-width="1.5" rx="2" />

          <!-- Clipped Field Ordinaries & Charges / Hanzi -->
          <g clip-path="url(#${uid}_clip)">
            ${renderField(def, W, H)}
            <!-- Inner Gold Border -->
            <rect x="${bannerX + 5}" y="${bannerY + 5}" width="${bannerW - 10}" height="${bannerH - 10}" fill="none" stroke="${PALETTE.or}" stroke-width="2.5" />
            <!-- Charges / Hanzi -->
            ${hanziText ? `
              <!-- Classical Sinitic Hanzi Logograph on Imperial Vexillum -->
              <text x="110" y="${def.charges.length > 0 ? 102 : 135}" text-anchor="middle" dominant-baseline="central" fill="${hanziColor}" stroke="${hanziStroke}" stroke-width="1.2" font-family="'Songti SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif" font-size="${hanziText.length > 1 ? (def.charges.length > 0 ? 36 : 46) : (def.charges.length > 0 ? 50 : 64)}" font-weight="900" letter-spacing="${hanziText.length > 1 ? '4' : '0'}">
                ${hanziText}
              </text>
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.55, 110, 166) : '').join('')}
            ` : `
              <!-- Standard Charges -->
              ${def.chargeCount > 1 ? renderMultiCharges(def, 110, 135, 0.82) : def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.82, 110, 135) : '').join('')}
            `}
          </g>

          <!-- Bottom Gold Fringe -->
          <g fill="${PALETTE.or}" stroke="${PALETTE.sable}" stroke-width="0.8">
            ${Array.from({ length: 15 }).map((_, i) => `
              <rect x="${bannerX + i * 10}" y="${bannerY + bannerH}" width="10" height="14" />
              <line x1="${bannerX + i * 10 + 5}" y1="${bannerY + bannerH}" x2="${bannerX + i * 10 + 5}" y2="${bannerY + bannerH + 12}" stroke="${PALETTE.brass}" stroke-width="1" />
            `).join('')}
          </g>
        </g>

        <!-- Golden Crossbar & Finials -->
        <rect x="20" y="38" width="180" height="8" rx="2" fill="${PALETTE.brass}" stroke="${PALETTE.sable}" stroke-width="1.5" />
        <circle cx="20" cy="42" r="7" fill="${PALETTE.or}" stroke="${PALETTE.sable}" stroke-width="1.5" />
        <circle cx="200" cy="42" r="7" fill="${PALETTE.or}" stroke="${PALETTE.sable}" stroke-width="1.5" />
      </svg>
    `;
  }

  // --- B. Three-Tailed Gonfanon (Kingdom Tier) ---
  function renderGonfanon(def) {
    const W = 220, H = 270;
    const gonfanonPath = "M 35 45 L 185 45 L 185 165 L 155 165 L 135 240 L 115 165 L 85 240 L 65 165 L 35 165 Z";
    const uid = getUniqueId('gonf');
    const fColor = PALETTE[def.field] || PALETTE.gules;
    const hanziText = def.hanziChar || (def.hanzi ? (def.hanzi.length <= 2 ? def.hanzi : def.hanzi.substring(0, 2)) : '');
    const hanziColor = (def.field === 'or' || def.field === 'argent') ? PALETTE.sable : (def.chargeColor || PALETTE.or);
    const hanziStroke = hanziColor === PALETTE.sable ? 'none' : PALETTE.sable;

    return `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" class="tarr-symbol-svg" aria-label="${def.blazonEn}">
        <defs>
          <clipPath id="${uid}_clip">
            <path d="${gonfanonPath}" />
          </clipPath>
        </defs>

        <!-- Lance Spearhead & Crossbar -->
        <line x1="15" y1="40" x2="205" y2="40" stroke="${PALETTE.wood}" stroke-width="8" stroke-linecap="round" />
        <line x1="15" y1="40" x2="205" y2="40" stroke="${PALETTE.sable}" stroke-width="1.5" />
        <!-- Spearhead Finial Left -->
        <polygon points="12,40 2,34 6,40 2,46" fill="${PALETTE.argent}" stroke="${PALETTE.sable}" stroke-width="1.2" />

        <!-- Banner Body Drop Shadow -->
        <path d="${gonfanonPath}" transform="translate(0, 4)" fill="rgba(0,0,0,0.25)" />

        <!-- Banner Body with 3 Tongues -->
        <g>
          <path d="${gonfanonPath}" fill="${fColor}" stroke="${PALETTE.sable}" stroke-width="2" />
          <g clip-path="url(#${uid}_clip)">
            ${renderField(def, W, H)}
            <!-- Decorative Border Piping -->
            <path d="M 40 50 L 180 50 L 180 160 L 152 160 L 135 228 L 118 160 L 82 228 L 65 160 L 40 160 Z" fill="none" stroke="${PALETTE.or}" stroke-width="2.5" opacity="0.9" />
            <!-- Charges / Hanzi placed in the upper square -->
            ${hanziText ? `
              <!-- Sinitic Hanzi Logograph on Kingdom Gonfanon -->
              <text x="110" y="${def.charges.length > 0 ? 86 : 105}" text-anchor="middle" dominant-baseline="central" fill="${hanziColor}" stroke="${hanziStroke}" stroke-width="1.2" font-family="'Songti SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif" font-size="${hanziText.length > 1 ? (def.charges.length > 0 ? 30 : 40) : (def.charges.length > 0 ? 42 : 54)}" font-weight="900" letter-spacing="${hanziText.length > 1 ? '3' : '0'}">
                ${hanziText}
              </text>
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.46, 110, 134) : '').join('')}
            ` : `
              <!-- Standard Charges -->
              ${def.chargeCount > 1 ? renderMultiCharges(def, 110, 105, 0.72) : def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.72, 110, 105) : '').join('')}
            `}
          </g>
        </g>
      </svg>
    `;
  }

  // --- C. Late-Roman Notitia Command Shield (Duchy Tier) ---
  function renderNotitiaScutum(def) {
    const W = 220, H = 250;
    const cx = 110, cy = 125, rx = 82, ry = 104;
    const uid = getUniqueId('scut');
    const fColor = PALETTE[def.field] || PALETTE.gules;
    const hanziText = def.hanziChar || (def.hanzi ? (def.hanzi.length <= 2 ? def.hanzi : def.hanzi.substring(0, 2)) : '');
    const hanziColor = (def.field === 'or' || def.field === 'argent') ? PALETTE.sable : (def.chargeColor || PALETTE.or);
    const hanziStroke = hanziColor === PALETTE.sable ? 'none' : PALETTE.sable;

    return `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" class="tarr-symbol-svg" aria-label="${def.blazonEn}">
        <defs>
          <clipPath id="${uid}_clip">
            <ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" />
          </clipPath>
          <radialGradient id="${uid}_umbo" cx="40%" cy="40%" r="65%">
            <stop offset="0%" stop-color="${PALETTE.argent}" />
            <stop offset="50%" stop-color="${PALETTE.brass}" />
            <stop offset="100%" stop-color="${PALETTE.sable}" />
          </radialGradient>
        </defs>

        <!-- Drop Shadow -->
        <ellipse cx="${cx}" cy="${cy + 5}" rx="${rx + 6}" ry="${ry + 6}" fill="rgba(0,0,0,0.3)" />

        <g>
          <!-- Outer Metallic Rim -->
          <ellipse cx="${cx}" cy="${cy}" rx="${rx + 6}" ry="${ry + 6}" fill="${PALETTE.brass}" stroke="${PALETTE.sable}" stroke-width="2" />
          <!-- Shield Base Face -->
          <ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${fColor}" />
          <!-- Shield Face Clipped Ordinaries & Charges / Hanzi -->
          <g clip-path="url(#${uid}_clip)">
            ${renderField(def, W, H)}
            <!-- Radiating / Concentric Notitia Ring -->
            <ellipse cx="${cx}" cy="${cy}" rx="${rx - 12}" ry="${ry - 12}" fill="none" stroke="${PALETTE.or}" stroke-width="3" stroke-dasharray="10 6" opacity="0.8" />
            <!-- Charges / Hanzi around Boss -->
            ${hanziText ? `
              <!-- Sinitic Hanzi Logograph on Notitia Scutum above Boss -->
              <text x="${cx}" y="${def.charges.length > 0 ? 75 : 82}" text-anchor="middle" dominant-baseline="central" fill="${hanziColor}" stroke="${hanziStroke}" stroke-width="1.2" font-family="'Songti SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif" font-size="${hanziText.length > 1 ? 26 : 36}" font-weight="900" letter-spacing="${hanziText.length > 1 ? '2' : '0'}">
                ${hanziText}
              </text>
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.45, cx, cy + 50) : '').join('')}
            ` : `
              <!-- Standard Charges -->
              ${def.chargeCount > 1 ? renderMultiCharges(def, cx, cy - 25, 0.65) : def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.65, cx, cy - 25) : '').join('')}
            `}
          </g>
          <!-- Inner Rim Stitching -->
          <ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="none" stroke="${PALETTE.sable}" stroke-width="2" />
          <!-- Central Metal Umbo (Shield Boss) -->
          <circle cx="${cx}" cy="${cy}" r="22" fill="url(#${uid}_umbo)" stroke="${PALETTE.sable}" stroke-width="2" />
          <circle cx="${cx}" cy="${cy}" r="14" fill="${PALETTE.or}" stroke="${PALETTE.sable}" stroke-width="1.2" />
          <!-- Rim Studs / Rivets -->
          ${[0, 45, 90, 135, 180, 225, 270, 315].map(deg => {
            const rad = (deg * Math.PI) / 180;
            const x = cx + (rx + 3) * Math.cos(rad);
            const y = cy + (ry + 3) * Math.sin(rad);
            return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.5" fill="${PALETTE.argent}" stroke="${PALETTE.sable}" stroke-width="0.8" />`;
          }).join('')}
        </g>
      </svg>
    `;
  }

  // --- D. Circular Chancellery Bulla / Municipal Seal (County Tier) ---
  function renderBullaSeal(def) {
    const W = 240, H = 240;
    const cx = 120, cy = 120, rOuter = 104, rText = 88, rInner = 72;
    const legendText = def.legend || '+ S. MAGISTRATVS • IMPERII •';
    const uid = getUniqueId('bulla');
    const fColor = PALETTE[def.field] || PALETTE.gules;
    const hanziText = def.hanziChar || (def.hanzi ? (def.hanzi.length <= 2 ? def.hanzi : def.hanzi.substring(0, 2)) : '');

    return `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" class="tarr-symbol-svg" aria-label="${def.blazonEn}">
        <defs>
          <clipPath id="${uid}_inner_clip">
            <circle cx="${cx}" cy="${cy}" r="${rInner}" />
          </clipPath>
          <!-- Circular text path along circumference -->
          <path id="${uid}_text_path" d="M ${cx - rText} ${cy} A ${rText} ${rText} 0 1 1 ${cx + rText} ${cy} A ${rText} ${rText} 0 1 1 ${cx - rText} ${cy}" fill="none" />
        </defs>

        <!-- Drop Shadow -->
        <circle cx="${cx}" cy="${cy + 4}" r="${rOuter}" fill="rgba(0,0,0,0.25)" />

        <g>
          <!-- Outer Wax / Lead Base Flange -->
          <circle cx="${cx}" cy="${cy}" r="${rOuter}" fill="${PALETTE.gules_dark}" stroke="${PALETTE.sable}" stroke-width="2.5" />
          <!-- Beaded Ring Outer -->
          <circle cx="${cx}" cy="${cy}" r="${rOuter - 4}" fill="none" stroke="${PALETTE.or}" stroke-width="1.8" stroke-dasharray="3 3" />
          
          <!-- Epigraphic Ring Track -->
          <circle cx="${cx}" cy="${cy}" r="${rText + 6}" fill="none" stroke="${PALETTE.or}" stroke-width="1" />
          <circle cx="${cx}" cy="${cy}" r="${rInner + 4}" fill="none" stroke="${PALETTE.or}" stroke-width="1.2" />

          <!-- Circular Inscription Text -->
          <text fill="${PALETTE.or_bright}" font-family="'Cinzel', 'Trajan Pro', serif" font-size="10" font-weight="700" letter-spacing="1.5">
            <textPath href="#${uid}_text_path" startOffset="50%" text-anchor="middle">
              ${legendText}
            </textPath>
          </text>

          <!-- Inner Shield / Field Area -->
          <circle cx="${cx}" cy="${cy}" r="${rInner}" fill="${fColor}" />
          <g clip-path="url(#${uid}_inner_clip)">
            ${renderField(def, W, H)}
            <!-- Inner Beaded Ring -->
            <circle cx="${cx}" cy="${cy}" r="${rInner - 2}" fill="none" stroke="${PALETTE.or}" stroke-width="1.5" />
            <!-- Central Civic / Canting Charge / Hanzi -->
            ${hanziText ? `
              <!-- Sinitic Hanzi Logograph on Bulla Seal -->
              <text x="${cx}" y="${def.charges.length > 0 ? 98 : 120}" text-anchor="middle" dominant-baseline="central" fill="${PALETTE.or_bright}" stroke="${PALETTE.sable}" stroke-width="1.2" font-family="'Songti SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif" font-size="${hanziText.length > 1 ? (def.charges.length > 0 ? 24 : 32) : (def.charges.length > 0 ? 32 : 44)}" font-weight="900" letter-spacing="${hanziText.length > 1 ? '2' : '0'}">
                ${hanziText}
              </text>
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.42, cx, cy + 24) : '').join('')}
            ` : `
              <!-- Standard Charges -->
              ${def.chargeCount > 1 ? renderMultiCharges(def, cx, cy, 0.62) : def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.62, cx, cy) : '').join('')}
            `}
          </g>
        </g>
      </svg>
    `;
  }

  // --- E. Sinosphere Vermilion Chop / Guóxī (Procedure 1 Counties) ---
  function renderSinosphereChop(def) {
    const W = 220, H = 220;
    const boxSize = 170, boxX = 25, boxY = 25;
    const hanziText = def.hanziChar || (def.hanzi ? (def.hanzi.length <= 2 ? def.hanzi : def.hanzi.substring(0, 2)) : '州');
    const ink = PALETTE[def.field] || PALETTE.vermilion;
    const inkDark = def.field === 'azure' ? PALETTE.azure : (def.field === 'vert' ? PALETTE.vert : PALETTE.vermilion_dark);
    const uid = getUniqueId('chop');

    return `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" class="tarr-symbol-svg" aria-label="${def.blazonEn}">
        <defs>
          <clipPath id="${uid}_clip">
            <rect x="${boxX + 10}" y="${boxY + 10}" width="${boxSize - 20}" height="${boxSize - 20}" rx="3" />
          </clipPath>
        </defs>

        <!-- Drop Shadow -->
        <rect x="${boxX + 2}" y="${boxY + 4}" width="${boxSize}" height="${boxSize}" rx="8" fill="rgba(0,0,0,0.2)" />

        <g>
          <!-- Parchment background under stamp -->
          <rect x="${boxX}" y="${boxY}" width="${boxSize}" height="${boxSize}" rx="8" fill="#f8f4e8" stroke="${PALETTE.sable}" stroke-width="1.5" />
          
          <!-- Outer Thick Seal Ink Border -->
          <rect x="${boxX + 4}" y="${boxY + 4}" width="${boxSize - 8}" height="${boxSize - 8}" rx="6" fill="none" stroke="${ink}" stroke-width="5" />
          <!-- Inner Fine Seal Ink Border -->
          <rect x="${boxX + 12}" y="${boxY + 12}" width="${boxSize - 24}" height="${boxSize - 24}" rx="4" fill="none" stroke="${ink}" stroke-width="1.8" />

          <!-- Meander Corner Ornaments -->
          <path d="M ${boxX + 15} ${boxY + 24} L ${boxX + 24} ${boxY + 24} L ${boxX + 24} ${boxY + 15}" fill="none" stroke="${ink}" stroke-width="1.5" />
          <path d="M ${boxX + boxSize - 15} ${boxY + 24} L ${boxX + boxSize - 24} ${boxY + 24} L ${boxX + boxSize - 24} ${boxY + 15}" fill="none" stroke="${ink}" stroke-width="1.5" />
          <path d="M ${boxX + 15} ${boxY + boxSize - 24} L ${boxX + 24} ${boxY + boxSize - 24} L ${boxX + 24} ${boxY + boxSize - 15}" fill="none" stroke="${ink}" stroke-width="1.5" />
          <path d="M ${boxX + boxSize - 15} ${boxY + boxSize - 24} L ${boxX + boxSize - 24} ${boxY + boxSize - 24} L ${boxX + boxSize - 24} ${boxY + boxSize - 15}" fill="none" stroke="${ink}" stroke-width="1.5" />

          <!-- Sinitic Watermark Charge in Background -->
          <g opacity="0.22" clip-path="url(#${uid}_clip)">
            ${def.charges.map(c => CHARGES[c] ? CHARGES[c](ink, 0.75, 110, 110) : '').join('')}
          </g>

          <!-- Seal Script / Classical Hanzi Logograph (Carved in Relief) -->
          <text x="110" y="120" text-anchor="middle" dominant-baseline="central" fill="${ink}" font-family="'Songti SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif" font-size="${hanziText.length > 1 ? 46 : 68}" font-weight="900" letter-spacing="${hanziText.length > 1 ? '4' : '0'}">
            ${hanziText}
          </text>

          <!-- Bottom Seal Legend -->
          <text x="110" y="174" text-anchor="middle" fill="${inkDark}" font-family="'Cinzel', serif" font-size="8" font-weight="700" letter-spacing="1">
            ${def.legend ? def.legend.split('•')[0].trim() : 'MAGISTRAT'}
          </text>
        </g>
      </svg>
    `;
  }

  // --- F. Pointed Mandorla / Vesica Piscis (Ecclesiastical Tier) ---
  function renderVesicaSeal(def) {
    const W = 220, H = 270;
    const vesicaPath = "M 110 25 C 185 85, 185 185, 110 245 C 35 185, 35 85, 110 25 Z";
    const uid = getUniqueId('vesica');
    const fColor = PALETTE[def.field] || PALETTE.purpure;
    const hanziText = def.hanziChar || (def.hanzi ? (def.hanzi.length <= 2 ? def.hanzi : def.hanzi.substring(0, 2)) : '');
    const hanziColor = (def.field === 'or' || def.field === 'argent') ? PALETTE.sable : (def.chargeColor || PALETTE.or);
    const hanziStroke = hanziColor === PALETTE.sable ? 'none' : PALETTE.sable;

    return `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" class="tarr-symbol-svg" aria-label="${def.blazonEn}">
        <defs>
          <clipPath id="${uid}_clip">
            <path d="${vesicaPath}" />
          </clipPath>
        </defs>

        <!-- Drop Shadow -->
        <path d="${vesicaPath}" transform="translate(0, 4)" fill="rgba(0,0,0,0.25)" />

        <g>
          <path d="${vesicaPath}" fill="${fColor}" stroke="${PALETTE.sable}" stroke-width="2.5" />
          <g clip-path="url(#${uid}_clip)">
            <!-- Inner Beaded Mandorla Rim -->
            <path d="${vesicaPath}" fill="none" stroke="${PALETTE.or}" stroke-width="4" stroke-dasharray="8 4" opacity="0.85" />
            <!-- Gothic Canopy Arch at Top -->
            <path d="M 65 75 Q 110 40 155 75 Q 110 65 65 75 Z" fill="${PALETTE.or}" stroke="${PALETTE.sable}" stroke-width="1.2" />
            <!-- Religious / Patriarchal Charges / Hanzi -->
            ${hanziText ? `
              <text x="110" y="${def.charges.length > 0 ? 105 : 140}" text-anchor="middle" dominant-baseline="central" fill="${hanziColor}" stroke="${hanziStroke}" stroke-width="1.2" font-family="'Songti SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif" font-size="${hanziText.length > 1 ? (def.charges.length > 0 ? 28 : 38) : (def.charges.length > 0 ? 38 : 50)}" font-weight="900" letter-spacing="${hanziText.length > 1 ? '2' : '0'}">
                ${hanziText}
              </text>
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor || PALETTE.or, 0.50, 110, 168) : '').join('')}
            ` : `
              ${def.chargeCount > 1 ? renderMultiCharges(def, 110, 140, 0.72) : def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor || PALETTE.or, 0.72, 110, 140) : '').join('')}
            `}
          </g>
          <!-- Border Trim -->
          <path d="${vesicaPath}" fill="none" stroke="${PALETTE.or}" stroke-width="1.5" />
        </g>
      </svg>
    `;
  }

  // --- G. Civic Holding Badge (Barony Tier) ---
  function renderCivicBadge(def) {
    const W = 180, H = 200;
    const badgePath = "M 30 25 L 150 25 L 150 110 C 150 155, 90 180, 90 180 C 90 180, 30 155, 30 110 Z";
    const uid = getUniqueId('badge');
    const fColor = PALETTE[def.field] || PALETTE.azure;
    const hanziText = def.hanziChar || (def.hanzi ? (def.hanzi.length <= 2 ? def.hanzi : def.hanzi.substring(0, 2)) : '');
    const hanziColor = (def.field === 'or' || def.field === 'argent') ? PALETTE.sable : (def.chargeColor || PALETTE.or);
    const hanziStroke = hanziColor === PALETTE.sable ? 'none' : PALETTE.sable;

    return `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" class="tarr-symbol-svg" aria-label="${def.blazonEn}">
        <defs>
          <clipPath id="${uid}_clip">
            <path d="${badgePath}" />
          </clipPath>
        </defs>

        <!-- Drop Shadow -->
        <path d="${badgePath}" transform="translate(0, 4)" fill="rgba(0,0,0,0.2)" />

        <g>
          <path d="${badgePath}" fill="${fColor}" stroke="${PALETTE.sable}" stroke-width="2" />
          <g clip-path="url(#${uid}_clip)">
            <rect x="30" y="25" width="120" height="155" fill="${fColor}" />
            <path d="${badgePath}" fill="none" stroke="${PALETTE.or}" stroke-width="2.5" />
            <!-- Holding Charge / Hanzi -->
            ${hanziText ? `
              <!-- Sinitic Hanzi Logograph on Civic Badge -->
              <text x="90" y="${def.charges.length > 0 ? 70 : 95}" text-anchor="middle" dominant-baseline="central" fill="${hanziColor}" stroke="${hanziStroke}" stroke-width="1.2" font-family="'Songti SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif" font-size="${hanziText.length > 1 ? (def.charges.length > 0 ? 24 : 34) : (def.charges.length > 0 ? 32 : 46)}" font-weight="900" letter-spacing="${hanziText.length > 1 ? '2' : '0'}">
                ${hanziText}
              </text>
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.44, 90, 118) : '').join('')}
            ` : `
              <!-- Standard Charges -->
              ${def.chargeCount > 1 ? renderMultiCharges(def, 90, 95, 0.65) : def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.65, 90, 95) : '').join('')}
            `}
          </g>
        </g>
      </svg>
    `;
  }

  // =========================================================================
  // 5. Main Public API & DOM Renderer
  // =========================================================================

  function generateSymbol(titleKey, props = {}, tier = 'county') {
    const def = analyzeTitle(titleKey, props, tier);
    let svgHtml = '';

    switch (def.medium) {
      case 'vexillum':
        svgHtml = renderVexillum(def);
        break;
      case 'gonfanon':
        svgHtml = renderGonfanon(def);
        break;
      case 'notitia_scutum':
        svgHtml = renderNotitiaScutum(def);
        break;
      case 'sinosphere_chop':
        svgHtml = renderSinosphereChop(def);
        break;
      case 'vesica_seal':
        svgHtml = renderVesicaSeal(def);
        break;
      case 'civic_badge':
        svgHtml = renderCivicBadge(def);
        break;
      case 'bulla_seal':
      default:
        svgHtml = renderBullaSeal(def);
        break;
    }

    const MEDIUM_LABELS = {
      vexillum: 'Keiserlicher Amtsvanen (Vexillum)',
      gonfanon: 'Amtsvanen (Gonfanon)',
      notitia_scutum: 'Gubernats-Heerschilt (Notitia Shield)',
      bulla_seal: 'Magistrats-Insigel (Chancellery Seal)',
      sinosphere_chop: 'Guóxī (Vermilion Seal of Investiture)',
      vesica_seal: 'Erzbischöfliches Insigel (Vesica Seal)',
      civic_badge: 'Herren-Wâpen (Holding Badge)'
    };

    return {
      svgHtml,
      medium: def.medium,
      mediumLabel: MEDIUM_LABELS[def.medium] || 'Amtszeichen',
      blazonTarr: def.blazonTarr,
      blazonEn: def.blazonEn,
      legend: def.legend,
      source: def.source,
      definition: def
    };
  }

  function renderSymbolToElement(containerElem, titleKey, props = {}, tier = 'county') {
    if (!containerElem) return;
    const res = generateSymbol(titleKey, props, tier);

    containerElem.innerHTML = `
      <div class="symbol-card-inner">
        <div class="symbol-graphic-wrapper" title="${res.blazonEn}">
          ${res.svgHtml}
        </div>
        <div class="symbol-meta-wrapper">
          <div class="symbol-badges-row">
            <span class="symbol-medium-badge">${res.mediumLabel}</span>
            <span class="symbol-source-badge">${res.source}</span>
          </div>
          <div class="symbol-blazon-text">
            <em>&ldquo;${res.blazonTarr}&rdquo;</em>
          </div>
          <div class="symbol-legend-code">
            <code>${res.legend}</code>
          </div>
        </div>
      </div>
    `;
    containerElem.classList.remove('hidden');
  }

  return {
    generateSymbol,
    renderSymbolToElement,
    PALETTE,
    CHARGES,
    TINCTURES,
    CHARGE_BLAZONS,
    ORDINARY_BLAZONS,
    TINCTURE_PATTERNS,
    CANONICAL_SINOSPHERE_HANZI,
    getChronologicalHorizon,
    formatBlazon,
    analyzeTitle,
    CANONICAL_HERALDRY
  };
}));
