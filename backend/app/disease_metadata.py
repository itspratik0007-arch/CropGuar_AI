from typing import Dict, Any, Optional, List

# PlantVillage 38 Classes metadata, reliable treatment notes, precautions, and related Plantopedia references
DISEASE_METADATA: Dict[str, Dict[str, Any]] = {
    "Apple Scab": {
        "crop": "Apple",
        "scientific_name": "Venturia inaequalis",
        "is_healthy": False,
        "description": "Apple scab is a common fungal disease causing dark, olive-green to black velvety spots on leaves and scabby lesions on fruits.",
        "precautions": [
            "Rake and destroy or compost fallen autumn leaves to reduce overwintering fungal spores.",
            "Prune canopy during dormancy to promote air circulation and speed up leaf drying.",
            "Water at the base using drip irrigation rather than overhead sprinklers.",
            "Consult your local agricultural extension service for regional preventive organic or bio-fungicide timings (e.g. copper/sulfur sprays at green tip)."
        ],
        "plantopedia_crop": "Tomato", # closest solanaceae/fruit profile reference or general
        "expert_note": "Early spring infections are primary. If lesions are widespread on fruit, professional pomological diagnostic confirmation is recommended."
    },
    "Apple with Black Rot": {
        "crop": "Apple",
        "scientific_name": "Botryosphaeria obtusa",
        "is_healthy": False,
        "description": "Black rot causes frogeye leaf spots, cankers on limbs, and firm brown rot expanding on maturing fruit with concentric rings.",
        "precautions": [
            "Prune out dead wood, fire blight strikes, and mummified fruit left on trees.",
            "Sanitize pruning shears with 70% isopropyl alcohol between cuts.",
            "Burn or safely discard infected prunings away from orchards.",
            "Maintain overall tree vigor through balanced soil nutrition and weed control."
        ],
        "expert_note": "Fruit rot symptoms can be confused with bitter rot. Laboratory culture or local extension verification is recommended."
    },
    "Cedar Apple Rust": {
        "crop": "Apple",
        "scientific_name": "Gymnosporangium juniperi-virginianae",
        "is_healthy": False,
        "description": "A heteroecious rust fungus requiring both apple trees and Eastern red cedar (Juniperus) to complete its complex two-year life cycle.",
        "precautions": [
            "Where possible, remove nearby wild cedar or juniper trees within a 1-2 mile radius.",
            "Plant rust-resistant apple cultivars when establishing new orchards.",
            "Inspect foliage in late spring for bright orange-yellow circular spots.",
            "Apply approved protective rust fungicides in early spring if high cedar density surrounds the orchard."
        ],
        "expert_note": "Defoliation occurs only under severe epidemics. Rust galls on alternate juniper hosts generate telial horns after spring rains."
    },
    "Healthy Apple": {
        "crop": "Apple",
        "scientific_name": "Malus domestica",
        "is_healthy": True,
        "description": "The foliage appears healthy with normal chlorophyll pigmentation, intact leaf margins, and no visible fungal or bacterial lesioning.",
        "precautions": [
            "Continue regular canopy scouting for aphid, mite, or fungal onset.",
            "Maintain appropriate mulching and weed-free drip zones.",
            "Perform seasonal dormant pruning to preserve light penetration."
        ],
        "expert_note": "A healthy leaf visual prediction indicates absence of visible foliar symptoms in the photographed area."
    },
    "Healthy Blueberry Plant": {
        "crop": "Blueberry",
        "scientific_name": "Vaccinium corymbosum",
        "is_healthy": True,
        "description": "Vibrant foliage with uniform green coloration and healthy vascular development.",
        "precautions": [
            "Maintain acidic soil pH (between 4.5 and 5.5) using pine bark or elemental sulfur.",
            "Ensure regular, shallow watering without waterlogging.",
            "Mulch with acidic organic material like aged sawdust or pine needles."
        ],
        "expert_note": "Monitor soil acidity periodically as alkaline irrigation water can induce iron chlorosis."
    },
    "Cherry with Powdery Mildew": {
        "crop": "Cherry",
        "scientific_name": "Podosphaera clandestina",
        "is_healthy": False,
        "description": "Characterized by white, talcum-like powdery fungal mycelium on young leaves, shoots, and developing cherry fruit.",
        "precautions": [
            "Improve orchard canopy airflow and prune crowded inner branches.",
            "Avoid excessive nitrogen fertilization which stimulates overly succulent susceptible shoots.",
            "Scout new terminal flush during warm, humid, overcast weather.",
            "Consider preventative horticultural oils or potassium bicarbonate early in the season."
        ],
        "expert_note": "Infection thrives in high humidity without requiring free standing water on leaves."
    },
    "Healthy Cherry Plant": {
        "crop": "Cherry",
        "scientific_name": "Prunus avium",
        "is_healthy": True,
        "description": "Healthy cherry foliage with robust vascular venation and no observable sporulation or bacterial spots.",
        "precautions": [
            "Maintain dormant copper hygiene sprays before bud break.",
            "Monitor for fruit fly and aphid vector pressure in early summer.",
            "Keep root zones well-drained."
        ],
        "expert_note": "Good seasonal leaf retention supports bud initiation for next season's crop."
    },
    "Corn (Maize) with Cercospora and Gray Leaf Spot": {
        "crop": "Corn (Maize)",
        "scientific_name": "Cercospora zeae-maydis",
        "is_healthy": False,
        "description": "Gray leaf spot produces narrow, rectangular tan lesions delimited by leaf veins, coalescing under heavy pressure to blight entire leaves.",
        "precautions": [
            "Rotate crops away from corn for at least 1-2 years to allow crop residue to break down.",
            "Select corn hybrids with documented tolerance to Cercospora gray leaf spot.",
            "Incorporate conventional tillage where erosion risk allows, or use residue management.",
            "Scout lower leaves around tasseling and silking."
        ],
        "plantopedia_crop": "Wheat",
        "expert_note": "Disease progress is favored by extended warm, cloudy, high-humidity weather."
    },
    "Corn (Maize) with Common Rust": {
        "crop": "Corn (Maize)",
        "scientific_name": "Puccinia sorghi",
        "is_healthy": False,
        "description": "Foliar disease producing cinnamon-brown powdery pustules (uredinia) scattered across both upper and lower leaf surfaces.",
        "precautions": [
            "Plant resistant commercial or local hybrid maize varieties.",
            "Plant early in the season to evade peak late-summer spore migrations.",
            "Monitor pustule coverage on leaves at and above the ear leaf during pollination.",
            "Consult local agronomic thresholds before considering any fungicide application."
        ],
        "plantopedia_crop": "Wheat",
        "expert_note": "Rust spores are airborne and often travel northward with seasonal weather fronts."
    },
    "Corn (Maize) with Northern Leaf Blight": {
        "crop": "Corn (Maize)",
        "scientific_name": "Exserohilum turcicum",
        "is_healthy": False,
        "description": "Produces distinct long, elliptical cigar-shaped grayish-green to tan lesions that can measure up to 15 cm in length.",
        "precautions": [
            "Use crop rotation and bury infected residue to reduce primary inoculum.",
            "Plant hybrids possessing genetic resistance (e.g. Ht genes).",
            "Scout canopy during cool (18-27°C) wet weather with long dew periods."
        ],
        "plantopedia_crop": "Wheat",
        "expert_note": "Can cause substantial yield loss if upper leaves are infected during early grain fill."
    },
    "Healthy Corn (Maize) Plant": {
        "crop": "Corn (Maize)",
        "scientific_name": "Zea mays",
        "is_healthy": True,
        "description": "Uniform green canopy showing vigorous photosynthetic tissue, clear midrib, and no necrotic lesions.",
        "precautions": [
            "Maintain balanced side-dressed nitrogen and potassium application.",
            "Scout regularly during V6 through R2 reproductive stages.",
            "Ensure weed competition is controlled in early vegetative growth."
        ],
        "plantopedia_crop": "Wheat",
        "expert_note": "Visual leaf health indicates good physiological status for photosynthetic carbohydrate synthesis."
    },
    "Grape with Black Rot": {
        "crop": "Grape",
        "scientific_name": "Guignardia bidwellii",
        "is_healthy": False,
        "description": "Fungal disease causing small circular reddish-brown leaf spots with tiny black pycnidia, and turning berries into shriveled, hard black mummies.",
        "precautions": [
            "Remove and destroy all mummified berries from vines and ground during winter pruning.",
            "Prune and train vines to open up canopy exposure to sunlight and wind.",
            "Apply protectant sprays starting from early shoot development through post-bloom.",
            "Practice prompt summer shoot positioning."
        ],
        "expert_note": "Berry infection occurs primarily from bloom until berries reach 5-8% sugar content."
    },
    "Grape with Esca (Black Measles)": {
        "crop": "Grape",
        "scientific_name": "Phaeomoniella chlamydospora & associated fungi",
        "is_healthy": False,
        "description": "A complex wood-decay disease manifesting as 'tiger-stripe' interveinal chlorosis and necrosis on leaves and dark spot measles on fruit.",
        "precautions": [
            "Avoid pruning wounds during wet weather when fungal airborne spores are abundant.",
            "Apply pruning wound sealants or biological wound protectants.",
            "Mark symptomatic vines in summer for separate late-dormant pruning.",
            "Replace chronically declining trunk wood where possible."
        ],
        "expert_note": "Esca is a vascular trunk disease. Foliar sprays do not cure wood infections; sanitation is essential."
    },
    "Grape with Isariopsis Leaf Spot": {
        "crop": "Grape",
        "scientific_name": "Pseudocercospora cladosporioides",
        "is_healthy": False,
        "description": "Causes irregular brown necrotic spots on grape foliage, often surrounded by faint yellow halos, potentially causing premature defoliation.",
        "precautions": [
            "Maintain trellis air ventilation to accelerate canopy drying after rain.",
            "Rake fallen infected leaves at the end of the harvest season.",
            "Monitor lower and inner canopy leaves as harvest approaches."
        ],
        "expert_note": "More prevalent in warm, humid vineyard microclimates. Confirm with extension if confused with downy mildew."
    },
    "Healthy Grape Plant": {
        "crop": "Grape",
        "scientific_name": "Vitis vinifera",
        "is_healthy": True,
        "description": "Lush, well-developed grape leaf blade with consistent emerald green coloration and healthy vascular margins.",
        "precautions": [
            "Maintain regular canopy thinning and shoot positioning.",
            "Follow integrated pest management (IPM) guidelines for vineyard scouting.",
            "Ensure adequate micronutrient balance (magnesium, iron, and boron)."
        ],
        "expert_note": "Healthy leaf coverage supports optimal bunch shading and cluster sugar accumulation."
    },
    "Orange with Citrus Greening": {
        "crop": "Orange",
        "scientific_name": "Candidatus Liberibacter asiaticus (Huanglongbing / HLB)",
        "is_healthy": False,
        "description": "A devastating systemic bacterial infection transmitted by Asian citrus psyllids, causing blotchy mottle leaf patterns, yellow veins, and small, bitter, lopsided fruit.",
        "precautions": [
            "Control Asian citrus psyllid vector populations using integrated vector management.",
            "Plant only certified disease-free nursery stock from screenhouses.",
            "Scout for asymmetrical, blotchy yellow leaf mottling that crosses leaf veins.",
            "Report suspected detections to your local agricultural authority or plant health board for official PCR testing."
        ],
        "expert_note": "HLB has no established cure once a tree is infected. Immediate PCR laboratory confirmation is strongly recommended."
    },
    "Peach with Bacterial Spot": {
        "crop": "Peach",
        "scientific_name": "Xanthomonas arboricola pv. pruni",
        "is_healthy": False,
        "description": "Bacterial disease causing angular purple-brown spots on leaves that drop out, creating a 'shot-hole' appearance, along with pitted lesions on fruit.",
        "precautions": [
            "Plant cultivars with confirmed genetic tolerance or resistance to Xanthomonas.",
            "Avoid overhead irrigation and windy sandy sites that abrade leaf cuticles.",
            "Apply copper-based sprays during late dormancy and early season according to local university spray guides.",
            "Maintain tree nutrition; avoid both nitrogen deficiency and excessive growth."
        ],
        "expert_note": "Bacterial pathogen enters through natural openings (stomata) and mechanical wounds."
    },
    "Healthy Peach Plant": {
        "crop": "Peach",
        "scientific_name": "Prunus persica",
        "is_healthy": True,
        "description": "Vibrant lanceolate peach leaf without shot-hole perforations, gumming, or chlorotic mottling.",
        "precautions": [
            "Monitor early spring foliage for peach leaf curl and aphids.",
            "Ensure open-center vase pruning to maximize interior sunlight.",
            "Keep soil well-drained to protect shallow fibrous feeder roots."
        ],
        "expert_note": "Consistent canopy scouting supports high stone fruit yield and tree longevity."
    },
    "Bell Pepper with Bacterial Spot": {
        "crop": "Bell Pepper",
        "scientific_name": "Xanthomonas campestris pv. vesicatoria",
        "is_healthy": False,
        "description": "Causes small, water-soaked, circular to irregular dark brown spots on pepper leaves that turn necrotic, leading to defoliation and sunscalded fruit.",
        "precautions": [
            "Purchase certified disease-free, hot-water-treated seed or pathogen-free transplants.",
            "Rotate out of solanaceous crops (peppers, tomatoes, eggplants) for at least 2 years.",
            "Avoid working in fields or harvesting while foliage is wet from rain or dew.",
            "Disinfect stakes, trays, and field equipment before planting."
        ],
        "plantopedia_crop": "Chilli",
        "expert_note": "The pathogen is seed-borne and splash-dispersed. Copper sprays should be used judiciously if copper resistance is known in your region."
    },
    "Healthy Bell Pepper Plant": {
        "crop": "Bell Pepper",
        "scientific_name": "Capsicum annuum",
        "is_healthy": True,
        "description": "Glossy, deep green pepper leaf blade with intact margins and healthy petioles.",
        "precautions": [
            "Maintain steady moisture through drip irrigation to prevent blossom end rot.",
            "Provide light shade netting if high midsummer temperatures exceed 35°C.",
            "Scout for thrips and aphids on leaf undersides."
        ],
        "plantopedia_crop": "Chilli",
        "expert_note": "Strong vegetative growth supports good fruit setting."
    },
    "Potato with Early Blight": {
        "crop": "Potato",
        "scientific_name": "Alternaria solani",
        "is_healthy": False,
        "description": "Fungal disease marked by dark brown to black circular lesions on older leaves, exhibiting characteristic concentric target rings.",
        "precautions": [
            "Practice 3-to-4 year crop rotation away from potatoes, tomatoes, and other nightshades.",
            "Maintain plant vigor with balanced nitrogen; stressed plants are significantly more vulnerable.",
            "Apply mulch to reduce soil splashing onto lower foliage.",
            "Destroy potato vine residue after harvest."
        ],
        "plantopedia_crop": "Potato",
        "expert_note": "Target-ring spots typically begin on lower foliage and advance upward as crop canopy ages."
    },
    "Potato with Late Blight": {
        "crop": "Potato",
        "scientific_name": "Phytophthora infestans",
        "is_healthy": False,
        "description": "A destructive oomycete disease causing large, water-soaked pale green to dark brown lesions that rapidly turn black and necrosis, often with white mildew on leaf undersides.",
        "precautions": [
            "Plant only certified disease-free seed tubers; destroy cull piles immediately.",
            "Scout diligently during cool, wet, overcast weather (temperatures 15-20°C with high humidity).",
            "Eliminate volunteer potato plants in adjacent fields.",
            "Kill vines 2-3 weeks before harvest to prevent tuber contamination at digging."
        ],
        "plantopedia_crop": "Potato",
        "expert_note": "Late blight is the historical cause of the Irish Potato Famine. Rapid community spread occurs under high moisture; prompt expert assessment is strongly recommended."
    },
    "Healthy Potato Plant": {
        "crop": "Potato",
        "scientific_name": "Solanum tuberosum",
        "is_healthy": True,
        "description": "Lush, compound potato leaves showing no necrosis, curling, or water-soaked lesions.",
        "precautions": [
            "Perform periodic earthing up (hilling) to keep developing tubers safely covered from light.",
            "Maintain uniform soil moisture during tuber initiation and bulking.",
            "Scout canopy weekly for Colorado potato beetle and flea beetle damage."
        ],
        "plantopedia_crop": "Potato",
        "expert_note": "Healthy vegetative canopy provides the starch energy required for high-yield tuber development."
    },
    "Healthy Raspberry Plant": {
        "crop": "Raspberry",
        "scientific_name": "Rubus idaeus",
        "is_healthy": True,
        "description": "Pinnately compound raspberry leaf with serrated borders, healthy green color, and clean underside hairs.",
        "precautions": [
            "Provide trellis support to keep canes off moist soil.",
            "Prune out spent floricanes right after summer harvest.",
            "Ensure well-drained sandy loam soil to avert Phytophthora root rot."
        ],
        "expert_note": "Good cane air spacing minimises gray mold (Botrytis) and cane blight."
    },
    "Healthy Soybean Plant": {
        "crop": "Soybean",
        "scientific_name": "Glycine max",
        "is_healthy": True,
        "description": "Trifoliate soybean leaf exhibiting uniform green lamina, intact veins, and no pustules or chlorosis.",
        "precautions": [
            "Scout for soybean cyst nematode and fungal frogeye leaf spot during pod fill.",
            "Ensure proper seed inoculation with Rhizobia for optimal nodulation.",
            "Practice rotating with non-host crops like corn."
        ],
        "plantopedia_crop": "Soybean",
        "expert_note": "Visual canopy health correlates with efficient nitrogen fixation in root nodules."
    },
    "Squash with Powdery Mildew": {
        "crop": "Squash",
        "scientific_name": "Podosphaera xanthii",
        "is_healthy": False,
        "description": "Powdery fungal talc patches on leaf surfaces and petioles, causing leaves to turn chlorotic, curl, wither, and prematurely senesce.",
        "precautions": [
            "Select squash varieties with genetic resistance to powdery mildew.",
            "Space plants generously to promote rapid air circulation between vines.",
            "Plant in full sun; powdery mildew thrives in dense, shaded canopy zones.",
            "Consider preventative treatments like dilute neem oil or potassium bicarbonate early."
        ],
        "expert_note": "Unlike downy mildew, powdery mildew does not require standing dew to germinate and proliferate."
    },
    "Strawberry with Leaf Scorch": {
        "crop": "Strawberry",
        "scientific_name": "Diplocarpon earlianum",
        "is_healthy": False,
        "description": "Fungal infection causing numerous small, irregular dark purple to brownish blotches on upper leaf surfaces that merge to give leaves a scorched appearance.",
        "precautions": [
            "Plant in full sunlight with adequate row spacing and plastic or straw mulch.",
            "Mow and incorporate or destroy old foliage immediately following renovation.",
            "Water using drip lines; avoid late afternoon overhead sprinkler cycles."
        ],
        "expert_note": "Leaf scorch can be distinguished from leaf spot by the absence of white centers in the purplish lesions."
    },
    "Healthy Strawberry Plant": {
        "crop": "Strawberry",
        "scientific_name": "Fragaria × ananassa",
        "is_healthy": True,
        "description": "Trifoliate strawberry leaf showing vibrant emerald green coloration, healthy leaf serration, and clear veins.",
        "precautions": [
            "Renew strawberry mulch annually to keep developing berries off bare earth.",
            "Scout for two-spotted spider mites during hot, dry spells.",
            "Remove runner offshoots if aiming for maximum crown crown berry size."
        ],
        "expert_note": "Healthy leaf crowns support abundant floral bud development."
    },
    "Tomato with Bacterial Spot": {
        "crop": "Tomato",
        "scientific_name": "Xanthomonas perforans / euvesicatoria",
        "is_healthy": False,
        "description": "Bacterial disease producing small, dark, water-soaked spots with yellow halos on leaves, accompanied by raised brown scabs on green tomatoes.",
        "precautions": [
            "Use certified disease-free seeds or hot-water-treated seed stock.",
            "Sanitize tomato stakes, cages, and pruning snips with 10% bleach solution.",
            "Do not prune, tie, or harvest plants while leaves are wet.",
            "Rotate fields with non-solanaceous crops for a minimum of 2 years."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "Rain splashes and wind-driven rain are major dispersal vectors. Seek laboratory extension confirmation if unsure."
    },
    "Tomato with Early Blight": {
        "crop": "Tomato",
        "scientific_name": "Alternaria solani",
        "is_healthy": False,
        "description": "Characterized by brown-black spots with distinct concentric rings (target pattern) surrounded by yellow chlorotic halos on older lower leaves.",
        "precautions": [
            "Prune lowest 2-3 branches above the soil line to prevent splash inoculation.",
            "Apply straw, plastic, or paper mulch over soil around the base of plants.",
            "Water strictly at root level via drip or soaker hoses.",
            "Stake or cage indeterminate vines to keep foliage upright and airy."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "Lesions typically begin on the oldest leaves closest to ground level and move upward."
    },
    "Tomato with Late Blight": {
        "crop": "Tomato",
        "scientific_name": "Phytophthora infestans",
        "is_healthy": False,
        "description": "Fast-moving water-soaked lesions that rapidly expand into large, dark brown, greasy blotches on leaves and stems, with white fuzzy mold on leaf undersides in moist weather.",
        "precautions": [
            "Inspect foliage regularly during cool, foggy, humid, or rainy periods.",
            "Remove and bag severely infected plants immediately; do not leave them in open compost.",
            "Ensure wide plant spacing for rapid morning leaf drying.",
            "Consult regional university pest alerts to monitor regional spore movement."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "Late blight can destroy healthy tomato crops in days under cool, wet conditions. Professional diagnosis is recommended."
    },
    "Tomato with Leaf Mold": {
        "crop": "Tomato",
        "scientific_name": "Passalora fulva (Cladosporium fulvum)",
        "is_healthy": False,
        "description": "Produces pale yellow blotches on the upper surface of leaves that correspond to olive-green to grayish velvety fungal growth on the underside.",
        "precautions": [
            "Increase greenhouse or high-tunnel ventilation and reduce relative humidity below 85%.",
            "Space plants adequately and prune suckers to optimize interior airflow.",
            "Avoid splashing water on upper canopy surfaces."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "Predominantly a problem in greenhouses, poly-tunnels, and warm humid enclosed environments."
    },
    "Tomato with Septoria Leaf Spot": {
        "crop": "Tomato",
        "scientific_name": "Septoria lycopersici",
        "is_healthy": False,
        "description": "Numerous small circular spots (2-3 mm) with dark brown margins and gray or tan centers containing tiny black fruiting bodies (pycnidia).",
        "precautions": [
            "Remove lower infected leaves as soon as first spots appear.",
            "Mulch heavily around tomato bases to create a physical splash barrier.",
            "Rotate crops annually away from tomato, potato, and eggplant.",
            "Disinfect wire cages and wooden stakes at season end."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "Septoria focuses heavily on foliage rather than fruit, but severe leaf loss exposes fruit to sunscald."
    },
    "Tomato with Spider Mites or Two-spotted Spider Mite": {
        "crop": "Tomato",
        "scientific_name": "Tetranychus urticae",
        "is_healthy": False,
        "description": "Mite infestation causing fine pale yellow or white speckling/stippling on leaf surfaces, followed by bronze discoloration and fine webbing under leaves.",
        "precautions": [
            "Spray leaf undersides with a strong jet of water to disrupt mite webs and dislodge colonies.",
            "Encourage beneficial predatory mites (e.g. Phytoseiulus persimilis) in enclosed gardens.",
            "Avoid broad-spectrum chemical insecticides that eradicate natural mite predators.",
            "Apply insecticidal soap or horticultural oil during early morning or evening."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "Spider mites proliferate rapidly under hot, dry, and dusty microclimate conditions."
    },
    "Tomato with Target Spot": {
        "crop": "Tomato",
        "scientific_name": "Corynespora cassiicola",
        "is_healthy": False,
        "description": "Fungal lesions with brown centers and faint concentric circles that can appear on leaves, stems, and fruit, often causing premature defoliation.",
        "precautions": [
            "Maintain generous row spacing to allow sun and air penetration.",
            "Avoid overhead irrigation; keep foliage dry.",
            "Remove crop debris after harvest.",
            "Rotate out of host crops (including tomatoes, peppers, and cucumbers)."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "Symptoms can resemble early blight; laboratory spore examination clarifies exact species."
    },
    "Tomato Yellow Leaf Curl Virus": {
        "crop": "Tomato",
        "scientific_name": "Tomato yellow leaf curl virus (TYLCV)",
        "is_healthy": False,
        "description": "Viral infection transmitted by silverleaf whiteflies (Bemisia tabaci), producing severe leaf stunting, upward cupping/curling, yellowing of margins, and bushy growth with flower abortion.",
        "precautions": [
            "Manage whitefly vectors with fine exclusion insect nets (50-mesh) in nurseries.",
            "Use yellow sticky traps to scout whitefly populations early.",
            "Plant TYLCV-resistant or tolerant tomato hybrids.",
            "Rogue out and destroy infected viral symptomatic plants promptly to prevent vector feeding."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "TYLCV is a begomovirus. Viruses cannot be cured with chemical fungicides; vector management is critical."
    },
    "Tomato Mosaic Virus": {
        "crop": "Tomato",
        "scientific_name": "Tomato mosaic virus (ToMV)",
        "is_healthy": False,
        "description": "Mechanically transmitted virus causing mottled light-and-dark green foliage, leaf distortion (shoestring appearance), and stunted vine vigor.",
        "precautions": [
            "Wash hands with soap and water before handling plants; tobacco users should take extra hygiene steps.",
            "Disinfect pruners and trellising clips between handling individual plants.",
            "Plant certified virus-resistant varieties (labeled with 'T' or 'ToMV').",
            "Remove and safely dispose of infected plants immediately."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "ToMV is extremely stable and easily spread by hands, tools, and clothing through mechanical contact."
    },
    "Healthy Tomato Plant": {
        "crop": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "is_healthy": True,
        "description": "Vibrant, green compound tomato leaves with intact margins, healthy glandular trichomes, and no spots or curling.",
        "precautions": [
            "Maintain consistent soil moisture to prevent blossom end rot and fruit splitting.",
            "Apply mulch around root base and stake vines for upright airflow.",
            "Prune bottom foliage touching the soil to maintain clean lower canopy."
        ],
        "plantopedia_crop": "Tomato",
        "expert_note": "Optimal leaf health allows maximum solar energy conversion for sweet, robust tomato fruit development."
    }
}

SUPPORTED_CROPS: List[str] = [
    "Apple",
    "Blueberry",
    "Cherry",
    "Corn (Maize)",
    "Grape",
    "Orange",
    "Peach",
    "Bell Pepper",
    "Potato",
    "Raspberry",
    "Soybean",
    "Squash",
    "Strawberry",
    "Tomato"
]

def get_disease_info(label: str) -> Dict[str, Any]:
    default_info = {
        "crop": "General Crop",
        "scientific_name": "Botanical assessment needed",
        "is_healthy": "healthy" in label.lower(),
        "description": f"Classification result for {label}.",
        "precautions": [
            "Isolate the plant or affected branch to avoid potential spread.",
            "Consult your local agricultural extension service for on-site diagnostic testing.",
            "Ensure regular irrigation and avoid wetting plant leaves."
        ],
        "expert_note": "Model prediction should be verified by a local agronomist before taking chemical intervention."
    }
    return DISEASE_METADATA.get(label, default_info)
