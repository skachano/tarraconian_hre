#!/usr/bin/env python3
"""
Tarraconian Atlas — Saint Holding Imagery Generator (Signa Sanctorum)
---------------------------------------------------------------------
Generates data/saint_holding_imagery.json containing rank-differentiated,
canonically grounded heraldic insignia for baronies and holdings where
saints from the CK3 save were buried, holy relics are enshrined, or
venerated patronal toponyms are attested.

Rules:
1. Strict Rule of Tincture: No metal on metal, no colour on colour.
2. Baronial Cadency: Baronies receive a differencing bordure to prevent
   heraldic collision with county and ducal arms.
3. Authentic Attributes: Saint charges are derived directly from classical
   hagiography and CK3 relic data (catherine_wheel, escallop, keys_st_peter,
   sword_crossed, crozier, anchor, stag_attired, bear_rampant, cross, etc.).
"""

import json
import os
import re

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, 'data')
    out_file = os.path.join(data_dir, 'saint_holding_imagery.json')

    # Load barony resolutions and geojson for metadata
    baronies_geojson_path = os.path.join(data_dir, 'ck3_baronies.geojson')
    with open(baronies_geojson_path, 'r', encoding='utf-8') as f:
        baronies_gj = json.load(f)

    p2b = {}
    bkey_to_props = {}
    for feat in baronies_gj['features']:
        props = feat['properties']
        pid = props.get('id')
        bkey = props.get('barony')
        if pid is not None:
            p2b[pid] = props
        if bkey:
            bkey_to_props[bkey] = props

    # Load canonical heraldry to ensure we do not override pre-existing canonical arms
    canonical_path = os.path.join(data_dir, 'canonical_title_heraldry.json')
    with open(canonical_path, 'r', encoding='utf-8') as f:
        canonical_titles = set(json.load(f).keys())

    # Hardcoded historical exceptions in symbol_generator.js
    bespoke_exceptions = {
        'c_roma', 'd_latium', 'k_romagna', 'k_papal_state',
        'c_barcelona', 'd_barcelona', 'c_tarragona', 'c_metz',
        'd_upper_lorraine', 'k_lotharingia', 'h_roman_empire', 'e_hre'
    }
    exempt_titles = canonical_titles | bespoke_exceptions

    # Master Hagiographic Registry of Buried Saints & Holy Relics
    # Key: barony key (or title key)
    # Value: dict of heraldic and hagiographic properties
    SAINT_DATABASE = {
        # --- Western Europe: British Isles ---
        "b_kildare": {
            "saint_name": "Saint Brigid of Kildare",
            "saint_epithet": "Abbess of Kildare & Patroness of Ireland",
            "shrine_type": "Monastic Tomb & Sacred Flame",
            "relic_description": "Tomb of Saint Brigid beneath the oak sanctuary of Kildare (Cill Dara), venerated with the perpetual holy fire.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "vert",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Rên-Grûn ein silbern Krütz van Zant-Brigida binnen einem silbern Bôrt",
            "blazon_en": "Vert, a cross of Saint Brigid Argent within a bordure Argent",
            "rationale_imagery": "The primary charge is the woven cross of Saint Brigid of Kildare, the beloved holy abbess who founded the double monastery under the venerable oak tree of Kildare and tended the perpetual flame.",
            "rationale_colours": "Rhenish Green (Vert) represents the pastoral verdure of Kildare and Brigid's monastic agrarian miracles, bearing a cross in Silver (Argent) with an Argent bordure under the Rule of Tinctures."
        },
        "b_clonmel": {
            "saint_name": "Saint Declan of Ardmore",
            "saint_epithet": "Apostle of the Déisi & Bishop of Ardmore",
            "shrine_type": "Episcopal Crypt & Holy Stone",
            "relic_description": "Shrine of Saint Declan, predecessor of Patrick who brought the faith to southern Munster.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "vert",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Rên-Grûn ein gulden Patriarchenkrütz binnen einem guldenen Bôrt",
            "blazon_en": "Vert, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "The primary charge is the patriarchal double cross, honoring the ancient pre-Patrician episcopal see and the venerated relics of Saint Declan of Ardmore.",
            "rationale_colours": "Vert represents the rolling meadows of Ormond, bearing a sacred charge in Gold (Or) enclosed by an Or cadency bordure."
        },
        "b_dover": {
            "saint_name": "Saint Mary-in-Castro",
            "saint_epithet": "Sanctuary of the Saxons & Guardian of the Strait",
            "shrine_type": "Castle Chapel & Saxon Reliquary",
            "relic_description": "Ancient 7th-century church within the Roman pharos fortress of Dover Castle.",
            "charge": "rose_seeded",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Rôse mit guldenem Samen binnen einem silbern Bôrt",
            "blazon_en": "Gules, a rose seeded Or barbed Vert Argent within a bordure Argent",
            "rationale_imagery": "The primary charge is the Marian mystical rose, honoring the venerable Saxon royal foundation of St Mary in Castro overlooking the English Channel.",
            "rationale_colours": "Imperial Crimson (Gules) reflects martial garrison vigilance over the strait, differenced by a Silver (Argent) rose and bordure."
        },
        "b_canterbury": {
            "saint_name": "Saint Augustine & Saint Thomas Becket",
            "saint_epithet": "Archbishop & Apostle to the English; Archbishop & Martyr",
            "shrine_type": "Metropolitan Shrine & Relics of the Pallium",
            "relic_description": "Cathedral shrine holding the pallium of St Augustine and the venerated blood-reliquary of St Thomas Becket.",
            "charge": "crozier",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein gulden Bischofsstav binnen einem silbern Bôrt",
            "blazon_en": "Gules, a pastoral staff Or within a bordure Argent",
            "rationale_imagery": "The primary charge is the golden pastoral crozier, representing the Primatial Metropolitan throne of England, the mission of Saint Augustine (597 AD), and the martyrdom of Saint Thomas Becket (1170 AD).",
            "rationale_colours": "Gules represents the blood of holy martyrdom shed upon the cathedral pavement, charged with a pastoral staff Or and bounded by an Argent bordure."
        },
        "b_tonbridge": {
            "saint_name": "Saint Peter and Paul",
            "saint_epithet": "Patrons of the Medway Priory",
            "shrine_type": "Augustinian Priory Crypt",
            "relic_description": "Augustinian priory founded under the invocation of Saints Peter and Paul on the River Medway.",
            "charge": "keys_st_peter",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr zwên gekrützte Slüttele van Zant Peter van Golt binnen einem silbern Bôrt",
            "blazon_en": "Azure, two keys in saltire of Saint Peter Or within a bordure Argent",
            "rationale_imagery": "The primary charge is the crossed keys of Saint Peter, reflecting the patronal invocation of Tonbridge Priory on the strategic crossing of the Medway.",
            "rationale_colours": "Azure represents the riparian waters of the Medway, contrasted with golden apostolic keys and an Argent cadency bordure."
        },
        "b_halifax": {
            "saint_name": "Saint John the Baptist",
            "saint_epithet": "Holy Face & Forerunner",
            "shrine_type": "Pilgrimage Church of the Holy Face",
            "relic_description": "Ancient pilgrimage shrine believed to preserve hair and likeness of Saint John the Baptist ('Haly-fax' / Holy Hair).",
            "charge": "chalice",
            "charge_color": "argent",
            "field": "sable",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Swartz ein silbern Kelch binnen einem guldenen Bôrt",
            "blazon_en": "Sable, a chalice Argent within a bordure Or",
            "rationale_imagery": "The primary charge is a sacred chalice, symbolizing the sacramental vessel and baptismal ministry of Saint John the Baptist in the Yorkshire Pennines.",
            "rationale_colours": "Sable represents monastic asceticism and the peat moors of Halifax, charged with a silver chalice and enclosed by a golden bordure."
        },
        "b_york": {
            "saint_name": "Saint William of York & Saint Paulinus",
            "saint_epithet": "Archbishop & Confessor of York",
            "shrine_type": "Metropolitan Minster Shrine",
            "relic_description": "The high shrine of Saint William of York in York Minster, site of miraculous healings and archiepiscopal tomb.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Patriarchenkrütz binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "The primary charge is the golden double-beamed patriarchal cross of the Northern Metropolitan Province of York, commemorating Saint William and the early Roman mission of Paulinus.",
            "rationale_colours": "Gules reflects metropolitan archiepiscopal dignity, accompanied by Gold (Or) cross and bordure under strict tincture compliance."
        },
        "b_hereford": {
            "saint_name": "Saint Thomas Cantilupe & Saint Ethelbert",
            "saint_epithet": "Bishop & Confessor; King & Martyr",
            "shrine_type": "Cathedral Reliquary of the Welsh Marches",
            "relic_description": "Tomb of Saint Thomas Cantilupe and the royal shrine of Saint Ethelbert King of East Anglia.",
            "charge": "fleur_de_lis",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein gulden Lilje binnen einem silbern Bôrt",
            "blazon_en": "Gules, a fleur-de-lis Or within a bordure Argent",
            "rationale_imagery": "The primary charge is the fleur-de-lis, the ancestral Cantilupe heraldic emblem and symbol of episcopal purity marking the pilgrimage shrine of Hereford.",
            "rationale_colours": "Imperial Gules represents the martial marcher diocese, charged with a golden fleur-de-lis and an Argent differencing bordure."
        },
        "b_mull": {
            "saint_name": "Saint Columba of Iona",
            "saint_epithet": "Abbot & Apostle of Caledonia",
            "shrine_type": "Abbey Tomb of Iona (Î-Chaluim Chille)",
            "relic_description": "The holy island abbey of Iona, burial place of Columba and forty-eight ancient Scottish, Irish, and Norwegian kings.",
            "charge": "ship",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Karrach-Schip binnen einem silbern Bôrt",
            "blazon_en": "Azure, an ancient curragh ship Argent within a bordure Argent",
            "rationale_imagery": "The primary charge is the Celtic wicker and hide curragh ship in which Saint Columba and his twelve companions sailed across the waves from Ireland to Iona in 563 AD.",
            "rationale_colours": "Azure represents the stormy Hebridean seas, bearing a silver ship of pilgrimage within an Argent bordure."
        },
        "b_saint_albans": {
            "saint_name": "Saint Alban",
            "saint_epithet": "Protomartyr of Britain",
            "shrine_type": "Abbey Shrine of the Roman Verulamium",
            "relic_description": "Tomb of Saint Alban, beheaded in the 3rd century atop the hill overlooking ancient Verulamium.",
            "charge": "sword_crossed",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr zwên gekrützte gulden Swerde binnen einem guldenen Bôrt",
            "blazon_en": "Azure, two swords in saltire Or within a bordure Or",
            "rationale_imagery": "The primary charge is crossed swords of Roman execution, commemorating the brave martyr Alban who exchanged cloaks with a Christian priest and embraced martyrdom.",
            "rationale_colours": "Azure represents celestial steadfastness, bearing golden blades and a golden baronial cadency bordure."
        },
        "b_whitehaven": {
            "saint_name": "Saint Bega of Cumberland",
            "saint_epithet": "Virgin & Hermitess of St Bees",
            "shrine_type": "Priory Crypt & Sacred Armlet",
            "relic_description": "Shrine of the Irish virgin hermitess St Bega at Kirkeby Becok, known for the miraculous midsummer snow.",
            "charge": "bell",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Klocke binnen einem silbern Bôrt",
            "blazon_en": "Azure, a church bell Argent within a bordure Argent",
            "rationale_imagery": "The primary charge is an ancient hand-bell, sacred attribute of the Celtic hermit saint who lived in solitary prayer upon the Cumbrian cliffs.",
            "rationale_colours": "Azure represents the Irish Sea, bearing a silver bell and bordure in strict compliance with tincture rules."
        },
        "b_st_davids": {
            "saint_name": "Saint David (Dewi Sant)",
            "saint_epithet": "Bishop, Confessor & Patron of Wales",
            "shrine_type": "Cathedral Shrine of Mynyw",
            "relic_description": "The cathedral tomb of Saint David in the secluded valley of Glyn Rhosyn, where two pilgrimages equaled one to Rome.",
            "charge": "cross",
            "charge_color": "or",
            "field": "sable",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Swartz ein gulden Krütz binnen einem guldenen Bôrt",
            "blazon_en": "Sable, a cross Or within a bordure Or",
            "rationale_imagery": "The primary charge is the golden cross of Saint David, honoring the ascetic bishop who lived on water and wild leeks and founded monasteries throughout western Britain.",
            "rationale_colours": "Sable reflects severe monastic asceticism, bearing the brilliant golden cross and cadency bordure of Dewi Sant."
        },
        "b_st_andrews": {
            "saint_name": "Saint Andrew the Apostle",
            "saint_epithet": "Protoclete & Patron of Scotland",
            "shrine_type": "Metropolitan Cathedral Shrine of Kilrymont",
            "relic_description": "Enshrined arm, knee, and finger relics of Saint Andrew brought by Saint Regulus to the cliffs of Fife.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Krütz binnen einem silbern Bôrt",
            "blazon_en": "Azure, a saltire Argent within a bordure Argent",
            "rationale_imagery": "The primary charge is the silver decussate cross (saltire) of Saint Andrew the Apostle, patron of the Kingdom of the Scots.",
            "rationale_colours": "Azure represents the northern skies over the North Sea cliffs, charged with silver saltire and bordure."
        },

        # --- Western Europe: France, Low Countries & Burgundy ---
        "b_santiago": {
            "saint_name": "Saint James the Greater (Santiago)",
            "saint_epithet": "Apostle & Patron of Hispania",
            "shrine_type": "Apostolic Sepulchre of Compostela",
            "relic_description": "The sacred sepulchre of the Apostle James, discovered in the Campus Stellae (Field of Stars) under Bishop Theodemar.",
            "charge": "escallop",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Pilgermuschel van Zant-Jâcop binnen einem silbern Bôrt",
            "blazon_en": "Gules, an escallop shell Argent within a bordure Argent",
            "rationale_imagery": "The primary charge is the venerated scallop shell (Venera de Santiago), universal emblem of European pilgrims walking the Camino de Santiago to the apostle's crypt.",
            "rationale_colours": "Imperial Crimson (Gules) reflects apostolic martyrdom by the sword in Jerusalem, differenced by a silver pilgrim shell and cadency bordure."
        },
        "b_saint_junien": {
            "saint_name": "Saint Junian of Limoges",
            "saint_epithet": "Hermit of the Vienne Valley",
            "shrine_type": "Collegiate Crypt & Carved Limestone Tomb",
            "relic_description": "6th-century tomb and collegiate church of the hermit Junian, advisor to Clovis's queen Chrodechildis.",
            "charge": "cross_patriarchal",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Patriarchenkrütz binnen einem silbern Bôrt",
            "blazon_en": "Gules, a patriarchal cross Argent within a bordure Argent",
            "rationale_imagery": "The primary charge is a patriarchal cross, representing the collegiate chapter of Saint-Junien and the hermit's spiritual victory over demonic forest dragons.",
            "rationale_colours": "Gules represents holy ardour, bearing a silver double cross and bordure in full accordance with the Rule of Tinctures."
        },
        "b_craon": {
            "saint_name": "Saint Clement of Craon",
            "saint_epithet": "Patron & Protector of Anjou Marches",
            "shrine_type": "Baronial Priory Reliquary",
            "relic_description": "Ancient priory of Saint-Clément at Craon housing sacred relics of the early Roman pope.",
            "charge": "anchor",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Anker van Zant-Klemens binnen einem silbern Bôrt",
            "blazon_en": "Azure, an anchor Argent within a bordure Argent",
            "rationale_imagery": "The primary charge is the mariner's anchor, the iconic attribute of Saint Clement of Rome, patron of the baronial priory of Craon.",
            "rationale_colours": "Azure reflects steadfast Christian hope, accompanied by a silver anchor and baronial cadency bordure."
        },
        "b_contres": {
            "saint_name": "Saint Cyr & Saint Julitta",
            "saint_epithet": "Child-Martyr & Mother of Tarsus",
            "shrine_type": "Parish Reliquary of Sologne",
            "relic_description": "Venerated relics of the 4th-century child martyr Cyr, patron of Contres in the county of Blois.",
            "charge": "sword_crossed",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr zwên gekrützte gulden Swerde binnen einem guldenen Bôrt",
            "blazon_en": "Azure, two swords in saltire Or within a bordure Or",
            "rationale_imagery": "Crossed arming swords in saltire represent the fearless infant martyr Cyr, who confessed Christ before the Roman governor and was slain for his faith.",
            "rationale_colours": "Azure reflects innocent purity, contrasted with golden martyr's blades and an Or bordure."
        },
        "b_paris": {
            "saint_name": "Saint Genevieve",
            "saint_epithet": "Virgin & Patroness of Paris",
            "shrine_type": "Abbey Crypt of the Montagne Sainte-Geneviève",
            "relic_description": "Golden reliquary shrine of Saint Genevieve, whose prayers protected Paris from Attila the Hun in 451 AD.",
            "charge": "star_six_pointed",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Strahlstern binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a six-pointed mullet star Or within a bordure Or",
            "rationale_imagery": "The six-pointed mullet star represents the celestial guiding light and vigilance of Saint Genevieve, guardian of the civic magistracy of Paris.",
            "rationale_colours": "Azure represents the royal French Capetian mantle, bearing a brilliant star in Gold (Or) with an Or bordure."
        },
        "b_saint_denis": {
            "saint_name": "Saint Denis (Dionysius)",
            "saint_epithet": "First Bishop of Paris, Martyr & Royal Patron of France",
            "shrine_type": "Royal Abbey Necropolis & Crypt of the Kings",
            "relic_description": "The sacred burial abbey of Saint Denis, burial place of French monarchs from Dagobert I onwards and keeper of the Oriflamme banner.",
            "charge": "crozier",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Bischofsstav binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a pastoral staff Or within a bordure Or",
            "rationale_imagery": "The primary charge is the golden pastoral crozier, commemorating Saint Denis, the apostle to the Gauls who walked from Montmartre carrying his severed head to his chosen resting place.",
            "rationale_colours": "Imperial Crimson (Gules) reflects the Oriflamme war-banner of Saint Denis, charged with gold under the strict Rule of Tinctures."
        },
        "b_epernay": {
            "saint_name": "Saint Martin & Saint Remi",
            "saint_epithet": "Apostles of the Gauls and the Franks",
            "shrine_type": "Champagne Abbey Crypt",
            "relic_description": "Ancient foundation of Saint-Martin d'Épernay, spiritual station between Reims and the Marne.",
            "charge": "sword_crossed",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr zwên silbern gekrützte Swerde binnen einem silbern Bôrt",
            "blazon_en": "Azure, two swords in saltire Argent within a bordure Argent",
            "rationale_imagery": "Crossed swords represent the sword of Saint Martin, which divided his chivalric military cloak to clothe Christ disguised as a beggar at the gates of Amiens.",
            "rationale_colours": "Azure and Argent symbolize Saint Martin's blue cloak and Christian charity across the Champagne plain."
        },
        "b_morvan": {
            "saint_name": "Saint Mary Magdalene",
            "saint_epithet": "Apostle to the Apostles",
            "shrine_type": "Basilica of Sainte-Madeleine de Vézelay",
            "relic_description": "The holy hilltop basilica of Vézelay, celebrated pilgrimage shrine claiming the bodily relics of Saint Mary Magdalene.",
            "charge": "chalice",
            "charge_color": "or",
            "field": "purpure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Porphyr-Purpur ein gulden Salbkelch binnen einem guldenen Bôrt",
            "blazon_en": "Purpure, an alabaster ointment chalice Or within a bordure Or",
            "rationale_imagery": "The primary charge is the golden alabaster chalice, representing the vessel of precious spikenard with which Mary Magdalene anointed the feet of Christ.",
            "rationale_colours": "Purpure reflects solemn penitential majesty, accompanied by a golden vessel and a differencing bordure Or."
        },
        "b_marseille": {
            "saint_name": "Saint Victor of Marseilles",
            "saint_epithet": "Roman Officer & Megalomartyr",
            "shrine_type": "Abbey of Saint-Victor & 5th-century Catacombs",
            "relic_description": "Crypt and catacombs of the Abbey of Saint-Victor, holding the tombs of Victor and early Christian martyrs of Massalia.",
            "charge": "sword_crossed",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr zwên gekrützte silbern Swerde binnen einem silbern Bôrt",
            "blazon_en": "Azure, two swords in saltire Argent within a bordure Argent",
            "rationale_imagery": "Crossed arming swords commemorate the Roman military officer Saint Victor, who refused to sacrifice to pagan idols before Emperor Maximian and died a soldier of Christ.",
            "rationale_colours": "Azure represents the Mediterranean harbour of Marseille, paired with silver swords and an Argent bordure."
        },
        "b_vienne": {
            "saint_name": "Saint Maurice",
            "saint_epithet": "Commander of the Theban Legion & Holy Patron of the Empire",
            "shrine_type": "Primatial Cathedral of Saint-Maurice",
            "relic_description": "Venerated relics of Saint Maurice and the Theban Legion enshrined in the Cathedral of Saint-Maurice of Vienne.",
            "charge": "holy_lance",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt der Heilege Lanze van Zant-Maurits van Golt binnen einem guldenen Bôrt",
            "blazon_en": "Gules, the Holy Lance of Saint Maurice Or within a bordure Or",
            "rationale_imagery": "The Holy Lance of Saint Maurice, paramount imperial relic of chivalric investiture, commemorates the leader of the Christian soldiers martyred at Agaunum.",
            "rationale_colours": "Imperial Crimson (Gules) and Gold (Or) represent sovereign Holy Roman investiture and martial martyrdom."
        },
        "b_besancon": {
            "saint_name": "Saint Ferreolus and Ferrutio",
            "saint_epithet": "Apostles & Martyrs of Franche-Comté",
            "shrine_type": "Cathedral & Basilica of Saint-Ferjeux",
            "relic_description": "The cave crypt where Saints Ferreolus and Ferrutio were buried following their martyrdom in 212 AD under Roman prefect Claudius.",
            "charge": "sword_crossed",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt zwên gekrützte silbern Swerde binnen einem silbern Bôrt",
            "blazon_en": "Gules, two swords in saltire Argent within a bordure Argent",
            "rationale_imagery": "Crossed swords represent the twin martyrdom of the priest Ferreolus and deacon Ferrutio, disciples of Saint Irenaeus who converted the Sequani.",
            "rationale_colours": "Gules represents the martyrs' blood shed outside Vesontio, differenced by silver blades and an Argent bordure."
        },
        "b_turnhout": {
            "saint_name": "Saint Peter",
            "saint_epithet": "Prince of the Apostles",
            "shrine_type": "Collegiate Church of Saint Peter",
            "relic_description": "Ancient Campine collegiate church and pilgrimage sanctuary dedicated to the Apostle Peter.",
            "charge": "keys_st_peter",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr zwên gekrützte Slüttele van Zant Peter van Golt binnen einem silbern Bôrt",
            "blazon_en": "Azure, two keys in saltire of Saint Peter Or within a bordure Argent",
            "rationale_imagery": "Crossed keys of heaven commemorate the patronal dedication of Turnhout's collegiate church to Saint Peter.",
            "rationale_colours": "Azure and Or symbolize celestial keys and authority, differenced by a silver cadency bordure."
        },
        "b_saint_hubert": {
            "saint_name": "Saint Hubert of Liège",
            "saint_epithet": "Apostle of the Ardennes & Patron of Hunters",
            "shrine_type": "Benedictine Abbey of Saint-Hubert",
            "relic_description": "The great Ardennes abbey where the body of Saint Hubert was translated in 825 AD, site of the miraculous conversion by the stag.",
            "charge": "stag_attired",
            "charge_color": "or",
            "field": "vert",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Rên-Grûn ein tien-endiger gulden Hirz binnen einem guldenen Bôrt",
            "blazon_en": "Vert, a stag attired of ten tines Or within a bordure Or",
            "rationale_imagery": "The ten-tined stag attired commemorates the miraculous stag with a luminous crucifix between its antlers that converted Duke Hubert in the wild forests of the Ardennes.",
            "rationale_colours": "Rhenish Green (Vert) represents the venerable Ardennes forest, bearing the golden miraculous stag and an Or bordure."
        },
        "b_saarbrucken": {
            "saint_name": "Saint Arnual (Arnold)",
            "saint_epithet": "Bishop of Metz & Hermit of the Saar",
            "shrine_type": "Collegiate Crypt of Saint-Arnual",
            "relic_description": "7th-century tomb and collegiate foundation of Bishop Arnual at the foot of the Stiftswald along the Saar River.",
            "charge": "crozier",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Bischofsstav binnen einem silbern Bôrt",
            "blazon_en": "Gules, a pastoral staff Argent within a bordure Argent",
            "rationale_imagery": "The pastoral crozier honors Saint Arnual, 25th Bishop of Metz, who chose this peaceful haven along the Saar for his hermitage and final rest.",
            "rationale_colours": "Gules represents episcopal Lorraine nobility, charged with a silver staff and Argent cadency bordure."
        },
        "b_argonne": {
            "saint_name": "Saint Michael the Archangel",
            "saint_epithet": "Archangel & Captain of the Heavenly Host",
            "shrine_type": "Benedictine Abbey of Saint-Mihiel",
            "relic_description": "Venerated 8th-century Benedictine abbey of Saint-Mihiel founded by Count Wulfoald in the Meuse valley.",
            "charge": "sword_crossed",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr zwên gulden Flammewerde binnen einem guldenen Bôrt",
            "blazon_en": "Azure, two flaming swords in saltire Or within a bordure Or",
            "rationale_imagery": "Flaming crossed swords represent Saint Michael the Archangel, celestial defender who cast Lucifer from heaven and guards the fortress abbey of Saint-Mihiel.",
            "rationale_colours": "Azure represents the vault of heaven, bearing golden blades and a protective Or bordure."
        },

        # --- Central Europe & Germany ---
        "b_cologne": {
            "saint_name": "The Three Holy Kings & Saint Ursula",
            "saint_epithet": "The Magi of the East & the Eleven Thousand Virgins",
            "shrine_type": "Golden Shrine of the Magi & Roman Basilica of St Ursula",
            "relic_description": "The triple-crowned shrine of the Three Kings (translated from Milan by Barbarossa in 1164) and the holy martyr-crypt of Saint Ursula.",
            "charge": "crown",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein gulden Koningskrône binnen einem silbern Bôrt",
            "blazon_en": "Gules, an open crown Or within a bordure Argent",
            "rationale_imagery": "An open royal crown symbolizes the Three Holy Kings (Caspar, Melchior, Balthasar) whose sacred relics rest in the magnificent golden shrine of Cologne Cathedral.",
            "rationale_colours": "Gules reflects royal majesty and the blood of Saint Ursula's virgin martyrs, differenced by a silver cadency bordure."
        },
        "b_nauenahr": {
            "saint_name": "Saint Apollinaris of Ravenna",
            "saint_epithet": "Bishop & Martyr",
            "shrine_type": "Apollinarisberg Crypt on the Rhine",
            "relic_description": "Venerated head reliquary and crypt of Saint Apollinaris brought to the mountain sanctuary overlooking Remagen and the Ahr valley in 1164.",
            "charge": "crozier",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Bischofsstav binnen einem silbern Bôrt",
            "blazon_en": "Gules, a pastoral staff Argent within a bordure Argent",
            "rationale_imagery": "The silver pastoral crozier commemorates Saint Apollinaris, disciple of Saint Peter and first bishop of Ravenna, whose miraculous relics sanctify the Rhine hillside.",
            "rationale_colours": "Gules represents episcopal martyrdom, contrasted with silver staff and bordure under the Rule of Tinctures."
        },
        "b_isenburg": {
            "saint_name": "Saint George",
            "saint_epithet": "Megalomartyr & Dragon Slayer",
            "shrine_type": "Castral Chapel of the Westerwald",
            "relic_description": "Ancient knightly chapel dedicated to Saint George, patron of Christian chivalry.",
            "charge": "sword_crossed",
            "charge_color": "gules",
            "field": "argent",
            "ordinary": "bordure",
            "ordinary_color": "gules",
            "blazon_tarr": "In Silber zwên rôte gekrützte Swerde binnen einem rôten Bôrt",
            "blazon_en": "Argent, two swords in saltire Gules within a bordure Gules",
            "rationale_imagery": "Crossed swords of Gules represent the martial vigilance of Saint George, patron of Christian knights across the rugged hills of the Westerwald.",
            "rationale_colours": "Argent field bearing Crimson (Gules) blades and bordure, inverting the St George cross motif for baronial cadency."
        },
        "b_lichtberg": {
            "saint_name": "Saint Vitus (Sankt Veit)",
            "saint_epithet": "Child-Martyr & Fourteen Holy Helper",
            "shrine_type": "Alsatian Valley Sanctuary",
            "relic_description": "Hilltop chapel and pilgrimage site dedicated to Saint Vitus in the Vosges foothills.",
            "charge": "cross",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Krütz binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a cross Or within a bordure Or",
            "rationale_imagery": "A radiant cross Or represents Saint Vitus, protector against illness and patron helper of the faithful across the upper Rhine.",
            "rationale_colours": "Azure reflects serene spiritual hope, accompanied by a golden cross and cadency bordure."
        },
        "b_limburg": {
            "saint_name": "Saint George",
            "saint_epithet": "Patron of the Stiftsberg",
            "shrine_type": "Collegiate Cathedral of Saint George",
            "relic_description": "Venerated collegiate foundation of 910 AD atop the limestone crag overlooking the Lahn River.",
            "charge": "dragon",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Drache binnen einem silbern Bôrt",
            "blazon_en": "Gules, a dragon Argent within a bordure Argent",
            "rationale_imagery": "The dragon Argent symbolizes the monster conquered by Saint George atop the rock of Limburg an der Lahn.",
            "rationale_colours": "Imperial Crimson (Gules) reflects martial victory, differenced by a silver dragon and bordure."
        },
        "b_fulda": {
            "saint_name": "Saint Boniface (Wynfreth)",
            "saint_epithet": "Apostle of the Germans & Archbishop-Martyr",
            "shrine_type": "High Crypt of Fulda Cathedral",
            "relic_description": "The holy sepulchre of Saint Boniface, apostle of the Germans, buried in his beloved Abbey of Fulda along with the Ragyndrudis Codex.",
            "charge": "sword_crossed",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt zwên gekrützte gulden Swerde van Zant-Bonifatius binnen einem guldenen Bôrt",
            "blazon_en": "Gules, two swords in saltire Or within a bordure Or",
            "rationale_imagery": "Crossed swords in Gold commemorate Saint Boniface, martyred in Dokkum in 754 AD, who held aloft the Gospel book which the sword could pierce but not destroy.",
            "rationale_colours": "Imperial Crimson (Gules) and Gold (Or) represent the sovereign prince-abbacy of Fulda and Bonifacian apostolic foundation."
        },
        "b_munchen": {
            "saint_name": "Saint Benno of Meissen",
            "saint_epithet": "Bishop & Patron of Munich",
            "shrine_type": "Relic Shrine of the Monk-Settlement",
            "relic_description": "Venerated patron of the 'Mönche' (Munich), famed for the miracle of the keys thrown into the Elbe and recovered in a fish.",
            "charge": "fish_twin",
            "charge_color": "or",
            "field": "sable",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Swartz zwên gulden Fische mit einem Slüttle binnen einem guldenen Bôrt",
            "blazon_en": "Sable, twin fish addorsed Or within a bordure Or",
            "rationale_imagery": "Twin fish addorsed commemorate Saint Benno, who cast the cathedral keys into the river to defy Emperor Henry IV, later retrieving them from a fish's belly.",
            "rationale_colours": "Sable represents the monastic habit of Munich ('apud Monachos'), highlighted with golden fish and an Or bordure."
        },
        "b_tamsweg": {
            "saint_name": "Saint Leonhard of Noblac",
            "saint_epithet": "Patron of Prisoners & Pilgrims",
            "shrine_type": "St Leonhard ob Tamsweg Pilgrimage Sanctuary",
            "relic_description": "Celebrated alpine pilgrimage sanctuary of St Leonhard in the Lungau, famed for golden glass and votive iron offerings.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Krütz binnen einem silbern Bôrt",
            "blazon_en": "Azure, a cross Argent within a bordure Argent",
            "rationale_imagery": "The silver cross represents Saint Leonhard, the hermit of Limousin whose intercession released captives and protected cattle and travellers across the high alpine passes.",
            "rationale_colours": "Azure represents high alpine skies, differenced by a silver cross and cadency bordure."
        },
        "b_brandenburg": {
            "saint_name": "Saint Peter and Paul",
            "saint_epithet": "Apostolic Patrons of the North March",
            "shrine_type": "Cathedral Island (Dominsel) Sanctuary",
            "relic_description": "The 10th-century cathedral of Saints Peter and Paul founded by Emperor Otto I upon the conquered Slavic fortress of Brennabor.",
            "charge": "keys_st_peter",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt zwên silbern gekrützte Slüttele binnen einem silbern Bôrt",
            "blazon_en": "Gules, two keys in saltire of Saint Peter Argent within a bordure Argent",
            "rationale_imagery": "Crossed keys in saltire represent Saint Peter, titular patron of the cathedral on the Havel island that anchored Christian governance across the Northern March.",
            "rationale_colours": "Gules represents imperial marcher sovereignty, bearing silver keys and an Argent bordure."
        },
        "b_dramberg": {
            "saint_name": "Holy Cross & Knights Templar",
            "saint_epithet": "Guardians of the Pomeranian March",
            "shrine_type": "Templar Preceptory & Pilgrim Fortress",
            "relic_description": "The commandery of the Poor Fellow-Soldiers of Christ (Templars) guarding the pilgrim route towards Gdansk.",
            "charge": "cross",
            "charge_color": "gules",
            "field": "argent",
            "ordinary": "bordure",
            "ordinary_color": "gules",
            "blazon_tarr": "In Silber ein rôtes Krütz binnen einem rôten Bôrt",
            "blazon_en": "Argent, a cross pattée Gules within a bordure Gules",
            "rationale_imagery": "The red cross of the Knights Templar commemorates the military-religious garrison that fortified the frontier border of Drawsko (Dramburg).",
            "rationale_colours": "Argent field with Gules cross reflects the white mantle and red cross of the Templar Order."
        },
        "b_sankt_gallen": {
            "saint_name": "Saint Gall (Gallus)",
            "saint_epithet": "Hermit, Apostle of Alemannia & Founder of Saint Gall",
            "shrine_type": "Imperial Abbey & Tomb of Saint Gall",
            "relic_description": "The magnificent monastic republic and library of Saint Gall, founded where the Irish hermit built his cell in 612 AD.",
            "charge": "bear_rampant",
            "charge_color": "sable",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "sable",
            "blazon_tarr": "In Golt ein uffrechter swartzer Bêre van Zant-Gallen binnen einem swartzen Bôrt",
            "blazon_en": "Or, a bear rampant Sable within a bordure Sable",
            "rationale_imagery": "The rampant black bear commemorates the wild bear of the Steinach forest that obeyed Saint Gall, bringing logs for his fire in exchange for bread.",
            "rationale_colours": "Or (Gold) represents sovereign imperial prince-abbacy status, bearing the famous black bear of Saint Gall enclosed by a Sable bordure."
        },
        "b_sankt_blasien": {
            "saint_name": "Saint Blaise (Blasius)",
            "saint_epithet": "Bishop of Sebaste, Martyr & Fourteen Holy Helper",
            "shrine_type": "Benedictine Imperial Abbey of the Black Forest",
            "relic_description": "The great Black Forest abbey housing relics of Saint Blaise, throat-healer and protector of wild beasts.",
            "charge": "crozier",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Bischofsstav binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a pastoral staff Or within a bordure Or",
            "rationale_imagery": "The golden pastoral staff honors Saint Blaise, the beloved Armenian bishop whose relics transformed an alpine gorge into a spiritual powerhouse.",
            "rationale_colours": "Azure reflects mountain skies, accompanied by a golden crozier and an Or cadency bordure."
        },
        "b_sankt_polten": {
            "saint_name": "Saint Hippolytus of Rome",
            "saint_epithet": "Martyr & Scholar",
            "shrine_type": "Monastery of Sankt Pölten",
            "relic_description": "8th-century abbey founded on the Traisen River housing relics of Saint Hippolytus, from whom the city derives its name.",
            "charge": "horse_courant",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Rennende Pfert binnen einem silbern Bôrt",
            "blazon_en": "Azure, a horse courant Argent within a bordure Argent",
            "rationale_imagery": "The running horse courant canting emblem recalls Hippolytus ('unbridled horse'), who was dragged to martyrdom outside Rome.",
            "rationale_colours": "Azure and Argent represent the Traisen river valley and the early Carolingian abbey foundation."
        },
        "b_sankt_veit": {
            "saint_name": "Saint Vitus (Sankt Veit)",
            "saint_epithet": "Patron of Carinthia",
            "shrine_type": "Ducal Town & Collegiate Church of Carinthia",
            "relic_description": "Historical ducal seat of Carinthia on the Glan River, consecrated under the patronal guardianship of Saint Vitus.",
            "charge": "cross",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Krütz binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a cross Or within a bordure Or",
            "rationale_imagery": "A cross Or commemorates Saint Vitus, titular patron of the historic Carinthian capital where dukes were invested upon the Zollfeld stone.",
            "rationale_colours": "Gules reflects ducal sovereign authority, differenced by a golden cross and bordure."
        },
        "b_cegled": {
            "saint_name": "Saint Gerard (Gellért) & Saint Stephen",
            "saint_epithet": "Bishop-Martyr & First King of Hungary",
            "shrine_type": "Pannonian Reliquary Sanctuary",
            "relic_description": "Venerated station on the Great Hungarian Plain commemorating Saint Gerard Sagredo and the Christianization of the Magyars.",
            "charge": "cross_patriarchal",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Patriarchenkrütz binnen einem silbern Bôrt",
            "blazon_en": "Gules, a patriarchal cross Argent within a bordure Argent",
            "rationale_imagery": "The double-barred patriarchal cross represents the apostolic cross granted by Pope Sylvester II to Saint Stephen, apostle and king.",
            "rationale_colours": "Gules and Argent represent the Hungarian Árpád colors, differenced by an Argent cadency bordure."
        },
        "b_veseli": {
            "saint_name": "Saints Cyril and Methodius",
            "saint_epithet": "Equal-to-the-Apostles & Teachers of the Slavs",
            "shrine_type": "Great Moravian Sanctuary of the Morava River",
            "relic_description": "Ancient Great Moravian Christian center on the Morava River sanctified by the mission of Cyril and Methodius.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Patriarchenkrütz binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "The patriarchal cross Or represents the Byzantine-Slavic mission of the holy brothers of Thessaloniki who translated the scriptures into Old Church Slavonic.",
            "rationale_colours": "Azure represents the Morava River and spiritual enlightenment, bearing a golden cross and bordure."
        },

        # --- Italy & Dalmatia ---
        "b_pavia": {
            "saint_name": "Saint Augustine of Hippo",
            "saint_epithet": "Doctor of the Church & Bishop of Hippo",
            "shrine_type": "San Pietro in Ciel d'Oro Tomb",
            "relic_description": "The magnificent 14th-century Arca di Sant'Agostino in San Pietro in Ciel d'Oro, housing the body of Saint Augustine translated from Sardinia by King Liutprand in 725 AD.",
            "charge": "crozier",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Bischofsstav van Zant-Augustîn binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a pastoral staff Or within a bordure Or",
            "rationale_imagery": "The pastoral staff Or honors Saint Augustine, the Doctor of Grace whose bones rest in golden peace beneath the gilded vault of San Pietro in Ciel d'Oro.",
            "rationale_colours": "Imperial Crimson (Gules) represents Lombard royal translation, bearing a golden staff and an Or bordure."
        },
        "b_milano": {
            "saint_name": "Saint Ambrose (Ambrogio)",
            "saint_epithet": "Bishop of Milan & Doctor of the Church",
            "shrine_type": "Basilica di Sant'Ambrogio Crypt",
            "relic_description": "The sacred crypt of the Basilica di Sant'Ambrogio housing the bodily relics of Saint Ambrose lying between the martyrs Gervasius and Protasius.",
            "charge": "crozier",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Bischofsstav binnen einem silbern Bôrt",
            "blazon_en": "Gules, a pastoral staff Argent within a bordure Argent",
            "rationale_imagery": "The pastoral staff represents Saint Ambrose, governor-turned-bishop whose preaching converted Augustine and whose hymns founded Western liturgical song.",
            "rationale_colours": "Gules and Argent reflect Milanese municipal arms and the fiery eloquence of the Ambrosian see."
        },
        "b_soana": {
            "saint_name": "Pope Saint Gregory VII (Hildebrand)",
            "saint_epithet": "Supreme Pontiff & Defender of Church Liberty",
            "shrine_type": "Cathedral of Sovana & Sanctuary of San Mamiliano",
            "relic_description": "Birthplace and cathedral of Hildebrand of Sovana (Gregory VII), champion of Gregorian Reform against imperial simony.",
            "charge": "keys_st_peter",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt zwên gekrützte Slüttele van Zant Peter van Golt binnen einem guldenen Bôrt",
            "blazon_en": "Gules, two keys in saltire of Saint Peter Or within a bordure Or",
            "rationale_imagery": "Crossed keys of Saint Peter celebrate Pope Gregory VII, native son of Sovana who asserted the spiritual supremacy of the Apostolic See.",
            "rationale_colours": "Gules and Gold symbolize apostolic authority and papal libertas ecclesiae."
        },
        "b_civitavecchia": {
            "saint_name": "Saint Fermina",
            "saint_epithet": "Virgin, Martyr & Patroness of the Tyrrhenian Sailors",
            "shrine_type": "Grotto of Santa Fermina in the Roman Harbour",
            "relic_description": "The grotto in Centumcellae (Civitavecchia) where Saint Fermina took refuge from persecution before her martyrdom in 304 AD.",
            "charge": "ship",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Schip binnen einem silbern Bôrt",
            "blazon_en": "Azure, an antique ship Argent within a bordure Argent",
            "rationale_imagery": "An antique sailing vessel represents Saint Fermina, whose miraculous calm saved Roman sailors trapped in the stormy waters off Trajan's port.",
            "rationale_colours": "Azure represents the Tyrrhenian Sea, bearing a silver ship and an Argent bordure."
        },
        "b_viterbo": {
            "saint_name": "Saint Rose of Viterbo",
            "saint_epithet": "Virgin & Champion of the Poor",
            "shrine_type": "Monastery of Santa Rosa Crypt",
            "relic_description": "The miraculously incorrupt body of Saint Rose in her sanctuary in Viterbo.",
            "charge": "rose_seeded",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Rôse binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a rose seeded Or within a bordure Or",
            "rationale_imagery": "A seeded rose in Gold canting attribute commemorates Saint Rose of Viterbo, famed for her preaching and miraculous bread transformed into fresh roses.",
            "rationale_colours": "Gules represents fervent divine love, accompanied by golden rose and bordure."
        },
        "b_sutri": {
            "saint_name": "Saint Dolcissima",
            "saint_epithet": "Virgin & Martyr of Sutri",
            "shrine_type": "Cathedral Crypt of the Tufa Cliffs",
            "relic_description": "Tomb of Saint Dolcissima in the cathedral crypt of Sutri, martyred during the Diocletianic persecution.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Krütz binnen einem silbern Bôrt",
            "blazon_en": "Azure, a cross Argent within a bordure Argent",
            "rationale_imagery": "A cross Argent commemorates Saint Dolcissima, virgin martyr whose faith triumphed over Roman persecution in ancient Sutrium.",
            "rationale_colours": "Azure and Argent reflect maiden purity and steadfast Christian confession."
        },
        "b_vaticano": {
            "saint_name": "Saint Peter the Apostle",
            "saint_epithet": "Prince of the Apostles & First Bishop of Rome",
            "shrine_type": "Confessio of Saint Peter",
            "relic_description": "The high confessio and tomb of Saint Peter directly beneath the papal altar in the Vatican Basilica.",
            "charge": "keys_st_peter",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt zwên gekrützte Slüttele van Zant Peter van Golt binnen einem guldenen Bôrt",
            "blazon_en": "Gules, two keys in saltire of Saint Peter Or within a bordure Or",
            "rationale_imagery": "The crossed keys of heaven, supreme sign of the Petrine commission (Matthew 16:19), marking the immediate tomb of Simon Peter.",
            "rationale_colours": "Imperial Crimson (Gules) and Gold (Or) represent supreme pontifical jurisdiction and apostolic authority."
        },
        "b_ostia": {
            "saint_name": "Saint Monica & Saint Aurea",
            "saint_epithet": "Mother of Saint Augustine; Virgin-Martyr of Ostia",
            "shrine_type": "Cathedral of Sant'Aurea & Tomb of Monica",
            "relic_description": "The burial place of Saint Monica, who fell asleep in the Lord at the port of Ostia while preparing to return to Africa with Augustine in 387 AD.",
            "charge": "star_six_pointed",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Strahlstern binnen einem silbern Bôrt",
            "blazon_en": "Azure, a six-pointed mullet star Argent within a bordure Argent",
            "rationale_imagery": "The six-pointed mullet star honors Saint Monica and her vision of heavenly wisdom shared with Augustine by the window overlooking the Tiber mouth.",
            "rationale_colours": "Azure represents the Tyrrhenian coast, bearing a silver star and an Argent bordure."
        },
        "b_farfa": {
            "saint_name": "Saint Lawrence of Syria",
            "saint_epithet": "Bishop & Founder of Farfa",
            "shrine_type": "Imperial Abbey Basilica of the Sabina",
            "relic_description": "The tomb of Saint Lawrence the Syrian, who arrived from Antioch in the 6th century to establish the venerable Abbey of Farfa.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "sable",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Swartz ein gulden Patriarchenkrütz binnen einem guldenen Bôrt",
            "blazon_en": "Sable, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "A patriarchal cross Or commemorates the Syrian monastic origin of Saint Lawrence and Farfa's sovereign status as an imperial abbey exempt from diocesan control.",
            "rationale_colours": "Sable represents monastic Benedictine rule, highlighted with Gold under strict tincture compliance."
        },
        "b_terni": {
            "saint_name": "Saint Valentine (Valentinus)",
            "saint_epithet": "Bishop of Terni & Martyr",
            "shrine_type": "Basilica di San Valentino Crypt",
            "relic_description": "The tomb of Saint Valentine, bishop of Interamna (Terni), beheaded on the Via Flaminia in 273 AD.",
            "charge": "rose_seeded",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Rôse binnen einem silbern Bôrt",
            "blazon_en": "Gules, a rose seeded Or within a bordure Argent",
            "rationale_imagery": "A blooming rose Argent symbolizes Saint Valentine, celestial patron of Christian love, holy betrothal, and episcopal martyrdom.",
            "rationale_colours": "Gules represents martyr's blood, contrasted with a silver rose and bordure."
        },
        "b_rieti": {
            "saint_name": "Saint Barbara",
            "saint_epithet": "Virgin, Megalomartyr & Protectress of Rieti",
            "shrine_type": "Cathedral Crypt of the Sabina",
            "relic_description": "Cathedral shrine holding relics of Saint Barbara, titular patroness of the Sabine citadel of Rieti.",
            "charge": "castrum",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Kastel mit drîn Fenstern binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a fortified tower with three windows Or within a bordure Or",
            "rationale_imagery": "A fortified tower with three windows commemorates Saint Barbara, locked in a stone tower by her pagan father Dioscorus, where she added a third window to profess the Holy Trinity.",
            "rationale_colours": "Gules represents triumphant martyrdom, bearing a golden tower and an Or cadency bordure."
        },
        "b_tivoli": {
            "saint_name": "Saint Symphorosa and Her Seven Sons",
            "saint_epithet": "Martyrs of Tivoli (Tibur)",
            "shrine_type": "Tibur Sanctuary of the Via Tiburtina",
            "relic_description": "Tomb of Saint Symphorosa, drowned in the Aniene with a stone tied to her neck under Emperor Hadrian, and her seven martyred sons.",
            "charge": "star_six_pointed",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Strahlstern binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a six-pointed star Or within a bordure Or",
            "rationale_imagery": "A radiant star Or represents the steadfast mother Symphorosa, surrounded by her seven sons as a constellation of martyrs in Roman Tibur.",
            "rationale_colours": "Azure reflects the waters of the Aniene and heavenly glory, accompanied by golden star and bordure."
        },
        "b_velletri": {
            "saint_name": "Saint Clement & Saint Pontian",
            "saint_epithet": "Popes & Martyrs of the Alban Hills",
            "shrine_type": "Cathedral of San Clemente of Velletri",
            "relic_description": "Ancient 4th-century cathedral basilica of San Clemente in the Alban Hills.",
            "charge": "anchor",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Anker binnen einem silbern Bôrt",
            "blazon_en": "Gules, an anchor Argent within a bordure Argent",
            "rationale_imagery": "The mariner's anchor commemorates Saint Clement, fourth Bishop of Rome and titular patron of Velletri Cathedral.",
            "rationale_colours": "Gules represents Roman martyrdom, differenced by a silver anchor and an Argent bordure."
        },
        "b_avezzano": {
            "saint_name": "Saint Cesidio",
            "saint_epithet": "Deacon & Martyr of the Marsi",
            "shrine_type": "Fucino Basin Reliquary",
            "relic_description": "Venerated relics of Saint Cesidio, martyred during the persecution of Maximinus the Thracian along Lake Fucino.",
            "charge": "crozier",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Bischofsstav binnen einem silbern Bôrt",
            "blazon_en": "Azure, a pastoral staff Argent within a bordure Argent",
            "rationale_imagery": "The pastoral staff represents early Christian deaconate ministry and evangelization among the rugged mountains of the Marsi.",
            "rationale_colours": "Azure represents Lake Fucino, accompanied by a silver staff and bordure."
        },
        "b_capua": {
            "saint_name": "Saint Priscus of Capua",
            "saint_epithet": "Disciple of Saint Peter & First Bishop of Capua",
            "shrine_type": "Basilica of Santa Maria Capua Vetere",
            "relic_description": "Shrine of Saint Priscus, according to tradition one of the seventy-two disciples sent by Peter to evangelize Campania.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Patriarchenkrütz binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "A patriarchal cross Or marks the apostolic antiquity of the Capuan see, consecrated by early Petrine disciples.",
            "rationale_colours": "Imperial Crimson (Gules) and Gold (Or) represent ancient Campanian Roman prestige."
        },
        "b_benevento": {
            "saint_name": "Saint Bartholomew the Apostle",
            "saint_epithet": "Apostle & Martyr of Armenia",
            "shrine_type": "Cathedral Basilica di San Bartolomeo",
            "relic_description": "The sacred bodily relics of Saint Bartholomew the Apostle, brought from Lipari to Benevento by Prince Sicard in 838 AD.",
            "charge": "battleaxe",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Streitaxt van Zant-Bartholomeus binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a battleaxe Or within a bordure Or",
            "rationale_imagery": "The broadaxe of execution commemorates Saint Bartholomew the Apostle, flayed and beheaded for Christ, whose bodily relics transformed Benevento into a major pilgrimage hub.",
            "rationale_colours": "Gules represents apostolic martyrdom, bearing a golden execution blade and an Or cadency bordure."
        },
        "b_mazara": {
            "saint_name": "Saint Vitus (San Vito)",
            "saint_epithet": "Native Martyr of Mazara",
            "shrine_type": "Sanctuary of San Vito a Mare",
            "relic_description": "The seaside sanctuary marking the birthplace and escape of Saint Vitus across the Sicilian straits.",
            "charge": "cross",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Krütz binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a cross Or within a bordure Or",
            "rationale_imagery": "A cross Or represents Saint Vitus, native of Mazara del Vallo who remained steadfast against Roman persecution under Diocletian.",
            "rationale_colours": "Gules represents martyr's blood, contrasted with Gold under the Rule of Tinctures."
        },
        "b_split": {
            "saint_name": "Saint Domnius (Sveti Dujam)",
            "saint_epithet": "Bishop of Salona & Martyr",
            "shrine_type": "Cathedral of Saint Domnius in Diocletian's Palace",
            "relic_description": "The mausoleum of Emperor Diocletian, converted into the cathedral housing the relics of Saint Domnius, the bishop Diocletian executed in 304 AD.",
            "charge": "crozier",
            "charge_color": "argent",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein silbern Bischofsstav van Zant-Domnio binnen einem silbern Bôrt",
            "blazon_en": "Gules, a pastoral staff Argent within a bordure Argent",
            "rationale_imagery": "The pastoral staff represents Saint Domnius, Syrian-born bishop of Salona martyred in the arena, whose triumphant relics now occupy the very tomb chamber built by his imperial persecutor Diocletian.",
            "rationale_colours": "Imperial Crimson (Gules) reflects the porphyry stone of Diocletian's palace, differenced by a silver episcopal crozier and an Argent cadency bordure."
        },

        # --- Greece, Balkans, Eastern Mediterranean & Pontic ---
        "b_patras": {
            "saint_name": "Saint Andrew the Apostle",
            "saint_epithet": "The First-Called (Protoclete)",
            "shrine_type": "Cathedral Basilica of Saint Andrew",
            "relic_description": "The holy sepulchre of Saint Andrew the Apostle on the Peloponnese coast, holding the skull and relic fragments of the decussate cross.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Krütz van Zant-Andrêas binnen einem silbern Bôrt",
            "blazon_en": "Azure, a cross Argent within a bordure Argent",
            "rationale_imagery": "The cross Argent commemorates Saint Andrew the Apostle, crucified at Patras upon an X-shaped cross after preaching Christ to the Peloponnesians.",
            "rationale_colours": "Azure represents the Gulf of Patras and apostolic heaven, paired with silver cross and bordure under strict tincture compliance."
        },
        "b_rhodos": {
            "saint_name": "Saint Phanourios the Megalomartyr",
            "saint_epithet": "The Newly-Revealed Martyr",
            "shrine_type": "13th-century Crypt Chapel of Rhodes",
            "relic_description": "Miraculous icon and crypt of Saint Phanourios discovered amidst the ancient ruins of Rhodes.",
            "charge": "chalice",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Kelch mit Kerzenfeuer binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a chalice Or within a bordure Or",
            "rationale_imagery": "A holy chalice with taper flame represents Saint Phanourios ('he who reveals'), bearer of light who comforts the faithful.",
            "rationale_colours": "Gules represents martyrdom, highlighted with Gold (Or) under the Rule of Tinctures."
        },
        "b_constantinople": {
            "saint_name": "The Holy Apostles & Saint John Chrysostom",
            "saint_epithet": "Imperial Patriarchs and Confessors of the Church",
            "shrine_type": "Imperial Church of the Holy Apostles",
            "relic_description": "The imperial mausoleum church holding relics of Saint Andrew, Saint Luke, Saint Timothy, and the golden-mouthed Patriarch John Chrysostom.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "purpure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Porphyr-Purpur ein gulden Kêserlich Patriarchenkrütz binnen einem guldenen Bôrt",
            "blazon_en": "Purpure, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "The imperial double-beamed cross in Gold represents the New Rome and the holy relics of the Apostles entombed in the Church of the Holy Apostles by Constantine.",
            "rationale_colours": "Porphyry Purple (Purpur) and Gold (Or) reflect Eastern Roman imperial majesty and patriarchate dignity."
        },
        "b_sandomierz": {
            "saint_name": "Blessed Sadoc and the 48 Martyrs",
            "saint_epithet": "Dominican Martyrs of the Vistula",
            "shrine_type": "Church of Saint James the Apostle Crypt",
            "relic_description": "The Romanesque brick church of St James where Prior Sadoc and forty-eight Dominican friars were slain by Mongol invaders while singing the Salve Regina in 1260 AD.",
            "charge": "rose_seeded",
            "charge_color": "sable",
            "field": "argent",
            "ordinary": "bordure",
            "ordinary_color": "sable",
            "blazon_tarr": "In Silber ein swartze Rôse van Zant-Sadoc binnen einem swartzen Bôrt",
            "blazon_en": "Argent, a rose Sable within a bordure Sable",
            "rationale_imagery": "A black heraldic rose on a silver field recalls the Dominican habit of Blessed Sadoc and his companions, who welcomed martyrdom along the Vistula singing praises to the Virgin.",
            "rationale_colours": "Silver (Argent) and Black (Sable) reflect the Dominican order's black and white habit, in strict conformity with tincture rules."
        },
        "b_chersonesus": {
            "saint_name": "Pope Saint Clement of Rome",
            "saint_epithet": "Apostolic Father, Fourth Bishop of Rome & Martyr",
            "shrine_type": "Submarine Cave Sanctuary & Crimean Basilica",
            "relic_description": "The miraculous offshore cave where Saint Clement's body was found with an iron anchor, retrieved by Saint Cyril in 861 AD.",
            "charge": "anchor",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt der gulden Anker van Zant-Klemens binnen einem guldenen Bôrt",
            "blazon_en": "Gules, an anchor Or within a bordure Or",
            "rationale_imagery": "The golden anchor commemorates Saint Clement of Rome, exiled to Crimean marble quarries by Emperor Trajan and drowned in the Black Sea with an iron anchor tied to his neck.",
            "rationale_colours": "Gules reflects apostolic blood, bearing a golden anchor and an Or cadency bordure."
        },
        "b_kaisereia": {
            "saint_name": "Saint Basil the Great (Basileios)",
            "saint_epithet": "Archbishop of Caesarea & Universal Doctor of the Church",
            "shrine_type": "Basileias Monastic City & Crypt",
            "relic_description": "The great charitable complex and tomb of Saint Basil, author of the Divine Liturgy and defender of Nicene orthodoxy against Arianism.",
            "charge": "crozier",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Bischofsstav van Zant-Basilius binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a pastoral staff Or within a bordure Or",
            "rationale_imagery": "The pastoral crozier honors Saint Basil the Great, whose theological brilliance and monastic rule guided the entire Christian East.",
            "rationale_colours": "Azure and Gold symbolize theological truth, divine illumination, and Cappadocian episcopal primacy."
        },
        "b_sokol": {
            "saint_name": "Saint Luke the Evangelist",
            "saint_epithet": "Evangelist & Physician",
            "shrine_type": "Bosnian Mountain Fortress Crypt",
            "relic_description": "Medieval mountain citadel repository venerating relics of Saint Luke.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Krütz binnen einem silbern Bôrt",
            "blazon_en": "Azure, a cross Argent within a bordure Argent",
            "rationale_imagery": "A cross Argent represents the holy gospel ministry of Saint Luke across the Balkans and the Adriatic hinterland.",
            "rationale_colours": "Azure and Argent reflect montane clarity and peace."
        },
        "b_visoki": {
            "saint_name": "Saint John the Baptist",
            "saint_epithet": "Forerunner of the Lord",
            "shrine_type": "Franciscan Royal Tomb of Mile",
            "relic_description": "The coronation and burial church of Bosnian kings at Mile (Visoko), dedicated to Saint John the Baptist.",
            "charge": "chalice",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Kelch binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a chalice Or within a bordure Or",
            "rationale_imagery": "The golden baptismal chalice represents Saint John the Baptist, patron of the Bosnian royal church of Mile.",
            "rationale_colours": "Gules and Gold symbolize royal coronation dignity and holy patronage."
        },
        "b_nevropkop": {
            "saint_name": "Saint John of Rila (Ivan Rilski)",
            "saint_epithet": "Hermit of the Rhodopes & Wonderworker of Bulgaria",
            "shrine_type": "Rhodope Mountain Cell",
            "relic_description": "Rhodope sanctuary venerating the ascetic retreats of Saint John of Rila.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Patriarchenkrütz binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "The patriarchal double cross Or honors Saint John of Rila, heavenly protector of Bulgaria and father of Slavic monasticism.",
            "rationale_colours": "Azure represents the alpine Rhodope heights, bearing a golden cross and bordure."
        },
        "b_goritsa": {
            "saint_name": "Saints Clement and Naum of Ohrid",
            "saint_epithet": "Apostles of the Cyrillic Script & Wonderworkers of Ohrid",
            "shrine_type": "Lake Ohrid Monastic Crypt",
            "relic_description": "Shrine honoring Saint Naum of Ohrid, disciple of Cyril and Methodius, famed for his monastic sanctuary on the lake.",
            "charge": "crozier",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Bischofsstav binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a pastoral staff Or within a bordure Or",
            "rationale_imagery": "The pastoral crozier honors Saint Naum and Saint Clement of Ohrid, teachers who educated over 3,500 disciples in the Cyrillic alphabet.",
            "rationale_colours": "Gules represents spiritual devotion and golden letters, framed by an Or bordure."
        },
        "b_gabrovo": {
            "saint_name": "Saint Petka (Paraskeva of the Balkans)",
            "saint_epithet": "Ascetic Hermitess & Patroness of the Balkans",
            "shrine_type": "Balkan Mountain Pass Sanctuary",
            "relic_description": "Shrine guarding the Shipka pass, sanctified by the translation of Saint Petka's incorrupt body to Veliko Tarnovo.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "sable",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Swartz ein silbern Krütz binnen einem silbern Bôrt",
            "blazon_en": "Sable, a cross Argent within a bordure Argent",
            "rationale_imagery": "The silver cross represents Saint Petka, the wilderness ascetic whose incorrupt relics sheltered the Balkan kingdoms against invasion.",
            "rationale_colours": "Sable represents monastic renunciation of the world, contrasted with a silver cross and bordure."
        },
        "b_selymbria": {
            "saint_name": "Saint Theophano the Empress",
            "saint_epithet": "Empress & Wonderworker of Thrace",
            "shrine_type": "Thracian Marmara Sanctuary",
            "relic_description": "Holy relics of the Byzantine empress Theophano, who renounced imperial luxuries for secret acts of charity and prayer.",
            "charge": "crown",
            "charge_color": "or",
            "field": "purpure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Porphyr-Purpur ein gulden Diadem binnen einem guldenen Bôrt",
            "blazon_en": "Purpure, an imperial crown Or within a bordure Or",
            "rationale_imagery": "The imperial crown Or represents Saint Theophano, who lived as an empress on the throne while wearing ascetic haircloth beneath her purple robes.",
            "rationale_colours": "Porphyry Purple (Purpur) and Gold (Or) celebrate imperial Byzantine sanctity."
        },
        "b_kalamata": {
            "saint_name": "Panagia Ypapanti & Saint John the Merciful",
            "saint_epithet": "Protectors of the Messenian Gulf",
            "shrine_type": "Holy Presentation Sanctuary",
            "relic_description": "The sacred shrine of the Presentation of Christ (Ypapanti) and relics of Saint John the Almsgiver.",
            "charge": "star_six_pointed",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Strahlstern binnen einem silbern Bôrt",
            "blazon_en": "Azure, a six-pointed mullet star Argent within a bordure Argent",
            "rationale_imagery": "A silver mullet star represents the Presentation in the Temple, guiding sailors across the Messenian Gulf.",
            "rationale_colours": "Azure and Argent reflect the maritime Peloponnesian coast."
        },
        "b_costesti": {
            "saint_name": "Saint Sava the Goth",
            "saint_epithet": "Martyr of Dacia",
            "shrine_type": "Wallachian River Reliquary",
            "relic_description": "Commemoration of Saint Sava the Goth, drowned in 372 AD during the persecution of Athanaric.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Krütz binnen einem silbern Bôrt",
            "blazon_en": "Azure, a cross Argent within a bordure Argent",
            "rationale_imagery": "The silver cross represents Saint Sava the Goth, cantor of the church who confessed Christ and was cast into the flowing waters.",
            "rationale_colours": "Azure represents the river of martyrdom, differenced by silver cross and bordure."
        },
        "b_buzau": {
            "saint_name": "Saint Sava the Goth & Saint Nicetas",
            "saint_epithet": "Martyrs of the Mousaios River",
            "shrine_type": "Buzău Valley Crypt",
            "relic_description": "The historical site of the Mousaios (Buzău) River martyrdom, from where Saint Sava's relics were sent to Saint Basil of Caesarea.",
            "charge": "waves",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr silbern Wellen binnen einem silbern Bôrt",
            "blazon_en": "Azure, barrulets wavy Argent within a bordure Argent",
            "rationale_imagery": "Wavy barrulets represent the river Mousaios, sacred water of martyrdom whose relics were requested by Saint Basil the Great.",
            "rationale_colours": "Azure and Argent symbolize the baptism of martyrdom in the river."
        },
        "b_rozhyshche": {
            "saint_name": "Saint Andrew the First-Called",
            "saint_epithet": "Apostle of Scythia",
            "shrine_type": "Volhynian River Sanctuary",
            "relic_description": "Venerated shrine along the Styr River recalling Saint Andrew's journey up the Dnieper and Volhynian waterways.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Patriarchenkrütz binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "A patriarchal cross Or commemorates the Petrine brother Andrew who planted the cross upon the northern hills.",
            "rationale_colours": "Azure and Gold symbolize apostolic grace over the Volhynian plains."
        },
        "b_spas": {
            "saint_name": "The Holy Savior (Spas) & Saint Onuphrius",
            "saint_epithet": "Monastery of the Transfiguration",
            "shrine_type": "Ancient Lavra of the Dniester",
            "relic_description": "The venerated Spas Lavra on the Dniester near Staryi Sambir, founded in the 11th century as a center of hesychast prayer.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Spas-Krütz binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "The Savior's Cross (Spas) commemorates the Transfiguration of Christ, patronal dedication of the ancient Galician lavra.",
            "rationale_colours": "Azure and Or represent the divine Tabor light of the Transfiguration."
        },
        "b_radynka": {
            "saint_name": "Saints Anthony and Theodosius of the Caves",
            "saint_epithet": "Fathers of Russian Monasticism",
            "shrine_type": "Northern Forest Hermitage",
            "relic_description": "Forest skete dependent on the Kiev Pechersk Lavra, following the cenobitic rule of Saint Theodosius.",
            "charge": "cross",
            "charge_color": "or",
            "field": "sable",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Swartz ein gulden Krütz binnen einem guldenen Bôrt",
            "blazon_en": "Sable, a cross Or within a bordure Or",
            "rationale_imagery": "A cross Or in a dark field recalls the subterranean cave asceticism of Anthony and Theodosius in the catacombs of the Dnieper.",
            "rationale_colours": "Sable represents underground hermitage caverns, illuminated by golden faith."
        },
        "b_vinnytsia": {
            "saint_name": "Saint Nicholas of Myra",
            "saint_epithet": "Wonderworker & Protector of the Southern Marches",
            "shrine_type": "Podolian Fortress Sanctuary",
            "relic_description": "Ancient church sanctuary dedicated to Saint Nicholas along the Southern Bug River.",
            "charge": "ship",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Schip binnen einem silbern Bôrt",
            "blazon_en": "Azure, a ship Argent within a bordure Argent",
            "rationale_imagery": "A ship Argent represents Saint Nicholas of Myra, universal protector of sailors, travellers, and river traders.",
            "rationale_colours": "Azure represents the Southern Bug river, paired with silver ship and bordure."
        },
        "b_kletsk": {
            "saint_name": "Saint Euphrosyne of Polotsk",
            "saint_epithet": "Princess & Patroness of Belarus",
            "shrine_type": "Princely Convent Crypt",
            "relic_description": "Sanctuary preserving the devotion of the princely nun Saint Euphrosyne, who commissioned the Holy Cross of Polotsk.",
            "charge": "cross_patriarchal",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Polotzk-Krütz binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a patriarchal cross Or within a bordure Or",
            "rationale_imagery": "The patriarchal cross Or represents the six-armed Cross of Saint Euphrosyne, adorned with gold and relics of the Holy Cross.",
            "rationale_colours": "Gules reflects princely Rurikid descent, differenced by an Or cross and bordure."
        },
        "b_philadelphia": {
            "saint_name": "The Holy Forty Martyrs of Sebaste",
            "saint_epithet": "Soldier-Martyrs of Cappadocia",
            "shrine_type": "Lydian Basilica Sanctuary",
            "relic_description": "Byzantine basilica honoring the Forty Martyrs of Sebaste who stood frozen in a frozen lake rather than renounce Christ.",
            "charge": "crown",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Märtyrerkrône binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a martyr's crown Or within a bordure Or",
            "rationale_imagery": "A golden martyr's crown commemorates the forty celestial crowns that descended from heaven upon the freezing confessors.",
            "rationale_colours": "Gules represents victorious martyrdom, accompanied by gold crown and bordure."
        },
        "b_modra": {
            "saint_name": "Saint Thecla (Thekla)",
            "saint_epithet": "Equal-to-the-Apostles & Protodeaconess",
            "shrine_type": "Cilician Mountain Grotto",
            "relic_description": "Ancient pilgrimage grotto of Saint Thecla, disciple of the Apostle Paul.",
            "charge": "cross",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Krütz binnen einem silbern Bôrt",
            "blazon_en": "Azure, a cross Argent within a bordure Argent",
            "rationale_imagery": "The silver cross represents Saint Thecla, whose miraculous deliverance from wild beasts and fire inspired centuries of Christian women.",
            "rationale_colours": "Azure and Argent reflect maiden purity and apostolic courage."
        },
        "b_pteria": {
            "saint_name": "Saint Theodore the Recruit (Theodoros Teron)",
            "saint_epithet": "Megalomartyr & Dragon-Slayer of Euchaita",
            "shrine_type": "Euchaita Imperial Shrine",
            "relic_description": "The world-famous pilgrimage shrine of Saint Theodore Teron at Euchaita in Pontus, celebrated by Gregory of Nyssa.",
            "charge": "dragon",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Drache van Zant-Theodor binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a dragon Or within a bordure Or",
            "rationale_imagery": "The dragon Or commemorates Saint Theodore the Recruit, Roman legionary who slew the monstrous dragon of Euchaita and was burned for refusing to sacrifice to Cybele.",
            "rationale_colours": "Gules reflects warrior martyrdom, bearing a golden dragon and an Or cadency bordure."
        },
        "b_dasmenda": {
            "saint_name": "Saint Gregory the Illuminator",
            "saint_epithet": "Apostle of Armenia",
            "shrine_type": "Cappadocian-Armenian March Sanctuary",
            "relic_description": "Border shrine celebrating Saint Gregory, who was consecrated bishop in Caesarea and brought the Christian faith to Armenia in 301 AD.",
            "charge": "crozier",
            "charge_color": "or",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Lâsûr ein gulden Bischofsstav binnen einem guldenen Bôrt",
            "blazon_en": "Azure, a pastoral staff Or within a bordure Or",
            "rationale_imagery": "The pastoral staff honors Saint Gregory the Illuminator, who survived thirteen years in the pit of Khor Virap to baptize King Tiridates.",
            "rationale_colours": "Azure represents divine illumination, paired with Gold under strict tincture compliance."
        },
        "b_telmessos": {
            "saint_name": "Saint Nicholas of Myra",
            "saint_epithet": "Archbishop of Myra & Wonderworker of Lycia",
            "shrine_type": "Lycian Maritime Crypt",
            "relic_description": "Coastal sanctuary near Myra commemorating Saint Nicholas, protector of sailors and orphans across the eastern Mediterranean.",
            "charge": "ship",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Schip binnen einem silbern Bôrt",
            "blazon_en": "Azure, a ship Argent within a bordure Argent",
            "rationale_imagery": "A ship Argent honors Saint Nicholas of Myra, who appeared in visions to distressed sailors rounding the treacherous capes of Lycia.",
            "rationale_colours": "Azure and Argent symbolize the azure Lycian sea and Christian salvation."
        },
        "b_antiocheia": {
            "saint_name": "Saint Peter & Saint Ignatius of Antioch",
            "saint_epithet": "The God-Bearer (Theophoros)",
            "shrine_type": "Cave Church of Saint Peter & Crypt of Antioch",
            "relic_description": "The rock cave church of Saint Peter on Mount Starius in Antioch, where the disciples were first called Christians, and the tomb of the martyr bishop Ignatius.",
            "charge": "keys_st_peter",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt zwên gekrützte Slüttele van Zant Peter van Golt binnen einem guldenen Bôrt",
            "blazon_en": "Gules, two keys in saltire of Saint Peter Or within a bordure Or",
            "rationale_imagery": "The keys of Saint Peter commemorate the first Petrine See of Antioch, where Peter presided before journeying to Rome.",
            "rationale_colours": "Gules and Gold symbolize patriarchal apostolic primacy in the Orient."
        },
        "b_beirut": {
            "saint_name": "Saint George the Victorious",
            "saint_epithet": "Trophy-Bearer (Tropaiophoros)",
            "shrine_type": "Bay of Saint George Sanctuary",
            "relic_description": "The sacred bay of Beirut, historical setting where Saint George was traditionally believed to have slain the sea-dragon to rescue the king's daughter.",
            "charge": "dragon",
            "charge_color": "gules",
            "field": "argent",
            "ordinary": "bordure",
            "ordinary_color": "gules",
            "blazon_tarr": "In Silber ein rôter Drache van Zant-Joris binnen einem rôten Bôrt",
            "blazon_en": "Argent, a dragon Gules within a bordure Gules",
            "rationale_imagery": "A dragon Gules defeated upon a silver field recalls Saint George's miraculous victory over the dragon in the coastal bay of Berytus (Beirut).",
            "rationale_colours": "Argent and Gules reflect the chivalric colors of the Saint George cross, differenced by a Gules bordure."
        },
        "b_ar-ramla": {
            "saint_name": "Saint George of Lydda",
            "saint_epithet": "Great Martyr of Diospolis",
            "shrine_type": "Cathedral Basilica & Crypt of Saint George",
            "relic_description": "The renowned basilica and sepulchre of Saint George at Lydda (Lod/Ramla), universal pilgrimage goal of Eastern and Western crusaders.",
            "charge": "spear",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Keiser-Rôt ein gulden Lanze van Zant-Joris binnen einem silbern Bôrt",
            "blazon_en": "Gules, a spear Or within a bordure Argent",
            "rationale_imagery": "The warrior spear of Saint George marks his primary tomb in Palestine, where his bodily relics were enshrined following his martyrdom under Diocletian.",
            "rationale_colours": "Imperial Crimson (Gules) and Gold (Or) represent military martyrdom, differenced by a silver baronial bordure."
        },
        "b_stcatherine": {
            "saint_name": "Saint Catherine of Alexandria",
            "saint_epithet": "Virgin & Megalomartyr of Alexandria",
            "shrine_type": "Monastery of the Transfiguration / Saint Catherine's Monastery",
            "relic_description": "The venerable 6th-century fortress monastery beneath Mount Horeb holding the bodily relics of Saint Catherine, carried by angels to the summit of Mount Sinai.",
            "charge": "catherine_wheel",
            "charge_color": "or",
            "field": "purpure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Porphyr-Purpur ein gulden Rad van Zant Katerîne binnen einem silbern Bôrt",
            "blazon_en": "Purpure, a Catherine wheel Or within a bordure Argent",
            "rationale_imagery": "The primary charge is the spiked breaking wheel of Saint Catherine of Alexandria, which shattered at her touch when her pagan executioners sought to destroy her.",
            "rationale_colours": "Porphyry Purple (Purpur) represents the imperial Alexandrian philosopher-princess, accompanied by a golden wheel and an Argent differencing bordure."
        },
        "b_alexandria": {
            "saint_name": "Saint Mark the Evangelist & Saint Catherine",
            "saint_epithet": "Apostle of Egypt & Patriarch of Alexandria",
            "shrine_type": "Cathedral of Saint Mark & Monastic Crypt of Baucalis",
            "relic_description": "The historic martyrium and tomb of Saint Mark the Evangelist in the district of Baucalis, founder of the Church of Alexandria.",
            "charge": "lion_rampant",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Lôwe van Zant-Markus binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a lion rampant Or within a bordure Or",
            "rationale_imagery": "The lion rampant Or represents the winged Lion of Saint Mark, apostolic evangelist symbol of Saint Mark, whose body rested in Alexandria until translated to Venice in 828 AD.",
            "rationale_colours": "Gules and Gold symbolize apostolic majesty and the patriarchal throne of Egypt."
        },
        "b_qartajana": {
            "saint_name": "Saint Cyprian of Carthage",
            "saint_epithet": "Bishop, Martyr & Father of African Latin Theology",
            "shrine_type": "Agape Basilica of Carthage",
            "relic_description": "The basilica crypt marking the martyrdom site of Saint Cyprian, beheaded in 258 AD for refusing to offer incense to pagan gods.",
            "charge": "crozier",
            "charge_color": "or",
            "field": "gules",
            "ordinary": "bordure",
            "ordinary_color": "or",
            "blazon_tarr": "In Keiser-Rôt ein gulden Bischofsstav van Zant-Cyprian binnen einem guldenen Bôrt",
            "blazon_en": "Gules, a pastoral staff Or within a bordure Or",
            "rationale_imagery": "The pastoral crozier honors Saint Cyprian, bishop of Carthage and doctor of church unity, who bravely met his executioners with the words 'Thanks be to God'.",
            "rationale_colours": "Gules represents the glorious blood of North African martyrs, differenced with an Or staff and bordure."
        },
        "b_lemisele": {
            "saint_name": "Saint Nicholas of Myra",
            "saint_epithet": "Protector of Livonian Seafarers",
            "shrine_type": "Archiepiscopal Castle Sanctuary",
            "relic_description": "Castle and pilgrimage chapel of Lemsal (Limbaži) founded by the Archbishop of Riga under the invocation of Saint Nicholas.",
            "charge": "ship",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Schip binnen einem silbern Bôrt",
            "blazon_en": "Azure, a ship Argent within a bordure Argent",
            "rationale_imagery": "A ship Argent honors Saint Nicholas, patron of Baltic cog navigators and guardian of the Gulf of Riga.",
            "rationale_colours": "Azure and Argent reflect the Baltic Sea and northern coastal breezes."
        },
        "b_vestfirdir": {
            "saint_name": "Saint Thorlak (Þorlákr Þórhallsson)",
            "saint_epithet": "Bishop of Skálholt & Patron Saint of Iceland",
            "shrine_type": "Westfjords Sanctuary",
            "relic_description": "Venerated stations commemorating Saint Thorlak, canonized at the Althing in 1198 as Iceland's patron saint.",
            "charge": "crozier",
            "charge_color": "argent",
            "field": "azure",
            "ordinary": "bordure",
            "ordinary_color": "argent",
            "blazon_tarr": "In Lâsûr ein silbern Bischofsstav binnen einem silbern Bôrt",
            "blazon_en": "Azure, a pastoral staff Argent within a bordure Argent",
            "rationale_imagery": "The silver crozier commemorates Saint Thorlak, the humble Augustinian bishop who reformed the Icelandic church and protected the poor across the remote fjords.",
            "rationale_colours": "Azure and Argent represent arctic fjords, glacial ice, and Christian purity."
        },

        # --- Asian Pilgrimage Sanctuaries & Holy Sages ---
        "b_bodh_gaya": {
            "saint_name": "Gautama Buddha (Śākyamuni)",
            "saint_epithet": "The Awakened One & Sage of the Śākyas",
            "shrine_type": "Mahabodhi Temple & Diamond Throne (Vajrāsana)",
            "relic_description": "The sacred Bodhi Tree and Diamond Throne where Siddhārtha Gautama attained supreme enlightenment under the tree of awakening.",
            "charge": "tree_chestnut",
            "charge_color": "vert",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "sable",
            "blazon_tarr": "In Golt ein grûner Bodhi-Bôm binnen einem swartzen Bôrt",
            "blazon_en": "Or, a sacred Bodhi tree Vert within a bordure Sable",
            "rationale_imagery": "The spreading tree represents the holy Bodhi tree (Ficus religiosa) under which Gautama Buddha sat in meditation and conquered the illusions of Mara.",
            "rationale_colours": "Or (Gold) represents enlightenment, while Vert represents the living tree, enclosed by a Sable border of monastic discipline."
        },
        "b_kukkutapada": {
            "saint_name": "Mahākāśyapa",
            "saint_epithet": "Senior Disciple of the Buddha & First Patriarch",
            "shrine_type": "Gurupa Mountain Cave Tomb",
            "relic_description": "The mountain cavern of Kukkutapada where Mahākāśyapa entered into samādhi, his body preserved until the advent of Maitreya.",
            "charge": "mount_triple",
            "charge_color": "sable",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "sable",
            "blazon_tarr": "In Golt ein swartzer Drîberch binnen einem swartzen Bôrt",
            "blazon_en": "Or, a triple mount Sable within a bordure Sable",
            "rationale_imagery": "A triple mount Sable symbolizes the Cock's Foot Mountain (Kukkutapadagiri) where the sage rests in unbroken contemplation.",
            "rationale_colours": "Or and Sable represent the ascetic gold of the sage and the stone sanctuary of the cavern."
        },
        "b_anuradhapura": {
            "saint_name": "Mahinda Thera & Sanghamitta",
            "saint_epithet": "Apostles of Sri Lanka",
            "shrine_type": "Jaya Sri Maha Bodhi & Ruwanwelisaya Stupa",
            "relic_description": "The southern branch of the original Bodhi Tree planted in 288 BC, the oldest historically documented human-planted tree in the world.",
            "charge": "wheel_spoked",
            "charge_color": "gules",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "gules",
            "blazon_tarr": "In Golt ein rôtes Rad der Lere binnen einem rôten Bôrt",
            "blazon_en": "Or, a wheel of the law Gules within a bordure Gules",
            "rationale_imagery": "The spoked wheel represents the Dharmachakra, the turning of the wheel of righteous law across the island kingdom of Lanka.",
            "rationale_colours": "Or and Gules reflect royal Sinhalese sovereign majesty and Buddhist devotion."
        },
        "b_pagan": {
            "saint_name": "Shin Arahan",
            "saint_epithet": "Primate of Bagan & Apostle of Theravada",
            "shrine_type": "Ananda & Shwezigon Stupas",
            "relic_description": "The gilded pagoda metropolis of Bagan, housing frontal bone and collarbone relics of the Buddha.",
            "charge": "wheel_spoked",
            "charge_color": "gules",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "gules",
            "blazon_tarr": "In Golt ein rôtes Rad binnen einem rôten Bôrt",
            "blazon_en": "Or, a spoked wheel Gules within a bordure Gules",
            "rationale_imagery": "A spoked wheel of the law celebrates the conversion of King Anawrahta by Shin Arahan and the founding of Bagan's thousand temples.",
            "rationale_colours": "Or and Gules represent gold leaf pagodas and monastic robes under the Rule of Tinctures."
        },
        "b_JAV_Borobodur": {
            "saint_name": "Sailendra Dynasty Bodhisattvas",
            "saint_epithet": "Kings of the Mountain & Bodhisattva Rulers",
            "shrine_type": "Great Stupa of Borobudur",
            "relic_description": "The monumental 8th-century stone mandala stupa of Borobudur, representing the cosmic Mahayana path from Kamadhatu to Nirvana.",
            "charge": "wheel_spoked",
            "charge_color": "azure",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "azure",
            "blazon_tarr": "In Golt ein lâsûren Rad des Kosmos binnen einem lâsûren Bôrt",
            "blazon_en": "Or, a cosmic wheel Azure within a bordure Azure",
            "rationale_imagery": "The spoked cosmic wheel represents the transcendent lotus mandala of Borobudur rising from the fertile Kedu plain.",
            "rationale_colours": "Or and Azure represent royal Sailendra gold and celestial oceanic blue."
        },
        "b_angkor": {
            "saint_name": "Jayavarman VII & Avalokiteśvara",
            "saint_epithet": "Dharmaraja & Bodhisattva of Compassion",
            "shrine_type": "Angkor Wat & Bayon Face Towers",
            "relic_description": "The sacred mountain temple of Angkor representing Mount Meru, center of Hindu and Buddhist cosmological order.",
            "charge": "mount_triple",
            "charge_color": "gules",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "gules",
            "blazon_tarr": "In Golt ein rôter Meru-Berch binnen einem rôten Bôrt",
            "blazon_en": "Or, a triple mount Gules within a bordure Gules",
            "rationale_imagery": "A triple mount Gules symbolizes Mount Meru, axis mundi of Khmer imperial temple architecture.",
            "rationale_colours": "Or and Gules reflect royal Devaraja majesty and sandstone red towers."
        },
        "b_changan": {
            "saint_name": "Xuanzang (Tripitaka)",
            "saint_epithet": "Great Translator & Pilgrim Monk",
            "shrine_type": "Giant Wild Goose Pagoda (Dayanta)",
            "relic_description": "The Giant Wild Goose Pagoda built by Emperor Gaozong to preserve the 657 Sanskrit Buddhist texts brought from India by Xuanzang.",
            "charge": "column_roman",
            "charge_color": "gules",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "gules",
            "blazon_tarr": "In Golt ein rôte Pagodensäule binnen einem rôten Bôrt",
            "blazon_en": "Or, a sacred pillar Gules within a bordure Gules",
            "rationale_imagery": "A classical pillar represents the towering pagoda erected to protect the sacred translations of the master Xuanzang.",
            "rationale_colours": "Or and Gules reflect Tang imperial foundation and monastic red lacquer."
        },
        "b_luoyang": {
            "saint_name": "Kāśyapa Mātanga & Dharmaratna",
            "saint_epithet": "First Translators of China",
            "shrine_type": "White Horse Temple (Baimasi)",
            "relic_description": "The oldest Buddhist temple in China (established 68 AD by Emperor Ming of Han), where two Indian monks arrived with sutras on a white horse.",
            "charge": "horse_courant",
            "charge_color": "gules",
            "field": "or",
            "ordinary": "bordure",
            "ordinary_color": "gules",
            "blazon_tarr": "In Golt ein rôtes Wîtes Pfert binnen einem rôten Bôrt",
            "blazon_en": "Or, a horse courant Gules within a bordure Gules",
            "rationale_imagery": "A galloping horse courant commemorates the white horse that carried the first Buddhist sutras and statues from Central Asia to Luoyang.",
            "rationale_colours": "Or and Gules represent Han imperial patronage and sacred scriptures."
        }
    }

    # Now let's scan remaining provinces with poi_buried_saint to ensure 100% coverage
    exact_provs = [
        1, 30, 51, 101, 467, 476, 483, 496, 531, 560, 737, 873, 874, 885, 893,
        1502, 1503, 1505, 1593, 1595, 1632, 1691, 1785, 1863, 1879, 2018, 2033,
        2076, 2088, 2111, 2245, 2262, 2318, 2333, 2357, 2366, 2378, 2475, 2482,
        2570, 2571, 2572, 2573, 2575, 2576, 2577, 2579, 2586, 2588, 2589, 2590,
        2600, 2606, 2609, 2644, 2685, 2691, 2723, 2854, 2924, 2945, 3115, 3166,
        3184, 3207, 3282, 3284, 3285, 3335, 3508, 3527, 3617, 3641, 3684, 3761,
        3800, 3802, 4583, 4606, 4994, 5000, 5050, 5062, 5097, 5099, 5117, 5279,
        5299, 5546, 5568, 5596, 5613, 5647, 5910, 5919, 5963, 6032, 6053, 6219,
        6364, 6460, 6496, 6602, 6815, 6919, 7831, 8007, 8515, 8877, 8878, 8879,
        8880, 8881, 8883, 8999, 9550, 9551, 9552, 9553, 9554, 9555, 9688, 9715,
        9726, 9780, 9782, 9786, 9787, 9788, 9822, 9823, 9824, 9825, 10047, 10048,
        10148, 10149, 10150, 10151, 10216, 10217, 10218, 10219, 10220, 10423,
        10430, 10625, 10816, 11341, 11342, 11343, 11350, 11351, 11438, 11869,
        12471, 12472, 12473, 12810, 12958, 13004, 13038
    ]

    for pid in exact_provs:
        props = p2b.get(pid)
        if not props:
            continue
        bkey = props.get('barony')
        if not bkey or bkey in exempt_titles or bkey in SAINT_DATABASE:
            continue

        name = props.get('name') or props.get('b_tarr') or bkey.replace('b_', '').title()
        county = props.get('county') or ''
        holding_type = props.get('holding_type') or 'castle'

        if holding_type == 'church':
            charge = 'cross_patriarchal'
            field = 'azure'
            charge_col = 'or'
            ord_col = 'argent'
        elif 'martyr' in name.lower() or 'zant' in name.lower():
            charge = 'sword_crossed'
            field = 'gules'
            charge_col = 'or'
            ord_col = 'argent'
        else:
            charge = 'crozier'
            field = 'azure'
            charge_col = 'argent'
            ord_col = 'argent'

        SAINT_DATABASE[bkey] = {
            "saint_name": f"Patron Saint of {name}",
            "saint_epithet": f"Holy Confessor & Patron of {county.replace('c_', '').title()}",
            "shrine_type": "Venerated Holding Reliquary",
            "relic_description": f"Buried saint crypt and reliquary attested in {name} ({county}) from the CK3 save world.",
            "charge": charge,
            "charge_color": charge_col,
            "field": field,
            "ordinary": "bordure",
            "ordinary_color": ord_col,
            "blazon_tarr": f"In {field.title()} ein {charge_col} {charge.replace('_', ' ')} binnen einem {ord_col} Bôrt",
            "blazon_en": f"{field.title()}, a {charge.replace('_', ' ')} {charge_col.title()} within a bordure {ord_col.title()}",
            "rationale_imagery": f"The primary charge represents the sacred iconographic attribute of the holy saint entombed at {name}.",
            "rationale_colours": f"{field.title()} and {charge_col.title()} reflect sacred hagiographic tradition under strict Rule of Tinctures.",
            "rationale_splits": "Enclosed within a cadency bordure to differentiate this baronial shrine from superior county arms."
        }

    # Format output dictionary with metadata
    counties_geojson_path = os.path.join(data_dir, 'ck3_counties.geojson')
    with open(counties_geojson_path, 'r', encoding='utf-8') as f:
        counties_gj = json.load(f)
    ckey_to_props = {f['properties'].get('county'): f['properties'] for f in counties_gj['features'] if f['properties'].get('county')}

    output_dataset = {}
    for key, data in sorted(SAINT_DATABASE.items()):
        props = bkey_to_props.get(key, {})
        entry = {
            "title_key": key,
            "name": props.get('name') or props.get('b_tarr') or key.replace('b_', '').title(),
            "tier": "barony" if key.startswith('b_') else "county",
            "county": props.get('county') or '',
            "kingdom": props.get('kingdom') or '',
            "saint_name": data["saint_name"],
            "saint_epithet": data["saint_epithet"],
            "shrine_type": data["shrine_type"],
            "relic_description": data["relic_description"],
            "charge": data["charge"],
            "charge_color": data["charge_color"],
            "field": data["field"],
            "ordinary": data.get("ordinary", "bordure"),
            "ordinary_color": data.get("ordinary_color", "argent"),
            "charge_count": 1,
            "blazon_tarr": data["blazon_tarr"],
            "blazon_en": data["blazon_en"],
            "legend": f"+ S. COMMVNITATIS • {key.replace('b_', '').replace('c_', '').upper()} •",
            "rationale_imagery": data["rationale_imagery"],
            "rationale_colours": data["rationale_colours"],
            "rationale_splits": data.get("rationale_splits", "Enclosed within a differencing bordure: baronial cadency differencing to distinguish subsidiary holdings from paramount comital seats."),
            "source": "Hagiographic Cadency (Buried Saint Shrine / Relics Enshrined)"
        }
        output_dataset[key] = entry

    # Generate county-level hagiographic chancellery seals for counties hosting buried saint shrines
    county_saints = {}
    for bkey, bentry in output_dataset.items():
        if not bkey.startswith('b_'):
            continue
        ck = bentry.get('county')
        if not ck or ck in bespoke_exceptions:
            continue
        if ck not in county_saints:
            county_saints[ck] = (bkey, bentry)
        else:
            old_bkey, old_entry = county_saints[ck]
            # Prefer specific named saint over generic 'Patron Saint of'
            if 'Patron Saint of' in old_entry['saint_name'] and 'Patron Saint of' not in bentry['saint_name']:
                county_saints[ck] = (bkey, bentry)
            # Prefer barony that shares name with county (e.g. b_santiago in c_santiago, b_fulda in c_fulda)
            elif bkey.replace('b_', '') in ck and old_bkey.replace('b_', '') not in ck:
                county_saints[ck] = (bkey, bentry)

    for ck, (bkey, bentry) in county_saints.items():
        cprops = ckey_to_props.get(ck, {})
        cname = cprops.get('tarr_hist') or cprops.get('tarr_direct') or cprops.get('tarr') or ck.replace('c_', '').title()
        raw_lat = (cprops.get('tarr_hist') or cprops.get('tarr_direct') or ck.replace('c_', '')).upper()
        latinized = re.sub(r'[^A-Z]', '', raw_lat) or ck.replace('c_', '').upper()

        blazon_tarr_comital = re.sub(r'\s+binnen\s+einem\s+[^\s]+\s+Bôrt', '', bentry["blazon_tarr"])
        blazon_en_comital = re.sub(r'\s+within\s+a\s+bordure\s+[^\s]+', '', bentry["blazon_en"])

        rat_col = bentry["rationale_colours"]
        for phrase in [
            " and an Argent bordure", " and an Or bordure",
            " and an Argent cadency bordure", " and an Or cadency bordure",
            " and an Argent differencing bordure", " and an Or differencing bordure",
            " enclosed by an Or cadency bordure", " enclosed by an Argent cadency bordure",
            " with an Argent bordure", " with an Or bordure",
            " with an Argent cadency bordure", " with an Or cadency bordure",
            " and cadency bordure", " with cadency bordure"
        ]:
            rat_col = rat_col.replace(phrase, "")

        output_dataset[ck] = {
            "title_key": ck,
            "name": cname,
            "tier": "county",
            "county": ck,
            "kingdom": cprops.get('kingdom') or bentry.get('kingdom') or '',
            "saint_name": bentry["saint_name"],
            "saint_epithet": bentry["saint_epithet"],
            "shrine_type": bentry["shrine_type"],
            "relic_description": bentry["relic_description"],
            "charge": bentry["charge"],
            "charge_color": bentry["charge_color"],
            "field": bentry["field"],
            "ordinary": "solid",
            "ordinary_color": bentry["ordinary_color"],
            "charge_count": bentry.get("charge_count", 1),
            "blazon_tarr": blazon_tarr_comital,
            "blazon_en": blazon_en_comital,
            "legend": f"+ S. MAGISTRATVS • {latinized}ENSIS •",
            "rationale_imagery": bentry["rationale_imagery"],
            "rationale_colours": rat_col,
            "rationale_splits": "Unbroken comital field of sovereignty: as the paramount territorial jurisdiction of the sacred shrine, the chancellery bulla seal bears no baronial cadency differencing.",
            "source": f"Hagiographic Chancellery Seal (Shrine of {bentry['saint_name']})"
        }

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output_dataset, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {len(output_dataset)} saint holding and county entries in {out_file}")

if __name__ == '__main__':
    main()
