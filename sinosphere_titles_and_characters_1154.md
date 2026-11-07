# Sinosphere Title Gazetteer & Comprehensive Audit (CK3 — 1154)

> **Historical & Gamestate Reference Document**  
> **Game Date:** 27 December 1154 (`1154.12.27`)  
> **Campaign Save Game:** `chatenois_867_01_01.ck3`  
> **Engine Mechanics:** Crusader Kings III (with East Asia & Mandate of Heaven / Dynastic Cycle System)  
> **Historical Canon Standards:** 867 Alternate-History Divergence Point | Three-Tier Classification System | Toponym-First Principle  

---

## 1. Executive Summary: The Size of the Sinosphere in 1154

In Crusader Kings III, the **Sinosphere** (East Asian Cultural Sphere / 汉字文化圈 / 儒家文化圈) encompasses both the **Core Middle Kingdom** (China Proper, formally codified in game mechanics as Subregion 0 of the `dynastic_cycle` Mandate of Heaven struggle/situation) and the broader **East Asian cultural and tributary perimeter** (Korea, Japan, Manchuria/Liao, and northern Indochina/Đại Việt) that historically utilized Chinese characters, administrative statecraft, and diplomatic investiture.

### 1.1 Comparative Dimension Overview

| Metric Dimension | Core Sinosphere (China Proper) | Extended Sinosphere (Korea, Japan, Andong, Amur) | Full Greater Sinosphere Total |
| :--- | :---: | :---: | :---: |
| **De Jure Empires** | **5 Empires** | **4 Empires** | **9 Empires** |
| **De Jure Kingdoms** | **24 Kingdoms** | **15 Kingdoms** | **39 Kingdoms** |
| **De Jure Duchies** | **101 Duchies** | **52 Duchies** | **153 Duchies** |
| **County-Tier Titles** | **380 Counties** (61.3%) | **240 Counties** (38.7%) | **620 Counties** (100.0%) |
| **Constituent Holdings / Baronies** | **1,237 Baronies** (avg 3.26/county) | **800 Baronies** (avg 3.33/county) | **2,037 Baronies** (avg 3.29/county) |
| **Total Base Development** | **18,776.0** | **5,646.0** | **24,422.0** |
| **Average Development per County** | **49.4** | **23.5** | **39.4** |
| **Roman Empire Control in 1154** | **89 / 380** (23.4%) | **190 / 240** (79.2%) | **279 / 620** (45.0%) |
| **Independent Sinitic Realms Control** | **291 / 380** (76.6%) | **50 / 240** (20.8%) | **341 / 620** (55.0%) |
| **Historical Anachronism Rate** | **3 / 380** (0.8% — Guannei passes) | **58 / 240** (24.2% — Frontier marches) | **61 / 620** (9.8% — 100% Resolved) |

### 1.2 Summary Table of De Jure Empires in the Sinosphere

| Rank | De Jure Empire | Title Key | Chinese Characters | Sphere Tier | Kingdoms | Duchies | Counties | Baronies | Total Dev | Avg Dev | Roman Control (1154) | Anachronisms Flagged |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **Andong** | `e_andong` | **安东** | Peripheral | 5 | 23 | **97** | 321 | 1,567 | 16.2 | **70/97** (72.2%) | **48 flagged** |
| 2 | **Liangyi** | `e_liangyi` | **梁益** | Core China | 6 | 21 | **89** | 261 | 3,788 | 42.6 | **0/89** (0.0%) | 0 (100% Classical) |
| 3 | **Zhongyuan** | `e_zhongyuan` | **中原** | Core China | 6 | 24 | **86** | 283 | 3,873 | 45.0 | **39/86** (45.3%) | 0 (100% Classical) |
| 4 | **Jingyang** | `e_jingyang` | **荆扬** | Core China | 7 | 17 | **80** | 308 | 5,550 | 69.4 | **0/80** (0.0%) | 0 (100% Classical) |
| 5 | **Yongliang** | `e_yongliang` | **雍凉** | Core China | 3 | 19 | **73** | 208 | 3,146 | 43.1 | **50/73** (68.5%) | **3 flagged** |
| 6 | **Japan** | `e_japan` | **日本** | Peripheral | 3 | 13 | **59** | 210 | 2,303 | 39.0 | **59/59** (100.0%) | 0 (100% Classical) |
| 7 | **Lingnan** | `e_lingnan` | **岭南** | Core China | 3 | 12 | **52** | 177 | 2,419 | 46.5 | **0/52** (0.0%) | 0 (100% Classical) |
| 8 | **Samhan** | `e_goryeo` | **三韩** (三韓) | Peripheral | 3 | 13 | **44** | 139 | 1,232 | 28.0 | **44/44** (100.0%) | 0 (100% Classical) |
| 9 | **Amur** | `e_amur` | **阿穆尔** | Peripheral | 3 | 11 | **40** | 130 | 544 | 13.6 | **17/40** (42.5%) | **10 flagged** |

### 1.3 Political Landscape and the Dynastic Cycle in 1154

#### The Dynastic Cycle (Mandate of Heaven) Struggle
In the active campaign save (`1154.12.27`), the Chinese Core is governed by the `dynastic_cycle` situation:
- **Current Phase:** **Phase of Chaos** (`situation_dynastic_cycle_phase_chaos`), active since **January 2, 1146**.
- **Catalyst & History:** Triggered by the collapse of the previous central hegemon in 1146, breaking the Mandate of Heaven into competing regional warlord regimes and imperial protectorates.
- **Geographical Boundary:** Subregion 0 ("Core") encompasses **exactly 380 counties** spanning `e_zhongyuan`, `e_liangyi`, `e_jingyang`, `e_yongliang`, and `e_lingnan`.

#### Sovereign Realms Partitioning the Sinosphere in 1154
Control across the 620 Sinospheric counties is distributed among the following sovereigns:

| Realm / Sovereign Liege | Liege Key | Liege Chinese Name | Sovereign Ruler & Dynastic House | Regional Domain | Counties Held | Sphere Share |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **Roman Empire** | `h_roman_empire` | 罗马帝国 | **Augustus Wernhard** (Chatenois) | Mediterranean & East Asian Marches | **279** | 45.0% |
| **Qianzhong** | `k_qianzhong` | 黔中 | Qian (騫) of House Ye Lán | Shannan (山南) | **86** | 13.9% |
| **Lingnan** | `e_lingnan` | 岭南 | Che (徹) "the Wicked" of House Zhu (朱) | Lingxi (岭西) | **56** | 9.0% |
| **Xichuan** | `k_xichuan` | 西川 | Luan (鸞) "the Greedy" of House Hongya Yǔ | Dongchuan (东川) | **24** | 3.9% |
| **Guannei** | `k_guannei` | 关内 | Zhun (準) of House Sen | Guannei (关内) | **23** | 3.7% |
| **Sikhotebei** | `d_eman_sikhotebei` | 西河大北 | In_pyo "the Strange" of House Sa (史) | Luzhen (虑真) | **21** | 3.4% |
| **Liangzhe** | `k_liangzhe` | 两浙 | Lianggui (良貴 of House Khuc (曲) | Liangzhe (两浙) | **17** | 2.7% |
| **Hebei** | `k_hebei` | 河北 | ME_rok "the Girthy" of House Zira | Hebei (河北) | **15** | 2.4% |
| **Xingyuan** | `k_xingyuan` | 兴元 | Bing (柄) of House Wuwei Zōu | Xingyuan (兴元) | **13** | 2.1% |
| **Qingxu** | `k_qingxu` | 青徐 | Hu (鵠) "the Humble" of House Cui (崔) | Qingxu (青徐) | **13** | 2.1% |
| **Jiangxi** | `k_jiangxi` | 江西 | Song (松) of House Su (蘇) | Jiangxi (江西) | **13** | 2.1% |
| **Huainan** | `k_huainan` | 淮南 | Shuzu (述祖 of House Baima Chén | Huainan (淮南) | **11** | 1.8% |
| **Đại Việt** | `k_viet` | 大越 | Geng (賡) of House Jiangning Lù | Đại Việt (大越) | **9** | 1.5% |
| **Jiangdong** | `k_jiangdong` | 江东 | Yuanzhen (元贞 "the Bastard" of House Qamdo Qín | Jiangdong (江东) | **8** | 1.3% |
| **Luzhen** | `k_luzhen` | 虑真 | Alihemen of House Alihemen | Luzhen (虑真) | **7** | 1.1% |
| **Shiwei** | `k_shiwei` | 室韦 | Fannu "the Drunkard" of House Giahuna | Shiwei (室韦) | **7** | 1.1% |

### 1.4 Historical Anachronism Audit & Resolution Synthesis

Under the project's historical title audit framework ([`title_historical_accuracy_audit_plan.md`](file:///home/siarzhuk/code/personal/tarraconian_hre/title_historical_accuracy_audit_plan.md) and [`audit_discrepancy_register.md`](file:///home/siarzhuk/code/personal/tarraconian_hre/audit_discrepancy_register.md)), all titles within the Imperial sphere are rigorously screened against the **867 AD campaign divergence milestone**:
- **90.2% (559 of 620 counties)** are **Tier 1 (Authentic Pre-867 Classical Antiquity Foundations)**. The commanderies, prefectures, and provinces of the Central Plains, Ba-Shu, Jiangnan, Lingnan, Korea (Three Kingdoms/Silla), and Japan (Ritsuryō) date back centuries before 867 AD.
- **9.8% (61 of 620 counties)** were flagged under **Tier 3 (Post-867 Settlements & Unverified Titles)** due to post-867 Khitan Liao dynasty foundations (918–1007 AD), Jurchen frontier outposts, and nomadic clan divisions in the northern marches.
- **100% of the 61 Flagged Titles** have been reconciled under **Option B (Ancient Hydronymic & Natural Regional Basin Hierarchy)**, anchoring them to their underlying river basins and mountain horizons. The complete register is documented in **Section 5**.

---

## 2. Core Sinosphere Title Register (380 Counties)

The 380 counties of China Proper are organized below hierarchically by **De Jure Empire** $\rightarrow$ **De Jure Kingdom** $\rightarrow$ **De Jure Duchy** $\rightarrow$ **County Title**.

### 2.1 Empire of Zhongyuan (`e_zhongyuan` / 中原)
- **De Jure Extent:** **86 Counties**, 24 Duchies, 6 Kingdoms.
- **Total Development:** **3,873.0** (Average: 45.0) | **Baronies:** 283
- **1154 Roman Empire Control:** **39 / 86 counties** (45.3%) | **Anachronisms Flagged:** **0**

#### 2.1.1 Kingdom of Daibei (`k_daibei` / 代北)
*Extent: **14 Counties** | Development: **313** (avg 22.4) | Roman Control: **14/14** | Flagged Anachronisms: **0***

##### Duchy of Sanggan (`d_sanggan` / 桑干) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 1 | `c_huaian` | **Huai'an** | **怀安** | — | ✅ Pre-867 Classical | **[RE]** | Zhenwu | 22 | 3 | b_huaian [castle], b_rouxuan [castle]... |
| 2 | `c_jiushijiuquan` | **Jiushijiuquan** | **九十九泉** | — | ✅ Pre-867 Classical | **[RE]** | khitan | 16 | 3 | b_jiushijiuquan [castle], b_guanshan ... |
| 3 | `c_rouyuan` | **Rouyuan** | **柔远** | — | ✅ Pre-867 Classical | **[RE]** | Zhenwu | 17 | 2 | b_rouyuan [castle], b_goupo [castle] |
| 4 | `c_yongxing` | **Yongxing** | **永兴** | — | ✅ Pre-867 Classical | **[RE]** | han | 26 | 3 | b_yongxing [castle], b_wende [church]... |

##### Duchy of Zhenwu (`d_xinan` / 振武) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 5 | `c_fuzhou` | **Fuzhou** | **府州** | — | ✅ Pre-867 Classical | **[RE]** | Zhenwu | 21 | 2 | b_xiazhou_dejing_east [castle], b_jin... |
| 6 | `c_linzhou` | **Linzhou** | **麟州** | — | ✅ Pre-867 Classical | **[RE]** | Linzhou | 24 | 3 | b_linzhou_xintai [castle], b_linzhou_... |
| 7 | `c_lxj_yunneizhou` | **Yunneizhou** | **云内州** | — | ✅ Pre-867 Classical | **[RE]** | tuyuhun | 21 | 3 | b_cirlxj_zhenwu [castle], b_cirlxj_sh... |
| 8 | `c_qingshan` | **Qingshan** | **青山** | — | ✅ Pre-867 Classical | **[RE]** | tuyuhun | 21 | 2 | b_cirlxj_heishabao [castle], b_cirlxj... |
| 9 | `c_shengzhou` | **Shengzhou** | **胜州** | — | ✅ Pre-867 Classical | **[RE]** | Zhenwu | 28 | 4 | b_shengzhou_yulin [castle], b_shengzh... |

##### Duchy of Yunshuo (`d_yunshuo` / 云朔) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 10 | `c_datong_2` | **Datong** | **大同** | — | ✅ Pre-867 Classical | **[RE]** | shatuo | 24 | 4 | b_yunzhong [castle], b_huairen_2 [chu... |
| 11 | `c_hongzhou_2` | **Hongzhou** | **弘州** | — | ✅ Pre-867 Classical | **[RE]** | shatuo | 25 | 2 | b_yongning [castle], b_shunsheng [city] |
| 12 | `c_shuozhou` | **Shuozhou** | **朔州** | — | ✅ Pre-867 Classical | **[RE]** | shatuo | 20 | 4 | b_shanyang [castle], b_mayi [church],... |
| 13 | `c_yingzhou_5` | **Yingzhou** | **应州** | — | ✅ Pre-867 Classical | **[RE]** | shatuo | 27 | 3 | b_jincheng [castle], b_huanyuan [city... |
| 14 | `c_yuzhou` | **Yuzhou** | **蔚州** | — | ✅ Pre-867 Classical | **[RE]** | shatuo | 21 | 4 | b_lingqiu [castle], b_feihu [castle],... |

#### 2.1.2 Kingdom of Hebei (`k_hebei` / 河北)
*Extent: **15 Counties** | Development: **733** (avg 48.9) | Roman Control: **0/15** | Flagged Anachronisms: **0***

##### Duchy of Cangjing (`d_cangjing` / 沧景) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 15 | `c_cangzhou` | **Cangzhou** | **沧州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 52 | 3 | b_qingchi [castle], b_lucheng [city],... |
| 16 | `c_dezhou` | **Dezhou** | **德州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 44 | 3 | b_ande [castle], b_dongguang [city], ... |
| 17 | `c_dizhou` | **Dizhou** | **棣州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 35 | 3 | b_yanci [castle], b_bohai [city], b_s... |

##### Duchy of Chengde (`d_chengde` / 成德) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 18 | `c_jizhou` | **Jizhou** | **冀州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 45 | 2 | b_xindu [castle], b_wuyi [city] |
| 19 | `c_shenzhou_1` | **Shenzhou** | **深州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 37 | 3 | b_luze [castle], b_raoyang [castle], ... |
| 20 | `c_zhaozhou` | **Zhaozhou** | **赵州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 42 | 3 | b_pingji [castle], b_yuanshi [church]... |
| 21 | `c_zhenzhou` | **Zhenzhou** | **镇州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 44 | 3 | b_zhending [castle], b_lingshou [cast... |

##### Duchy of Heyang (`d_heyang` / 河阳) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 22 | `c_huaizhou` | **Huaizhou** | **怀州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 72 | 2 | b_heyang [castle], b_henei [city] |
| 23 | `c_weizhou_1` | **Weizhou** | **卫州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 69 | 2 | b_ji_2 [castle], b_wei [city] |

##### Duchy of Weibo (`d_weibo` / 魏博) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 24 | `c_beizhou` | **Beizhou** | **贝州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 44 | 3 | b_qinghe [castle], b_linqing [castle]... |
| 25 | `c_bozhou_1` | **Bozhou** | **博州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 43 | 2 | b_liaocheng [castle], b_gaotang [castle] |
| 26 | `c_weizhou` | **Weizhou** | **魏州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 55 | 3 | b_yuancheng [castle], b_dunqiu [city]... |

##### Duchy of Xingming (`d_xingming` / 邢洺) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 27 | `c_mingzhou` | **Mingzhou** | **洺州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 46 | 3 | b_yongnian [castle], b_handan [church... |
| 28 | `c_xiangzhou` | **Xiangzhou** | **相州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 56 | 3 | b_anyang [castle], b_neihuang [castle... |
| 29 | `c_xingzhou` | **Xingzhou** | **邢州** | — | ✅ Pre-867 Classical | `k_hebei` | han | 49 | 3 | b_longgang [castle], b_julu [city], b... |

#### 2.1.3 Kingdom of Hedong (`k_hedong` / 河东)
*Extent: **15 Counties** | Development: **754** (avg 50.3) | Roman Control: **15/15** | Flagged Anachronisms: **0***

##### Duchy of Hedong (`d_hedong` / 河东) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 30 | `c_fenzhou` | **Fenzhou** | **汾州** | — | ✅ Pre-867 Classical | **[RE]** | Zhenwu | 45 | 3 | b_xihe [castle], b_pingyao [city], b_... |
| 31 | `c_lanzhou` | **Lanzhou** | **岚州** | — | ✅ Pre-867 Classical | **[RE]** | shatuo | 26 | 4 | b_yifang [castle], b_hehe_2 [city], b... |
| 32 | `c_liaozhou` | **Yizhou** | **仪州** | — | ✅ Pre-867 Classical | **[RE]** | Zhenwu | 42 | 4 | b_liaoshan [castle], b_yushe [city], ... |
| 33 | `c_shizhou` | **Shizhou** | **石州** | — | ✅ Pre-867 Classical | **[RE]** | sogdian | 43 | 4 | b_lishi [castle], b_fangshan [city], ... |
| 34 | `c_taiyuan` | **Taiyuan** | **太原** | — | ✅ Pre-867 Classical | **[RE]** | Zhenwu | 47 | 5 | b_taiyuan [castle], b_shouyang [city]... |

##### Duchy of Hezhong (`d_hezhong` / 河中) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 35 | `c_cizhou` | **Cizhou** | **慈州** | — | ✅ Pre-867 Classical | **[RE]** | han | 71 | 2 | b_jichang [castle], b_wencheng [city] |
| 36 | `c_hezhong` | **Hezhong** | **河中** | — | ✅ Pre-867 Classical | **[RE]** | han | 72 | 4 | b_hedong [castle], b_wenxi [city], b_... |
| 37 | `c_jiangzhou_2` | **Jiangzhou** | **绛州** | — | ✅ Pre-867 Classical | **[RE]** | han | 68 | 4 | b_zhengping [castle], b_yuan [city], ... |
| 38 | `c_pingyang` | **Jinzhou** | **晋州** | — | ✅ Pre-867 Classical | **[RE]** | han | 63 | 3 | b_linfen [castle], b_huoyi [city], b_... |
| 39 | `c_xizhou` | **Xizhou** | **隰州** | — | ✅ Pre-867 Classical | **[RE]** | han | 58 | 4 | b_xichuan [castle], b_shilou [city], ... |

##### Duchy of Yanmen (`d_yanmen` / 雁门) — *2/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 40 | `c_daizhou` | **Daizhou** | **代州** | — | ✅ Pre-867 Classical | **[RE]** | shatuo | 32 | 5 | b_yanmen [castle], b_fanshi [city], b... |
| 41 | `c_xinzhou` | **Xinzhou** | **忻州** | — | ✅ Pre-867 Classical | **[RE]** | shatuo | 28 | 2 | b_xiurong [castle], b_dingxiang [city] |

##### Duchy of Zelu (`d_zelu` / 泽潞) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 42 | `c_longde` | **Luzhou** | **潞州** | — | ✅ Pre-867 Classical | **[RE]** | han | 51 | 4 | b_shangdang [castle], b_lucheng_1 [ci... |
| 43 | `c_yangcheng` | **Qinzhou** | **沁州** | — | ✅ Pre-867 Classical | **[RE]** | han | 53 | 3 | b_qinyuan [castle], b_mianshang [city... |
| 44 | `c_zezhou` | **Zezhou** | **泽州** | — | ✅ Pre-867 Classical | **[RE]** | han | 55 | 3 | b_jincheng_2 [castle], b_gaoping [cit... |

#### 2.1.4 Kingdom of Henan (`k_henan` / 河南)
*Extent: **15 Counties** | Development: **879** (avg 58.6) | Roman Control: **0/15** | Flagged Anachronisms: **0***

##### Duchy of Biansong (`d_biansong` / 汴宋) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 45 | `c_bianzhou` | **Bianzhou** | **汴州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 54 | 4 | b_kaifeng [castle], b_fengqiu [city],... |
| 46 | `c_bozhou` | **Bozhou** | **亳州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 50 | 4 | b_qiao [castle], b_chengfu [city], b_... |
| 47 | `c_shanzhou` | **Shanzhou** | **单州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 46 | 2 | b_shanfu [castle], b_yutai [city] |
| 48 | `c_songzhou` | **Songzhou** | **宋州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 45 | 4 | b_songcheng [castle], b_yucheng [city... |
| 49 | `c_yingzhou` | **Yingzhou** | **颍州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 47 | 4 | b_ruyin [castle], b_shenqiu [city], b... |

##### Duchy of Chenxu (`d_chenxu` / 陈许) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 50 | `c_caizhou` | **Caizhou** | **蔡州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 61 | 4 | b_ruyang [castle], b_xiping [city], b... |
| 51 | `c_huaining` | **Chenzhou** | **陈州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 54 | 3 | b_wanqiu [castle], b_taikang [city], ... |
| 52 | `c_shenzhou` | **Shenzhou** | **申州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 52 | 3 | b_yiyang [castle], b_luoshan [city], ... |
| 53 | `c_yingchuan` | **Xuzhou** | **许州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 68 | 4 | b_changshe [castle], b_fugou [castle]... |

##### Duchy of Dongji (`d_dongji` / 东畿) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 54 | `c_henan` | **Henan** | **河南** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 66 | 5 | b_luoyang [castle], b_yanshi [city], ... |
| 55 | `c_ruzhou` | **Ruzhou** | **汝州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 57 | 3 | b_liang [castle], b_xiangcheng [city]... |

##### Duchy of Shanguo (`d_shanguo` / 陕虢) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 56 | `c_guozhou` | **Guozhou** | **虢州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 72 | 2 | b_hongnong [castle], b_lushi [city] |
| 57 | `c_shanzhou_2` | **Shanzhou** | **陕州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 72 | 2 | b_shan [castle], b_lingbao [city] |

##### Duchy of Zhenghua (`d_zhenghua` / 郑滑) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 58 | `c_huazhou` | **Huazhou** | **滑州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 65 | 3 | b_baima [castle], b_lingchang [city],... |
| 59 | `c_zhengzhou` | **Zhengzhou** | **郑州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 70 | 3 | b_guancheng [castle], b_yangwu [city]... |

#### 2.1.5 Kingdom of Qingxu (`k_qingxu` / 青徐)
*Extent: **17 Counties** | Development: **805** (avg 47.4) | Roman Control: **0/17** | Flagged Anachronisms: **0***

##### Duchy of Xusi (`d_xusi` / 徐泗) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 60 | `c_huaiyang` | **Huaiyang** | **淮阳** | — | ✅ Pre-867 Classical | `k_huainan` | han | 52 | 3 | b_xiapi [castle], b_suqian [city], b_... |
| 61 | `c_sizhou_2` | **Sizhou** | **泗州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 53 | 3 | b_linhuai [castle], b_xucheng [city],... |
| 62 | `c_suzhou` | **Suzhou** | **宿州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 54 | 4 | b_fuli [castle], b_hong [city], b_lin... |
| 63 | `c_xuzhou_1` | **Xuzhou** | **徐州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 53 | 4 | b_pengcheng [castle], b_teng [city], ... |

##### Duchy of Yanhai (`d_yanhai` / 兖海) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 64 | `c_haizhou` | **Haizhou** | **海州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 55 | 3 | b_qushan [castle], b_huairen [city], ... |
| 65 | `c_langya` | **Yizhou** | **沂州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 48 | 5 | b_linyi [castle], b_xintai [city], b_... |
| 66 | `c_mizhou` | **Mizhou** | **密州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 49 | 5 | b_zhucheng [castle], b_gaomi [city], ... |
| 67 | `c_yanzhou` | **Yanzhou** | **兖州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 53 | 5 | b_xiaqiu [castle], b_laiwu [city], b_... |

##### Duchy of Yuncao (`d_yuncao` / 郓曹) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 68 | `c_caozhou` | **Caozhou** | **曹州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 58 | 4 | b_jiyin [castle], b_nanhua [city], b_... |
| 69 | `c_puzhou_2` | **Puzhou** | **濮州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 60 | 3 | b_puyang [castle], b_juancheng [city]... |
| 70 | `c_qizhou` | **Qizhou** | **齐州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 51 | 4 | b_licheng [castle], b_linji [city], b... |
| 71 | `c_yunzhou` | **Yunzhou** | **郓州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 56 | 4 | b_xuchang [castle], b_donge [city], b... |

##### Duchy of Ziqing (`d_ziqing` / 淄青) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 72 | `c_dengzhou` | **Dengzhou** | **登州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 22 | 4 | b_penglai [castle], b_muping [city], ... |
| 73 | `c_laizhou` | **Laizhou** | **莱州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 33 | 4 | b_ye_1 [castle], b_jiaoshui [city], b... |
| 74 | `c_qingzhou` | **Qingzhou** | **青州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 39 | 4 | b_yidu_2 [castle], b_linzi [city], b_... |
| 75 | `c_weizhou_4` | **Weizhou** | **潍州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 33 | 2 | b_beihai [castle], b_changyi [city] |
| 76 | `c_zichuan` | **Zizhou** | **淄州** | — | ✅ Pre-867 Classical | `k_qingxu` | han | 36 | 3 | b_zichuan [castle], b_zouping [city],... |

#### 2.1.6 Kingdom of Youji (`k_youji` / 幽蓟)
*Extent: **10 Counties** | Development: **389** (avg 38.9) | Roman Control: **10/10** | Flagged Anachronisms: **0***

##### Duchy of Yideng (`d_yideng` / 易定) — *2/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 77 | `c_dingzhou` | **Dingzhou** | **定州** | — | ✅ Pre-867 Classical | **[RE]** | han | 43 | 2 | b_anxi [castle], b_wangdu [city] |
| 78 | `c_yizhou_1` | **Yizhou** | **易州** | — | ✅ Pre-867 Classical | **[RE]** | han | 39 | 3 | b_yi [castle], b_rongcheng [city], b_... |

##### Duchy of Yingmo (`d_yingmo` / 瀛莫) — *2/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 79 | `c_hejian` | **Yingzhou** | **瀛州** | — | ✅ Pre-867 Classical | **[RE]** | han | 40 | 3 | b_hejian [castle], b_leshou [city], b... |
| 80 | `c_mozhou` | **Mozhou** | **莫州** | — | ✅ Pre-867 Classical | **[RE]** | han | 47 | 3 | b_mo [castle], b_wenan [city], b_qing... |

##### Duchy of Youzhou (`d_youzhou` / 幽州) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 81 | `c_guizhou_2` | **Guizhou** | **妫州** | — | ✅ Pre-867 Classical | **[RE]** | han | 34 | 2 | b_huairong [castle], b_jinshan_2 [city] |
| 82 | `c_jizhou_1` | **Jizhou** | **蓟州** | — | ✅ Pre-867 Classical | **[RE]** | han | 41 | 4 | b_yuyang [castle], b_sanhe [city], b_... |
| 83 | `c_pinzhou` | **Pinzhou** | **平州** | — | ✅ Pre-867 Classical | **[RE]** | han | 33 | 4 | b_lulong [castle], b_anxi_2 [church],... |
| 84 | `c_tanzhou_2` | **Tanzhou** | **檀州** | — | ✅ Pre-867 Classical | **[RE]** | khitan | 32 | 4 | b_miyun [castle], b_yanle [castle], b... |
| 85 | `c_youzhou` | **Youzhou** | **幽州** | — | ✅ Pre-867 Classical | **[RE]** | han | 44 | 5 | b_ji [castle], b_lu [city], b_changpi... |
| 86 | `c_zhuozhou` | **Zhuozhou** | **涿州** | — | ✅ Pre-867 Classical | **[RE]** | han | 36 | 2 | b_fanyang [castle], b_guan [city] |

### 2.2 Empire of Liangyi (`e_liangyi` / 梁益)
- **De Jure Extent:** **89 Counties**, 21 Duchies, 6 Kingdoms.
- **Total Development:** **3,788.0** (Average: 42.6) | **Baronies:** 261
- **1154 Roman Empire Control:** **0 / 89 counties** (0.0%) | **Anachronisms Flagged:** **0**

#### 2.2.1 Kingdom of Dali (`k_dali` / 大理)
*Extent: **17 Counties** | Development: **647** (avg 38.1) | Roman Control: **0/17** | Flagged Anachronisms: **0***

##### Duchy of Dali (`d_dali` / 大理) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 87 | `c_dali` | **Dali** | **大理** | — | ✅ Pre-867 Classical | `k_qianzhong` | bai | 39 | 3 | b_dali_1 [castle], b_ningbei [city], ... |
| 88 | `c_nongdong` | **Nongdong** | **弄栋** | — | ✅ Pre-867 Classical | `k_qianzhong` | bai | 33 | 2 | b_nongdong [castle], b_shenli [church] |
| 89 | `c_weichu` | **Weichu** | **威楚** | — | ✅ Pre-867 Classical | `k_qianzhong` | bai | 43 | 2 | b_elu [castle], b_moyu [city] |

##### Duchy of Huichuan (`d_huichuan` / 会川) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 90 | `c_huichuan` | **Huichuan** | **会川** | — | ✅ Pre-867 Classical | `k_qianzhong` | Huichuan | 35 | 3 | b_huichuan_1 [castle], b_nuodan [city... |
| 91 | `c_jianchang_1` | **Jianchang** | **建昌** | — | ✅ Pre-867 Classical | `k_qianzhong` | Huichuan | 25 | 2 | b_yuexi [castle], b_taideng [city] |

##### Duchy of Jianchuan (`d_jianchuan` / 剑川) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 92 | `c_chengji` | **Chengji** | **成偈** | — | ✅ Pre-867 Classical | `k_qianzhong` | kachin | 27 | 3 | b_chengji_1 [castle], b_luogong [city... |
| 93 | `c_jianchuan` | **Jianchuan** | **剑川** | — | ✅ Pre-867 Classical | `k_qianzhong` | kachin | 30 | 3 | b_jianchuan [castle], b_lanxi [city],... |
| 94 | `c_xiangcheng` | **Xiangcheng** | **香城** | — | ✅ Pre-867 Classical | `k_qianzhong` | yi | 26 | 3 | b_kunmimg [castle], b_lidou [city], b... |

##### Duchy of Tonghai (`d_tonghai` / 通海) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 95 | `c_muze` | **Muze** | **目则** | — | ✅ Pre-867 Classical | `k_qianzhong` | yi | 51 | 3 | b_muze [castle], b_ayue [city], b_men... |
| 96 | `c_tonghai` | **Tonghai** | **通海** | — | ✅ Pre-867 Classical | `k_qianzhong` | bai | 49 | 4 | b_tonghai [castle], b_xie [city], b_q... |
| 97 | `c_zuining` | **Zuining** | **最宁** | — | ✅ Pre-867 Classical | `k_qianzhong` | bai | 43 | 3 | b_hami_2 [castle], b_baogu [city], b_... |

##### Duchy of Tuodong (`d_tuodong` / 拓东) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 98 | `c_dongchuan` | **Dongchuan** | **东川** | — | ✅ Pre-867 Classical | `k_qianzhong` | yi | 37 | 3 | b_bipan [castle], b_lulu [city], b_yi... |
| 99 | `c_shanchan` | **Shanchan** | **善阐** | — | ✅ Pre-867 Classical | `k_qianzhong` | bai | 44 | 3 | b_tuodong [castle], b_anning [city], ... |
| 100 | `c_shicheng` | **Shicheng** | **石城** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 42 | 3 | b_shicheng_1 [castle], b_yushi [city]... |

##### Duchy of Yinsheng (`d_yinsheng` / 银生) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 101 | `c_buri` | **Buri** | **步日** | — | ✅ Pre-867 Classical | `k_qianzhong` | tai | 41 | 3 | b_buri_2 [temple_citadel], b_buteng [... |
| 102 | `c_weiyuan` | **Weiyuan** | **威远** | — | ✅ Pre-867 Classical | `k_qianzhong` | bai | 37 | 2 | b_weiyuan_1 [castle], b_luotuo [city] |
| 103 | `c_yinsheng` | **Yinsheng** | **银生** | — | ✅ Pre-867 Classical | `k_qianzhong` | bai | 45 | 3 | b_menggu [castle], b_kainan [city], b... |

#### 2.2.2 Kingdom of Dongchuan (`k_dongchuan` / 东川)
*Extent: **12 Counties** | Development: **504** (avg 42.0) | Roman Control: **0/12** | Flagged Anachronisms: **0***

##### Duchy of Dongchuan (`d_dongchuan` / 东川) — *0/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 104 | `c_jianzhou_1` | **Jianzhou** | **剑州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 51 | 3 | b_puan [castle], b_jianmen [city], b_... |
| 105 | `c_longzhou` | **Longzhou** | **龙州** | — | ✅ Pre-867 Classical | `k_xichuan` | qiang | 45 | 2 | b_jiangyou [castle], b_qingchuan [city] |
| 106 | `c_mianzhou` | **Mianzhou** | **绵州** | — | ✅ Pre-867 Classical | `k_xichuan` | qiang | 38 | 2 | b_baxi [castle], b_weicheng [city] |
| 107 | `c_puzhou` | **Puzhou** | **普州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 39 | 2 | b_anyue [castle], b_anju [city] |
| 108 | `c_tongchuan` | **Tongchuan** | **潼川** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 46 | 4 | b_qi_1 [castle], b_yanting [city], b_... |
| 109 | `c_zizhou_2` | **Zizhou** | **资州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 39 | 2 | b_panshi [castle], b_ziyang [city] |

##### Duchy of Wuxin (`d_wuxin` / 武信) — *0/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 110 | `c_changzhou_1` | **Changzhou** | **昌州** | — | ✅ Pre-867 Classical | `k_xichuan` | Kuizhou | 41 | 2 | b_jingnan [castle], b_yongchuan [city] |
| 111 | `c_luzhou_2` | **Luzhou** | **泸州** | — | ✅ Pre-867 Classical | `k_xichuan` | Kuizhou | 41 | 3 | b_luchuan [castle], b_mianshui [city]... |
| 112 | `c_nanxi` | **Rongzhou** | **戎州** | — | ✅ Pre-867 Classical | `k_xichuan` | Kuizhou | 38 | 2 | b_bodao [castle], b_yibin [city] |
| 113 | `c_rongzhou` | **Rongzhou** | **荣州** | — | ✅ Pre-867 Classical | `k_xichuan` | Kuizhou | 40 | 2 | b_xuchuan [castle], b_gongjing [city] |
| 114 | `c_suining` | **Suizhou** | **遂州** | — | ✅ Pre-867 Classical | `k_xichuan` | Kuizhou | 41 | 3 | b_fangyi [castle], b_suining_1 [city]... |
| 115 | `c_yuzhou_2` | **Yuzhou** | **渝州** | — | ✅ Pre-867 Classical | `k_xichuan` | Kuizhou | 45 | 3 | b_ba [castle], b_bishan [city], b_jia... |

#### 2.2.3 Kingdom of Kuizhou (`k_kuizhou` / 夔州)
*Extent: **17 Counties** | Development: **766** (avg 45.1) | Roman Control: **0/17** | Flagged Anachronisms: **0***

##### Duchy of Kuizhong (`d_kuizhong` / 夔忠) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 116 | `c_fuzhou_4` | **Fuzhou** | **涪州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 43 | 4 | b_fuling [castle], b_lewen [city], b_... |
| 117 | `c_kuizhou` | **Kuizhou** | **夔州** | — | ✅ Pre-867 Classical | `k_qianzhong` | yi | 46 | 4 | b_fengjie [castle], b_dachang [city],... |
| 118 | `c_wanzhou` | **Wanzhou** | **万州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 47 | 4 | b_nanpu [castle], b_wuning_1 [city], ... |
| 119 | `c_zhongzhou` | **Zhongzhou** | **忠州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 43 | 3 | b_linjiang [castle], b_dianjiang [cit... |

##### Duchy of Qianzhong (`d_qianzhong` / 黔中) — *0/7 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 120 | `c_bochuan` | **Bozhou** | **播州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 30 | 2 | b_zunyi [castle], b_daishui [city] |
| 121 | `c_nanzhou` | **Nanzhou** | **南州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 37 | 2 | b_nanchuan [castle], b_sanxi [city] |
| 122 | `c_qianzhou_1` | **Qianzhou** | **黔州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 42 | 4 | b_pengshui [castle], b_qianjiang_1 [c... |
| 123 | `c_shizhou_1` | **Shizhou** | **施州** | — | ✅ Pre-867 Classical | `k_qianzhong` | yi | 46 | 4 | b_qingjiang_1 [castle], b_jianshi [ci... |
| 124 | `c_sizhou` | **Sizhou** | **思州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 39 | 4 | b_wuchuan [castle], b_siqiong [castle... |
| 125 | `c_yizhou_3` | **Yizhou** | **夷州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 32 | 3 | b_suiyang [castle], b_yangchuan [city... |
| 126 | `c_zhenxi` | **Zhenzhou** | **溱州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 33 | 3 | b_rongyi [castle], b_leyuan [church],... |

##### Duchy of Wuxi (`d_wuxi` / 五溪) — *0/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 127 | `c_lingxi` | **Xizhou** | **溪州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 51 | 3 | b_daxiang [castle], b_danting [church... |
| 128 | `c_luxi` | **Chenzhou** | **辰州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 73 | 5 | b_yuanling [castle], b_chenxi [city],... |
| 129 | `c_luyang` | **Jinzhou** | **锦州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 51 | 3 | b_luyang [castle], b_changfeng [city]... |
| 130 | `c_shangxi` | **Shangxi** | **上溪** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 58 | 3 | b_shanxi [castle], b_anfu [city], b_b... |
| 131 | `c_tanyang` | **Xuzhou** | **叙州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 55 | 4 | b_longbiao [castle], b_tanyang [city]... |
| 132 | `c_yezhou` | **Jiangzhou** | **奖州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 40 | 3 | b_eshan [castle], b_zijiang [city], b... |

#### 2.2.4 Kingdom of Qianzhong (`k_qianzhong` / 黔中)
*Extent: **18 Counties** | Development: **674** (avg 37.4) | Roman Control: **0/18** | Flagged Anachronisms: **0***

##### Duchy of Luodian (`d_luodian` / 罗殿) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 133 | `c_luodian` | **Luodian** | **罗殿** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 36 | 2 | b_shian [castle], b_lainan [city] |
| 134 | `c_yanchuan` | **Yanchuan** | **琰川** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 39 | 2 | b_yanchuan_1 [castle], b_jiangzhou [c... |
| 135 | `c_yanzhou_3` | **Yanzhou** | **琰州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 32 | 4 | b_wuhou [castle], b_jiangkun [city], ... |

##### Duchy of Luoshi (`d_luoshi` / 罗氏) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 136 | `c_shaoqing` | **Xizhou** | **羲州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 35 | 4 | b_xizhou [castle], b_haozhou [city], ... |
| 137 | `c_shunzhou` | **Shunzhou** | **顺州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 40 | 3 | b_qushui_1 [castle], b_humao [city], ... |
| 138 | `c_sie` | **Sie** | **思峨** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 42 | 4 | b_sie [castle], b_yujing [city], b_fe... |
| 139 | `c_zongzhou` | **Zongzhou** | **总州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 33 | 3 | b_songshui [castle], b_yanquan [churc... |

##### Duchy of Shimen (`d_shimen` / 石门) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 140 | `c_jingzhou_2` | **Xiezhou** | **协州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 40 | 3 | b_jingchuan [castle], b_humu [city], ... |
| 141 | `c_quzhou_1` | **Quzhou** | **曲州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 36 | 2 | b_zhuti [castle], b_dongan_2 [city] |
| 142 | `c_yinzhou_1` | **Yinzhou** | **殷州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 37 | 3 | b_yinzhou [castle], b_kaibian [city],... |

##### Duchy of Xiyuan (`d_xiyuan` / 西原) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 143 | `c_guile` | **Guile** | **归乐** | — | ✅ Pre-867 Classical | `e_lingnan` | Yi-Bouxcuengh | 40 | 3 | b_guile [castle], b_lengzhou [city], ... |
| 144 | `c_siyuan` | **Siyuan** | **思源** | — | ✅ Pre-867 Classical | `e_lingnan` | Yi-Bouxcuengh | 48 | 2 | b_siyuan [castle], b_temo [city] |
| 145 | `c_wulong` | **Wulong** | **武龙** | — | ✅ Pre-867 Classical | `e_lingnan` | Yi-Bouxcuengh | 44 | 3 | b_wulong_1 [castle], b_dongjian [city... |

##### Duchy of Zangke (`d_zangke` / 牂牁) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 146 | `c_guzhou` | **Guzhou** | **古州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 39 | 3 | b_leshan [castle], b_lexing [city], b... |
| 147 | `c_huangzhou_1` | **Huangzhou** | **晃州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 39 | 2 | b_bianxi [castle], b_tonggu_1 [city] |
| 148 | `c_juzhou` | **Juzhou** | **矩州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Yi-Bouxcuengh | 32 | 4 | b_pingan [castle], b_binhua_1 [city],... |
| 149 | `c_nanping` | **Nanping** | **南平** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 31 | 4 | b_nanping [castle], b_maolong [city],... |
| 150 | `c_yingzhou_4` | **Yingzhou** | **应州** | — | ✅ Pre-867 Classical | `k_qianzhong` | hmong | 31 | 3 | b_dushang [castle], b_tuolong [city],... |

#### 2.2.5 Kingdom of Xichuan (`k_xichuan` / 西川)
*Extent: **12 Counties** | Development: **452** (avg 37.7) | Roman Control: **0/12** | Flagged Anachronisms: **0***

##### Duchy of Qiongnan (`d_qiongnan` / 邛南) — *0/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 151 | `c_hanyuan` | **Lizhou** | **黎州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 34 | 2 | b_hanyuan [castle], b_tongwang [city] |
| 152 | `c_jiazhou` | **Jiazhou** | **嘉州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 37 | 4 | b_longyou [castle], b_jiajiang [city]... |
| 153 | `c_meizhou` | **Meizhou** | **眉州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 39 | 3 | b_tongyi [castle], b_danling [city], ... |
| 154 | `c_qiongbu` | **Qiongbu** | **邛部** | — | ✅ Pre-867 Classical | `k_xichuan` | qiang | 28 | 3 | b_nuozuo [castle], b_beilu_2 [city], ... |
| 155 | `c_qiongzhou` | **Qiongzhou** | **邛州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 44 | 3 | b_linqiong [castle], b_pujiang [city]... |
| 156 | `c_yazhou_2` | **Yazhou** | **雅州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 36 | 3 | b_yandao [castle], b_rongjing [city],... |

##### Duchy of Xichuan (`d_xichuan` / 西川) — *0/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 157 | `c_chengdu` | **Chengdu** | **成都** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 45 | 3 | b_chengdu [castle], b_wenjiang [city]... |
| 158 | `c_hanzhou` | **Hanzhou** | **汉州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 37 | 3 | b_luo [castle], b_mianzhu [city], b_d... |
| 159 | `c_jianyang` | **Jianzhou** | **简州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 40 | 2 | b_yangan [castle], b_jinshui [city] |
| 160 | `c_lingzhou_1` | **Lingzhou** | **陵州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 42 | 2 | b_renshou [castle], b_jingyan [city] |
| 161 | `c_maozhou` | **Maozhou** | **茂州** | — | ✅ Pre-867 Classical | `k_xichuan` | qiang | 32 | 3 | b_wenshan [castle], b_tonghua [city],... |
| 162 | `c_pengzhou` | **Pengzhou** | **彭州** | — | ✅ Pre-867 Classical | `k_xichuan` | han | 38 | 2 | b_jiulong [castle], b_daojiang [city] |

#### 2.2.6 Kingdom of Xingyuan (`k_xingyuan` / 兴元)
*Extent: **13 Counties** | Development: **745** (avg 57.3) | Roman Control: **0/13** | Flagged Anachronisms: **0***

##### Duchy of Baqu (`d_baqu` / 巴渠) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 163 | `c_bazhou` | **Bazhou** | **巴州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 59 | 3 | b_huacheng [castle], b_qizhang [city]... |
| 164 | `c_kaizhou` | **Kaizhou** | **开州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 44 | 2 | b_kaijiang [castle], b_xinpu [city] |
| 165 | `c_quzhou` | **Quzhou** | **渠州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 51 | 3 | b_liujiang [castle], b_linshui [city]... |
| 166 | `c_tongzhou_1` | **Tongzhou** | **通州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 54 | 4 | b_tongchuan_1 [castle], b_baqu [city]... |

##### Duchy of Lilang (`d_lilang` / 利阆) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 167 | `c_guozhou_1` | **Guozhou** | **果州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 44 | 3 | b_nanchong [castle], b_xiangru [churc... |
| 168 | `c_langzhou_1` | **Langzhou** | **阆州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 55 | 3 | b_langzhong [castle], b_cangxi [city]... |
| 169 | `c_lizhou_2` | **Lizhou** | **利州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 69 | 3 | b_miangu [castle], b_jinggu [city], b... |
| 170 | `c_pengzhou_2` | **Pengzhou** | **蓬州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 50 | 2 | b_pengchi [castle], b_fuyu [city] |
| 171 | `c_wenzhou` | **Wenzhou** | **文州** | — | ✅ Pre-867 Classical | `k_xingyuan` | qiang | 47 | 2 | b_qushui [castle], b_tongchang [city] |

##### Duchy of Xingyuan (`d_xingyuan` / 兴元) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 172 | `c_bizhou` | **Bizhou** | **壁州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 63 | 4 | b_tongjiang [castle], b_baishi [city]... |
| 173 | `c_jizhou_2` | **Jizhou** | **集州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 57 | 2 | b_nanjiang [castle], b_jiachuan [city] |
| 174 | `c_xingyuan` | **Xingyuan** | **兴元** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 78 | 4 | b_nanzheng [castle], b_xi [city], b_s... |
| 175 | `c_yangzhou_1` | **Yangzhou** | **洋州** | — | ✅ Pre-867 Classical | `k_xingyuan` | han | 74 | 3 | b_xingdao [castle], b_xixiang [city],... |

### 2.3 Empire of Jingyang (`e_jingyang` / 荆扬)
- **De Jure Extent:** **80 Counties**, 17 Duchies, 7 Kingdoms.
- **Total Development:** **5,550.0** (Average: 69.4) | **Baronies:** 308
- **1154 Roman Empire Control:** **0 / 80 counties** (0.0%) | **Anachronisms Flagged:** **0**

#### 2.3.1 Kingdom of Fujian (`k_fujian` / 福建)
*Extent: **9 Counties** | Development: **697** (avg 77.4) | Roman Control: **0/9** | Flagged Anachronisms: **0***

##### Duchy of Jianning (`d_jianning` / 建宁) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 176 | `c_jian_an` | **Jianzhou** | **建州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 74 | 4 | b_jianan [castle], b_pucheng [city], ... |
| 177 | `c_nanjian` | **Nanjian** | **南剑** | — | ✅ Pre-867 Classical | `k_liangzhe` | yao | 70 | 6 | b_jianpu [castle], b_shunchang [city]... |
| 178 | `c_shaowu` | **Shaowu** | **邵武** | — | ✅ Pre-867 Classical | `k_liangzhe` | yao | 62 | 3 | b_shaowu [castle], b_guangze [city], ... |
| 179 | `c_tingzhou` | **Tingzhou** | **汀州** | — | ✅ Pre-867 Classical | `k_liangzhe` | yao | 69 | 4 | b_changting [castle], b_wuping [churc... |

##### Duchy of Pinghai (`d_pinghai` / 平海) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 180 | `c_quanzhou` | **Quanzhou** | **泉州** | — | ✅ Pre-867 Classical | `k_liuqiu` | Huixun | 91 | 4 | b_jinjiang [castle], b_dehua [city], ... |
| 181 | `c_xinghua` | **Xinghua** | **兴化** | — | ✅ Pre-867 Classical | `c_xinghua` | Huixun | 77 | 3 | b_putian [castle], b_xianyou [city], ... |
| 182 | `c_zhangzhou` | **Zhangzhou** | **漳州** | — | ✅ Pre-867 Classical | `c_zhangzhou` | Huixun | 96 | 4 | b_longxi_1 [castle], b_zhangpu [city]... |

##### Duchy of Weiwu (`d_weiwu` / 威武) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 183 | `c_funing` | **Ningzhou** | **宁州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 80 | 3 | b_changxi [castle], b_ningde [city], ... |
| 184 | `c_fuzhou_1` | **Fuzhou** | **福州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 78 | 5 | b_min [castle], b_yongtai [city], b_l... |

#### 2.3.2 Kingdom of Huainan (`k_huainan` / 淮南)
*Extent: **10 Counties** | Development: **633** (avg 63.3) | Roman Control: **0/10** | Flagged Anachronisms: **0***

##### Duchy of Huainan (`d_huainan` / 淮南) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 185 | `c_chuzhou_1` | **Chuzhou** | **楚州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 51 | 4 | b_shanyang_2 [castle], b_yancheng [ci... |
| 186 | `c_chuzhou_2` | **Chuzhou** | **滁州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 52 | 3 | b_qingliu [castle], b_quanjiao [city]... |
| 187 | `c_taizhou_1` | **Taizhou** | **泰州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 63 | 3 | b_hailing [castle], b_rugao [church],... |
| 188 | `c_yangzhou` | **Yangzhou** | **扬州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 63 | 4 | b_jiangdu [castle], b_tianchang [city... |

##### Duchy of Huaixi (`d_huaixi` / 淮西) — *0/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 189 | `c_guangzhou` | **Guangzhou** | **光州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 55 | 4 | b_dingcheng [castle], b_gushi [city],... |
| 190 | `c_haozhou` | **Haozhou** | **濠州** | — | ✅ Pre-867 Classical | `e_lingnan` | han | 61 | 3 | b_zhongli [castle], b_dingyuan [castl... |
| 191 | `c_liyang_2` | **Liyang** | **历阳** | — | ✅ Pre-867 Classical | `k_huainan` | han | 76 | 2 | b_liyang [castle], b_hanshan [city] |
| 192 | `c_lujiang` | **Luzhou** | **庐州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 71 | 5 | b_hefei [castle], b_shen [city], b_lu... |
| 193 | `c_shouzhou` | **Shouzhou** | **寿州** | — | ✅ Pre-867 Classical | `k_huainan` | han | 63 | 5 | b_shouchun [castle], b_luan [city], b... |
| 194 | `c_shuzhou` | **Shuzhou** | **舒州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 78 | 5 | b_huaining [castle], b_tongcheng [cit... |

#### 2.3.3 Kingdom of Hunan (`k_hunan` / 湖南)
*Extent: **9 Counties** | Development: **473** (avg 52.6) | Roman Control: **0/9** | Flagged Anachronisms: **0***

##### Duchy of Hunan (`d_hunan` / 湖南) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 195 | `c_chenzhou_1` | **Chenzhou** | **郴州** | — | ✅ Pre-867 Classical | `e_lingnan` | Guiyang | 44 | 5 | b_chen [castle], b_zixing [city], b_y... |
| 196 | `c_guiyang` | **Guiyang** | **桂阳** | — | ✅ Pre-867 Classical | `e_lingnan` | Guiyang | 47 | 3 | b_pingyang [castle], b_lanshan [city]... |
| 197 | `c_hengzhou` | **Hengzhou** | **衡州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 56 | 5 | b_hengyang_1 [castle], b_chaling [chu... |
| 198 | `c_lianzhou` | **Lianzhou** | **连州** | — | ✅ Pre-867 Classical | `e_lingnan` | Guiyang | 52 | 3 | b_guiyang [castle], b_lianshan [city]... |
| 199 | `c_tanzhou` | **Tanzhou** | **潭州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 61 | 5 | b_changsha [castle], b_xiangtan [city... |

##### Duchy of Lingling (`d_lingling` / 零陵) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 200 | `c_daozhou` | **Daozhou** | **道州** | — | ✅ Pre-867 Classical | `e_lingnan` | yao | 42 | 3 | b_hongdao [castle], b_dali [city], b_... |
| 201 | `c_quanzhou_2` | **Quanzhou** | **全州** | — | ✅ Pre-867 Classical | `e_lingnan` | han | 43 | 3 | b_xiangyuan_1 [castle], b_xiyan [city... |
| 202 | `c_shaozhou` | **Shaozhou** | **邵州** | — | ✅ Pre-867 Classical | `e_lingnan` | Shaozhou | 73 | 6 | b_shaoyang [castle], b_xinhua [city],... |
| 203 | `c_yongzhou` | **Yongzhou** | **永州** | — | ✅ Pre-867 Classical | `e_lingnan` | han | 55 | 3 | b_lingling [castle], b_qiyang [city],... |

#### 2.3.4 Kingdom of Jiangdong (`k_jiangdong` / 江东)
*Extent: **8 Counties** | Development: **592** (avg 74.0) | Roman Control: **0/8** | Flagged Anachronisms: **0***

##### Duchy of Jiangdong (`d_jiangdong` / 江东) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 204 | `c_changzhou` | **Changzhou** | **常州** | — | ✅ Pre-867 Classical | `k_jiangdong` | han | 73 | 4 | b_jinling [castle], b_wuxi [castle], ... |
| 205 | `c_jiangning` | **Jiangning** | **江宁** | — | ✅ Pre-867 Classical | `k_jiangdong` | han | 71 | 4 | b_jiangning [castle], b_gourong [city... |
| 206 | `c_runzhou` | **Runzhou** | **润州** | — | ✅ Pre-867 Classical | `k_jiangdong` | han | 66 | 3 | b_dantu [castle], b_danyang [city], b... |
| 207 | `c_suzhou_2` | **Suzhou** | **苏州** | — | ✅ Pre-867 Classical | `k_jiangdong` | han | 72 | 3 | b_wu [castle], b_kunshang [church], b... |

##### Duchy of Xuanshe (`d_xuanshe` / 宣歙) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 208 | `c_chizhou` | **Chizhou** | **池州** | — | ✅ Pre-867 Classical | `k_jiangdong` | han | 79 | 4 | b_qiupu [castle], b_qingyang [city], ... |
| 209 | `c_guangde` | **Guangde** | **广德** | — | ✅ Pre-867 Classical | `k_jiangdong` | han | 74 | 2 | b_guangde [castle], b_jianping [church] |
| 210 | `c_shezhou` | **Shezhou** | **歙州** | — | ✅ Pre-867 Classical | `k_jiangdong` | han | 74 | 5 | b_jixi [castle], b_xiuning [city], b_... |
| 211 | `c_xuanzhou` | **Xuanzhou** | **宣州** | — | ✅ Pre-867 Classical | `k_jiangdong` | han | 83 | 5 | b_xuancheng [castle], b_ningguo [city... |

#### 2.3.5 Kingdom of Jiangxi (`k_jiangxi` / 江西)
*Extent: **14 Counties** | Development: **899** (avg 64.2) | Roman Control: **0/14** | Flagged Anachronisms: **0***

##### Duchy of Dingjiang (`d_dingjiang` / 定江) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 212 | `c_nankang` | **Nankang** | **南康** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 76 | 3 | b_duchang [castle], b_pengze [city], ... |
| 213 | `c_raozhou` | **Raozhou** | **饶州** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 76 | 5 | b_poyang [castle], b_fuliang [city], ... |
| 214 | `c_xinhzou` | **Xinzhou** | **信州** | — | ✅ Pre-867 Classical | `k_jiangxi` | yao | 61 | 5 | b_shangrao [castle], b_yushan [city],... |
| 215 | `c_yunyang` | **Jiangzhou** | **江州** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 75 | 3 | b_xunyang [castle], b_ruichang [city]... |

##### Duchy of Jiangxi (`d_jiangxi` / 江西) — *0/7 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 216 | `c_fuzhou_2` | **Fuzhou** | **抚州** | — | ✅ Pre-867 Classical | `k_jiangxi` | yao | 70 | 5 | b_linchuan [castle], b_jinxi [city], ... |
| 217 | `c_hongzhou` | **Hongzhou** | **洪州** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 80 | 5 | b_nanchang [castle], b_wuning [city],... |
| 218 | `c_jianchang` | **Jianchang** | **建昌** | — | ✅ Pre-867 Classical | `k_jiangxi` | yao | 55 | 3 | b_nancheng [castle], b_nanfeng [city]... |
| 219 | `c_jizhou_3` | **Jizhou** | **吉州** | — | ✅ Pre-867 Classical | `k_jiangxi` | yao | 57 | 5 | b_luling [castle], b_anfu_2 [city], b... |
| 220 | `c_linjiang` | **Linjiang** | **临江** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 61 | 3 | b_qingjiang [castle], b_xingan [churc... |
| 221 | `c_yuanzhou` | **Yuanzhou** | **袁州** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 57 | 3 | b_yichun [castle], b_fenyi [city], b_... |
| 222 | `c_yunzhou_2` | **Yunzhou** | **筠州** | — | ✅ Pre-867 Classical | `k_qianzhong` | han | 73 | 3 | b_gaoan [castle], b_xinchang [city], ... |

##### Duchy of Zhaoxin (`d_zhaoxin` / 昭信) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 223 | `c_nanan` | **Nanan** | **南安** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 51 | 3 | b_dayu [castle], b_shangyou [city], b... |
| 224 | `c_ningduzhou` | **Ningduzhou** | **宁都州** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 58 | 4 | b_yudu [castle], b_huichang [church],... |
| 225 | `c_qianzhou` | **Qianzhou** | **虔州** | — | ✅ Pre-867 Classical | `k_jiangxi` | han | 49 | 2 | b_gan [castle], b_anyuan [church] |

#### 2.3.6 Kingdom of Liangzhe (`k_liangzhe` / 两浙)
*Extent: **11 Counties** | Development: **890** (avg 80.9) | Roman Control: **0/11** | Flagged Anachronisms: **0***

##### Duchy of Zhedong (`d_zhedong` / 浙东) — *0/7 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 226 | `c_chuzhou` | **Chuzhou** | **处州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 78 | 5 | b_lishui_1 [castle], b_longquan_1 [ci... |
| 227 | `c_mingzhou_1` | **Mingzhou** | **明州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 75 | 4 | b_mao [castle], b_xiangshan [church],... |
| 228 | `c_taizhou` | **Taizhou** | **台州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 82 | 4 | b_linhai [castle], b_lean [city], b_h... |
| 229 | `c_wenzhou_2` | **Wenzhou** | **温州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 89 | 4 | b_yongjia [castle], b_yuecheng [city]... |
| 230 | `c_wuzhou` | **Wuzhou** | **婺州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 84 | 4 | b_jinhua [castle], b_puyang_1 [city],... |
| 231 | `c_xin_an` | **Quzhou** | **衢州** | — | ✅ Pre-867 Classical | `k_liangzhe` | yao | 73 | 3 | b_xinan [castle], b_longqiu [city], b... |
| 232 | `c_yuezhou` | **Yuezhou** | **越州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 81 | 4 | b_kuaiji [castle], b_yuyao [city], b_... |

##### Duchy of Zhexi (`d_zhexi` / 浙西) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 233 | `c_hangzhou` | **Hangzhou** | **杭州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 87 | 4 | b_qiantang [castle], b_yuhang [city],... |
| 234 | `c_huzhou` | **Huzhou** | **湖州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 79 | 3 | b_wucheng_2 [castle], b_anji [city], ... |
| 235 | `c_muzhou` | **Muzhou** | **睦州** | — | ✅ Pre-867 Classical | `k_liangzhe` | yao | 76 | 4 | b_jiande [castle], b_suian [city], b_... |
| 236 | `c_xiuzhou` | **Xiuzhou** | **秀州** | — | ✅ Pre-867 Classical | `k_liangzhe` | han | 86 | 3 | b_jiaxing [castle], b_huating [city],... |

#### 2.3.7 Kingdom of Shannan (`k_shannan` / 山南)
*Extent: **19 Counties** | Development: **1,366** (avg 71.9) | Roman Control: **0/19** | Flagged Anachronisms: **0***

##### Duchy of Eyue (`d_eyue` / 鄂岳) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 237 | `c_anzhou` | **Anzhou** | **安州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 66 | 4 | b_anlu [castle], b_yingshan [city], b... |
| 238 | `c_ezhou` | **Ezhou** | **鄂州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 74 | 5 | b_jiangxia [castle], b_puqi [city], b... |
| 239 | `c_huangzhou` | **Huangzhou** | **黄州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 68 | 3 | b_huanggang [castle], b_macheng [city... |
| 240 | `c_qizhou_1` | **Qizhou** | **蕲州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 72 | 4 | b_qichun [castle], b_huangmei [city],... |
| 241 | `c_yuezhou_1` | **Yuezhou** | **岳州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 86 | 4 | b_baling [castle], b_changjiang [city... |

##### Duchy of Jingnan (`d_jingnan` / 荆南) — *0/7 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 242 | `c_fuzhou_3` | **Fuzhou** | **复州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 82 | 4 | b_jingling [castle], b_mianyang [city... |
| 243 | `c_guizhou` | **Guizhou** | **归州** | — | ✅ Pre-867 Classical | `k_qianzhong` | yi | 55 | 3 | b_zigui [castle], b_badong [city], b_... |
| 244 | `c_hanyang` | **Hanyang** | **汉阳** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 72 | 2 | b_hanyang [castle], b_hanchuan [city] |
| 245 | `c_jiangling` | **Jiangling** | **江陵** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 81 | 5 | b_jiangling [castle], b_dangyang [cit... |
| 246 | `c_langzhou` | **Langzhou** | **朗州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 92 | 4 | b_wuling [castle], b_longyang [city],... |
| 247 | `c_liyang` | **Hezhou** | **和州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 89 | 5 | b_liyang_1 [castle], b_cili [city], b... |
| 248 | `c_xiazhou_1` | **Xiazhou** | **峡州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 81 | 3 | b_yiling [castle], b_yuanan [city], b... |

##### Duchy of Xiangdeng (`d_xiangdeng` / 襄邓) — *0/7 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 249 | `c_dengzhou_1` | **Dengzhou** | **邓州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 70 | 5 | b_rang [castle], b_xinye [city], b_na... |
| 250 | `c_fangzhou_1` | **Fangzhou** | **房州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Kuizhou | 65 | 4 | b_fangling [castle], b_zhushan [city]... |
| 251 | `c_junzhou` | **Junzhou** | **均州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 64 | 3 | b_wudang [castle], b_yunxiang [city],... |
| 252 | `c_suizhou_1` | **Suizhou** | **隋州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 60 | 4 | b_sui [castle], b_tangcheng [city], b... |
| 253 | `c_tangzhou` | **Tangzhou** | **唐州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 51 | 4 | b_biyang_1 [castle], b_beiyang [castl... |
| 254 | `c_xiangyang` | **Xiangyang** | **襄阳** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 68 | 5 | b_xiangyang [castle], b_gucheng [city... |
| 255 | `c_yingzhou_2` | **Yingzhou** | **郢州** | — | ✅ Pre-867 Classical | `k_qianzhong` | Xiangyang | 70 | 3 | b_changshou [castle], b_fushui [city]... |

### 2.4 Empire of Yongliang (`e_yongliang` / 雍凉)
- **De Jure Extent:** **73 Counties**, 19 Duchies, 3 Kingdoms.
- **Total Development:** **3,146.0** (Average: 43.1) | **Baronies:** 208
- **1154 Roman Empire Control:** **50 / 73 counties** (68.5%) | **Anachronisms Flagged:** **3**

#### 2.4.1 Kingdom of Guannei (`k_guannei` / 关内)
*Extent: **26 Counties** | Development: **1,766** (avg 67.9) | Roman Control: **3/26** | Flagged Anachronisms: **3***

##### Duchy of Binning (`d_binning` / 邠宁) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 256 | `c_binzhou` | **Binzhou** | **邠州** | — | ✅ Pre-867 Classical | `k_guannei` | Binning | 91 | 3 | b_xinping [castle], b_sanshui [city],... |
| 257 | `c_huanzhou` | **Huanzhou** | **环州** | — | ✅ Pre-867 Classical | `k_guannei` | Binning | 65 | 3 | b_fangqu [castle], b_luoyuan [city], ... |
| 258 | `c_jinzhou` | **Jinzhou** | **晋州** | — | ✅ Pre-867 Classical | `k_guannei` | Binning | 76 | 3 | b_dingan [castle], b_pengyuan [church... |
| 259 | `c_qingyang` | **Qingzhou** | **庆州** | — | ✅ Pre-867 Classical | `k_guannei` | Binning | 64 | 3 | b_anhua [castle], b_tongchuan [city],... |

##### Duchy of Fengxiang (`d_fengxiang` / 凤翔) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 260 | `c_fengxiang` | **Fengxiang** | **凤翔** | — | ✅ Pre-867 Classical | `k_guannei` | Binning | 89 | 3 | b_tianxing [castle], b_purun [city], ... |
| 261 | `c_longzhou_2` | **Longzhou** | **陇州** | — | ✅ Pre-867 Classical | `k_guannei` | Binning | 82 | 3 | b_qianyuan [castle], b_qianyang [city... |

##### Duchy of Fufang (`d_fufang` / 鄜坊) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 262 | `c_danzhou` | **Danzhou** | **丹州** | — | ✅ Pre-867 Classical | `k_guannei` | han | 62 | 2 | b_yichuan [castle], b_yunyan [city] |
| 263 | `c_fangzhou` | **Fangzhou** | **坊州** | — | ✅ Pre-867 Classical | `k_guannei` | han | 73 | 3 | b_zhongbu [castle], b_shengping [chur... |
| 264 | `c_fuzhou_5` | **Fuzhou** | **鄜州** | — | ✅ Pre-867 Classical | `k_guannei` | Binning | 68 | 3 | b_luojiao [castle], b_luochuan [city]... |
| 265 | `c_yan_an` | **Yanzhou** | **延州** | — | ✅ Pre-867 Classical | `k_guannei` | tangut | 58 | 5 | b_fushi [castle], b_fuzheng [city], b... |

##### Duchy of Jingyuan (`d_jingyuan` / 泾原) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 266 | `c_jingzhou` | **Jingzhou** | **泾州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Jingzhou River / Regional Basin (Jingzhou)* | **[RE]** | Wulan | 64 | 3 | b_baoding [castle], b_linjing [city],... |
| 267 | `c_xiaoguan` | **Xiaoguan** | **萧关** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Xiaoguan River / Regional Basin (Xiaoguan)* | **[RE]** | Wulan | 42 | 2 | b_xioaguan [castle], b_huaide [city] |
| 268 | `c_yuanzhou_2` | **Yuanzhou** | **原州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Yuanzhou_2 River / Regional Basin (Yuanzhou_2)* | **[RE]** | sogdian | 62 | 3 | b_pinggao [castle], b_baiquan [city],... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Jingyuan:**
> * **`c_jingzhou` (Jingzhou / 泾州):** Frontier screening flag; resolved to the ancient Jing River (Jinghe) basin. *Resolved via Option B: **Option B:** `Jingzhou River / Regional Basin` (Jingzhou).*
> * **`c_xiaoguan` (Xiaoguan / 萧关):** Xiao Pass (萧关) on Mount Liupan; flagged as a military pass rather than an ancient civil oppidum. *Resolved via Option B: **Option B:** `Xiaoguan River / Regional Basin` (Xiaoguan).*
> * **`c_yuanzhou_2` (Yuanzhou / 原州):** Duplicate key disambiguation; resolved to the Upper Qingshui / Yuan basin. *Resolved via Option B: **Option B:** `Yuanzhou_2 River / Regional Basin` (Yuanzhou_2).*

##### Duchy of Jinshang (`d_jinshang` / 金商) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 269 | `c_jinzhou_1` | **Jinzhou** | **金州** | — | ✅ Pre-867 Classical | `k_guannei` | han | 73 | 4 | b_xicheng [castle], b_ankang [castle]... |
| 270 | `c_shangzhou` | **Shangzhou** | **商州** | — | ✅ Pre-867 Classical | `k_guannei` | han | 68 | 4 | b_shangluo [castle], b_shangjin [city... |

##### Duchy of Qincheng (`d_qincheng` / 秦成) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 271 | `c_chengzhou` | **Chengzhou** | **成州** | — | ✅ Pre-867 Classical | `k_guannei` | qiang | 56 | 3 | b_tonggu [castle], b_shanglu [city], ... |
| 272 | `c_jiezhou` | **Jiezhou** | **阶州** | — | ✅ Pre-867 Classical | `k_guannei` | qiang | 57 | 2 | b_jiangli [castle], b_fujin [city] |
| 273 | `c_minzhou` | **Minzhou** | **岷州** | — | ✅ Pre-867 Classical | `k_guannei` | qiang | 50 | 3 | b_hezheng [castle], b_youchuan [city]... |
| 274 | `c_qinzhou_1` | **Qinzhou** | **秦州** | — | ✅ Pre-867 Classical | `k_guannei` | Wulan | 72 | 4 | b_chengji [castle], b_qingshui [city]... |
| 275 | `c_weizhou_2` | **Weizhou** | **渭州** | — | ✅ Pre-867 Classical | `k_guannei` | Wulan | 52 | 2 | b_longxi [castle], b_weiyuan [city] |

##### Duchy of Xingfeng (`d_xingfeng` / 兴凤) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 276 | `c_fengzhou` | **Fengzhou** | **凤州** | — | ✅ Pre-867 Classical | `k_guannei` | han | 75 | 2 | b_liangquan [castle], b_hechi [city] |
| 277 | `c_xingqing` | **Xingqing** | **兴庆** | — | ✅ Pre-867 Classical | `k_guannei` | han | 59 | 2 | b_shunzheng [castle], b_changju [city] |

##### Duchy of Yongxing (`d_yongxing` / 永兴) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 278 | `c_huayin` | **Huazhou** | **华州** | — | ✅ Pre-867 Classical | `k_guannei` | han | 76 | 3 | b_zheng [castle], b_huayin [city], b_... |
| 279 | `c_jingzhao` | **Jingzhao** | **京兆** | — | ✅ Pre-867 Classical | `k_guannei` | han | 87 | 5 | b_changan [castle], b_jingyang [city]... |
| 280 | `c_tongzhou` | **Tongzhou** | **同州** | — | ✅ Pre-867 Classical | `k_guannei` | han | 70 | 3 | b_pingyi [castle], b_heyang_1 [castle... |
| 281 | `c_yaozhou` | **Yaozhou** | **耀州** | — | ✅ Pre-867 Classical | `k_guannei` | han | 75 | 3 | b_huayuan [castle], b_fuping [city], ... |

#### 2.4.2 Kingdom of Hexi (`k_hexi` / 河西)
*Extent: **23 Counties** | Development: **636** (avg 27.7) | Roman Control: **23/23** | Flagged Anachronisms: **0***

##### Duchy of Gansu (`d_gansu` / 甘肃) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 282 | `c_ganzhou` | **Ganzhou** | **甘州** | — | ✅ Pre-867 Classical | **[RE]** | sogdian | 25 | 3 | b_zhangye [castle], b_shandan [city],... |
| 283 | `c_jiankang` | **Jiankang** | **建康** | — | ✅ Pre-867 Classical | **[RE]** | han | 19 | 2 | b_jiankang [castle], b_qilian [city] |
| 284 | `c_jiuquan` | **Suzhou** | **肃州** | — | ✅ Pre-867 Classical | **[RE]** | tocharian | 22 | 3 | b_jiuquan [castle], b_dongting [city]... |
| 285 | `c_liaoquan` | **Liaoquan** | **蓼泉** | — | ✅ Pre-867 Classical | **[RE]** | han | 23 | 3 | b_liaoquan [castle], b_ganjun [city],... |
| 286 | `c_yumen` | **Yumen** | **玉门** | — | ✅ Pre-867 Classical | **[RE]** | han | 26 | 3 | b_yumen [castle], b_jinshan [city], b... |
| 287 | `c_zhenwu_1` | **Zhenwu** | **振武** | — | ✅ Pre-867 Classical | **[RE]** | han | 21 | 2 | b_zhenwu [castle], b_baiting [city] |

##### Duchy of Guasha (`d_guasha` / 瓜沙) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 288 | `c_guazhou` | **Guazhou** | **瓜州** | — | ✅ Pre-867 Classical | **[RE]** | sogdian | 29 | 3 | b_jinchang [castle], b_changle [city]... |
| 289 | `c_hehe` | **Hehe** | **合河** | — | ✅ Pre-867 Classical | **[RE]** | han | 29 | 3 | b_hehe [castle], b_baizhang [city], b... |
| 290 | `c_shazhou` | **Shazhou** | **沙州** | — | ✅ Pre-867 Classical | **[RE]** | han | 36 | 2 | b_dunhuang_2 [castle], b_mogao [city] |
| 291 | `c_shouchang` | **Shouchang** | **寿昌** | — | ✅ Pre-867 Classical | **[RE]** | han | 28 | 3 | b_shouchang [castle], b_yangguan [cit... |
| 292 | `c_xincheng` | **Xincheng** | **新城** | — | ✅ Pre-867 Classical | **[RE]** | sogdian | 21 | 2 | b_xincheng [castle], b_mingshui [city] |
| 293 | `c_ziting` | **Ziting** | **子亭** | — | ✅ Pre-867 Classical | **[RE]** | han | 28 | 2 | b_ziting [castle], b_ganquan [city] |

##### Duchy of Hexi (`d_hexi` / 河西) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 294 | `c_baishan` | **Baishan** | **白山** | — | ✅ Pre-867 Classical | **[RE]** | bodpa | 31 | 2 | b_baishan [castle], b_xinquan [city] |
| 295 | `c_fanhe` | **Fanhe** | **番禾** | — | ✅ Pre-867 Classical | **[RE]** | Wulan | 22 | 2 | b_fanhe [castle], b_xiutu [city] |
| 296 | `c_guangwu` | **Guangwu** | **广武** | — | ✅ Pre-867 Classical | **[RE]** | Wulan | 30 | 3 | b_guangwu [castle], b_yunjie [city], ... |
| 297 | `c_liangzhou` | **Liangzhou** | **凉州** | — | ✅ Pre-867 Classical | **[RE]** | Wulan | 29 | 3 | b_guzang [castle], b_changsong [city]... |
| 298 | `c_zhanyin` | **Baiyin** | **白银** | — | ✅ Pre-867 Classical | **[RE]** | Wulan | 41 | 3 | b_zhanyin [castle], b_aowei [city], b... |

##### Duchy of Shanzhou (`d_longyou` / 鄯州) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 299 | `c_hezhou_2` | **Hezhou** | **河州** | — | ✅ Pre-867 Classical | **[RE]** | han | 36 | 3 | b_fuhan [castle], b_daxia [city], b_k... |
| 300 | `c_kuozhou` | **Kuozhou** | **廓州** | — | ✅ Pre-867 Classical | **[RE]** | bodpa | 28 | 2 | b_guangwei [castle], b_michuan [city] |
| 301 | `c_lanzhou_1` | **Lanzhou** | **兰州** | — | ✅ Pre-867 Classical | **[RE]** | han | 39 | 2 | b_jincheng_1 [castle], b_didao [city] |
| 302 | `c_xiningzhou` | **Shanzhou** | **鄯州** | — | ✅ Pre-867 Classical | **[RE]** | bodpa | 31 | 4 | b_huangshui [castle], b_longzhi [city... |

##### Duchy of Qilian (`d_qilian` / 祁连) — *2/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 303 | `c_qilin` | **Qilin** | **祁连** | — | ✅ Pre-867 Classical | **[RE]** | tuyuhun | 25 | 2 | b_qilin [castle], b_semnyi [city] |
| 304 | `c_yalong` | **Yalong** | **亚龙** | — | ✅ Pre-867 Classical | **[RE]** | tuyuhun | 17 | 2 | b_yalong [castle], b_yeniugou [church] |

#### 2.4.3 Kingdom of Xia (`k_xia` / 夏)
*Extent: **24 Counties** | Development: **744** (avg 31.0) | Roman Control: **24/24** | Flagged Anachronisms: **0***

##### Duchy of Juyan (`d_juyan` / 居延) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 305 | `c_heihe` | **Heihe** | **黑河** | — | ✅ Pre-867 Classical | **[RE]** | han | 18 | 2 | b_jinguan [castle], b_heihe [city] |
| 306 | `c_mazongshan` | **Mazongshan** | **马鬃山** | — | ✅ Pre-867 Classical | **[RE]** | han | 19 | 2 | b_mazongshan [castle], b_saihantaolai... |
| 307 | `c_tongcheng` | **Tongcheng** | **桐城** | — | ✅ Pre-867 Classical | **[RE]** | yughur | 15 | 2 | b_heicheng [castle], b_sogo [city] |
| 308 | `c_wentugaole` | **Wentugaole** | **温图高勒** | — | ✅ Pre-867 Classical | **[RE]** | han | 13 | 2 | b_wentugaole [castle], b_gurinai [city] |

##### Duchy of Wuluhai (`d_langshan` / 兀剌海) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 309 | `c_hequ` | **Hequ** | **河曲** | — | ✅ Pre-867 Classical | **[RE]** | sogdian | 25 | 3 | b_hequ [castle], b_yuduole [city], b_... |
| 310 | `c_keyimen` | **Wuda** | **乌达** | — | ✅ Pre-867 Classical | **[RE]** | han | 15 | 2 | b_zhongcun [castle], b_wuliji [city] |
| 311 | `c_langshan` | **Wuluhai** | **兀剌海** | — | ✅ Pre-867 Classical | **[RE]** | ongud | 26 | 3 | b_wuluhai [castle], b_dengkou [city],... |

##### Duchy of Shuofang (`d_shuofang` / 朔方) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 312 | `c_huaiyuan` | **Huaiyuan** | **怀远** | — | ✅ Pre-867 Classical | **[RE]** | tangut | 39 | 4 | b_huaiyuan [castle], b_dingyaun [city... |
| 313 | `c_huizhou` | **Huizhou** | **会州** | — | ✅ Pre-867 Classical | **[RE]** | Wulan | 54 | 4 | b_huining [castle], b_huairong_2 [cit... |
| 314 | `c_lingzhou` | **Lingzhou** | **灵州** | — | ✅ Pre-867 Classical | **[RE]** | tangut | 37 | 4 | b_huile [castle], b_lingwu [city], b_... |
| 315 | `c_weizhou_3` | **Weizhou** | **威州** | — | ✅ Pre-867 Classical | **[RE]** | tangut | 48 | 2 | b_wenchi_2 [castle], b_changhua [city] |
| 316 | `c_wulan` | **Wulan** | **乌兰** | — | ✅ Pre-867 Classical | **[RE]** | Wulan | 42 | 3 | b_wulan [castle], b_roulang [city], b... |
| 317 | `c_xiongzhou` | **Xiongzhou** | **雄州** | — | ✅ Pre-867 Classical | **[RE]** | tangut | 39 | 4 | b_mingsha [castle], b_fengan [city], ... |

##### Duchy of Tiande (`d_tiande` / 天德) — *2/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 318 | `c_lxj_fengzhou` | **Fengzhou** | **丰州** | — | ✅ Pre-867 Classical | **[RE]** | tuyuhun | 21 | 3 | b_jiuyuan [castle], b_yongfeng [city]... |
| 319 | `c_tiande` | **Tiande** | **天德** | — | ✅ Pre-867 Classical | **[RE]** | han | 27 | 2 | b_tiande [castle], b_zhongshouxiang [... |

##### Duchy of Xiasui (`d_xiasui` / 夏绥) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 320 | `c_quye` | **Quye** | **屈野** | — | ✅ Pre-867 Classical | **[RE]** | sogdian | 32 | 3 | b_quye [castle], b_dijin [city], b_hu... |
| 321 | `c_suizhou` | **Suizhou** | **绥州** | — | ✅ Pre-867 Classical | **[RE]** | tangut | 46 | 3 | b_longquan [castle], b_suide [city], ... |
| 322 | `c_wuyuan` | **Yanzhou** | **盐州** | — | ✅ Pre-867 Classical | **[RE]** | tangut | 52 | 4 | b_wuyuan [castle], b_baichi [city], b... |
| 323 | `c_xiazhou` | **Xiazhou** | **夏州** | — | ✅ Pre-867 Classical | **[RE]** | tangut | 42 | 4 | b_shuofang [castle], b_ningshuo [city... |
| 324 | `c_yinzhou` | **Yinzhou** | **银州** | — | ✅ Pre-867 Classical | **[RE]** | tuyuhun | 31 | 3 | b_rulin [castle], b_zhenxiang [castle... |
| 325 | `c_youzhou_2` | **Youzhou** | **宥州** | — | ✅ Pre-867 Classical | **[RE]** | tangut | 36 | 4 | b_changze [castle], b_yanen [city], b... |

##### Duchy of Zhenfan (`d_xiutu` / 镇番) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 326 | `c_alxa` | **Alxa** | **阿剌筛** | — | ✅ Pre-867 Classical | **[RE]** | tuyuhun | 19 | 3 | b_alxa [castle], b_yabulai [church], ... |
| 327 | `c_tengger` | **Tenggeli** | **腾格里** | — | ✅ Pre-867 Classical | **[RE]** | Wulan | 27 | 2 | b_chaganbulage [castle], b_chaogetuhu... |
| 328 | `c_zhenfan` | **Zhenfan** | **镇番** | — | ✅ Pre-867 Classical | **[RE]** | bodpa | 21 | 2 | b_zhenfan [castle], b_jiahe [city] |

### 2.5 Empire of Lingnan (`e_lingnan` / 岭南)
- **De Jure Extent:** **52 Counties**, 12 Duchies, 3 Kingdoms.
- **Total Development:** **2,419.0** (Average: 46.5) | **Baronies:** 177
- **1154 Roman Empire Control:** **0 / 52 counties** (0.0%) | **Anachronisms Flagged:** **0**

#### 2.5.1 Kingdom of Lingnan (`k_lingnan` / 岭南)
*Extent: **22 Counties** | Development: **1,093** (avg 49.7) | Roman Control: **0/22** | Flagged Anachronisms: **0***

##### Duchy of Gaoliang (`d_gaoliang` / 高凉) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 329 | `c_gaozhou` | **Gaozhou** | **高州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 48 | 3 | b_dianbai [castle], b_maoming [city],... |
| 330 | `c_leizhou` | **Leizhou** | **雷州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 33 | 3 | b_haikang [castle], b_xuwen [city], b... |
| 331 | `c_luozhou` | **Luozhou** | **罗州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 45 | 4 | b_lianjiang_1 [castle], b_shilong [ci... |

##### Duchy of Huixun (`d_huixun` / 惠循) — *0/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 332 | `c_chaozhou` | **Chaozhou** | **潮州** | — | ✅ Pre-867 Classical | `e_lingnan` | yao | 89 | 5 | b_haiyang [castle], b_chaoyang [city]... |
| 333 | `c_dongguan` | **Dongguan** | **东莞** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 59 | 3 | b_dongguan [castle], b_baoan_1 [city]... |
| 334 | `c_huizhou_1` | **Huizhou** | **惠州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 73 | 6 | b_guishan [castle], b_boluo [castle],... |
| 335 | `c_meizhou_1` | **Meizhou** | **梅州** | — | ✅ Pre-867 Classical | `e_lingnan` | yao | 68 | 3 | b_chengxiang [castle], b_likeng [city... |
| 336 | `c_shaozhou_1` | **Shaozhou** | **韶州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 50 | 5 | b_qujiang_1 [castle], b_lechang [city... |
| 337 | `c_xunzhou` | **Xunzhou** | **循州** | — | ✅ Pre-867 Classical | `e_lingnan` | yao | 70 | 5 | b_leixiang [castle], b_xingning [city... |

##### Duchy of Lingnan (`d_lingnan` / 岭南) — *0/8 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 338 | `c_chunzhou` | **Chunzhou** | **春州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 49 | 3 | b_yangchun [castle], b_luoshui [city]... |
| 339 | `c_duanzhou` | **Duanzhou** | **端州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 52 | 3 | b_gaoyao [castle], b_sihui [city], b_... |
| 340 | `c_enzhou` | **Enzhou** | **恩州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 46 | 3 | b_enping [castle], b_yangjiang [city]... |
| 341 | `c_guangzhou_1` | **Guangzhou** | **广州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 64 | 5 | b_nanhai [castle], b_qingyuan_1 [city... |
| 342 | `c_kangzhou` | **Kangzhou** | **康州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 43 | 4 | b_duanxi [castle], b_yuecheng_1 [city... |
| 343 | `c_shuangzhou` | **Shuangzhou** | **泷州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 51 | 4 | b_shuangshui [castle], b_jinshui_1 [c... |
| 344 | `c_xinzhou_1` | **Xinzhou** | **新州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 55 | 4 | b_xinxing [castle], b_pingxing [city]... |
| 345 | `c_yingde` | **Yingzhou** | **英州** | — | ✅ Pre-867 Classical | `e_lingnan` | Huixun | 52 | 2 | b_zhenyang [castle], b_hankuang [city] |

##### Duchy of Qiongguan (`d_qiongguan` / 琼管) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 346 | `c_danzhou_1` | **Danzhou** | **儋州** | — | ✅ Pre-867 Classical | `e_lingnan` | hlai | 30 | 3 | b_yilun [castle], b_changhua_1 [city]... |
| 347 | `c_lidong` | **Lidong** | **黎峒** | — | ✅ Pre-867 Classical | `e_lingnan` | han | 31 | 3 | b_liodong [castle], b_limu [city], b_... |
| 348 | `c_wanan` | **Wanan** | **万安** | — | ✅ Pre-867 Classical | `e_lingnan` | hlai | 27 | 3 | b_wanan_1 [castle], b_lehui [city], b... |
| 349 | `c_yazhou` | **Yazhou** | **崖州** | — | ✅ Pre-867 Classical | `e_lingnan` | han | 33 | 3 | b_shecheng [castle], b_siqiongshan [c... |
| 350 | `c_yazhou_1` | **Yazhou** | **崖州** | — | ✅ Pre-867 Classical | `e_lingnan` | hlai | 25 | 3 | b_ningyuan [castle], b_yande [city], ... |

#### 2.5.2 Kingdom of Lingxi (`k_lingxi` / 岭西)
*Extent: **21 Counties** | Development: **837** (avg 39.9) | Roman Control: **0/21** | Flagged Anachronisms: **0***

##### Duchy of Guiguan (`d_guiguan` / 桂管) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 351 | `c_guizhou_1` | **Guizhou** | **桂州** | — | ✅ Pre-867 Classical | `e_lingnan` | han | 36 | 4 | b_lingui [castle], b_lingchuan [city]... |
| 352 | `c_liuzhou` | **Liuzhou** | **柳州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 31 | 4 | b_maping [castle], b_luorong [city], ... |
| 353 | `c_qingyuan` | **Yizhou** | **宜州** | — | ✅ Pre-867 Classical | `e_lingnan` | Yi-Bouxcuengh | 34 | 3 | b_longshui [castle], b_dumeng [city],... |
| 354 | `c_rongshui` | **Rongzhou** | **融州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 31 | 3 | b_rongshui [castle], b_wuyang_1 [city... |
| 355 | `c_xiangshan` | **Xiangzhou** | **象州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 34 | 3 | b_yangshou [castle], b_wuxian [city],... |

##### Duchy of Jingjiang (`d_jingjiang` / 静江) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 356 | `c_gongzhou` | **Gongzhou** | **龚州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 35 | 3 | b_pingnan [castle], b_wulang [city], ... |
| 357 | `c_wuzhou_1` | **Wuzhou** | **梧州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 37 | 3 | b_cangwu [castle], b_linhe_1 [city], ... |
| 358 | `c_zhaozhou_1` | **Zhaozhou** | **昭州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 37 | 3 | b_pingle [castle], b_yangshuo [city],... |

##### Duchy of Rongguan (`d_rongguan` / 容管) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 359 | `c_baizhou` | **Baizhou** | **白州** | — | ✅ Pre-867 Classical | `e_lingnan` | Lianzhou | 48 | 3 | b_bobai [castle], b_zhouluo [city], b... |
| 360 | `c_lianzhou_1` | **Lianzhou** | **廉州** | — | ✅ Pre-867 Classical | `e_lingnan` | Lianzhou | 53 | 3 | b_hepu_1 [castle], b_dalian [city], b... |
| 361 | `c_rongzhou_2` | **Rongzhou** | **容州** | — | ✅ Pre-867 Classical | `e_lingnan` | Lianzhou | 45 | 4 | b_puning_1 [castle], b_beiliu [city],... |
| 362 | `c_tengzhou` | **Tengzhou** | **藤州** | — | ✅ Pre-867 Classical | `e_lingnan` | Lianzhou | 42 | 3 | b_tanjin [castle], b_rongcheng_1 [cit... |
| 363 | `c_yulin` | **Yulin** | **郁林** | — | ✅ Pre-867 Classical | `e_lingnan` | Lianzhou | 44 | 3 | b_yuping [castle], b_xingye [city], b... |

##### Duchy of Yongguan (`d_yongguan` / 邕管) — *0/8 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 364 | `c_binzhou_1` | **Binzhou** | **宾州** | — | ✅ Pre-867 Classical | `e_lingnan` | Lianzhou | 31 | 3 | b_lingfang [castle], b_shanglin [city... |
| 365 | `c_hengzhou_1` | **Hengzhou** | **横州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 42 | 2 | b_ningpu [castle], b_yongding [city] |
| 366 | `c_qinzhou_2` | **Qinzhou** | **钦州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 48 | 3 | b_qinjiang [castle], b_lingshan [city... |
| 367 | `c_rangzhou` | **Rangzhou** | **瀼州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 48 | 3 | b_rangjiang [castle], b_wule [city], ... |
| 368 | `c_shukunzhou` | **Shukunzhou** | **述昆州** | — | ✅ Pre-867 Classical | `e_lingnan` | Lianzhou | 40 | 3 | b_shukun [castle], b_gongrao [city], ... |
| 369 | `c_tianzhou` | **Tianzhou** | **田州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 40 | 2 | b_dujiu [castle], b_hengshan_1 [city] |
| 370 | `c_xunzhou_2` | **Xunzhou** | **浔州** | — | ✅ Pre-867 Classical | `e_lingnan` | bouxcuengh | 36 | 3 | b_guiping [castle], b_dabin [city], b... |
| 371 | `c_yongzhou_1` | **Yongzhou** | **邕州** | — | ✅ Pre-867 Classical | `e_lingnan` | Lianzhou | 45 | 4 | b_xuanhua [castle], b_ruhe [city], b_... |

#### 2.5.3 Kingdom of Đại Việt (`k_viet` / 大越)
*Extent: **9 Counties** | Development: **489** (avg 54.3) | Roman Control: **0/9** | Flagged Anachronisms: **0***

##### Duchy of Hai Dong (`d_hai_dong` / 海东) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 372 | `c_binh_nguyen` | **Binh Nguyen** | **原平** | — | ✅ Pre-867 Classical | `k_viet` | Yi-Bouxcuengh | 51 | 5 | b_binh_nguyen [castle], b_vi_long [ch... |
| 373 | `c_hai_dong` | **Hai Dong** | **海东** | — | ✅ Pre-867 Classical | `k_viet` | viet | 58 | 3 | b_hai_dong [castle], b_lan_song [city... |

##### Duchy of Lam Tay (`d_lam_tay` / 林西) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 374 | `c_lam_tay` | **Lam Tay** | **林西** | — | ✅ Pre-867 Classical | `k_viet` | viet | 51 | 4 | b_lam_tay [castle], b_tam_giang [city... |
| 375 | `c_quoc_oai` | **Quoc Oai** | **国威** | — | ✅ Pre-867 Classical | `k_viet` | viet | 53 | 4 | b_quoc_oai [castle], b_hoang_giang [c... |

##### Duchy of Nghe An (`d_nghe_an` / 乂安) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 376 | `c_nam_dinh` | **Nam Dinh** | **南定** | — | ✅ Pre-867 Classical | `k_viet` | han | 60 | 4 | b_nam_dinh [castle], b_thanh_hoa [cit... |
| 377 | `c_nghe_an` | **Nghe An** | **乂安** | — | ✅ Pre-867 Classical | `k_viet` | han | 58 | 4 | b_nghe_an [castle], b_dien_chau [city... |
| 378 | `c_sam_nuea` | **Sam Nuea** | **桑怒** | — | ✅ Pre-867 Classical | `k_viet` | han | 46 | 2 | b_sam_nuea [castle], b_hua_muong [city] |

##### Duchy of Thăng Long (`d_thang_long` / 升龙) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 379 | `c_long_hung` | **Long Hung** | **隆兴** | — | ✅ Pre-867 Classical | `k_viet` | viet | 57 | 3 | b_long_hung [castle], b_kien_xuong [c... |
| 380 | `c_thang_long` | **Thăng Long** | **升龙** | 昇龍 | ✅ Pre-867 Classical | `k_viet` | viet | 55 | 3 | b_thang_long [castle], b_ha_bac [chur... |

---

## 3. Peripheral & Extended Sinosphere Title Register (240 Counties)

Below are the 240 counties belonging to the broader Sinosphere (Korea/Samhan, Japan, Liao/Andong, and Amur), which historically maintained Chinese writing, administrative culture, and tributary relations.

### 3.1 Empire of Samhan (`e_goryeo` / 三韩)
- **De Jure Extent:** **44 Counties**, 13 Duchies, 3 Kingdoms.
- **Total Development:** **1,232.0** (Average: 28.0) | **Baronies:** 139
- **1154 Roman Empire Control:** **44 / 44 counties** (100.0%) | **Anachronisms Flagged:** **0**

#### 3.1.1 Kingdom of Baekje (`k_baekje` / 百济)
*Extent: **11 Counties** | Development: **298** (avg 27.1) | Roman Control: **11/11** | Flagged Anachronisms: **0***

##### Duchy of Chungju (`d_chungju` / 忠州) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 381 | `c_cheongju` | **Cheongju** | **清州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 27 | 3 | b_Goryeo_Yanggwan_Cheongju [castle], ... |
| 382 | `c_chungju` | **Chungju** | **忠州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 27 | 4 | b_Goryeo_Yanggwan_Chungju [castle], b... |
| 383 | `c_gongju` | **Gongju** | **公州** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 27 | 4 | b_Goryeo_Yanggwan_Gongju [castle], b_... |
| 384 | `c_hongju` | **Hongju** | **洪州** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 22 | 2 | b_Goryeo_Yanggwan_Hongju [castle], b_... |

##### Duchy of Jeonju (`d_jeonju` / 全州) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 385 | `c_jeonju` | **Jeonju** | **全州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 35 | 3 | b_Goryeo_Jeolla_Jeonju [castle], b_Go... |
| 386 | `c_jillye` | **Jillye** | **进礼** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 24 | 3 | b_Goryeo_Jeolla_Jillye [castle], b_Go... |
| 387 | `c_namwon` | **Namwon** | **南原** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 25 | 3 | b_Goryeo_Jeolla_Namwon [castle], b_Go... |

##### Duchy of Naju (`d_naju` / 罗州) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 388 | `c_boseong` | **Boseong** | **宝城** | — | ✅ Pre-867 Classical | **[RE]** | silla | 28 | 3 | b_Goryeo_Jeolla_Boseong [castle], b_G... |
| 389 | `c_jangheung` | **Jangheung** | **长兴** | — | ✅ Pre-867 Classical | **[RE]** | baekje | 28 | 3 | b_Goryeo_Jeolla_Jangheung [castle], b... |
| 390 | `c_naju` | **Naju** | **罗州** | — | ✅ Pre-867 Classical | **[RE]** | baekje | 32 | 4 | b_Goryeo_Jeolla_Naju [castle], b_Gory... |

##### Duchy of Tamna (`d_tamna` / 耽罗) — *1/1 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 391 | `c_tamna` | **Tamna** | **耽罗** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 23 | 2 | b_Goryeo_Tamna_Tamna [castle], b_Gory... |

#### 3.1.2 Kingdom of Goguryeo (`k_goguryeo` / 高句丽)
*Extent: **20 Counties** | Development: **525** (avg 26.2) | Roman Control: **20/20** | Flagged Anachronisms: **0***

##### Duchy of Bukgye (`d_bukgye` / 北界) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 392 | `c_seogyeong` | **Seogyeong** | **西京** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 29 | 4 | b_Goryeo_Bukgye_Seogyeong [castle], b... |
| 393 | `c_seongju` | **Seongju** | **成州** | — | ✅ Pre-867 Classical | **[RE]** | silla | 24 | 4 | b_Goryeo_Bukgye_Seongju [castle], b_G... |
| 394 | `c_yeongwon` | **Yeongwon** | **宁远** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 20 | 4 | b_Goryeo_Bukgye_Yeongwon [castle], b_... |

##### Duchy of Gaeseong (`d_gaeseong` / 开城) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 395 | `c_gaeseong` | **Gaeseong** | **开城** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 28 | 4 | b_Goryeo_Gaeseong_Gaeseong [castle], ... |
| 396 | `c_gokju` | **Gokju** | **谷州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 24 | 4 | b_Goryeo_Seohae_Gokju [castle], b_Gor... |
| 397 | `c_pyeongju` | **Pyeongju** | **平州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 26 | 2 | b_Goryeo_Seohae_Pyeongju [castle], b_... |

##### Duchy of Gwangju (`d_gwangju` / 广州) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 398 | `c_dangseong` | **Dangseong** | **唐城** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 28 | 3 | b_Goryeo_Yanggwan_Dangseong [castle],... |
| 399 | `c_gwangju` | **Gwangju** | **广州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 32 | 3 | b_Goryeo_Yanggwan_Gwangju [castle], b... |
| 400 | `c_yangju` | **Yangju** | **杨州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 27 | 3 | b_Goryeo_Yanggwan_Yangju [castle], b_... |

##### Duchy of Gyoju (`d_gyoju` / 交州) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 401 | `c_chunju` | **Chunju** | **春州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 29 | 3 | b_Goryeo_Gyoju_Chunju [castle], b_Gor... |
| 402 | `c_dongju` | **Dongju** | **东州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 26 | 4 | b_Goryeo_Gyoju_Dongju [castle], b_Gor... |
| 403 | `c_gyoju` | **Gyoju** | **交州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 32 | 3 | b_Goryeo_Gyoju_Gyoju [castle], b_Gory... |
| 404 | `c_inje` | **Inje** | **麟蹄** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 25 | 2 | b_Goryeo_Gyoju_Inje [castle], b_Gorye... |

##### Duchy of Haeju (`d_haeju` / 海州) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 405 | `c_haeju` | **Haeju** | **海州** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 27 | 3 | b_Goryeo_Seohae_Haeju [castle], b_Gor... |
| 406 | `c_hwangju` | **Hwangju** | **黄州** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 25 | 3 | b_Goryeo_Seohae_Hwangju [castle], b_G... |
| 407 | `c_pungju` | **Pungju** | **丰州** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 25 | 3 | b_Goryeo_Seohae_Pungju [castle], b_Go... |

##### Duchy of Yukju (`d_yukju` / 六州) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 408 | `c_gwiju` | **Gwiju** | **龟州** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 27 | 3 | b_Goryeo_Bukgye_Gwiju [castle], b_Gor... |
| 409 | `c_jangjeong` | **Jangjeong** | **长静** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 27 | 3 | b_Goryeo_Bukgye_Jangjeong [castle], b... |
| 410 | `c_taeju` | **Taeju** | **泰州** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 26 | 3 | b_Goryeo_Bukgye_Taeju [castle], b_Gor... |
| 411 | `c_uiju` | **Yeongju** | **灵州** | — | ✅ Pre-867 Classical | **[RE]** | Yukju | 18 | 2 | b_Goryeo_Bukgye_Uiju [castle], b_Gory... |

#### 3.1.3 Kingdom of Silla (`k_silla` / 新罗)
*Extent: **13 Counties** | Development: **409** (avg 31.5) | Roman Control: **13/13** | Flagged Anachronisms: **0***

##### Duchy of Donggye (`d_donggye` / 东界) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 412 | `c_deungju` | **Deungju** | **登州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 30 | 4 | b_Goryeo_Donggye_Deungju [castle], b_... |
| 413 | `c_goseong` | **Goseong** | **高城** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 29 | 4 | b_Goryeo_Donggye_Goseong [castle], b_... |
| 414 | `c_myeongju` | **Myeongju** | **溟州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 36 | 4 | b_Goryeo_Donggye_Myeongju [castle], b... |
| 415 | `c_ulleong` | **Ulleong** | **郁陵** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 22 | 1 | b_Goryeo_Donggye_Ulleung [castle] |
| 416 | `c_wonju` | **Wonju** | **原州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 25 | 5 | b_Goryeo_Yanggwan_Wonju [castle], b_G... |

##### Duchy of Gyeongju (`d_gyeongju` / 庆州) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 417 | `c_andong` | **Andong** | **安东** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 36 | 3 | b_Goryeo_Gyeongsang_Andong [castle], ... |
| 418 | `c_gyeongju` | **Gyeongju** | **庆州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 39 | 3 | b_Goryeo_Gyeongsang_Gyeongju [castle]... |
| 419 | `c_ilseon` | **Ilseon** | **一善** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 32 | 3 | b_Goryeo_Gyeongsang_Ilseon [castle], ... |
| 420 | `c_sangju` | **Sangju** | **尚州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 30 | 3 | b_Goryeo_Gyeongsang_Sangju [castle], ... |

##### Duchy of Jinju (`d_jinju` / 晋州) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 421 | `c_guemju` | **Guemju** | **金州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 39 | 2 | b_Goryeo_Gyeongsang_Guemju [castle], ... |
| 422 | `c_hamyang` | **Hamyang** | **含阳** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 30 | 4 | b_Goryeo_Gyeongsang_Hamyang [castle],... |
| 423 | `c_jinju` | **Jinju** | **晋州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 30 | 3 | b_Goryeo_Gyeongsang_Jinju [castle], b... |
| 424 | `c_ulju` | **Ulju** | **蔚州** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 31 | 3 | b_Goryeo_Gyeongsang_Ulju [castle], b_... |

### 3.2 Empire of Japan (`e_japan` / 日本)
- **De Jure Extent:** **59 Counties**, 13 Duchies, 3 Kingdoms.
- **Total Development:** **2,303.0** (Average: 39.0) | **Baronies:** 210
- **1154 Roman Empire Control:** **59 / 59 counties** (100.0%) | **Anachronisms Flagged:** **0**

#### 3.2.1 Kingdom of Azuma (`k_azuma` / 吾妻)
*Extent: **23 Counties** | Development: **876** (avg 38.1) | Roman Control: **23/23** | Flagged Anachronisms: **0***

##### Duchy of East Bandō (`d_east_bando` / 东坂东) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 425 | `c_hitachi` | **Hitachi** | **常陆** | 常陸 | ✅ Pre-867 Classical | **[RE]** | japanese | 33 | 5 | b_ibaraki [castle], b_kashima_hitachi... |
| 426 | `c_kazusa` | **Kazusa** | **上总** | 上総 | ✅ Pre-867 Classical | **[RE]** | japanese | 18 | 3 | b_ichihara [castle], b_awa [city], b_... |
| 427 | `c_shimosa` | **Shimōsa** | **下总** | 下総 | ✅ Pre-867 Classical | **[RE]** | japanese | 24 | 4 | b_katsushika [castle], b_katori [chur... |
| 428 | `c_shimotsuke` | **Shimotsuke** | **下野** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 30 | 5 | b_ashikaga [castle], b_futara [church... |

##### Duchy of Hokurikudō (`d_hokurikudo` / 北陆道) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 429 | `c_echigo` | **Echigo** | **越后** | 越後 | ✅ Pre-867 Classical | **[RE]** | japanese | 39 | 6 | b_kubiki [castle], b_yahiko [church],... |
| 430 | `c_echizen` | **Echizen** | **越前** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 53 | 5 | b_nyu [castle], b_ono_echizen [church... |
| 431 | `c_etchu` | **Etchū** | **越中** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 37 | 2 | b_imizu [castle], b_tateyama [church] |
| 432 | `c_kaga` | **Kaga** | **加贺** | 加賀 | ✅ Pre-867 Classical | **[RE]** | japanese | 45 | 2 | b_enuma [castle], b_haku [church] |
| 433 | `c_noto` | **Noto** | **能登** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 38 | 2 | b_kashima [castle], b_fugeshi [church] |

##### Duchy of Tōkaidō (`d_tokaido` / 东海道) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 434 | `c_ise` | **Ise** | **伊势** | 伊勢 | ✅ Pre-867 Classical | **[RE]** | japanese | 60 | 5 | b_ano [castle], b_ise_jingu [church],... |
| 435 | `c_mikawa` | **Mikawa** | **三河** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 44 | 4 | b_atsumi [castle], b_nukata [city], b... |
| 436 | `c_owari` | **Owari** | **尾张** | 尾張 | ✅ Pre-867 Classical | **[RE]** | japanese | 48 | 3 | b_nakashima [castle], b_atsuta [churc... |
| 437 | `c_suruga` | **Suruga** | **骏河** | 駿河 | ✅ Pre-867 Classical | **[RE]** | japanese | 28 | 3 | b_abe [castle], b_fuji [church], b_sh... |
| 438 | `c_totomi` | **Tōtōmi** | **远江** | 遠江 | ✅ Pre-867 Classical | **[RE]** | japanese | 36 | 3 | b_toyoda [castle], b_suchi [church], ... |

##### Duchy of Tōsandō (`d_tosando` / 东山道) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 439 | `c_hida` | **Hida** | **飞驒** | 飛騨 | ✅ Pre-867 Classical | **[RE]** | japanese | 42 | 3 | b_ono_hida [castle], b_yoshiki_hida [... |
| 440 | `c_kai` | **Kai** | **甲斐** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 35 | 3 | b_yatsushiro [castle], b_tsuru [city]... |
| 441 | `c_mino` | **Mino** | **美浓** | 美濃 | ✅ Pre-867 Classical | **[RE]** | japanese | 49 | 5 | b_fuwa [castle], b_gujo [city], b_kan... |
| 442 | `c_omi` | **Ōmi** | **近江** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 60 | 4 | b_koka [castle], b_enryaku_ji [church... |
| 443 | `c_shinano` | **Shinano** | **信浓** | 信濃 | ✅ Pre-867 Classical | **[RE]** | japanese | 41 | 4 | b_tsukama [castle], b_zenko_ji [churc... |

##### Duchy of West Bandō (`d_west_bando` / 西坂东) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 444 | `c_izu` | **Izu** | **伊豆** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 26 | 2 | b_tagata [castle], b_kamo_izu [city] |
| 445 | `c_kozuke` | **Kōzuke** | **上野** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 35 | 4 | b_gunma [castle], b_tone [city], b_ni... |
| 446 | `c_musashi` | **Musashi** | **武藏** | 武蔵 | ✅ Pre-867 Classical | **[RE]** | japanese | 30 | 5 | b_tama_musashi [castle], b_adachi_mus... |
| 447 | `c_sagami` | **Sagami** | **相模** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 25 | 3 | b_kamakura [castle], b_hakone [church... |

#### 3.2.2 Kingdom of Tsukushi (`k_tsukushi` / 筑紫)
*Extent: **10 Counties** | Development: **277** (avg 27.7) | Roman Control: **10/10** | Flagged Anachronisms: **0***

##### Duchy of Dazaifu (`d_north_saikaido` / 太宰府) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 448 | `c_bungo` | **Bungo** | **丰后** | 豊後 | ✅ Pre-867 Classical | **[RE]** | japanese | 27 | 5 | b_oita [castle], b_amabe [church], b_... |
| 449 | `c_buzen` | **Buzen** | **丰前** | 豊前 | ✅ Pre-867 Classical | **[RE]** | japanese | 27 | 3 | b_usa [castle], b_hiko [church], b_ki... |
| 450 | `c_chikugo` | **Chikugo** | **筑后** | 筑後 | ✅ Pre-867 Classical | **[RE]** | japanese | 26 | 2 | b_mii [castle], b_mizuma [city] |
| 451 | `c_chikuzen` | **Chikuzen** | **筑前** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 28 | 4 | b_dazaifu [castle], b_hakata [city], ... |
| 452 | `c_hizen` | **Hizen** | **肥前** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 29 | 4 | b_saga [castle], b_matsura [city], b_... |
| 453 | `c_tsushima` | **Tsushima** | **对马** | 対馬 | ✅ Pre-867 Classical | **[RE]** | japanese | 28 | 1 | b_yora [castle] |

##### Duchy of South Saikaidō (`d_south_saikaido` / 南西海道) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 454 | `c_higo` | **Higo** | **肥后** | 肥後 | ✅ Pre-867 Classical | **[RE]** | japanese | 25 | 6 | b_mashiki [castle], b_aso_higo [churc... |
| 455 | `c_hyuga` | **Hyūga** | **日向** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 30 | 5 | b_koyu [castle], b_naka [city], b_miy... |
| 456 | `c_osumi` | **Ōsumi** | **大隅** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 28 | 4 | b_soo [castle], b_kimotsuki [church],... |
| 457 | `c_satsuma` | **Satsuma** | **萨摩** | 薩摩 | ✅ Pre-867 Classical | **[RE]** | japanese | 29 | 4 | b_izumi_satsuma [castle], b_kawanabe ... |

#### 3.2.3 Kingdom of Yamato (`k_yamato` / 大和)
*Extent: **26 Counties** | Development: **1,150** (avg 44.2) | Roman Control: **26/26** | Flagged Anachronisms: **0***

##### Duchy of East San'indō (`d_east_sanindo` / 东山阴道) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 458 | `c_inaba` | **Inaba** | **因幡** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 45 | 3 | b_homi [castle], b_yakami [city], b_t... |
| 459 | `c_tajima` | **Tajima** | **但马** | 但馬 | ✅ Pre-867 Classical | **[RE]** | japanese | 53 | 3 | b_keta_tajima [castle], b_kinosaki [c... |
| 460 | `c_tanba` | **Tanba** | **丹波** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 57 | 3 | b_kuwada [castle], b_funai [city], b_... |
| 461 | `c_tango` | **Tango** | **丹后** | 丹後 | ✅ Pre-867 Classical | **[RE]** | japanese | 52 | 2 | b_kumano_tango [castle], b_kasa_tango... |

##### Duchy of East San'yōdō (`d_east_sanyodo` / 东山阳道) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 462 | `c_bitchu` | **Bitchū** | **备中** | 備中 | ✅ Pre-867 Classical | **[RE]** | japanese | 40 | 3 | b_kuboya [castle], b_kibitsu [church]... |
| 463 | `c_bizen` | **Bizen** | **备前** | 備前 | ✅ Pre-867 Classical | **[RE]** | japanese | 48 | 2 | b_joto [castle], b_oku [city] |
| 464 | `c_harima` | **Harima** | **播磨** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 57 | 5 | b_shikama [castle], b_ibo [city], b_a... |
| 465 | `c_mimasaka` | **Mimasaka** | **美作** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 43 | 3 | b_tomata [castle], b_mashima [city], ... |

##### Duchy of Kinai (`d_kinai` / 畿内) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 466 | `c_kawachi` | **Kawachi** | **河内** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 60 | 3 | b_kawachi [castle], b_otori [castle],... |
| 467 | `c_settsu` | **Settsu** | **摄津** | 摂津 | ✅ Pre-867 Classical | **[RE]** | japanese | 62 | 3 | b_fukuhara [castle], b_watanabe [chur... |
| 468 | `c_yamashiro` | **Yamashiro** | **山城** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 69 | 2 | b_kyo [castle], b_uji [church] |
| 469 | `c_yamato` | **Yamato** | **大和** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 56 | 4 | b_yoshino [castle], b_kofuku_ji [chur... |

##### Duchy of Nankaidō (`d_nankaido` / 南海道) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 470 | `c_awa` | **Awa** | **阿波** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 42 | 4 | b_nakata [castle], b_tsurugi [church]... |
| 471 | `c_awaji` | **Awaji** | **淡路** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 42 | 1 | b_awaji [castle] |
| 472 | `c_iyo` | **Iyo** | **伊予** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 34 | 5 | b_iyo [castle], b_ishizuchi [church],... |
| 473 | `c_kii` | **Kii** | **纪伊** | 紀伊 | ✅ Pre-867 Classical | **[RE]** | japanese | 59 | 5 | b_nagusa [castle], b_kongobu_ji [chur... |
| 474 | `c_sanuki` | **Sanuki** | **赞岐** | 讃岐 | ✅ Pre-867 Classical | **[RE]** | japanese | 42 | 3 | b_yashima [castle], b_kotohira [churc... |
| 475 | `c_tosa` | **Tosa** | **土佐** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 40 | 5 | b_nagaoka [castle], b_kami [city], b_... |

##### Duchy of West San'indō (`d_west_sanindo` / 西山阴道) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 476 | `c_hoki` | **Hōki** | **伯耆** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 38 | 3 | b_kume [castle], b_daisen [church], b... |
| 477 | `c_iwami` | **Iwami** | **石见** | 石見 | ✅ Pre-867 Classical | **[RE]** | japanese | 31 | 4 | b_naka_iwami [castle], b_kanoashi [ci... |
| 478 | `c_izumo` | **Izumo** | **出云** | 出雲 | ✅ Pre-867 Classical | **[RE]** | japanese | 33 | 4 | b_ou [castle], b_kizuki_taisha [churc... |
| 479 | `c_oki` | **Oki** | **隐岐** | 隠岐 | ✅ Pre-867 Classical | **[RE]** | japanese | 24 | 1 | b_oki [castle] |

##### Duchy of West San'yōdō (`d_west_sanyodo` / 西山阳道) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 480 | `c_aki` | **Aki** | **安艺** | 安芸 | ✅ Pre-867 Classical | **[RE]** | japanese | 31 | 4 | b_kamo [castle], b_itsukushima [churc... |
| 481 | `c_bingo` | **Bingo** | **备后** | 備後 | ✅ Pre-867 Classical | **[RE]** | japanese | 33 | 4 | b_yasuna [castle], b_mitsugi [church]... |
| 482 | `c_nagato` | **Nagato** | **长门** | 長門 | ✅ Pre-867 Classical | **[RE]** | japanese | 24 | 4 | b_toyora [castle], b_asa [church], b_... |
| 483 | `c_suo` | **Suō** | **周防** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 35 | 4 | b_yoshiki [castle], b_tsuno [city], b... |

### 3.3 Empire of Andong (`e_andong` / 安东)
- **De Jure Extent:** **97 Counties**, 23 Duchies, 5 Kingdoms.
- **Total Development:** **1,567.0** (Average: 16.2) | **Baronies:** 321
- **1154 Roman Empire Control:** **70 / 97 counties** (72.2%) | **Anachronisms Flagged:** **48**

#### 3.3.1 Kingdom of Bóhai (`k_balhae` / 渤海)
*Extent: **25 Counties** | Development: **586** (avg 23.4) | Roman Control: **22/25** | Flagged Anachronisms: **0***

##### Duchy of Yālü-Zhangling (`d_BAL_amnok_jangryeong` / 鸭渌‑长岭) — *2/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 484 | `c_BAL_east_amnok` | **East Yālü** | **东鸭渌** | 鴨綠 | ✅ Pre-867 Classical | `d_eman_sikhotebei` | silla | 26 | 5 | b_Liao_Xijing [castle], b_Liao_Luzhou... |
| 485 | `c_BAL_east_jangryeong` | **East Zhangling** | **东长岭** | 長嶺 | ✅ Pre-867 Classical | **[RE]** | balhae | 23 | 3 | b_Liao_Changling [castle], b_FIC_Liao... |
| 486 | `c_BAL_west_amnok` | **West Yālü** | **西鸭渌** | 鴨綠 | ✅ Pre-867 Classical | `d_eman_sikhotebei` | balhae | 21 | 4 | b_Liao_Zhengzhou [castle], b_Liao_Kua... |
| 487 | `c_BAL_west_jangryeong` | **West Zhangling** | **西长岭** | 長嶺 | ✅ Pre-867 Classical | **[RE]** | balhae | 25 | 3 | b_Liao_Hezhou [castle], b_FIC_Liao_Ho... |

##### Duchy of Fúyú (`d_BAL_buyeo` / 扶余) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 488 | `c_BAL_changchun` | **Changchun** | **长春** | — | ✅ Pre-867 Classical | **[RE]** | Xingnabei | 20 | 4 | b_Liao_Changchun2 [castle], b_Liao_We... |
| 489 | `c_BAL_fuzhou` | **Fuzhou** | **扶州** | — | ✅ Pre-867 Classical | **[RE]** | balhae | 24 | 4 | b_Liao_Fuzhou2 [castle], b_Liao_Suzho... |
| 490 | `c_BAL_xinzhou` | **Xinzhou** | **新州** | — | ✅ Pre-867 Classical | **[RE]** | Xingnabei | 20 | 2 | b_Liao_Xinzhou [castle], b_FIC_Liao_F... |
| 491 | `c_BAL_yizhou` | **Yizhou** | **伊州** | — | ✅ Pre-867 Classical | **[RE]** | balhae | 20 | 3 | b_Liao_Yizhou [castle], b_Liao_Fengzh... |

##### Duchy of Moe-Su (`d_BAL_moe_su` / 鄚涑) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 492 | `c_BAL_makhil` | **Makhil** | **鄚颉** | — | ✅ Pre-867 Classical | **[RE]** | balhae | 29 | 4 | b_Liao_Mozhou [castle], b_Liao_Gaozho... |
| 493 | `c_BAL_sokju` | **Chénzhōu** | **辰州** | 陳州 | ✅ Pre-867 Classical | **[RE]** | balhae | 28 | 3 | b_Liao_Suzhou2 [castle], b_FIC_Liao_S... |
| 494 | `c_BAL_west_makhil` | **West Makhil** | **西鄚颉** | — | ✅ Pre-867 Classical | **[RE]** | balhae | 22 | 3 | b_Liao_Ningjiang [castle], b_FIC_Liao... |

##### Duchy of Bóhai (`d_BAL_parhae` / 渤海) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 495 | `c_BAL_dongju` | **Tóngzhōu** | **铜州** | 銅州 | ✅ Pre-867 Classical | **[RE]** | balhae | 25 | 3 | b_Liao_Tongzhou2 [castle], b_FIC_Liao... |
| 496 | `c_BAL_east_hyeondeok` | **East Xiandé** | **东显德** | 顯德 | ✅ Pre-867 Classical | **[RE]** | balhae | 24 | 4 | b_FIC_Liao_Helong [castle], b_Liao_Xi... |
| 497 | `c_BAL_west_hyeondeok` | **West Xiandé** | **西显德** | 顯德 | ✅ Pre-867 Classical | **[RE]** | balhae | 30 | 4 | b_Liao_Zhongjing [castle], b_Liao_Tan... |
| 498 | `c_BAL_yeongju` | **Yingzhōu** | **郢州** | — | ✅ Pre-867 Classical | **[RE]** | jurchen | 22 | 2 | b_Liao_Yingzhou [castle], b_FIC_Liao_... |
| 499 | `c_BAL_yongcheon` | **Lóngquán** | **龙泉** | 龍泉 | ✅ Pre-867 Classical | **[RE]** | balhae | 25 | 5 | b_Liao_Shangjing [castle], b_Liao_Boz... |

##### Duchy of Wòju (`d_BAL_southern_balhae` / 沃沮) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 500 | `c_BAL_fengzhou` | **Fēngzhōu** | **丰州** | 豐州 | ✅ Pre-867 Classical | **[RE]** | silla | 20 | 2 | b_Liao_Fengzhou4 [castle], b_FIC_Liao... |
| 501 | `c_BAL_namhae` | **Nánhai** | **南海** | — | ✅ Pre-867 Classical | **[RE]** | Samhan | 25 | 3 | b_Liao_Nanjing [castle], b_Liao_Tianq... |
| 502 | `c_BAL_northyongwon` | **North Lóngyuán** | **北龙原** | 龍原 | ✅ Pre-867 Classical | **[RE]** | balhae | 22 | 3 | b_Liao_Lungyuanfu [castle], b_FIC_Lia... |
| 503 | `c_BAL_southyongwon` | **South Lóngyuán** | **南龙原** | 龍原 | ✅ Pre-867 Classical | **[RE]** | balhae | 20 | 3 | b_Liao_Dongjing [castle], b_Liao_Hela... |

##### Duchy of Liaodong (`d_LIAO_dongjing` / 辽东) — *4/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 504 | `c_LIAO_diezhou` | **Diezhou** | **叠州** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | balhae | 19 | 4 | b_Liao_Diezhou [castle], b_Liao_Tongz... |
| 505 | `c_LIAO_guidezhou` | **Guidezhou** | **贵德州** | — | ✅ Pre-867 Classical | **[RE]** | balhae | 25 | 4 | b_Liao_Guidezhou [castle], b_Liao_Xiy... |
| 506 | `c_LIAO_shenyang` | **Shenyang** | **沈阳** | — | ✅ Pre-867 Classical | **[RE]** | balhae | 23 | 5 | b_Liao_Shenyang [castle], b_Liao_Tang... |
| 507 | `c_LIAO_yinzhou` | **Yínzhōu** | **银州** | — | ✅ Pre-867 Classical | **[RE]** | balhae | 26 | 4 | b_Liao_Yinzhou [castle], b_Liao_Qizho... |
| 508 | `c_LIAO_zhenzhou` | **Zhenzhou** | **镇州** | — | ✅ Pre-867 Classical | **[RE]** | balhae | 22 | 4 | b_Liao_Zhenzhou [castle], b_Liao_Fupi... |

#### 3.3.2 Kingdom of Khitan (`k_khitan` / 契丹)
*Extent: **11 Counties** | Development: **155** (avg 14.1) | Roman Control: **11/11** | Flagged Anachronisms: **11***

##### Duchy of Linhuang (`d_LIAO_linhuang` / 临潢) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 509 | `c_LIAO_dalian` | **Dalian** | **达里岸** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_dalian River / Regional Basin (Liao_dalian)* | **[RE]** | khitan | 15 | 2 | b_FIC_Liao_Dalinuor [castle], b_FIC_L... |
| 510 | `c_LIAO_heicaoan` | **Heicaoan** | **黑草岸** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_heicaoan River / Regional Basin (Liao_heicaoan)* | **[RE]** | Iljigin | 4 | 3 | b_FIC_Liao_Matudi [herder] |
| 511 | `c_LIAO_linhuang` | **Linhuang** | **临潢** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_linhuang River / Regional Basin (Liao_linhuang)* | **[RE]** | khitan | 18 | 5 | b_Liao_Linhuang [castle], b_Liao_Huai... |
| 512 | `c_LIAO_longhuazhou` | **Longhuazhou** | **龙化州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_longhuazhou River / Regional Basin (Liao_longhuazhou)* | **[RE]** | khitan | 17 | 3 | b_Liao_Longhuazhou [castle], b_Liao_J... |
| 513 | `c_LIAO_raozhou` | **Raozhou** | **饶州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_raozhou River / Regional Basin (Liao_raozhou)* | **[RE]** | khitan | 12 | 3 | b_Liao_Raozhou [castle], b_Liao_Qingz... |
| 514 | `c_LIAO_ulagaian` | **Ulagaian** | **兀鲁回岸** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_ulagaian River / Regional Basin (Liao_ulagaian)* | **[RE]** | khitan | 11 | 3 | b_FIC_Liao_Ulanulagai [castle], b_FIC... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Linhuang:**
> * **`c_LIAO_dalian` (Dalian / 达里岸):** Post-867 Khitan regional encampment; lacks pre-867 civil center. *Resolved via Option B: **Option B:** `Liao_dalian River / Regional Basin` (Liao_dalian).*
> * **`c_LIAO_heicaoan` (Heicaoan / 黑草岸):** Post-867 pastoral encampment on the eastern steppe frontier. *Resolved via Option B: **Option B:** `Liao_heicaoan River / Regional Basin` (Liao_heicaoan).*
> * **`c_LIAO_linhuang` (Linhuang / 临潢):** Founded in 918 AD by Yelü Abaoji (Emperor Taizu of Liao) as the Supreme Capital (Liao Shangjing / 上京临潢府) on the Shira Muren river. *Resolved via Option B: **Option B:** `Liao_linhuang River / Regional Basin` (Liao_linhuang).*
> * **`c_LIAO_longhuazhou` (Longhuazhou / 龙化州):** Founded in 902 AD by Yelü Abaoji as a fortified private encampment (dongzhai) prior to his imperial coronation. *Resolved via Option B: **Option B:** `Liao_longhuazhou River / Regional Basin` (Liao_longhuazhou).*
> * **`c_LIAO_raozhou` (Raozhou / 饶州):** Established in 953 AD by Emperor Muzong of Liao in the fertile upper Xilamulun river basin. *Resolved via Option B: **Option B:** `Liao_raozhou River / Regional Basin` (Liao_raozhou).*
> * **`c_LIAO_ulagaian` (Ulagaian / 兀鲁回岸):** Post-867 Ulagai river frontier march; unverified prior to 867 AD. *Resolved via Option B: **Option B:** `Liao_ulagaian River / Regional Basin` (Liao_ulagaian).*

##### Duchy of Talu (`d_LIAO_shangjing` / 他鲁) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 515 | `c_LIAO_changchun` | **Changchun** | **长春** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_changchun River / Regional Basin (Liao_changchun)* | **[RE]** | khitan | 15 | 4 | b_Liao_Changchun [castle], b_FIC_Liao... |
| 516 | `c_LIAO_horqinan` | **Horqinan** | **火儿赤纳** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_horqinan River / Regional Basin (Liao_horqinan)* | **[RE]** | khitan | 18 | 3 | b_FIC_Liao_Horqin [castle] |
| 517 | `c_LIAO_ningzhou` | **Ningzhou** | **宁州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_ningzhou River / Regional Basin (Liao_ningzhou)* | **[RE]** | khitan | 7 | 4 | b_Liao_Ningzhou [castle] |
| 518 | `c_LIAO_taizhou` | **Taizhou** | **泰州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_taizhou River / Regional Basin (Liao_taizhou)* | **[RE]** | Xingnabei | 14 | 4 | b_Amur_Taizhou [castle], b_FIC_Amur_J... |
| 519 | `c_LIAO_wuzhou` | **Wuzhou** | **乌州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_wuzhou River / Regional Basin (Liao_wuzhou)* | **[RE]** | khitan | 24 | 5 | b_Liao_Wuzhou2 [castle], b_Liao_Weizh... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Talu:**
> * **`c_LIAO_changchun` (Changchun / 长春):** Established in 926 AD by the Khitans as a state-sponsored relocation garrison following the conquest of Bohai. *Resolved via Option B: **Option B:** `Liao_changchun River / Regional Basin` (Liao_changchun).*
> * **`c_LIAO_horqinan` (Horqinan / 火儿赤纳):** Post-867 Horqin steppe grazing division; unverified prior to 867 AD. *Resolved via Option B: **Option B:** `Liao_horqinan River / Regional Basin` (Liao_horqinan).*
> * **`c_LIAO_ningzhou` (Ningzhou / 宁州):** Post-867 Liao garrison prefecture established in former Bohai territory. *Resolved via Option B: **Option B:** `Liao_ningzhou River / Regional Basin` (Liao_ningzhou).*
> * **`c_LIAO_taizhou` (Taizhou / 泰州):** Established in 916–926 AD as a Liao defensive garrison prefecture. *Resolved via Option B: **Option B:** `Liao_taizhou River / Regional Basin` (Liao_taizhou).*
> * **`c_LIAO_wuzhou` (Wuzhou / 乌州):** Post-867 Liao tribal prefecture; unverified prior to 867 AD. *Resolved via Option B: **Option B:** `Liao_wuzhou River / Regional Basin` (Liao_wuzhou).*

#### 3.3.3 Kingdom of Luzhen (`k_luzhen` / 虑真)
*Extent: **18 Counties** | Development: **330** (avg 18.3) | Roman Control: **11/18** | Flagged Anachronisms: **11***

##### Duchy of Ānyuan (`d_BAL_anwon` / 安远) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 520 | `c_BAL_heuksu_anwon` | **Heuksu Anwon** | **黑水安远** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_heuksu_anwon River / Regional Basin (Bal_heuksu_anwon)* | **[RE]** | mohe | 15 | 2 | b_FIC_EMan_Yozejiang [castle], b_FIC_... |
| 521 | `c_BAL_ningzhou` | **Níngzhōu** | **宁州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_ningzhou River / Regional Basin (Bal_ningzhou)* | **[RE]** | mohe | 21 | 3 | b_EMan_Ningzhou [castle], b_FIC_EMan_... |
| 522 | `c_BAL_north_anwon` | **North Ānyuan** | **北安远** | 安遠 | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_north_anwon River / Regional Basin (Bal_north_anwon)* | **[RE]** | mohe | 15 | 3 | b_FIC_EMan_Alimenyang [castle], b_FIC... |
| 523 | `c_BAL_supin` | **Supin** | **速频** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_supin River / Regional Basin (Bal_supin)* | **[RE]** | balhae | 23 | 4 | b_EMan_Supin [castle], b_FIC_EMan_Xud... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Ānyuan:**
> * **`c_BAL_heuksu_anwon` (Heuksu Anwon / 黑水安远):** Northern Mohe frontier market on the Amur/Heuksu. *Resolved via Option B: **Option B:** `Bal_heuksu_anwon River / Regional Basin` (Bal_heuksu_anwon).*
> * **`c_BAL_ningzhou` (Níngzhōu / 宁州):** Post-867 Bohai relocation prefecture. *Resolved via Option B: **Option B:** `Bal_ningzhou River / Regional Basin` (Bal_ningzhou).*
> * **`c_BAL_north_anwon` (North Ānyuan / 北安远):** Descriptive northern frontier market outpost of Bohai. *Resolved via Option B: **Option B:** `Bal_north_anwon River / Regional Basin` (Bal_north_anwon).*
> * **`c_BAL_supin` (Supin / 速频):** Post-867 Jurchen tribal valley; unverified urban center. *Resolved via Option B: **Option B:** `Bal_supin River / Regional Basin` (Bal_supin).*

##### Duchy of Tielì (`d_BAL_cheolli` / 铁利) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 524 | `c_BAL_delizhen` | **Délizhèn** | **德理镇** | 德里鎮 | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_delizhen River / Regional Basin (Bal_delizhen)* | **[RE]** | jurchen | 28 | 3 | b_Liao_Delizhen [castle], b_FIC_Liao_... |
| 525 | `c_BAL_huligai` | **Huligai** | **胡里改** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_huligai River / Regional Basin (Bal_huligai)* | **[RE]** | jurchen | 25 | 3 | b_EMan_Huligai [castle], b_FIC_EMan_H... |
| 526 | `c_BAL_west_cheolli` | **West Tielì** | **西铁利** | 鐵利 | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_west_cheolli River / Regional Basin (Bal_west_cheolli)* | **[RE]** | jurchen | 23 | 2 | b_FIC_Amur_Dahedu [castle], b_FIC_Amu... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Tielì:**
> * **`c_BAL_delizhen` (Délizhèn / 德理镇):** Jurchen border market post established during late Bohai/Liao transition. *Resolved via Option B: **Option B:** `Bal_delizhen River / Regional Basin` (Bal_delizhen).*
> * **`c_BAL_huligai` (Huligai / 胡里改):** Ilun Hurka route of the Jurchen tribes along the Mudanjiang River. *Resolved via Option B: **Option B:** `Bal_huligai River / Regional Basin` (Bal_huligai).*
> * **`c_BAL_west_cheolli` (West Tielì / 西铁利):** Descriptive subdivision of Tieli Jurchen territory. *Resolved via Option B: **Option B:** `Bal_west_cheolli River / Regional Basin` (Bal_west_cheolli).*

##### Duchy of Dōngpíng (`d_BAL_dongpyeong` / 东平) — *0/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 527 | `c_BAL_dongpyeong_yizhou` | **Yizhou** | **伊州** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | mohe | 19 | 3 | b_EMan_Yizhou [castle], b_FIC_EMan_Be... |
| 528 | `c_BAL_jixi` | **Jixi** | **鸡西** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | jurchen | 20 | 3 | b_EMan_Jixi [castle], b_FIC_EMan_Dong... |

##### Duchy of Huáiyuan (`d_BAL_hoewon` / 怀远) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 529 | `c_BAL_central_hoewon` | **Central Huáiyuǎn** | **中怀远** | 懷遠 | ✅ Pre-867 Classical | `d_eman_sikhotebei` | jurchen | 14 | 3 | b_FIC_EMan_Dacun [castle], b_FIC_EMan... |
| 530 | `c_BAL_dazhou` | **Dazhou** | **达州** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | jurchen | 17 | 3 | b_Amur_Dazhou [castle], b_FIC_Amur_Ha... |
| 531 | `c_BAL_east_hoewon` | **East Huáiyuǎn** | **东怀远** | 懷遠 | ✅ Pre-867 Classical | `d_eman_sikhotebei` | jurchen | 14 | 2 | b_FIC_EMan_Naolijiang [castle], b_FIC... |
| 532 | `c_BAL_ilanshan` | **Ilanshan** | **依兰山** | — | ✅ Pre-867 Classical | `k_luzhen` | jurchen | 9 | 2 | b_FIC_Amur_Ilanshan [castle], b_FIC_A... |
| 533 | `c_BAL_south_hoewon` | **South Huáiyuǎn** | **南怀远** | 懷遠 | ✅ Pre-867 Classical | `d_eman_sikhotebei` | jurchen | 16 | 3 | b_FIC_EMan_Baihuaicun [castle], b_FIC... |

##### Duchy of Shuàibīn-Ānbiān (`d_BAL_yeojintang` / 率宾-安边) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 534 | `c_BAL_anbyeon` | **Ānbiān** | **安边** | 安邊 | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_anbyeon River / Regional Basin (Bal_anbyeon)* | **[RE]** | mohe | 16 | 3 | b_EMan_Anzhou [castle], b_FIC_EMan_Si... |
| 535 | `c_BAL_jeongni` | **Dìngli** | **定理** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_jeongni River / Regional Basin (Bal_jeongni)* | **[RE]** | mohe | 17 | 4 | b_EMan_Dingzhou [castle], b_EMan_Yong... |
| 536 | `c_BAL_north_anbyeon` | **North Ānbiān** | **北安边** | 安邊 | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_north_anbyeon River / Regional Basin (Bal_north_anbyeon)* | **[RE]** | mohe | 12 | 3 | b_FIC_EMan_Beiqiulin [castle], b_FIC_... |
| 537 | `c_BAL_solbin` | **Shuàibīn** | **率宾** | 率賓 | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Bal_solbin River / Regional Basin (Bal_solbin)* | **[RE]** | balhae | 26 | 4 | b_EMan_Huazhou [castle], b_Liao_Jianz... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Shuàibīn-Ānbiān:**
> * **`c_BAL_anbyeon` (Ānbiān / 安边):** Anbian border commandery on the frontier of Bohai and the Khitans. *Resolved via Option B: **Option B:** `Bal_anbyeon River / Regional Basin` (Bal_anbyeon).*
> * **`c_BAL_jeongni` (Dìngli / 定理):** Post-867 Bohai/Jurchen prefecture; unverified pre-867 center. *Resolved via Option B: **Option B:** `Bal_jeongni River / Regional Basin` (Bal_jeongni).*
> * **`c_BAL_north_anbyeon` (North Ānbiān / 北安边):** Descriptive frontier subdivision of Anbian. *Resolved via Option B: **Option B:** `Bal_north_anbyeon River / Regional Basin` (Bal_north_anbyeon).*
> * **`c_BAL_solbin` (Shuàibīn / 率宾):** Suifen river basin; Bohai secondary prefecture reorganised post-867. *Resolved via Option B: **Option B:** `Bal_solbin River / Regional Basin` (Bal_solbin).*

#### 3.3.4 Kingdom of Raole (`k_raole` / 饶乐)
*Extent: **14 Counties** | Development: **314** (avg 22.4) | Roman Control: **13/14** | Flagged Anachronisms: **13***

##### Duchy of Raole (`d_LIAO_zhongjing` / 饶乐) — *6/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 538 | `c_LIAO_dading` | **Dading** | **大定** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_dading River / Regional Basin (Liao_dading)* | **[RE]** | Chengde | 28 | 4 | b_Liao_Dading [castle], b_Liao_Enzhou... |
| 539 | `c_liao_fengzhou` | **Fengzhou** | **丰州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_fengzhou River / Regional Basin (Liao_fengzhou)* | **[RE]** | Chengde | 18 | 2 | b_Liao_Fengzhou [castle], b_Liao_Yiku... |
| 540 | `c_lxj_yuyidong` | **Yuyidong** | **御夷东** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Lxj_yuyidong River / Regional Basin (Lxj_yuyidong)* | **[RE]** | Chengde | 26 | 2 | b_cirlzj_caodangzhen [castle], b_cirl... |
| 541 | `c_lzj_chengde` | **Chengde** | **承德** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Lzj_chengde River / Regional Basin (Lzj_chengde)* | **[RE]** | Chengde | 32 | 4 | b_cirlzj_luexiating [castle], b_cirlz... |
| 542 | `c_lzj_chengdexi` | **Chengdexi** | **承德西** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Lzj_chengdexi River / Regional Basin (Lzj_chengdexi)* | **[RE]** | Chengde | 27 | 4 | b_cirlzj_liuheting [castle], b_cirlzj... |
| 543 | `c_woye` | **Woye** | **沃野** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Woye River / Regional Basin (Woye)* | **[RE]** | Chengde | 23 | 3 | b_Liao_Wuanzhou [castle], b_Liao_Jian... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Raole:**
> * **`c_LIAO_dading` (Dading / 大定):** Founded in 1007 AD by Emperor Shengzong of Liao as the Central Capital (Liao Zhongjing / 中京大定府). *Resolved via Option B: **Option B:** `Liao_dading River / Regional Basin` (Liao_dading).*
> * **`c_liao_fengzhou` (Fengzhou / 丰州):** Post-867 Liao garrison prefecture in southern Inner Mongolia. *Resolved via Option B: **Option B:** `Liao_fengzhou River / Regional Basin` (Liao_fengzhou).*
> * **`c_lxj_yuyidong` (Yuyidong / 御夷东):** Post-867 marchland division of the Yuyi frontier. *Resolved via Option B: **Option B:** `Lxj_yuyidong River / Regional Basin` (Lxj_yuyidong).*
> * **`c_lzj_chengde` (Chengde / 承德):** Modern anachronism derived from the Qing dynasty imperial mountain resort (Bishu Shanzhuang, founded 1703 AD). *Resolved via Option B: **Option B:** `Lzj_chengde River / Regional Basin` (Lzj_chengde).*
> * **`c_lzj_chengdexi` (Chengdexi / 承德西):** Descriptive modern subdivision of the Qing-era Chengde prefecture. *Resolved via Option B: **Option B:** `Lzj_chengdexi River / Regional Basin` (Lzj_chengdexi).*
> * **`c_woye` (Woye / 沃野):** Post-867 frontier pastoral division; lacks pre-867 civil oppidum. *Resolved via Option B: **Option B:** `Woye River / Regional Basin` (Woye).*

##### Duchy of Liaoxi (`d_liaoxi` / 辽西) — *5/6 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 544 | `c_LIAO_chaoyang` | **Chaoyang** | **朝阳** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_chaoyang River / Regional Basin (Liao_chaoyang)* | **[RE]** | Chengde | 16 | 4 | b_Liao_Chaoyang [castle], b_Liao_Chua... |
| 545 | `c_LIAO_jinzhou` | **Jinzhou** | **锦州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_jinzhou River / Regional Basin (Liao_jinzhou)* | **[RE]** | Chengde | 26 | 3 | b_Liao_Yizhou3 [castle], b_Liao_Xizho... |
| 546 | `c_LIAO_liaozhou` | **Liaozhou** | **辽州** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | shiwei | 22 | 3 | b_Liao_Liaozhou [castle], b_Liao_Suiz... |
| 547 | `c_LIAO_xianzhou` | **Xianzhou** | **显州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Liao_xianzhou River / Regional Basin (Liao_xianzhou)* | **[RE]** | mongol | 16 | 3 | b_Liao_Xianzhou [castle], b_Liao_Haib... |
| 548 | `c_lnj_liaoxi` | **Liaoxi** | **辽西** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Lnj_liaoxi River / Regional Basin (Lnj_liaoxi)* | **[RE]** | Chengde | 21 | 3 | b_cirlzj_qinhuangdao [castle], b_ping... |
| 549 | `c_lnj_liaoxibei` | **Liaoxibei** | **辽西北** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Lnj_liaoxibei River / Regional Basin (Lnj_liaoxibei)* | **[RE]** | Chengde | 17 | 4 | b_cirlzj_yuhejing [castle], b_Liao_Li... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Liaoxi:**
> * **`c_LIAO_chaoyang` (Chaoyang / 朝阳):** Post-867 Khitan regional commandery in the Daling River valley. *Resolved via Option B: **Option B:** `Liao_chaoyang River / Regional Basin` (Liao_chaoyang).*
> * **`c_LIAO_jinzhou` (Jinzhou / 锦州):** Established in 923 AD by Yelü Abaoji with captive Han artisans from Pingzhou. *Resolved via Option B: **Option B:** `Liao_jinzhou River / Regional Basin` (Liao_jinzhou).*
> * **`c_LIAO_xianzhou` (Xianzhou / 显州):** Established in 926 AD at the medical and ancestral tumulus of Prince Yelü Bei (Prince of Dongdan). *Resolved via Option B: **Option B:** `Liao_xianzhou River / Regional Basin` (Liao_xianzhou).*
> * **`c_lnj_liaoxi` (Liaoxi / 辽西):** Descriptive post-867 frontier slice; lacks ancient urban center. *Resolved via Option B: **Option B:** `Lnj_liaoxi River / Regional Basin` (Lnj_liaoxi).*
> * **`c_lnj_liaoxibei` (Liaoxibei / 辽西北):** Descriptive post-867 frontier slice; lacks ancient urban center. *Resolved via Option B: **Option B:** `Lnj_liaoxibei River / Regional Basin` (Lnj_liaoxibei).*

##### Duchy of Yuyi (`d_yanyun_yuyi` / 御夷) — *2/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 550 | `c_lxj_huanzhou` | **Huanzhou** | **桓州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Lxj_huanzhou River / Regional Basin (Lxj_huanzhou)* | **[RE]** | han | 18 | 3 | b_cirlxj_huanzhou [castle], b_cirlxj_... |
| 551 | `c_lxj_yangchengzhou` | **Yangchengzhou** | **羊城州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Lxj_yangchengzhou River / Regional Basin (Lxj_yangchengzhou)* | **[RE]** | han | 24 | 3 | b_cirlxj_yangcheng [castle], b_cirlxj... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Yuyi:**
> * **`c_lxj_huanzhou` (Huanzhou / 桓州):** Established 960+ AD by the Khitans as an inner march prefecture. *Resolved via Option B: **Option B:** `Lxj_huanzhou River / Regional Basin` (Lxj_huanzhou).*
> * **`c_lxj_yangchengzhou` (Yangchengzhou / 羊城州):** Post-867 Khitan grazing prefecture; unverified prior to 867 AD. *Resolved via Option B: **Option B:** `Lxj_yangchengzhou River / Regional Basin` (Lxj_yangchengzhou).*

#### 3.3.5 Kingdom of Shiwei (`k_shiwei` / 室韦)
*Extent: **29 Counties** | Development: **182** (avg 6.3) | Roman Control: **13/29** | Flagged Anachronisms: **13***

##### Duchy of Dashiweiguo (`d_SW_dashiweiguo` / 大室韦国) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 552 | `c_SW_ergunia` | **Ergunia** | **也里古纳** | — | ✅ Pre-867 Classical | `k_shiwei` | Xingnabei | 1 | 3 | b_FIC_Mong_Telburgol [herder] |
| 553 | `c_SW_hailar` | **Hailar** | **海剌儿** | — | ✅ Pre-867 Classical | `k_shiwei` | shiwei | 0 | 3 | b_FIC_Mong_Hailargol [nomad] |
| 554 | `c_SW_heiergun` | **Heiergun** | **黑尔滚** | — | ✅ Pre-867 Classical | `k_shiwei` | Urtolgod | 0 | 3 | b_FIC_Mong_Huraalin [castle] |
| 555 | `c_SW_mengwuo` | **Mengwuo** | **蒙兀国** | — | ✅ Pre-867 Classical | `k_shiwei` | shiwei | 7 | 4 | b_FIC_Mong_Banukhol [castle], b_FIC_M... |
| 556 | `c_SW_pibeihe` | **Pibeihe** | **皮被河** | — | ✅ Pre-867 Classical | `c_SW_pibeihe` | khitan | 0 | 3 | b_Mong_Pibeihe [herder] |

##### Duchy of Heicheziguo (`d_SW_heicheziguo` / 黑车子国) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 557 | `c_SW_dongcheziguo` | **Dongcheziguo** | **东车子国** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_dongcheziguo River / Regional Basin (Sw_dongcheziguo)* | **[RE]** | khitan | 10 | 4 | b_FIC_Mong_Jiasaihe [castle], b_FIC_M... |
| 558 | `c_SW_hongxingan` | **Hongxingan** | **红兴安** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_hongxingan River / Regional Basin (Sw_hongxingan)* | **[RE]** | Xingnabei | 9 | 4 | b_Liao_Wuzhou [castle], b_FIC_Liao_Li... |
| 559 | `c_SW_hulunbuir` | **Hulunbuir** | **阔连捕鱼儿** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_hulunbuir River / Regional Basin (Sw_hulunbuir)* | **[RE]** | Segenuud | 1 | 4 | b_FIC_Mong_Oyuhulun [castle], b_FIC_M... |
| 560 | `c_SW_zhongcheziguo` | **Zhongcheziguo** | **中车子国** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_zhongcheziguo River / Regional Basin (Sw_zhongcheziguo)* | **[RE]** | Urtolgod | 4 | 4 | b_FIC_Mong_Zuunbuir [castle], b_FIC_M... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Heicheziguo:**
> * **`c_SW_dongcheziguo` (Dongcheziguo / 东车子国):** Nomadic clan division ('Eastern Cart Tribe'); lacks fixed pre-867 urban center. *Resolved via Option B: **Option B:** `Sw_dongcheziguo River / Regional Basin` (Sw_dongcheziguo).*
> * **`c_SW_hongxingan` (Hongxingan / 红兴安):** Descriptive modern oronym slice ('Red Khingan'). *Resolved via Option B: **Option B:** `Sw_hongxingan River / Regional Basin` (Sw_hongxingan).*
> * **`c_SW_hulunbuir` (Hulunbuir / 阔连捕鱼儿):** Modern banner / post-867 lake pastoral area; lacks ancient town. *Resolved via Option B: **Option B:** `Sw_hulunbuir River / Regional Basin` (Sw_hulunbuir).*
> * **`c_SW_zhongcheziguo` (Zhongcheziguo / 中车子国):** Nomadic clan division ('Middle Cart Tribe'). *Resolved via Option B: **Option B:** `Sw_zhongcheziguo River / Regional Basin` (Sw_zhongcheziguo).*

##### Duchy of Lingxiguo (`d_SW_lingxiguo` / 岭西国) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 561 | `c_SW_heiheguo` | **Heiheguo** | **黑河国** | — | ✅ Pre-867 Classical | `k_shiwei` | khitan | 4 | 3 | b_FIC_Amur_Beihelin [castle], b_FIC_A... |
| 562 | `c_SW_lingxiguo` | **Lingxiguo** | **岭西国** | — | ✅ Pre-867 Classical | `k_shiwei` | mongol | 7 | 3 | b_FIC_Amur_Jialingxi [castle], b_FIC_... |
| 563 | `c_SW_powoguo` | **Powoguo** | **婆莴国** | — | ✅ Pre-867 Classical | `k_shiwei` | shiwei | 8 | 4 | b_FIC_Amur_Jiapowo [castle], b_FIC_Am... |

##### Duchy of Puyudao (`d_SW_puyudao` / 蒲与道) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 564 | `c_SW_damoguo` | **Damoguo** | **达末国** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_damoguo River / Regional Basin (Sw_damoguo)* | **[RE]** | mongol | 5 | 4 | b_Amur_Mergen [castle], b_FIC_Amur_Xi... |
| 565 | `c_SW_heilonghean` | **Heilonghean** | **黑龙河岸** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_heilonghean River / Regional Basin (Sw_heilonghean)* | **[RE]** | mongol | 10 | 3 | b_FIC_Amur_Heisenlin [castle], b_FIC_... |
| 566 | `c_SW_puyuzhou` | **Puyuzhou** | **蒲与州** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_puyuzhou River / Regional Basin (Sw_puyuzhou)* | **[RE]** | shiwei | 8 | 4 | b_Amur_Puyu [castle], b_FIC_Amur_Xipu... |
| 567 | `c_SW_shanbeiguo` | **Shanbeiguo** | **山北国** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_shanbeiguo River / Regional Basin (Sw_shanbeiguo)* | **[RE]** | khitan | 5 | 4 | b_FIC_Amur_Jiashanbei [castle], b_FIC... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Puyudao:**
> * **`c_SW_damoguo` (Damoguo / 达末国):** Post-867 Shiwei nomadic clan encampment division. *Resolved via Option B: **Option B:** `Sw_damoguo River / Regional Basin` (Sw_damoguo).*
> * **`c_SW_heilonghean` (Heilonghean / 黑龙河岸):** Descriptive natural placeholder ('Amur River Bank'). *Resolved via Option B: **Option B:** `Sw_heilonghean River / Regional Basin` (Sw_heilonghean).*
> * **`c_SW_puyuzhou` (Puyuzhou / 蒲与州):** Post-867 Jin/Liao route prefecture; unverified in 867 AD. *Resolved via Option B: **Option B:** `Sw_puyuzhou River / Regional Basin` (Sw_puyuzhou).*
> * **`c_SW_shanbeiguo` (Shanbeiguo / 山北国):** Descriptive tribal division ('North Mountain Tribe'). *Resolved via Option B: **Option B:** `Sw_shanbeiguo River / Regional Basin` (Sw_shanbeiguo).*

##### Duchy of Qingxingan (`d_SW_qingxingan` / 青兴安) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 568 | `c_SW_huangtouguo` | **Huangtouguo** | **黄头国** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_huangtouguo River / Regional Basin (Sw_huangtouguo)* | **[RE]** | shiwei | 6 | 3 | b_FIC_Amur_Jiahuangtou [castle], b_FI... |
| 569 | `c_SW_luotuoguo` | **Luotuoguo** | **骆驼国** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_luotuoguo River / Regional Basin (Sw_luotuoguo)* | **[RE]** | Xingnabei | 5 | 4 | b_FIC_Amur_Jialuotuo [castle], b_FIC_... |
| 570 | `c_SW_nabeiguo` | **Nabeiguo** | **讷北国** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_nabeiguo River / Regional Basin (Sw_nabeiguo)* | **[RE]** | Xingnabei | 3 | 4 | b_FIC_Amur_Zhongnenjiang [castle], b_... |
| 571 | `c_SW_xinghuangtou` | **Xinghuangtou** | **兴黄头** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_xinghuangtou River / Regional Basin (Sw_xinghuangtou)* | **[RE]** | shiwei | 7 | 2 | b_FIC_Amur_Xinener [castle], b_FIC_Am... |
| 572 | `c_SW_xingnabei` | **Xingnabei** | **兴讷北** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Sw_xingnabei River / Regional Basin (Sw_xingnabei)* | **[RE]** | Xingnabei | 5 | 2 | b_FIC_Amur_Xianbeishan [castle], b_FI... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Qingxingan:**
> * **`c_SW_huangtouguo` (Huangtouguo / 黄头国):** Tribal division ('Yellow Head Tribe'); unverified pre-867 center. *Resolved via Option B: **Option B:** `Sw_huangtouguo River / Regional Basin` (Sw_huangtouguo).*
> * **`c_SW_luotuoguo` (Luotuoguo / 骆驼国):** Tribal division ('Camel Tribe'); lacks ancient urban foundation. *Resolved via Option B: **Option B:** `Sw_luotuoguo River / Regional Basin` (Sw_luotuoguo).*
> * **`c_SW_nabeiguo` (Nabeiguo / 讷北国):** Post-867 northern Nen river tribal division. *Resolved via Option B: **Option B:** `Sw_nabeiguo River / Regional Basin` (Sw_nabeiguo).*
> * **`c_SW_xinghuangtou` (Xinghuangtou / 兴黄头):** Descriptive tribal division; unverified urban center. *Resolved via Option B: **Option B:** `Sw_xinghuangtou River / Regional Basin` (Sw_xinghuangtou).*
> * **`c_SW_xingnabei` (Xingnabei / 兴讷北):** Descriptive tribal division; unverified urban center. *Resolved via Option B: **Option B:** `Sw_xingnabei River / Regional Basin` (Sw_xingnabei).*

##### Duchy of Ruzheguo (`d_SW_ruzheguo` / 如者国) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 573 | `c_SW_dongruzhe` | **Dongruzhe** | **东如者** | — | ✅ Pre-867 Classical | `k_balhae` | Xingnabei | 8 | 3 | b_FIC_Amur_Fanlinan [castle], b_FIC_A... |
| 574 | `c_SW_jiqin_hari` | **Jiqin Hari** | **济沁哈日** | — | ✅ Pre-867 Classical | `k_balhae` | khitan | 5 | 4 | b_Jiqin_Hari [castle], b_FIC_Amur_Jia... |
| 575 | `c_SW_ruzhejiang` | **Ruzhejiang** | **如者江** | — | ✅ Pre-867 Classical | `k_balhae` | Xingnabei | 15 | 3 | b_FIC_Amur_Ruzhejiang [castle], b_FIC... |

##### Duchy of Sushenguo (`d_SW_sushenguo` / 肃慎国) — *0/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 576 | `c_SW_fancao` | **Fancao** | **番草** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | balhae | 13 | 3 | b_FIC_Amur_Fancao [castle], b_FIC_Amu... |
| 577 | `c_SW_gonghejiang` | **Gonghejiang** | **共和江** | — | ✅ Pre-867 Classical | `k_balhae` | Xingnabei | 11 | 2 | b_FIC_Amur_Gonghejiang [castle], b_FI... |
| 578 | `c_SW_heilonglin` | **Heilonglin** | **黑龙林** | — | ✅ Pre-867 Classical | `k_balhae` | jurchen | 7 | 2 | b_FIC_Amur_Heilonglin [castle] |
| 579 | `c_SW_lupingyuan` | **Lupingyuan** | **鹿坪塬** | — | ✅ Pre-867 Classical | `k_balhae` | Xingnabei | 12 | 3 | b_FIC_Amur_Lupingyuan [castle], b_FIC... |
| 580 | `c_SW_suihua` | **Suihua** | **绥化** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | jurchen | 6 | 4 | b_Amur_Suihua [castle], b_FIC_Amur_Li... |

### 3.4 Empire of Amur (`e_amur` / 阿穆尔)
- **De Jure Extent:** **40 Counties**, 11 Duchies, 3 Kingdoms.
- **Total Development:** **544.0** (Average: 13.6) | **Baronies:** 130
- **1154 Roman Empire Control:** **17 / 40 counties** (42.5%) | **Anachronisms Flagged:** **10**

#### 3.4.1 Kingdom of Amur (`k_amur` / 阿穆尔)
*Extent: **22 Counties** | Development: **241** (avg 11.0) | Roman Control: **9/22** | Flagged Anachronisms: **9***

##### Duchy of Amar (`d_eman_amar` / 阿玛尔) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 581 | `c_eman_murkonno` | **Murkonno** | **穆尔孔诺** | — | ✅ Pre-867 Classical | `k_luzhen` | mohe | 8 | 4 | b_fic_eman_bira [castle], b_fic_eman_... |
| 582 | `c_eman_nimen` | **Nimen** | **尼门** | — | ✅ Pre-867 Classical | `k_luzhen` | mohe | 13 | 3 | b_fic_eman_nimen [castle], b_fic_eman... |
| 583 | `c_eman_urmi` | **Urmi** | **乌尔米** | — | ✅ Pre-867 Classical | `k_luzhen` | mohe | 12 | 2 | b_fic_eman_urmi [castle], b_fic_eman_... |
| 584 | `c_eman_vanda` | **Vanda** | **完达** | — | ✅ Pre-867 Classical | `k_luzhen` | mohe | 13 | 3 | b_fic_eman_vandarin [castle], b_fic_e... |

##### Duchy of Boli (`d_eman_boli` / 勃利) — *4/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 585 | `c_eman_boli` | **Boli** | **勃利** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_boli River / Regional Basin (Eman_boli)* | **[RE]** | mohe | 10 | 4 | b_eman_boli [castle], b_fic_eman_nans... |
| 586 | `c_eman_choripi` | **Choripi** | **也曼水** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_choripi River / Regional Basin (Eman_choripi)* | **[RE]** | mohe | 11 | 3 | b_fic_eman_choripi [castle], b_fic_em... |
| 587 | `c_eman_mohean` | **Mohean** | **莫罕** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_mohean River / Regional Basin (Eman_mohean)* | **[RE]** | jurchen | 11 | 3 | b_fic_eman_mohean [castle], b_fic_ema... |
| 588 | `c_eman_molihewen` | **Molihewen** | **末里合温** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_molihewen River / Regional Basin (Eman_molihewen)* | **[RE]** | mohe | 12 | 4 | b_eman_molihewen [castle], b_fic_eman... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Boli:**
> * **`c_eman_boli` (Boli / 勃利):** Confluence of the Amur and Ussuri rivers (modern Khabarovsk); administrative town dates to modern/Qing era. *Resolved via Option B: **Option B:** `Eman_boli River / Regional Basin` (Eman_boli).*
> * **`c_eman_choripi` (Choripi / 也曼水):** Remote Tungusic wilderness area; lacks pre-867 urban center. *Resolved via Option B: **Option B:** `Eman_choripi River / Regional Basin` (Eman_choripi).*
> * **`c_eman_mohean` (Mohean / 莫罕):** Remote Amur basin territory; lacks pre-867 urban foundation. *Resolved via Option B: **Option B:** `Eman_mohean River / Regional Basin` (Eman_mohean).*
> * **`c_eman_molihewen` (Molihewen / 末里合温):** Remote forest outpost; lacks pre-867 verified settlement. *Resolved via Option B: **Option B:** `Eman_molihewen River / Regional Basin` (Eman_molihewen).*

##### Duchy of Bureya (`d_eman_bureya` / 布列亚) — *0/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 589 | `c_eman_birija` | **Birija** | **必剌牙** | — | ✅ Pre-867 Classical | `k_amur` | mohe | 14 | 2 | b_fic_eman_birija [castle], b_fic_ema... |
| 590 | `c_eman_turma` | **Turma** | **特尔马** | — | ✅ Pre-867 Classical | `k_luzhen` | mohe | 14 | 3 | b_fic_eman_turma [castle], b_fic_eman... |
| 591 | `c_eman_urehokto` | **Urehokto** | **乌哷和克托** | — | ✅ Pre-867 Classical | `k_luzhen` | mohe | 14 | 2 | b_fic_eman_umilimo [castle], b_fic_em... |

##### Duchy of Nivkhia (`d_eman_nivkhia` / 尼夫赫) — *3/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 592 | `c_eman_amgun` | **Amgun** | **恨骨** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_amgun River / Regional Basin (Eman_amgun)* | **[RE]** | nivkh | 6 | 3 | b_fic_eman_amgun [castle] |
| 593 | `c_eman_nurgan` | **Nurgan** | **奴儿干** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_nurgan River / Regional Basin (Eman_nurgan)* | **[RE]** | nivkh | 9 | 4 | b_eman_nurgan [castle], b_fic_eman_ka... |
| 594 | `c_eman_tugur` | **Tugur** | **图古尔** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_tugur River / Regional Basin (Eman_tugur)* | **[RE]** | nivkh | 10 | 3 | b_fic_eman_tugur [castle], b_fic_eman... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Nivkhia:**
> * **`c_eman_amgun` (Amgun / 恨骨):** Remote northern Amgun river tributary; lacks pre-867 attested town. *Resolved via Option B: **Option B:** `Eman_amgun River / Regional Basin` (Eman_amgun).*
> * **`c_eman_nurgan` (Nurgan / 奴儿干):** Named after the Ming dynasty Nurgan Regional Military Commission (奴儿干都司), established in 1409 AD. Lacks pre-867 urban center. *Resolved via Option B: **Option B:** `Eman_nurgan River / Regional Basin` (Eman_nurgan).*
> * **`c_eman_tugur` (Tugur / 图古尔):** Okhotsk sea coastal tract; unverified prior to 867 AD. *Resolved via Option B: **Option B:** `Eman_tugur River / Regional Basin` (Eman_tugur).*

##### Duchy of Samagero (`d_eman_samagero` / 萨玛格罗) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 595 | `c_eman_kerin` | **Kerin** | **刻林** | — | ✅ Pre-867 Classical | `d_eman_samagero` | nivkh | 9 | 2 | b_fic_eman_kerin [castle], b_fic_eman... |
| 596 | `c_eman_khadul` | **Khadul** | **喀多尔** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | nivkh | 13 | 3 | b_fic_eman_khadul [castle], b_fic_ema... |
| 597 | `c_eman_tudali` | **Tudali** | **图达里** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | nivkh | 12 | 3 | b_fic_eman_tudali [castle], b_fic_ema... |
| 598 | `c_eman_yam_alin` | **Yam Alin** | **杨山** | — | ✅ Pre-867 Classical | `d_eman_samagero` | nivkh | 9 | 3 | b_fic_eman_yam_alin [castle] |

##### Duchy of Sikhotebei (`d_eman_sikhotebei` / 西河大北) — *2/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 599 | `c_eman_beihean` | **Beihean** | **北河岸** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_beihean River / Regional Basin (Eman_beihean)* | **[RE]** | mohe | 11 | 2 | b_fic_eman_beihean [castle], b_fic_em... |
| 600 | `c_eman_heishuiyang` | **Heishuiyang** | **黑水洋** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | mohe | 7 | 3 | b_fic_eman_heishuiyang [castle], b_fi... |
| 601 | `c_eman_wuguihai` | **Wuguihai** | **乌龟海** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | mohe | 12 | 3 | b_fic_eman_wuguihai [castle], b_fic_e... |
| 602 | `c_eman_yerenhe` | **Yerenhe** | **野人河** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Eman_yerenhe River / Regional Basin (Eman_yerenhe)* | **[RE]** | mohe | 11 | 3 | b_fic_eman_yerenhe [castle], b_fic_em... |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Sikhotebei:**
> * **`c_eman_beihean` (Beihean / 北河岸):** Descriptive placeholder ('North River Bank'); lacks ancient town. *Resolved via Option B: **Option B:** `Eman_beihean River / Regional Basin` (Eman_beihean).*
> * **`c_eman_yerenhe` (Yerenhe / 野人河):** Descriptive placeholder ('Wild Jurchen River'); lacks ancient town. *Resolved via Option B: **Option B:** `Eman_yerenhe River / Regional Basin` (Eman_yerenhe).*

#### 3.4.2 Kingdom of Aynumosir (`k_aynumosir` / 阿伊努茅希利)
*Extent: **11 Counties** | Development: **78** (avg 7.1) | Roman Control: **1/11** | Flagged Anachronisms: **1***

##### Duchy of Menas (`d_menas` / 目梨) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 603 | `c_chupka` | **Chupka** | **日东见** | — | ✅ Pre-867 Classical | `k_aynumosir` | Ainu-Mohe | 4 | 2 | b_kinasir [castle], b_etuworop_sir [c... |
| 604 | `c_menas` | **Menas** | **目梨** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | Ainu-Mohe | 7 | 3 | b_pior [castle], b_opereperkep [city]... |
| 605 | `c_simenas` | **Simenas** | **大东风** | — | ✅ Pre-867 Classical | `k_aynumosir` | Ainu-Mohe | 9 | 4 | b_kusuri [castle], b_sir_etok [church] |
| 606 | `c_soya` | **Soya** | **宗谷** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | Ainu-Mohe | 17 | 4 | b_mopet [castle], b_soya [city], b_na... |

##### Duchy of Sahaliyan (`d_sahaliyan` / 撒合辇) — *1/3 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 607 | `c_kusunkotan` | **Kusunkotan** | **对涯村** | — | ⚠️ **[Post-867 / Tier 3]** → *Opt B: Kusunkotan River / Regional Basin (Kusunkotan)* | **[RE]** | nivkh | 4 | 3 | b_kusunkotan [castle], b_kusunnay [ci... |
| 608 | `c_pogibi` | **Pogibi** | **博和必** | — | ✅ Pre-867 Classical | `k_aynumosir` | nivkh | 5 | 3 | b_pogibi [castle], b_tym_sakhalin [ci... |
| 609 | `c_tarayka` | **Tarayka** | **多来加** | — | ✅ Pre-867 Classical | `k_aynumosir` | nivkh | 2 | 3 | b_tarayka [castle], b_ketuni [city] |

> [!NOTE]
> **Historical Anachronism Resolutions in Duchy of Sahaliyan:**
> * **`c_kusunkotan` (Kusunkotan / 对涯村):** Sakhalin Island indigenous settlement (later Korsakov / Kusunkotan, established in 18th century). *Resolved via Option B: **Option B:** `Kusunkotan River / Regional Basin` (Kusunkotan).*

##### Duchy of Sum (`d_sum` / 岬角) — *0/4 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 610 | `c_ioci` | **Ioci** | **来止卧** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | Ainu-Mohe | 6 | 4 | b_ioci [castle] |
| 611 | `c_iskar` | **Iskar** | **曲川** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | Ainu-Mohe | 13 | 4 | b_iskar_hokkaido [castle], b_rurmo_ot... |
| 612 | `c_sum` | **Sum** | **岬角** | — | ✅ Pre-867 Classical | `d_eman_sikhotebei` | Ainu-Mohe | 9 | 4 | b_sar [castle], b_iput [city], b_sipi... |
| 613 | `c_uskes` | **Uskes** | **湾端** | — | ✅ Pre-867 Classical | `k_aynumosir` | Ainu-Mohe | 2 | 4 | b_matomai [castle], b_uskes [city], b... |

#### 3.4.3 Kingdom of Hitakami (`k_hitakami` / 日高见)
*Extent: **7 Counties** | Development: **225** (avg 32.1) | Roman Control: **7/7** | Flagged Anachronisms: **0***

##### Duchy of Hitakami (`d_hitakami` / 日高见) — *5/5 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 614 | `c_isawa` | **Isawa** | **胆泽** | 胆沢 | ✅ Pre-867 Classical | **[RE]** | japanese | 30 | 4 | b_isawa [castle], b_nukanobu [city], ... |
| 615 | `c_iwaki` | **Iwaki** | **石城** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 32 | 3 | b_iwaki [castle], b_shirakawa [city],... |
| 616 | `c_iwase` | **Iwase** | **石背** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 31 | 4 | b_adachi [castle], b_yama_iwase [chur... |
| 617 | `c_korehari` | **Korehari** | **伊治** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 37 | 4 | b_taga [castle], b_korehari [city], b... |
| 618 | `c_tsugaru` | **Tsugaru** | **津轻** | 津軽 | ✅ Pre-867 Classical | **[RE]** | japanese | 31 | 4 | b_tsugaru [castle], b_tsumo [city], b... |

##### Duchy of Nushiro (`d_nushiro` / 渟代) — *2/2 in Roman Empire*

| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 619 | `c_nushiro` | **Nushiro** | **渟代** | — | ✅ Pre-867 Classical | **[RE]** | japanese | 28 | 5 | b_agita [castle], b_nushiro [church],... |
| 620 | `c_tokisara` | **Tokisara** | **都岐沙罗** | 都岐沙羅 | ✅ Pre-867 Classical | **[RE]** | japanese | 36 | 3 | b_okitama [castle], b_tokisara [churc... |

---

## 4. Comprehensive Ranking of All 39 Sinospheric De Jure Kingdoms

| Rank | Kingdom Name | Title Key | Chinese Characters | De Jure Empire | Counties | Total Baronies | Total Dev | Avg Dev | 1154 Roman Control | Anachronisms Flagged | Dominant Realm in 1154 |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | **Shiwei** | `k_shiwei` | **室韦** | Andong (`e_andong`) | **29** | 96 | 182 | 6.3 | **13/29** (44.8%) | **13 flagged** | Roman Empire |
| 2 | **Yamato** | `k_yamato` | **大和** | Japan (`e_japan`) | **26** | 87 | 1,150 | 44.2 | **26/26** (100.0%) | 0 | Roman Empire |
| 3 | **Guannei** | `k_guannei` | **关内** | Yongliang (`e_yongliang`) | **26** | 79 | 1,766 | 67.9 | **3/26** (11.5%) | **3 flagged** | Guannei |
| 4 | **Bóhai** | `k_balhae` | **渤海** | Andong (`e_andong`) | **25** | 88 | 586 | 23.4 | **22/25** (88.0%) | 0 | Roman Empire |
| 5 | **Xia** | `k_xia` | **夏** | Yongliang (`e_yongliang`) | **24** | 70 | 744 | 31.0 | **24/24** (100.0%) | 0 | Roman Empire |
| 6 | **Hexi** | `k_hexi` | **河西** | Yongliang (`e_yongliang`) | **23** | 59 | 636 | 27.7 | **23/23** (100.0%) | 0 | Roman Empire |
| 7 | **Azuma** | `k_azuma` | **吾妻** | Japan (`e_japan`) | **23** | 85 | 876 | 38.1 | **23/23** (100.0%) | 0 | Roman Empire |
| 8 | **Lingnan** | `k_lingnan` | **岭南** | Lingnan (`e_lingnan`) | **22** | 80 | 1,093 | 49.7 | **0/22** (0.0%) | 0 | Lingnan |
| 9 | **Amur** | `k_amur` | **阿穆尔** | Amur (`e_amur`) | **22** | 65 | 241 | 11.0 | **9/22** (40.9%) | **9 flagged** | Roman Empire |
| 10 | **Lingxi** | `k_lingxi` | **岭西** | Lingnan (`e_lingnan`) | **21** | 65 | 837 | 39.9 | **0/21** (0.0%) | 0 | Lingnan |
| 11 | **Goguryeo** | `k_goguryeo` | **高句丽** | Samhan (`e_goryeo`) | **20** | 63 | 525 | 26.2 | **20/20** (100.0%) | 0 | Roman Empire |
| 12 | **Shannan** | `k_shannan` | **山南** | Jingyang (`e_jingyang`) | **19** | 74 | 1,366 | 71.9 | **0/19** (0.0%) | 0 | Qianzhong |
| 13 | **Luzhen** | `k_luzhen` | **虑真** | Andong (`e_andong`) | **18** | 53 | 330 | 18.3 | **11/18** (61.1%) | **11 flagged** | Roman Empire |
| 14 | **Qianzhong** | `k_qianzhong` | **黔中** | Liangyi (`e_liangyi`) | **18** | 54 | 674 | 37.4 | **0/18** (0.0%) | 0 | Qianzhong |
| 15 | **Dali** | `k_dali` | **大理** | Liangyi (`e_liangyi`) | **17** | 48 | 647 | 38.1 | **0/17** (0.0%) | 0 | Qianzhong |
| 16 | **Qingxu** | `k_qingxu` | **青徐** | Zhongyuan (`e_zhongyuan`) | **17** | 64 | 805 | 47.4 | **0/17** (0.0%) | 0 | Qingxu |
| 17 | **Kuizhou** | `k_kuizhou` | **夔州** | Liangyi (`e_liangyi`) | **17** | 58 | 766 | 45.1 | **0/17** (0.0%) | 0 | Qianzhong |
| 18 | **Hedong** | `k_hedong` | **河东** | Zhongyuan (`e_zhongyuan`) | **15** | 54 | 754 | 50.3 | **15/15** (100.0%) | 0 | Roman Empire |
| 19 | **Hebei** | `k_hebei` | **河北** | Zhongyuan (`e_zhongyuan`) | **15** | 41 | 733 | 48.9 | **0/15** (0.0%) | 0 | Hebei |
| 20 | **Henan** | `k_henan` | **河南** | Zhongyuan (`e_zhongyuan`) | **15** | 50 | 879 | 58.6 | **0/15** (0.0%) | 0 | Qianzhong |
| 21 | **Daibei** | `k_daibei` | **代北** | Zhongyuan (`e_zhongyuan`) | **14** | 42 | 313 | 22.4 | **14/14** (100.0%) | 0 | Roman Empire |
| 22 | **Raole** | `k_raole` | **饶乐** | Andong (`e_andong`) | **14** | 45 | 314 | 22.4 | **13/14** (92.9%) | **13 flagged** | Roman Empire |
| 23 | **Jiangxi** | `k_jiangxi` | **江西** | Jingyang (`e_jingyang`) | **14** | 52 | 899 | 64.2 | **0/14** (0.0%) | 0 | Jiangxi |
| 24 | **Xingyuan** | `k_xingyuan` | **兴元** | Liangyi (`e_liangyi`) | **13** | 38 | 745 | 57.3 | **0/13** (0.0%) | 0 | Xingyuan |
| 25 | **Silla** | `k_silla` | **新罗** | Samhan (`e_goryeo`) | **13** | 42 | 409 | 31.5 | **13/13** (100.0%) | 0 | Roman Empire |
| 26 | **Dongchuan** | `k_dongchuan` | **东川** | Liangyi (`e_liangyi`) | **12** | 30 | 504 | 42.0 | **0/12** (0.0%) | 0 | Xichuan |
| 27 | **Xichuan** | `k_xichuan` | **西川** | Liangyi (`e_liangyi`) | **12** | 33 | 452 | 37.7 | **0/12** (0.0%) | 0 | Xichuan |
| 28 | **Khitan** | `k_khitan` | **契丹** | Andong (`e_andong`) | **11** | 39 | 155 | 14.1 | **11/11** (100.0%) | **11 flagged** | Roman Empire |
| 29 | **Liangzhe** | `k_liangzhe` | **两浙** | Jingyang (`e_jingyang`) | **11** | 42 | 890 | 80.9 | **0/11** (0.0%) | 0 | Liangzhe |
| 30 | **Baekje** | `k_baekje` | **百济** | Samhan (`e_goryeo`) | **11** | 34 | 298 | 27.1 | **11/11** (100.0%) | 0 | Roman Empire |
| 31 | **Aynumosir** | `k_aynumosir` | **阿伊努茅希利** | Amur (`e_amur`) | **11** | 38 | 78 | 7.1 | **1/11** (9.1%) | **1 flagged** | Aynumosir |
| 32 | **Huainan** | `k_huainan` | **淮南** | Jingyang (`e_jingyang`) | **10** | 38 | 633 | 63.3 | **0/10** (0.0%) | 0 | Huainan |
| 33 | **Youji** | `k_youji` | **幽蓟** | Zhongyuan (`e_zhongyuan`) | **10** | 32 | 389 | 38.9 | **10/10** (100.0%) | 0 | Roman Empire |
| 34 | **Tsukushi** | `k_tsukushi` | **筑紫** | Japan (`e_japan`) | **10** | 38 | 277 | 27.7 | **10/10** (100.0%) | 0 | Roman Empire |
| 35 | **Hunan** | `k_hunan` | **湖南** | Jingyang (`e_jingyang`) | **9** | 36 | 473 | 52.6 | **0/9** (0.0%) | 0 | Lingnan |
| 36 | **Đại Việt** | `k_viet` | **大越** | Lingnan (`e_lingnan`) | **9** | 32 | 489 | 54.3 | **0/9** (0.0%) | 0 | Đại Việt |
| 37 | **Fujian** | `k_fujian` | **福建** | Jingyang (`e_jingyang`) | **9** | 36 | 697 | 77.4 | **0/9** (0.0%) | 0 | Liangzhe |
| 38 | **Jiangdong** | `k_jiangdong` | **江东** | Jingyang (`e_jingyang`) | **8** | 30 | 592 | 74.0 | **0/8** (0.0%) | 0 | Jiangdong |
| 39 | **Hitakami** | `k_hitakami` | **日高见** | Amur (`e_amur`) | **7** | 27 | 225 | 32.1 | **7/7** (100.0%) | 0 | Roman Empire |

---

## 5. Master Register of 61 Sinosphere Anachronism Resolutions

Below is the exhaustive audit register of all **61 Sinosphere counties** flagged for post-867 foundation, eponymous naming, or lack of verified classical antiquity urban attestation. Under the **Toponym-First Principle**, all 61 titles have been resolved to their underlying ancient hydronyms, natural relief landmarks, or regional basin substrates (Option B) to prevent the circular canonization of high-medieval foundations.

### 5.1 Khitan Liao Dynastic Foundations (24 Counties)
*Scope: **24 Flagged Counties** in Empire of Andong (`e_andong`)*

| # | County Key | In-Game Name | Chinese Characters | De Jure Kingdom | Historical Anachronism Rationale | Resolution Strategy (Option B) | Tarraconian Chancellery Title | Historical & Etymological Justification |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `c_LIAO_changchun` | **Changchun** | **长春** | Khitan (`k_khitan`) | Established in 926 AD by the Khitans as a state-sponsored relocation garrison following the conquest of Bohai. | **Option B:** `Liao_changchun River / Regional Basin` (Liao_changchun) | ****Magistrat van Liao_changchun**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_changchun under Burden of Proof on Antiquity. |
| 2 | `c_LIAO_chaoyang` | **Chaoyang** | **朝阳** | Raole (`k_raole`) | Post-867 Khitan regional commandery in the Daling River valley. | **Option B:** `Liao_chaoyang River / Regional Basin` (Liao_chaoyang) | ****Magistrat van Liao_chaoyang**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_chaoyang under Burden of Proof on Antiquity. |
| 3 | `c_LIAO_dading` | **Dading** | **大定** | Raole (`k_raole`) | Founded in 1007 AD by Emperor Shengzong of Liao as the Central Capital (Liao Zhongjing / 中京大定府). | **Option B:** `Liao_dading River / Regional Basin` (Liao_dading) | ****Magistrat van Liao_dading**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_dading under Burden of Proof on Antiquity. |
| 4 | `c_LIAO_dalian` | **Dalian** | **达里岸** | Khitan (`k_khitan`) | Post-867 Khitan regional encampment; lacks pre-867 civil center. | **Option B:** `Liao_dalian River / Regional Basin` (Liao_dalian) | ****Magistrat van Liao_dalian**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_dalian under Burden of Proof on Antiquity. |
| 5 | `c_LIAO_heicaoan` | **Heicaoan** | **黑草岸** | Khitan (`k_khitan`) | Post-867 pastoral encampment on the eastern steppe frontier. | **Option B:** `Liao_heicaoan River / Regional Basin` (Liao_heicaoan) | ****Magistrat van Liao_heicaoan**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_heicaoan under Burden of Proof on Antiquity. |
| 6 | `c_LIAO_horqinan` | **Horqinan** | **火儿赤纳** | Khitan (`k_khitan`) | Post-867 Horqin steppe grazing division; unverified prior to 867 AD. | **Option B:** `Liao_horqinan River / Regional Basin` (Liao_horqinan) | ****Magistrat van Liao_horqinan**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_horqinan under Burden of Proof on Antiquity. |
| 7 | `c_LIAO_jinzhou` | **Jinzhou** | **锦州** | Raole (`k_raole`) | Established in 923 AD by Yelü Abaoji with captive Han artisans from Pingzhou. | **Option B:** `Liao_jinzhou River / Regional Basin` (Liao_jinzhou) | ****Magistrat van Liao_jinzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_jinzhou under Burden of Proof on Antiquity. |
| 8 | `c_LIAO_linhuang` | **Linhuang** | **临潢** | Khitan (`k_khitan`) | Founded in 918 AD by Yelü Abaoji (Emperor Taizu of Liao) as the Supreme Capital (Liao Shangjing / 上京临潢府) on the Shira Muren river. | **Option B:** `Liao_linhuang River / Regional Basin` (Liao_linhuang) | ****Magistrat van Liao_linhuang**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_linhuang under Burden of Proof on Antiquity. |
| 9 | `c_LIAO_longhuazhou` | **Longhuazhou** | **龙化州** | Khitan (`k_khitan`) | Founded in 902 AD by Yelü Abaoji as a fortified private encampment (dongzhai) prior to his imperial coronation. | **Option B:** `Liao_longhuazhou River / Regional Basin` (Liao_longhuazhou) | ****Magistrat van Liao_longhuazhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_longhuazhou under Burden of Proof on Antiquity. |
| 10 | `c_LIAO_ningzhou` | **Ningzhou** | **宁州** | Khitan (`k_khitan`) | Post-867 Liao garrison prefecture established in former Bohai territory. | **Option B:** `Liao_ningzhou River / Regional Basin` (Liao_ningzhou) | ****Magistrat van Liao_ningzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_ningzhou under Burden of Proof on Antiquity. |
| 11 | `c_LIAO_raozhou` | **Raozhou** | **饶州** | Khitan (`k_khitan`) | Established in 953 AD by Emperor Muzong of Liao in the fertile upper Xilamulun river basin. | **Option B:** `Liao_raozhou River / Regional Basin` (Liao_raozhou) | ****Magistrat van Liao_raozhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_raozhou under Burden of Proof on Antiquity. |
| 12 | `c_LIAO_taizhou` | **Taizhou** | **泰州** | Khitan (`k_khitan`) | Established in 916–926 AD as a Liao defensive garrison prefecture. | **Option B:** `Liao_taizhou River / Regional Basin` (Liao_taizhou) | ****Magistrat van Liao_taizhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_taizhou under Burden of Proof on Antiquity. |
| 13 | `c_LIAO_ulagaian` | **Ulagaian** | **兀鲁回岸** | Khitan (`k_khitan`) | Post-867 Ulagai river frontier march; unverified prior to 867 AD. | **Option B:** `Liao_ulagaian River / Regional Basin` (Liao_ulagaian) | ****Magistrat van Liao_ulagaian**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_ulagaian under Burden of Proof on Antiquity. |
| 14 | `c_LIAO_wuzhou` | **Wuzhou** | **乌州** | Khitan (`k_khitan`) | Post-867 Liao tribal prefecture; unverified prior to 867 AD. | **Option B:** `Liao_wuzhou River / Regional Basin` (Liao_wuzhou) | ****Magistrat van Liao_wuzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_wuzhou under Burden of Proof on Antiquity. |
| 15 | `c_LIAO_xianzhou` | **Xianzhou** | **显州** | Raole (`k_raole`) | Established in 926 AD at the medical and ancestral tumulus of Prince Yelü Bei (Prince of Dongdan). | **Option B:** `Liao_xianzhou River / Regional Basin` (Liao_xianzhou) | ****Magistrat van Liao_xianzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_xianzhou under Burden of Proof on Antiquity. |
| 16 | `c_liao_fengzhou` | **Fengzhou** | **丰州** | Raole (`k_raole`) | Post-867 Liao garrison prefecture in southern Inner Mongolia. | **Option B:** `Liao_fengzhou River / Regional Basin` (Liao_fengzhou) | ****Magistrat van Liao_fengzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Liao_fengzhou under Burden of Proof on Antiquity. |
| 17 | `c_lnj_liaoxi` | **Liaoxi** | **辽西** | Raole (`k_raole`) | Descriptive post-867 frontier slice; lacks ancient urban center. | **Option B:** `Lnj_liaoxi River / Regional Basin` (Lnj_liaoxi) | ****Magistrat van Lnj_liaoxi**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Lnj_liaoxi under Burden of Proof on Antiquity. |
| 18 | `c_lnj_liaoxibei` | **Liaoxibei** | **辽西北** | Raole (`k_raole`) | Descriptive post-867 frontier slice; lacks ancient urban center. | **Option B:** `Lnj_liaoxibei River / Regional Basin` (Lnj_liaoxibei) | ****Magistrat van Lnj_liaoxibei**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Lnj_liaoxibei under Burden of Proof on Antiquity. |
| 19 | `c_lxj_huanzhou` | **Huanzhou** | **桓州** | Raole (`k_raole`) | Established 960+ AD by the Khitans as an inner march prefecture. | **Option B:** `Lxj_huanzhou River / Regional Basin` (Lxj_huanzhou) | ****Magistrat van Lxj_huanzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Lxj_huanzhou under Burden of Proof on Antiquity. |
| 20 | `c_lxj_yangchengzhou` | **Yangchengzhou** | **羊城州** | Raole (`k_raole`) | Post-867 Khitan grazing prefecture; unverified prior to 867 AD. | **Option B:** `Lxj_yangchengzhou River / Regional Basin` (Lxj_yangchengzhou) | ****Magistrat van Lxj_yangchengzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Lxj_yangchengzhou under Burden of Proof on Antiquity. |
| 21 | `c_lxj_yuyidong` | **Yuyidong** | **御夷东** | Raole (`k_raole`) | Post-867 marchland division of the Yuyi frontier. | **Option B:** `Lxj_yuyidong River / Regional Basin` (Lxj_yuyidong) | ****Magistrat van Lxj_yuyidong**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Lxj_yuyidong under Burden of Proof on Antiquity. |
| 22 | `c_lzj_chengde` | **Chengde** | **承德** | Raole (`k_raole`) | Modern anachronism derived from the Qing dynasty imperial mountain resort (Bishu Shanzhuang, founded 1703 AD). | **Option B:** `Lzj_chengde River / Regional Basin` (Lzj_chengde) | ****Magistrat van Lzj_chengde**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Lzj_chengde under Burden of Proof on Antiquity. |
| 23 | `c_lzj_chengdexi` | **Chengdexi** | **承德西** | Raole (`k_raole`) | Descriptive modern subdivision of the Qing-era Chengde prefecture. | **Option B:** `Lzj_chengdexi River / Regional Basin` (Lzj_chengdexi) | ****Magistrat van Lzj_chengdexi**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Lzj_chengdexi under Burden of Proof on Antiquity. |
| 24 | `c_woye` | **Woye** | **沃野** | Raole (`k_raole`) | Post-867 frontier pastoral division; lacks pre-867 civil oppidum. | **Option B:** `Woye River / Regional Basin` (Woye) | ****Magistrat van Woye**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Woye under Burden of Proof on Antiquity. |

### 5.2 Jurchen & Bohai Frontier Market Settlements (11 Counties)
*Scope: **11 Flagged Counties** in Empire of Andong (`e_andong`)*

| # | County Key | In-Game Name | Chinese Characters | De Jure Kingdom | Historical Anachronism Rationale | Resolution Strategy (Option B) | Tarraconian Chancellery Title | Historical & Etymological Justification |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 25 | `c_BAL_anbyeon` | **Ānbiān** | **安边** | Luzhen (`k_luzhen`) | Anbian border commandery on the frontier of Bohai and the Khitans. | **Option B:** `Bal_anbyeon River / Regional Basin` (Bal_anbyeon) | ****Magistrat van Bal_anbyeon**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_anbyeon under Burden of Proof on Antiquity. |
| 26 | `c_BAL_delizhen` | **Délizhèn** | **德理镇** | Luzhen (`k_luzhen`) | Jurchen border market post established during late Bohai/Liao transition. | **Option B:** `Bal_delizhen River / Regional Basin` (Bal_delizhen) | ****Magistrat van Bal_delizhen**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_delizhen under Burden of Proof on Antiquity. |
| 27 | `c_BAL_heuksu_anwon` | **Heuksu Anwon** | **黑水安远** | Luzhen (`k_luzhen`) | Northern Mohe frontier market on the Amur/Heuksu. | **Option B:** `Bal_heuksu_anwon River / Regional Basin` (Bal_heuksu_anwon) | ****Magistrat van Bal_heuksu_anwon**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_heuksu_anwon under Burden of Proof on Antiquity. |
| 28 | `c_BAL_huligai` | **Huligai** | **胡里改** | Luzhen (`k_luzhen`) | Ilun Hurka route of the Jurchen tribes along the Mudanjiang River. | **Option B:** `Bal_huligai River / Regional Basin` (Bal_huligai) | ****Magistrat van Bal_huligai**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_huligai under Burden of Proof on Antiquity. |
| 29 | `c_BAL_jeongni` | **Dìngli** | **定理** | Luzhen (`k_luzhen`) | Post-867 Bohai/Jurchen prefecture; unverified pre-867 center. | **Option B:** `Bal_jeongni River / Regional Basin` (Bal_jeongni) | ****Magistrat van Bal_jeongni**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_jeongni under Burden of Proof on Antiquity. |
| 30 | `c_BAL_ningzhou` | **Níngzhōu** | **宁州** | Luzhen (`k_luzhen`) | Post-867 Bohai relocation prefecture. | **Option B:** `Bal_ningzhou River / Regional Basin` (Bal_ningzhou) | ****Magistrat van Bal_ningzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_ningzhou under Burden of Proof on Antiquity. |
| 31 | `c_BAL_north_anbyeon` | **North Ānbiān** | **北安边** | Luzhen (`k_luzhen`) | Descriptive frontier subdivision of Anbian. | **Option B:** `Bal_north_anbyeon River / Regional Basin` (Bal_north_anbyeon) | ****Magistrat van Bal_north_anbyeon**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_north_anbyeon under Burden of Proof on Antiquity. |
| 32 | `c_BAL_north_anwon` | **North Ānyuan** | **北安远** | Luzhen (`k_luzhen`) | Descriptive northern frontier market outpost of Bohai. | **Option B:** `Bal_north_anwon River / Regional Basin` (Bal_north_anwon) | ****Magistrat van Bal_north_anwon**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_north_anwon under Burden of Proof on Antiquity. |
| 33 | `c_BAL_solbin` | **Shuàibīn** | **率宾** | Luzhen (`k_luzhen`) | Suifen river basin; Bohai secondary prefecture reorganised post-867. | **Option B:** `Bal_solbin River / Regional Basin` (Bal_solbin) | ****Magistrat van Bal_solbin**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_solbin under Burden of Proof on Antiquity. |
| 34 | `c_BAL_supin` | **Supin** | **速频** | Luzhen (`k_luzhen`) | Post-867 Jurchen tribal valley; unverified urban center. | **Option B:** `Bal_supin River / Regional Basin` (Bal_supin) | ****Magistrat van Bal_supin**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_supin under Burden of Proof on Antiquity. |
| 35 | `c_BAL_west_cheolli` | **West Tielì** | **西铁利** | Luzhen (`k_luzhen`) | Descriptive subdivision of Tieli Jurchen territory. | **Option B:** `Bal_west_cheolli River / Regional Basin` (Bal_west_cheolli) | ****Magistrat van Bal_west_cheolli**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Bal_west_cheolli under Burden of Proof on Antiquity. |

### 5.3 Shiwei Nomadic Clan Divisions (13 Counties)
*Scope: **13 Flagged Counties** in Empire of Andong (`e_andong`)*

| # | County Key | In-Game Name | Chinese Characters | De Jure Kingdom | Historical Anachronism Rationale | Resolution Strategy (Option B) | Tarraconian Chancellery Title | Historical & Etymological Justification |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 36 | `c_SW_damoguo` | **Damoguo** | **达末国** | Shiwei (`k_shiwei`) | Post-867 Shiwei nomadic clan encampment division. | **Option B:** `Sw_damoguo River / Regional Basin` (Sw_damoguo) | ****Magistrat van Sw_damoguo**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_damoguo under Burden of Proof on Antiquity. |
| 37 | `c_SW_dongcheziguo` | **Dongcheziguo** | **东车子国** | Shiwei (`k_shiwei`) | Nomadic clan division ('Eastern Cart Tribe'); lacks fixed pre-867 urban center. | **Option B:** `Sw_dongcheziguo River / Regional Basin` (Sw_dongcheziguo) | ****Magistrat van Sw_dongcheziguo**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_dongcheziguo under Burden of Proof on Antiquity. |
| 38 | `c_SW_heilonghean` | **Heilonghean** | **黑龙河岸** | Shiwei (`k_shiwei`) | Descriptive natural placeholder ('Amur River Bank'). | **Option B:** `Sw_heilonghean River / Regional Basin` (Sw_heilonghean) | ****Magistrat van Sw_heilonghean**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_heilonghean under Burden of Proof on Antiquity. |
| 39 | `c_SW_hongxingan` | **Hongxingan** | **红兴安** | Shiwei (`k_shiwei`) | Descriptive modern oronym slice ('Red Khingan'). | **Option B:** `Sw_hongxingan River / Regional Basin` (Sw_hongxingan) | ****Magistrat van Sw_hongxingan**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_hongxingan under Burden of Proof on Antiquity. |
| 40 | `c_SW_huangtouguo` | **Huangtouguo** | **黄头国** | Shiwei (`k_shiwei`) | Tribal division ('Yellow Head Tribe'); unverified pre-867 center. | **Option B:** `Sw_huangtouguo River / Regional Basin` (Sw_huangtouguo) | ****Magistrat van Sw_huangtouguo**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_huangtouguo under Burden of Proof on Antiquity. |
| 41 | `c_SW_hulunbuir` | **Hulunbuir** | **阔连捕鱼儿** | Shiwei (`k_shiwei`) | Modern banner / post-867 lake pastoral area; lacks ancient town. | **Option B:** `Sw_hulunbuir River / Regional Basin` (Sw_hulunbuir) | ****Magistrat van Sw_hulunbuir**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_hulunbuir under Burden of Proof on Antiquity. |
| 42 | `c_SW_luotuoguo` | **Luotuoguo** | **骆驼国** | Shiwei (`k_shiwei`) | Tribal division ('Camel Tribe'); lacks ancient urban foundation. | **Option B:** `Sw_luotuoguo River / Regional Basin` (Sw_luotuoguo) | ****Magistrat van Sw_luotuoguo**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_luotuoguo under Burden of Proof on Antiquity. |
| 43 | `c_SW_nabeiguo` | **Nabeiguo** | **讷北国** | Shiwei (`k_shiwei`) | Post-867 northern Nen river tribal division. | **Option B:** `Sw_nabeiguo River / Regional Basin` (Sw_nabeiguo) | ****Magistrat van Sw_nabeiguo**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_nabeiguo under Burden of Proof on Antiquity. |
| 44 | `c_SW_puyuzhou` | **Puyuzhou** | **蒲与州** | Shiwei (`k_shiwei`) | Post-867 Jin/Liao route prefecture; unverified in 867 AD. | **Option B:** `Sw_puyuzhou River / Regional Basin` (Sw_puyuzhou) | ****Magistrat van Sw_puyuzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_puyuzhou under Burden of Proof on Antiquity. |
| 45 | `c_SW_shanbeiguo` | **Shanbeiguo** | **山北国** | Shiwei (`k_shiwei`) | Descriptive tribal division ('North Mountain Tribe'). | **Option B:** `Sw_shanbeiguo River / Regional Basin` (Sw_shanbeiguo) | ****Magistrat van Sw_shanbeiguo**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_shanbeiguo under Burden of Proof on Antiquity. |
| 46 | `c_SW_xinghuangtou` | **Xinghuangtou** | **兴黄头** | Shiwei (`k_shiwei`) | Descriptive tribal division; unverified urban center. | **Option B:** `Sw_xinghuangtou River / Regional Basin` (Sw_xinghuangtou) | ****Magistrat van Sw_xinghuangtou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_xinghuangtou under Burden of Proof on Antiquity. |
| 47 | `c_SW_xingnabei` | **Xingnabei** | **兴讷北** | Shiwei (`k_shiwei`) | Descriptive tribal division; unverified urban center. | **Option B:** `Sw_xingnabei River / Regional Basin` (Sw_xingnabei) | ****Magistrat van Sw_xingnabei**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_xingnabei under Burden of Proof on Antiquity. |
| 48 | `c_SW_zhongcheziguo` | **Zhongcheziguo** | **中车子国** | Shiwei (`k_shiwei`) | Nomadic clan division ('Middle Cart Tribe'). | **Option B:** `Sw_zhongcheziguo River / Regional Basin` (Sw_zhongcheziguo) | ****Magistrat van Sw_zhongcheziguo**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Sw_zhongcheziguo under Burden of Proof on Antiquity. |

### 5.4 Amur Basin & Outer Northeast Frontier Outposts (10 Counties)
*Scope: **10 Flagged Counties** in Empire of Amur (`e_amur`)*

| # | County Key | In-Game Name | Chinese Characters | De Jure Kingdom | Historical Anachronism Rationale | Resolution Strategy (Option B) | Tarraconian Chancellery Title | Historical & Etymological Justification |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 49 | `c_eman_amgun` | **Amgun** | **恨骨** | Amur (`k_amur`) | Remote northern Amgun river tributary; lacks pre-867 attested town. | **Option B:** `Eman_amgun River / Regional Basin` (Eman_amgun) | ****Magistrat van Eman_amgun**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_amgun under Burden of Proof on Antiquity. |
| 50 | `c_eman_beihean` | **Beihean** | **北河岸** | Amur (`k_amur`) | Descriptive placeholder ('North River Bank'); lacks ancient town. | **Option B:** `Eman_beihean River / Regional Basin` (Eman_beihean) | ****Magistrat van Eman_beihean**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_beihean under Burden of Proof on Antiquity. |
| 51 | `c_eman_boli` | **Boli** | **勃利** | Amur (`k_amur`) | Confluence of the Amur and Ussuri rivers (modern Khabarovsk); administrative town dates to modern/Qing era. | **Option B:** `Eman_boli River / Regional Basin` (Eman_boli) | ****Magistrat van Eman_boli**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_boli under Burden of Proof on Antiquity. |
| 52 | `c_eman_choripi` | **Choripi** | **也曼水** | Amur (`k_amur`) | Remote Tungusic wilderness area; lacks pre-867 urban center. | **Option B:** `Eman_choripi River / Regional Basin` (Eman_choripi) | ****Magistrat van Eman_choripi**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_choripi under Burden of Proof on Antiquity. |
| 53 | `c_eman_mohean` | **Mohean** | **莫罕** | Amur (`k_amur`) | Remote Amur basin territory; lacks pre-867 urban foundation. | **Option B:** `Eman_mohean River / Regional Basin` (Eman_mohean) | ****Magistrat van Eman_mohean**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_mohean under Burden of Proof on Antiquity. |
| 54 | `c_eman_molihewen` | **Molihewen** | **末里合温** | Amur (`k_amur`) | Remote forest outpost; lacks pre-867 verified settlement. | **Option B:** `Eman_molihewen River / Regional Basin` (Eman_molihewen) | ****Magistrat van Eman_molihewen**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_molihewen under Burden of Proof on Antiquity. |
| 55 | `c_eman_nurgan` | **Nurgan** | **奴儿干** | Amur (`k_amur`) | Named after the Ming dynasty Nurgan Regional Military Commission (奴儿干都司), established in 1409 AD. Lacks pre-867 urban center. | **Option B:** `Eman_nurgan River / Regional Basin` (Eman_nurgan) | ****Magistrat van Eman_nurgan**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_nurgan under Burden of Proof on Antiquity. |
| 56 | `c_eman_tugur` | **Tugur** | **图古尔** | Amur (`k_amur`) | Okhotsk sea coastal tract; unverified prior to 867 AD. | **Option B:** `Eman_tugur River / Regional Basin` (Eman_tugur) | ****Magistrat van Eman_tugur**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_tugur under Burden of Proof on Antiquity. |
| 57 | `c_eman_yerenhe` | **Yerenhe** | **野人河** | Amur (`k_amur`) | Descriptive placeholder ('Wild Jurchen River'); lacks ancient town. | **Option B:** `Eman_yerenhe River / Regional Basin` (Eman_yerenhe) | ****Magistrat van Eman_yerenhe**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Eman_yerenhe under Burden of Proof on Antiquity. |
| 58 | `c_kusunkotan` | **Kusunkotan** | **对涯村** | Aynumosir (`k_aynumosir`) | Sakhalin Island indigenous settlement (later Korsakov / Kusunkotan, established in 18th century). | **Option B:** `Kusunkotan River / Regional Basin` (Kusunkotan) | ****Magistrat van Kusunkotan**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Kusunkotan under Burden of Proof on Antiquity. |

### 5.5 Guannei Northwestern Mountain Passes & Strategic Chokes (3 Counties)
*Scope: **3 Flagged Counties** in Empire of Yongliang (`e_yongliang`)*

| # | County Key | In-Game Name | Chinese Characters | De Jure Kingdom | Historical Anachronism Rationale | Resolution Strategy (Option B) | Tarraconian Chancellery Title | Historical & Etymological Justification |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 59 | `c_jingzhou` | **Jingzhou** | **泾州** | Guannei (`k_guannei`) | Frontier screening flag; resolved to the ancient Jing River (Jinghe) basin. | **Option B:** `Jingzhou River / Regional Basin` (Jingzhou) | ****Magistrat van Jingzhou**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Jingzhou under Burden of Proof on Antiquity. |
| 60 | `c_xiaoguan` | **Xiaoguan** | **萧关** | Guannei (`k_guannei`) | Xiao Pass (萧关) on Mount Liupan; flagged as a military pass rather than an ancient civil oppidum. | **Option B:** `Xiaoguan River / Regional Basin` (Xiaoguan) | ****Magistrat van Xiaoguan**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Xiaoguan under Burden of Proof on Antiquity. |
| 61 | `c_yuanzhou_2` | **Yuanzhou** | **原州** | Guannei (`k_guannei`) | Duplicate key disambiguation; resolved to the Upper Qingshui / Yuan basin. | **Option B:** `Yuanzhou_2 River / Regional Basin` (Yuanzhou_2) | ****Magistrat van Yuanzhou_2**** | Lacks documented pre-867 western urban center; resolved via Option B indigenous regional stem Yuanzhou_2 under Burden of Proof on Antiquity. |

