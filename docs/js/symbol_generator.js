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
    bridge: (color = PALETTE.argent, scale = 1, cx = 110, cy = 120, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-60, -25)" fill="${color}" stroke="${accent}" stroke-width="2">
        <rect x="5" y="0" width="110" height="12" rx="2" />
        <path d="M 5 12 L 5 40 L 22 40 Q 38 18 54 40 L 66 40 Q 82 18 98 40 L 115 40 L 115 12 Z" />
        <!-- Water below bridge -->
        <path d="M 5 44 C 20 40 35 48 50 44 C 65 40 80 48 95 44 C 105 42 112 45 115 44" fill="none" stroke="${PALETTE.azure}" stroke-width="3" stroke-linecap="round" />
      </g>
    `,

    // Wavy Water Bars (Hydronyms / Maritime)
    waves: (color = PALETTE.azure, scale = 1, cx = 110, cy = 130) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-65, -20)" fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round">
        <path d="M 0 0 C 18 -8 28 8 45 0 C 62 -8 72 8 90 0 C 108 -8 118 8 130 0" />
        <path d="M 0 16 C 18 8 28 24 45 16 C 62 8 72 24 90 16 C 108 8 118 24 130 16" />
        <path d="M 0 32 C 18 24 28 40 45 32 C 62 24 72 40 90 32 C 108 24 118 40 130 32" opacity="0.75" />
      </g>
    `,

    // Ringing Bell (Swenigorot canting charge)
    bell: (color = PALETTE.or, scale = 1, cx = 110, cy = 80, accent = PALETTE.sable) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-30, -35)" fill="${color}" stroke="${accent}" stroke-width="2" stroke-linejoin="round">
        <rect x="24" y="0" width="12" height="8" rx="2" fill="${accent}" />
        <path d="M 30 8 C 22 10 16 22 14 36 C 12 48 6 52 4 56 L 56 56 C 54 52 48 48 46 36 C 44 22 38 10 30 8 Z" />
        <circle cx="30" cy="62" r="5" fill="${PALETTE.brass}" stroke="${accent}" stroke-width="1.5" />
      </g>
    `,

    // St. Peter's Crossed Keys (Rome / Papal / Bishopric)
    keys_st_peter: (colorOr = PALETTE.or, scale = 1, cx = 110, cy = 110, colorArg = PALETTE.argent) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-45, -45)" stroke="${PALETTE.sable}" stroke-width="1.5" stroke-linecap="round">
        <!-- Gold Key (Dexter) -->
        <g fill="${colorOr}">
          <line x1="12" y1="78" x2="78" y2="12" stroke="${colorOr}" stroke-width="5" />
          <line x1="12" y1="78" x2="78" y2="12" stroke="${PALETTE.sable}" stroke-width="1.5" />
          <circle cx="16" cy="74" r="12" stroke-width="2" />
          <circle cx="16" cy="74" r="5" fill="${PALETTE.sable}" />
          <!-- Wards -->
          <path d="M 72 18 L 84 30 L 78 36 L 73 31 L 70 34 L 65 29 Z" />
        </g>
        <!-- Silver Key (Sinister) -->
        <g fill="${colorArg}">
          <line x1="78" y1="78" x2="12" y2="12" stroke="${colorArg}" stroke-width="5" />
          <line x1="78" y1="78" x2="12" y2="12" stroke="${PALETTE.sable}" stroke-width="1.5" />
          <circle cx="74" cy="74" r="12" stroke-width="2" />
          <circle cx="74" cy="74" r="5" fill="${PALETTE.sable}" />
          <!-- Wards -->
          <path d="M 18 18 L 6 30 L 12 36 L 17 31 L 20 34 L 25 29 Z" />
        </g>
      </g>
    `,

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
    tree_chestnut: (color = PALETTE.vert, scale = 1, cx = 110, cy = 115, trunk = PALETTE.wood) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-45, -55)" stroke="${PALETTE.sable}" stroke-width="1.8">
        <!-- Trunk & Roots -->
        <path d="M 40 50 L 38 85 L 20 98 M 42 85 L 45 98 M 52 85 L 70 98 L 50 50 Z" fill="${trunk}" />
        <!-- Foliage Crown (3 lobes) -->
        <path d="M 20 55 C 5 45 5 25 25 20 C 25 5 65 5 65 20 C 85 25 85 45 70 55 C 80 70 55 75 45 65 C 35 75 10 70 20 55 Z" fill="${color}" />
      </g>
    `,

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
    ship: (color = PALETTE.wood, scale = 1, cx = 110, cy = 120, sail = PALETTE.argent) => `
      <g transform="translate(${cx}, ${cy}) scale(${scale}) translate(-50, -45)" stroke="${PALETTE.sable}" stroke-width="1.8" stroke-linejoin="round">
        <!-- Hull -->
        <path d="M 5 45 C 15 68 85 68 95 45 L 85 45 L 75 52 L 25 52 L 15 45 Z" fill="${color}" />
        <!-- Mast & Cross -->
        <line x1="50" y1="10" x2="50" y2="52" stroke="${color}" stroke-width="4" />
        <polygon points="50,6 58,10 50,14" fill="${PALETTE.gules}" stroke="${PALETTE.sable}" stroke-width="1" />
        <!-- Full Billowing Square Sail -->
        <path d="M 28 16 Q 50 12 72 16 Q 80 32 72 44 Q 50 40 28 44 Q 20 32 28 16 Z" fill="${sail}" />
        <!-- Waves below -->
        <path d="M 0 65 Q 12 60 25 65 Q 37 70 50 65 Q 62 60 75 65 Q 87 70 100 65" fill="none" stroke="${PALETTE.azure}" stroke-width="3" stroke-linecap="round" />
      </g>
    `,

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
    dragon: { tarrNoun: 'Drache', enNoun: 'dragon', enArticle: 'a' }
  };

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

  function formatBlazon(fieldKey, chargeKey, chargeColorHex) {
    const fieldTinc = TINCTURES[fieldKey] || TINCTURES.gules;
    let chargeTincKey = 'argent';
    if (chargeColorHex === PALETTE.or) chargeTincKey = 'or';
    else if (chargeColorHex === PALETTE.sable) chargeTincKey = 'sable';
    else if (chargeColorHex === PALETTE.gules) chargeTincKey = 'gules';
    else if (chargeColorHex === PALETTE.azure) chargeTincKey = 'azure';
    else if (chargeColorHex === PALETTE.vert) chargeTincKey = 'vert';
    const chargeTinc = TINCTURES[chargeTincKey] || TINCTURES.argent;

    const chargeMeta = CHARGE_BLAZONS[chargeKey] || {
      tarrNoun: 'Emblem',
      enNoun: (chargeKey || 'charge').replace(/_/g, ' '),
      enArticle: 'a'
    };

    let blazonTarr = '';
    if (chargeKey === 'waves') {
      blazonTarr = `In ${fieldTinc.tarr} Meereswâgen van ${chargeTinc.tarr}`;
    } else if (chargeKey === 'keys_st_peter') {
      blazonTarr = `In ${fieldTinc.tarr} zwên gekrützte Slüttele van Zant Peter van ${chargeTinc.tarr}`;
    } else {
      const adj = chargeTinc.tarrAdj;
      blazonTarr = `In ${fieldTinc.tarr} ein ${adj} ${chargeMeta.tarrNoun}`;
    }

    let blazonEn = '';
    const art = chargeMeta.enArticle ? `${chargeMeta.enArticle} ` : '';
    blazonEn = `${fieldTinc.en}, ${art}${chargeMeta.enNoun} ${chargeTinc.en}`;

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
  // 4. Deterministic Hash & Canting Analyzer
  // =========================================================================
  function hashString(str) {
    let hash = 5381;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) + hash) + str.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash);
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
        hanzi: hanzi || '州',
        hanziChar: charStr,
        chargeColor: PALETTE.or,
        blazonTarr: `In ${fieldTinc.tarr} das Siegel-Schriftzeichen ${charStr} begleitet van einem goldenen ${chargeMeta.tarrNoun}`,
        blazonEn: `${fieldTinc.en}, the seal-script glyph ${charStr} accompanied by ${chargeMeta.enArticle ? chargeMeta.enArticle + ' ' : ''}${chargeMeta.enNoun} Or`,
        legend: `${(props.tarr_hist || props.tarr || tarrName || key).toUpperCase()} • ${charStr}之印`,
        source: 'Procedure 1 Sinosphere Continuity Protocol'
      };
    }

    // 3. Canting Morpheme Toponymic Derivation Engine
    let detectedField = 'gules';
    let detectedCharge = 'castrum';
    let detectedOrdinary = 'solid';

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

    // Architectural / topographic morphemes
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
    } else {
      // Deterministic charges pool
      const chargeList = ['castrum', 'roman_gate', 'mount_triple', 'ship', 'tree_chestnut', 'lion_rampant', 'waves', 'crown'];
      detectedCharge = chargeList[(h >> 3) % chargeList.length];
    }

    // Select suitable contrast charge color
    const chargeColor = (detectedField === 'argent' || detectedField === 'or') ? PALETTE.sable : PALETTE.argent;

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

    const blazon = formatBlazon(detectedField, detectedCharge, chargeColor);

    return {
      medium: chosenMedium,
      field: detectedField,
      ordinary: detectedOrdinary,
      charges: [detectedCharge],
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
    const clipAttr = clipId ? `clip-path="url(#${clipId})"` : '';

    if (def.ordinary === 'pales' || def.ordinary === 'pales_undy') {
      const isUndy = def.ordinary === 'pales_undy';
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

    if (def.ordinary === 'per_pale') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width / 2}" height="${height}" fill="${PALETTE.argent}" />
          <rect x="${width / 2}" y="0" width="${width / 2}" height="${height}" fill="${PALETTE.sable}" />
        </g>
      `;
    }

    if (def.ordinary === 'bend') {
      return `
        <g ${clipAttr}>
          <rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" />
          <polygon points="0,0 ${width * 0.35},0 ${width},${height * 0.65} ${width},${height} ${width * 0.65},${height} 0,${height * 0.35}" fill="${PALETTE.gules}" stroke="${PALETTE.sable}" stroke-width="1.5" />
        </g>
      `;
    }

    return `<rect x="0" y="0" width="${width}" height="${height}" fill="${fColor}" ${clipAttr} />`;
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
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.82, 110, 135) : '').join('')}
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
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.72, 110, 105) : '').join('')}
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
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.65, cx, cy - 25) : '').join('')}
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
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.62, cx, cy) : '').join('')}
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
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor || PALETTE.or, 0.72, 110, 140) : '').join('')}
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
              ${def.charges.map(c => CHARGES[c] ? CHARGES[c](def.chargeColor, 0.65, 90, 95) : '').join('')}
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
    TINCTURE_PATTERNS,
    CANONICAL_SINOSPHERE_HANZI,
    formatBlazon,
    analyzeTitle
  };
}));
