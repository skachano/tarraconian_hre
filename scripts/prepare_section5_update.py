import json, re

with open("data/sinosphere_title_calques.json") as f:
    calques = json.load(f)

# Comprehensive database of authentic physical river basins and historical etymologies for all 61 flagged titles
# Format: key -> (real_option_b, tarr_title, historical_etymo_note)
section5_db = {
    # 5.1 Khitan Liao Dynastic Foundations (24 Counties)
    "c_LIAO_changchun": (
        "Yitong River / Songhua Basin (伊通河 / 宋瓦水)",
        "Magistrat van Langlentz-in-Chitân",
        "Auspicious foundation established in 926 AD by Yelü Abaoji after conquering Bohai; named 'Eternal Spring' (长春). Calqued semantically to Langlentz-in-Chitân and anchored geographically to the Yitong River basin."
    ),
    "c_LIAO_chaoyang": (
        "Daling River Basin (大凌河 / 白狼水)",
        "Magistrat van Hôfsunne",
        "Post-867 Khitan regional commandery in the ancient White Wolf River (Baitulangshui / Daling River) valley; named Chaoyang ('Facing the Sun'). Calqued to Hôfsunne."
    ),
    "c_LIAO_dading": (
        "Upper Daling River / Zhongjing Basin (大凌河上源)",
        "Magistrat van Grôzfest",
        "Founded in 1007 AD by Emperor Shengzong of Liao as the Central Capital (Liao Zhongjing / 中京大定府). The name signifies 'Great Settlement/Firm Peace'. Calqued to Grôzfest."
    ),
    "c_LIAO_dalian": (
        "Dalai Nur / Hulun Lake Basin (达赉湖 / 达里泊)",
        "Magistrat van Grôzgâvouwe",
        "Post-867 Khitan lakeside encampment on the eastern steppe; characters 达里岸 denote 'Great Meadow Strand / Coast'. Calqued to Grôzgâvouwe."
    ),
    "c_LIAO_heicaoan": (
        "Laoha River Basin (老哈河 / 乌尔吉木伦)",
        "Magistrat van Swartzwêdouwe",
        "Post-867 pastoral encampment along the fertile riverbanks; characters 黑草岸 literally mean 'Black Grass Shore/Strand'. Calqued to Swartzwêdouwe."
    ),
    "c_LIAO_horqinan": (
        "Horqin Steppe / Nonni Basin (科尔沁草原 / 嫩江)",
        "Magistrat van Korschînmarch",
        "Post-867 Horqin steppe grazing division; phonetic adaptation of Mongolic/Khitan Khorchin ('Quiver Bearer') to Tarraconian Korschînmarch."
    ),
    "c_LIAO_jinzhou": (
        "Xiaoling River / Liaodong Corridor (小凌河 / 锦川)",
        "Magistrat van Sîdenziergouwe",
        "Established in 923 AD by Abaoji with captive Han silk weavers; named 'Brocade Prefecture' (锦州). Calqued to Sîdenziergouwe."
    ),
    "c_LIAO_linhuang": (
        "Shira Muren / Huang River Basin (潢水 / 临潢川)",
        "Magistrat van Bîdemhuangflôz",
        "Founded in 918 AD by Abaoji as the Supreme Capital (Liao Shangjing) on the ancient Huangshui (Shira Muren); characters 临潢 literally mean 'Overlooking the Huang River'. Calqued to Bîdemhuangflôz."
    ),
    "c_LIAO_longhuazhou": (
        "Xar Moron Confluence Basin (西拉木伦河与老哈河汇流处)",
        "Magistrat van Drachenkeêregouwe",
        "Founded in 902 AD as Abaoji's fortified encampment; characters 龙化州 denote 'Dragon Transformation Prefecture'. Calqued to Drachenkeêregouwe."
    ),
    "c_LIAO_ningzhou": (
        "Fuzhou River Basin (复州河 / 宁州川)",
        "Magistrat van Rûwegouwe-in-Chitân",
        "Post-867 Liao garrison prefecture in southern Liaodong; characters 宁州 denote 'Tranquil Prefecture'. Calqued to Rûwegouwe-in-Chitân."
    ),
    "c_LIAO_raozhou": (
        "Lower Laoha River Basin (老哈河下游)",
        "Magistrat van Rîchdomgouwe",
        "Established in 953 AD by Emperor Muzong on rich alluvial grazing grounds; characters 饶州 denote 'Abundant/Bountiful Prefecture'. Calqued to Rîchdomgouwe."
    ),
    "c_LIAO_taizhou": (
        "Taoer River Basin (洮儿河 / 泰州川)",
        "Magistrat van Grôzfridgouwe-in-Chitân",
        "Post-867 Khitan border commandery on the Taoer River; characters 泰州 denote 'Exalted Peace Prefecture'. Calqued to Grôzfridgouwe-in-Chitân."
    ),
    "c_LIAO_ulagaian": (
        "Ulz River / Ulagaian Basin (乌勒吉河 / 兀鲁回水)",
        "Magistrat van Ûlûhûîstrant",
        "Post-867 pastoral march on the Ulz/Ulagaian river; characters 兀鲁回岸 denote 'Ulagaian Shore/Strand'. Calqued to Ûlûhûîstrant."
    ),
    "c_LIAO_wuzhou": (
        "Wuerxun River / Hulun Buir Basin (乌尔逊河)",
        "Magistrat van Swartzgouwe",
        "Post-867 Liao frontier prefecture; characters 乌州 denote 'Dark/Raven Prefecture'. Calqued to Swartzgouwe."
    ),
    "c_LIAO_xianzhou": (
        "Yiwulü Mountain Basin (医巫闾山山麓)",
        "Magistrat van Vermaertgouwe",
        "Established in 926 AD at the ancestral tumulus of Prince Yelü Bei; characters 显州 denote 'Illustrious Prefecture'. Calqued to Vermaertgouwe."
    ),
    "c_liao_fengzhou": (
        "Dahei River / Hetao Basin (大黑河 / 丰州川)",
        "Magistrat van Rîchgouwe-in-Chitân",
        "Post-867 Liao garrison prefecture in southern Inner Mongolia; characters 丰州 denote 'Bountiful Harvest Prefecture'. Calqued to Rîchgouwe-in-Chitân."
    ),
    "c_lnj_liaoxi": (
        "Western Liao River Basin (西辽河)",
        "Magistrat van Ljôwest",
        "Descriptive frontier division west of the Liao River; characters 辽西 denote 'West of the Liao'. Calqued to Ljôwest."
    ),
    "c_lnj_liaoxibei": (
        "Northern Laoha River Basin (老哈河北原)",
        "Magistrat van Ljôwestnord",
        "Northwestern march of the Liao river basin; characters 辽西北 denote 'Northwest of the Liao'. Calqued to Ljôwestnord."
    ),
    "c_lxj_huanzhou": (
        "Xilin River / Shandian Basin (锡林郭勒 / 闪电河)",
        "Magistrat van Stamgouwe",
        "Established 960+ AD as an inner steppe march prefecture; characters 桓州 denote 'Pillar/Trunk Prefecture'. Calqued to Stamgouwe."
    ),
    "c_lxj_yangchengzhou": (
        "Hanggai Steppe / Yangcheng Basin (羊城川)",
        "Magistrat van Schâpburchgouwe",
        "Post-867 pastoral sheep-grazing prefecture; characters 羊城州 denote 'Sheep Walled Castle Prefecture'. Calqued to Schâpburchgouwe."
    ),
    "c_lxj_yuyidong": (
        "Eastern Yuyi March / Upper Luan Basin (滦河上源)",
        "Magistrat van Keisersebisôst",
        "Post-867 marchland division of the ancient Yuyi frontier; characters 御夷东 denote 'East of Defending the Barbarians'. Calqued to Keisersebisôst."
    ),
    "c_lzj_chengde": (
        "Rehe / Wulie River Basin (热河 / 武烈河)",
        "Magistrat van Ontfangdôget",
        "Modern vanilla anachronism derived from the Qing imperial mountain resort (1703 AD); characters 承德 denote 'Inheriting Virtue'. Calqued to Ontfangdôget and anchored to the Wulie River basin."
    ),
    "c_lzj_chengdexi": (
        "Upper Luan River Gorge (滦河峡谷)",
        "Magistrat van Ontfangdôgetwest",
        "Descriptive subdivision of the mountainous Chengde basin; characters 承德西 denote 'West of Inheriting Virtue'. Calqued to Ontfangdôgetwest."
    ),
    "c_woye": (
        "Woye Mountain / Urad Basin (乌拉特前旗 / 沃野山)",
        "Magistrat van Vettfelt",
        "Ancient Han-dynasty frontier garrison name meaning 'Fertile Fields'; calqued semantically to Vettfelt and anchored to the northern Yellow River bend."
    ),

    # 5.2 Jurchen & Bohai Frontier Market Settlements (11 Counties)
    "c_BAL_anbyeon": (
        "Mudan River Basin (牡丹江 / 忽汗河)",
        "Magistrat van Fridmarch",
        "Anbian frontier commandery between Bohai and the Khitans; characters 安边 denote 'Pacified Frontier March'. Calqued to Fridmarch."
    ),
    "c_BAL_delizhen": (
        "Tumen River Basin (图们江 / 德理川)",
        "Magistrat van Dôgetmarct",
        "Bohai/Jurchen trading outpost on the Tumen River; characters 德理镇 denote 'Virtuous Governance Garrison/Market'. Calqued to Dôgetmarct."
    ),
    "c_BAL_heuksu_anwon": (
        "Lower Amur / Blackwater Confluence (黑水下游)",
        "Magistrat van Swartzwazzer-Fridferne",
        "Mohe border post along the Lower Amur (Heishui / Blackwater); characters 黑水安远 denote 'Blackwater Pacified Distance'. Calqued to Swartzwazzer-Fridferne."
    ),
    "c_BAL_huligai": (
        "Mudan River / Huligai Basin (胡里改川 / 依兰)",
        "Magistrat van Hûligâibache",
        "Ancient Jurchen tribal heartland of the Huligai (Ilantala); phonetic adaptation of indigenous Tungusic stem Huligai to Hûligâibache."
    ),
    "c_BAL_jeongni": (
        "Partizanskaya / Suchan River Basin (苏城河 / 定理川)",
        "Magistrat van Festrecht",
        "Coastal Bohai commandery in Primorye; characters 定理 denote 'Settled Law / Order'. Calqued to Festrecht."
    ),
    "c_BAL_ningzhou": (
        "Razdolnaya / Suifen River Basin (绥芬河)",
        "Magistrat van Rûwegouwe-in-Lûdsen",
        "Eastern Bohai coastal prefecture; characters 宁州 denote 'Tranquil Prefecture'. Calqued to Rûwegouwe-in-Lûdsen."
    ),
    "c_BAL_north_anbyeon": (
        "Upper Mudan River Basin (忽汗河上源)",
        "Magistrat van Nord-Fridmarch",
        "Northern division of the Anbian frontier march; characters 北安边 denote 'Northern Pacified Frontier'. Calqued to Nord-Fridmarch."
    ),
    "c_BAL_north_anwon": (
        "Anyuan Mountain / Ussuri Basin (安远岭 / 乌苏里江上源)",
        "Magistrat van Nord-Fridferne",
        "Northern division of the Anyuan outpost; characters 北安远 denote 'Northern Pacified Distance'. Calqued to Nord-Fridferne."
    ),
    "c_BAL_solbin": (
        "Shuibin / Suifen River Basin (绥芬河 / 率宾川)",
        "Magistrat van Solbînflôz",
        "Historical Bohai province of Solbin / Shuibin on the Suifen River (near modern Ussuriysk); phonetic adaptation to Solbînflôz."
    ),
    "c_BAL_supin": (
        "Bikin River Basin (比金河 / 速频水)",
        "Magistrat van Snellflôz",
        "Jurchen river outpost on the Bikin/Supin river; characters 速频 denote 'Swift Stream / Rapid Current'. Calqued to Snellflôz."
    ),
    "c_BAL_west_cheolli": (
        "Huanashan / West Tieli Basin (铁利川 / 依兰西)",
        "Magistrat van West-Îsenlant",
        "Western march of the Tieli (Iron) tribe along the Sungari River; characters 西铁利 denote 'Western Iron Land'. Calqued to West-Îsenlant."
    ),

    # 5.3 Shiwei Steppe Marches (13 Counties)
    "c_SW_damoguo": (
        "Argun River / Damuo Steppe (额尔古纳河 / 达末原)",
        "Magistrat van Rêkendlant",
        "Remote Shiwei clan territory on the Argun River; characters 达末国 denote 'Reach the Terminus Country'. Calqued to Rêkendlant."
    ),
    "c_SW_dongcheziguo": (
        "Eastern Hailar River Basin (海拉尔河东)",
        "Magistrat van dem Ôst-Wagenlant",
        "Eastern Cart/Wagon clan division of the Shiwei; characters 东车子国 denote 'Eastern Wagon Land'. Calqued to dem Ôst-Wagenlant."
    ),
    "c_SW_heilonghean": (
        "Upper Heilongjiang (Amur) Northern Shore (黑龙江上游北岸)",
        "Magistrat van Swartzdrachenflôzouwe",
        "Riparian territory on the northern bank of the Upper Amur; characters 黑龙河岸 literally denote 'Black Dragon River Strand/Meadow'. Calqued to Swartzdrachenflôzouwe."
    ),
    "c_SW_hongxingan": (
        "Greater Khingan Ridge (大兴安岭中脊)",
        "Magistrat van Rôtupgancfrid",
        "Mountain ridge territory across the central Khingan; characters 红兴安 denote 'Red Flourishing Peace'. Calqued to Rôtupgancfrid."
    ),
    "c_SW_huangtouguo": (
        "Gen River / Huangtou Steppe (根河 / 黄头原)",
        "Magistrat van Gelbhoubtlant",
        "Yellow-head Shiwei tribal roaming grounds on the Gen River; characters 黄头国 denote 'Yellow Head Land'. Calqued to Gelbhoubtlant."
    ),
    "c_SW_hulunbuir": (
        "Hulun Lake Basin (呼伦湖 / 阔连海子)",
        "Magistrat van Wîdschakelvancfischken",
        "Historical transcription of Hulun Buir (阔连捕鱼儿 'Wide Lake Fishing Waters'); calqued to Wîdschakelvancfischken."
    ),
    "c_SW_luotuoguo": (
        "Yakeshi / Camel Range Plateau (牙克石高原)",
        "Magistrat van Bontroskameêllant",
        "Shiwei nomadic grazing tract; characters 骆驼国 denote 'Camel Country'. Calqued to Bontroskameêllant."
    ),
    "c_SW_nabeiguo": (
        "North Nenjiang (Nonni) Basin (嫩江北源)",
        "Magistrat van Swîchnordlant",
        "Northern Nonni forest clan division; characters 讷北国 denote 'Taciturn North Land'. Calqued to Swîchnordlant."
    ),
    "c_SW_puyuzhou": (
        "Wuyur River Basin (乌裕尔河 / 蒲与川)",
        "Magistrat van Lischtbîgouwe",
        "Puyu prefecture on the Wuyur River; characters 蒲与州 denote 'Bulrush Riverbank Prefecture'. Calqued to Lischtbîgouwe."
    ),
    "c_SW_shanbeiguo": (
        "Northern Khingan Slope (大兴安岭北坡)",
        "Magistrat van Berchnordlant",
        "Shiwei clan land on the northern mountain slopes; characters 山北国 denote 'North of the Mountains Land'. Calqued to Berchnordlant."
    ),
    "c_SW_xinghuangtou": (
        "Chaoer River / Xinghuangtou Plateau (绰尔河)",
        "Magistrat van Upgancgelbhoubt",
        "Southeastern division of the Yellow-head Shiwei; characters 兴黄头 denote 'Flourishing Yellow Head'. Calqued to Upgancgelbhoubt."
    ),
    "c_SW_xingnabei": (
        "Duobukur River Basin (多布库尔河)",
        "Magistrat van Upgancswîchnord",
        "Eastern division of the northern Nonni forest clans; characters 兴讷北 denote 'Flourishing Northern Nen'. Calqued to Upgancswîchnord."
    ),
    "c_SW_zhongcheziguo": (
        "Middle Hailar River Basin (海拉尔河中游)",
        "Magistrat van dem Midden-Wagenlant",
        "Central Cart/Wagon clan division of the Shiwei; characters 中车子国 denote 'Middle Wagon Land'. Calqued to dem Midden-Wagenlant."
    ),

    # 5.4 Lower Amur Wilderness Marches (10 Counties)
    "c_eman_amgun": (
        "Amgun River Basin (阿姆贡河 / 恨骨川)",
        "Magistrat van dem Amgûnflôze",
        "Ancient Evenk/Nivkh river basin of the Amgun; phonetic adaptation of the indigenous hydronym to Amgûnflôz (with Chinese characters 恨骨)."
    ),
    "c_eman_beihean": (
        "Middle Amur Northern Shore (阿穆尔河北岸)",
        "Magistrat van dem Nordflôzstrant",
        "Descriptive northern bank of the Middle Amur river; characters 北河岸 denote 'North River Strand/Shore'. Calqued to dem Nordflôzstrant."
    ),
    "c_eman_boli": (
        "Amur-Ussuri Confluence Basin (黑龙江与乌苏里江汇流处 / 伯力)",
        "Magistrat van Bôli",
        "Historic indigenous Tungusic settlement at the confluence of the Amur and Ussuri rivers (modern Khabarovsk); phonetic adaptation to Bôli."
    ),
    "c_eman_choripi": (
        "Chor / Khor River Basin (霍尔河 / 也曼水)",
        "Magistrat van Tschoripîflôz",
        "Indigenous Ussuri tributary basin (Chor/Khor river); characters 也曼水 denote 'Yeman River'. Phonetic adaptation to Tschoripîflôz."
    ),
    "c_eman_mohean": (
        "Bureya River Basin (布列亚河 / 莫罕川)",
        "Magistrat van Môhân",
        "Remote Amur tributary basin (Bureya/Mohean); phonetic adaptation to Môhân."
    ),
    "c_eman_molihewen": (
        "Zeya River Basin (结雅河 / 末里合温川)",
        "Magistrat van Môlîhêwên",
        "Tungusic forest outpost on the Zeya river; phonetic adaptation of indigenous stem to Môlîhêwên."
    ),
    "c_eman_nurgan": (
        "Amur Estuary / Liman Coast (黑龙江入海口 / 奴儿干特林)",
        "Magistrat van Nûrgânmarch",
        "Territory at the maritime mouth of the Amur; named after the ancient Tungusic/Evenk toponym Nurgan (later Ming commission). Adapted to Nûrgânmarch."
    ),
    "c_eman_tugur": (
        "Tugur Bay & River Coast (图古尔湾 / 鄂霍次克海岸)",
        "Magistrat van Tûgûrbucht",
        "Okhotsk sea coastal tract and Tugur river; phonetic adaptation of indigenous Evenk stem Tugur to Tûgûrbucht."
    ),
    "c_eman_yerenhe": (
        "Anyuy River Basin (阿纽伊河 / 野人水)",
        "Magistrat van dem Wiltmansflôze",
        "Descriptive historical Chinese hydronym for the wild Jurchen forest river (Anyuy basin); characters 野人河 denote 'Wild Jurchen River'. Calqued to dem Wiltmansflôze."
    ),
    "c_kusunkotan": (
        "Aniva Bay / Southern Sakhalin Coast (亚尼瓦湾 / 库页岛南端)",
        "Magistrat van Tegenstrantdorp",
        "Indigenous Ainu settlement Kusun-kotan ('Village on the Opposite Coast'). Chinese characters 对涯村 literally translate the Ainu meaning ('Opposite Shore Village'). Calqued to Tegenstrantdorp."
    ),

    # 5.5 Guannei Northwestern Mountain Passes & Strategic Chokes (3 Counties)
    "c_jingzhou": (
        "Jing River Basin (泾水 / 安定原)",
        "Magistrat van Zînflôzgouwe",
        "Ancient classical commandery named after the Jing River (attested 1000 BC in the Shijing); characters 泾州 denote 'Jing River Prefecture'. Calqued to Zînflôzgouwe."
    ),
    "c_xiaoguan": (
        "Mount Liupan / Xiao Pass Choke (六盘山 / 萧关峡)",
        "Magistrat van Schilfklûse",
        "Xiao Pass (萧关) across Mount Liupan, fortified by Qin/Han antiquity (2nd century BC); characters 萧关 denote 'Artemisia/Reed Pass'. Calqued to Schilfklûse."
    ),
    "c_yuanzhou_2": (
        "Upper Qingshui River Basin (清水河上源 / 原州原)",
        "Magistrat van Veltgouwe-in-Schjê",
        "Ancient Northern Wei commandery on the Upper Qingshui; characters 原州 denote 'Highland Plain Prefecture'. Calqued to Veltgouwe-in-Schjê."
    ),
}

print("Loaded section5_db entries:", len(section5_db))
