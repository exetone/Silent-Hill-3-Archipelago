GAME_NAME = "Silent Hill 3"
WORLD_VERSION = "1.0.4"
CLIENT_VERSION = "1.0.4"
PROTOCOL_VERSION = 2
CATALOGUE_VERSION = "2026-10-04-subway-b4"

ITEM_HEALTH_DRINK = "Health Drink"
ITEM_FIRST_AID_KIT = "First-Aid Kit"
ITEM_HANDGUN_BULLETS = "Handgun Bullets"
ITEM_SHOTGUN_SHELLS = "Shotgun Shells"
ITEM_BEEF_JERKY = "Beef Jerky"
ITEM_STUN_GUN_BATTERY = "Stun Gun Battery"
ITEM_RADIO = "Radio"

ITEM_FLASHLIGHT = "Flashlight"
ITEM_TONGS = "Tongs"
ITEM_KEY_TAKEN_WITH_TONGS = "Key Taken with Tongs"
ITEM_OXYDOL = "Oxydol"
ITEM_PORK_LIVER = "Pork Liver"
ITEM_MATCHBOOK = "Matchbook"
ITEM_PENDANT = "Pendant"
ITEM_HOUSE_KEY = "House Key"

ITEM_KNIFE = "Knife"
ITEM_HANDGUN = "Handgun"
ITEM_SHOTGUN = "Shotgun"
ITEM_STEEL_PIPE = "Steel Pipe"
ITEM_KATANA = "Katana"
ITEM_STUN_GUN = "Stun Gun"
ITEM_UNLIMITED_SUBMACHINE_GUN = "Unlimited Submachine Gun"
ITEM_BEAM_SABER = "Beam Saber"
ITEM_FLAMETHROWER = "Flamethrower"
ITEM_GOLD_PIPE = "Gold Pipe"
ITEM_SILVER_PIPE = "Silver Pipe"

# Keep the original two public item IDs stable for compatibility. New items are
# appended in a deterministic block rather than renumbering existing items.
ITEM_NAME_TO_ID = {
    ITEM_HEALTH_DRINK: 0x53483001,
    ITEM_FIRST_AID_KIT: 0x53483002,
    ITEM_HANDGUN_BULLETS: 0x53483003,
    ITEM_SHOTGUN_SHELLS: 0x53483004,
    ITEM_BEEF_JERKY: 0x53483005,
    ITEM_STUN_GUN_BATTERY: 0x53483006,
    ITEM_RADIO: 0x53483007,
    ITEM_FLASHLIGHT: 0x53483008,
    ITEM_TONGS: 0x53483009,
    ITEM_KEY_TAKEN_WITH_TONGS: 0x5348300A,
    ITEM_OXYDOL: 0x5348300B,
    ITEM_PORK_LIVER: 0x5348300C,
    ITEM_MATCHBOOK: 0x5348300D,
    ITEM_PENDANT: 0x5348300E,
    ITEM_HOUSE_KEY: 0x5348300F,
    ITEM_KNIFE: 0x53483010,
    ITEM_HANDGUN: 0x53483011,
    ITEM_SHOTGUN: 0x53483012,
    ITEM_STEEL_PIPE: 0x53483013,
    ITEM_KATANA: 0x53483014,
    ITEM_STUN_GUN: 0x53483015,
    ITEM_UNLIMITED_SUBMACHINE_GUN: 0x53483016,
    ITEM_BEAM_SABER: 0x53483017,
    ITEM_FLAMETHROWER: 0x53483018,
    ITEM_GOLD_PIPE: 0x53483019,
    ITEM_SILVER_PIPE: 0x5348301A,
}

# Receiver mappings use only catalogue-proven normal inventory raw IDs.
# Special game-state rewards such as Heather Beam are deliberately excluded.
ITEM_ID_TO_RAW = {
    ITEM_NAME_TO_ID[ITEM_HEALTH_DRINK]: 18,
    ITEM_NAME_TO_ID[ITEM_FIRST_AID_KIT]: 19,
    ITEM_NAME_TO_ID[ITEM_HANDGUN_BULLETS]: 15,
    ITEM_NAME_TO_ID[ITEM_SHOTGUN_SHELLS]: 16,
    ITEM_NAME_TO_ID[ITEM_BEEF_JERKY]: 21,
    ITEM_NAME_TO_ID[ITEM_STUN_GUN_BATTERY]: 14,
    ITEM_NAME_TO_ID[ITEM_RADIO]: 31,
    ITEM_NAME_TO_ID[ITEM_FLASHLIGHT]: 34,
    ITEM_NAME_TO_ID[ITEM_TONGS]: 37,
    ITEM_NAME_TO_ID[ITEM_KEY_TAKEN_WITH_TONGS]: 38,
    ITEM_NAME_TO_ID[ITEM_OXYDOL]: 57,
    ITEM_NAME_TO_ID[ITEM_PORK_LIVER]: 58,
    ITEM_NAME_TO_ID[ITEM_MATCHBOOK]: 59,
    ITEM_NAME_TO_ID[ITEM_PENDANT]: 36,
    ITEM_NAME_TO_ID[ITEM_HOUSE_KEY]: 35,
    ITEM_NAME_TO_ID[ITEM_KNIFE]: 1,
    ITEM_NAME_TO_ID[ITEM_HANDGUN]: 10,
    ITEM_NAME_TO_ID[ITEM_SHOTGUN]: 11,
    ITEM_NAME_TO_ID[ITEM_STEEL_PIPE]: 2,
    ITEM_NAME_TO_ID[ITEM_KATANA]: 4,
    ITEM_NAME_TO_ID[ITEM_STUN_GUN]: 9,
    ITEM_NAME_TO_ID[ITEM_UNLIMITED_SUBMACHINE_GUN]: 13,
    ITEM_NAME_TO_ID[ITEM_BEAM_SABER]: 5,
    ITEM_NAME_TO_ID[ITEM_FLAMETHROWER]: 6,
    ITEM_NAME_TO_ID[ITEM_GOLD_PIPE]: 7,
    ITEM_NAME_TO_ID[ITEM_SILVER_PIPE]: 8,
}

ITEM_CLASSIFICATION = {
    ITEM_HEALTH_DRINK: "filler",
    ITEM_FIRST_AID_KIT: "filler",
    ITEM_HANDGUN_BULLETS: "filler",
    ITEM_SHOTGUN_SHELLS: "filler",
    ITEM_BEEF_JERKY: "filler",
    ITEM_STUN_GUN_BATTERY: "filler",
    ITEM_RADIO: "filler",
    ITEM_FLASHLIGHT: "progression",
    ITEM_TONGS: "progression",
    ITEM_KEY_TAKEN_WITH_TONGS: "progression",
    ITEM_OXYDOL: "progression",
    ITEM_PORK_LIVER: "progression",
    ITEM_MATCHBOOK: "progression",
    ITEM_PENDANT: "progression",
    ITEM_HOUSE_KEY: "progression",
    ITEM_KNIFE: "useful",
    ITEM_HANDGUN: "useful",
    ITEM_SHOTGUN: "useful",
    ITEM_STEEL_PIPE: "useful",
    ITEM_KATANA: "useful",
    ITEM_STUN_GUN: "useful",
    ITEM_UNLIMITED_SUBMACHINE_GUN: "useful",
    ITEM_BEAM_SABER: "useful",
    ITEM_FLAMETHROWER: "useful",
    ITEM_GOLD_PIPE: "useful",
    ITEM_SILVER_PIPE: "useful",
}

# Stable new IDs: existing public item IDs are never renumbered.
COSTUME_RAW_IDS = {
    "Transform Costume": 82,
    '"Golden Rooster" Shirt': 96,
    '"Royal Flush" Shirt': 97,
    '"Block Head" Shirt': 98,
    '"The Light" Shirt': 99,
    '"God of Thunder" Shirt': 100,
    '"Killer Rabbit" Shirt': 101,
    '"Transience" Shirt': 102,
    '"Onsen" Shirt': 103,
    "\"Don't Touch\" Shirt": 104,
    '"Heather" Shirt': 105,
    '"Zipper" Shirt': 106,
}
for _offset, (_name, _raw) in enumerate(COSTUME_RAW_IDS.items()):
    ITEM_NAME_TO_ID[_name] = 0x5348301B + _offset
    ITEM_ID_TO_RAW[ITEM_NAME_TO_ID[_name]] = _raw
    ITEM_CLASSIFICATION[_name] = "filler"

# Full gathered player-facing catalogue. Starting inventory entries are retained as metadata,
# while the 207 non-start entries are assigned stable location IDs below.
STARTING_ITEM_CATALOGUE = (
    (1, 'Starting Item - House Key', 'House Key', 'Progression', '35', '-'),
    (2, 'Starting Item - Pendant', 'Pendant', 'Progression', '36', 'Live remove/give test passed; corrected owned-state mapping 0x0712CA84 mask 0x10.'),
    (3, 'Starting Item - Transform Costume', 'Transform Costume', 'Filler', '82', '-'),
    (4, 'Starting Item - "Golden Rooster" Shirt', '"Golden Rooster" Shirt', 'Filler', '96', 'Raw ID 96 directly confirmed; lifecycle test passed.'),
    (5, 'Starting Item - "Royal Flush" Shirt', '"Royal Flush" Shirt', 'Filler', '97', 'Confirmed shirt-sequence mapping.'),
    (6, 'Starting Item - "Block Head" Shirt', '"Block Head" Shirt', 'Filler', '98', 'Confirmed shirt-sequence mapping.'),
    (7, 'Starting Item - "The Light" Shirt', '"The Light" Shirt', 'Filler', '99', 'Confirmed shirt-sequence mapping.'),
    (8, 'Starting Item - "God of Thunder" Shirt', '"God of Thunder" Shirt', 'Filler', '100', 'Confirmed shirt-sequence mapping.'),
    (9, 'Starting Item - "Killer Rabbit" Shirt', '"Killer Rabbit" Shirt', 'Filler', '101', 'Confirmed shirt-sequence mapping.'),
    (10, 'Starting Item - "Transience" Shirt', '"Transience" Shirt', 'Filler', '102', 'Confirmed shirt-sequence mapping.'),
    (11, 'Starting Item - "Onsen" Shirt', '"Onsen" Shirt', 'Filler', '103', 'Confirmed shirt-sequence mapping.'),
    (12, 'Starting Item - "Don\'t Touch" Shirt', '"Don\'t Touch" Shirt', 'Filler', '104', 'Confirmed shirt-sequence mapping.'),
    (13, 'Starting Item - "Heather" Shirt', '"Heather" Shirt', 'Filler', '105', 'Confirmed shirt-sequence mapping.'),
    (14, 'Starting Item - "Zipper" Shirt', '"Zipper" Shirt', 'Filler', '106', 'Confirmed shirt-sequence mapping.'),
    (15, 'Starting Item - Heather Beam', 'Heather Beam', 'Useful', '-', 'Vanilla catalogue item; native beam is intended to start disabled in AP and become an AP reward later.'),
    (16, 'Starting Item - Knife', 'Knife', 'Useful', '1', 'Live remove/give test passed; corrected owned-state mapping 0x0712CA80 mask 0x02.'),
)

CHECK_CATALOGUE = (
    {'index': 17, 'name': 'Mall 1F Toilet Fast Travel', 'vanilla': 'Mall 1F Toilet Fast Travel', 'requirements': 'Start', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 18, 'name': 'Mall 1F Alleyway - Unlimited Submachine Gun', 'vanilla': 'Unlimited Submachine Gun', 'requirements': '-', 'classification': 'Useful', 'raw_id': 13, 'persist_flag': None, 'notes': '-'},
    {'index': 19, 'name': 'Mall 1F Boutique - Handgun', 'vanilla': 'Handgun', 'requirements': '-', 'classification': 'Useful', 'raw_id': 10, 'persist_flag': None, 'notes': '-'},
    {'index': 20, 'name': 'Mall 1F Boutique - Handgun Bullets 1', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 909, 'notes': '-'},
    {'index': 21, 'name': 'Mall 1F Boutique - Handgun Bullets 2', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 910, 'notes': '-'},
    {'index': 22, 'name': 'Mall 1F Hallway - Shopping Mall Map', 'vanilla': 'Shopping Mall Map', 'requirements': '-', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Map.'},
    {'index': 23, 'name': 'Mall 2F Bakery - Tongs', 'vanilla': 'Tongs', 'requirements': '-', 'classification': 'Progression', 'raw_id': 37, 'persist_flag': None, 'notes': '-'},
    {'index': 24, 'name': 'Mall 2F Supply Room - Beef Jerky', 'vanilla': 'Beef Jerky', 'requirements': '-', 'classification': 'Filler', 'raw_id': 21, 'persist_flag': 920, 'notes': '-'},
    {'index': 25, 'name': 'Mall 2F Storeroom - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': '-', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 915, 'notes': '-'},
    {'index': 26, 'name': 'Mall 2F Storeroom - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': '-', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 916, 'notes': '-'},
    {'index': 27, 'name': 'Mall 2F Storeroom - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 918, 'notes': '-'},
    {'index': 28, 'name': 'Mall 2F Storeroom - Key Taken with Tongs', 'vanilla': 'Key Taken with Tongs', 'requirements': 'Tongs', 'classification': 'Progression', 'raw_id': 38, 'persist_flag': None, 'notes': '-'},
    {'index': 29, 'name': 'Mall 2F Storeroom Fast Travel', 'vanilla': '2nd Floor Storeroom Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 30, 'name': 'Mall 2F Hallway - Beam Saber', 'vanilla': 'Beam Saber', 'requirements': '-', 'classification': 'Useful', 'raw_id': 5, 'persist_flag': None, 'notes': '-'},
    {'index': 31, 'name': 'Mall 2F Bakery - Flamethrower', 'vanilla': 'Flamethrower', 'requirements': '-', 'classification': 'Useful', 'raw_id': 6, 'persist_flag': None, 'notes': '-'},
    {'index': 32, 'name': 'Mall 2F Bookstore - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': 'Tongs / Key', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 912, 'notes': '-'},
    {'index': 33, 'name': 'Mall 2F Bookstore - Shakespeare Anthology 1', 'vanilla': 'Shakespeare Anthology 1', 'requirements': 'Tongs / Key', 'classification': 'Progression', 'raw_id': 39, 'persist_flag': None, 'notes': 'Five separate progressive checks; no numeric-order logic assumption.'},
    {'index': 34, 'name': 'Mall 2F Bookstore - Shakespeare Anthology 2', 'vanilla': 'Shakespeare Anthology 2', 'requirements': 'Tongs / Key', 'classification': 'Progression', 'raw_id': 40, 'persist_flag': None, 'notes': 'Five separate progressive checks; no numeric-order logic assumption.'},
    {'index': 35, 'name': 'Mall 2F Bookstore - Shakespeare Anthology 3', 'vanilla': 'Shakespeare Anthology 3', 'requirements': 'Tongs / Key', 'classification': 'Progression', 'raw_id': 41, 'persist_flag': None, 'notes': 'Five separate progressive checks; no numeric-order logic assumption.'},
    {'index': 36, 'name': 'Mall 2F Bookstore - Shakespeare Anthology 4', 'vanilla': 'Shakespeare Anthology 4', 'requirements': 'Tongs / Key', 'classification': 'Progression', 'raw_id': 42, 'persist_flag': None, 'notes': 'Five separate progressive checks; no numeric-order logic assumption.'},
    {'index': 37, 'name': 'Mall 2F Bookstore - Shakespeare Anthology 5', 'vanilla': 'Shakespeare Anthology 5', 'requirements': 'Tongs / Key', 'classification': 'Progression', 'raw_id': 43, 'persist_flag': None, 'notes': 'Five separate progressive checks; no numeric-order logic assumption.'},
    {'index': 38, 'name': 'Mall 2F Elevator - Radio', 'vanilla': 'Radio', 'requirements': 'All 5 Shakespeare Anthology Books', 'classification': 'Filler', 'raw_id': 31, 'persist_flag': None, 'notes': '-'},
    {'index': 39, 'name': 'Otherworld Mall 1F First Aid Room Fast Travel', 'vanilla': 'First Aid Room Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': 'Known from established 29-save Fast Travel list.'},
    {'index': 40, 'name': 'Otherworld Mall 1F First Aid Room - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': '-', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 930, 'notes': '-'},
    {'index': 41, 'name': 'Otherworld Mall 1F First Aid Room - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': '-', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 931, 'notes': '-'},
    {'index': 42, 'name': 'Otherworld Mall 1F First Aid Room - Ampoule', 'vanilla': 'Ampoule', 'requirements': '-', 'classification': 'Filler', 'raw_id': 20, 'persist_flag': 934, 'notes': '-'},
    {'index': 43, 'name': 'Otherworld Mall 1F Supply Room - Handgun Bullets 1', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 938, 'notes': '-'},
    {'index': 44, 'name': 'Otherworld Mall 1F Supply Room - Handgun Bullets 2', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 939, 'notes': '-'},
    {'index': 45, 'name': 'Otherworld Mall 1F Supply Room - First-Aid Kit', 'vanilla': 'First-Aid Kit', 'requirements': '-', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': 936, 'notes': '-'},
    {'index': 46, 'name': 'Otherworld Mall 1F Supply Room - Flashlight', 'vanilla': 'Flashlight', 'requirements': '-', 'classification': 'Progression', 'raw_id': 34, 'persist_flag': None, 'notes': '-'},
    {'index': 47, 'name': "Otherworld Mall 1F Ladies' Room - Bleach", 'vanilla': 'Bleach', 'requirements': '-', 'classification': 'Progression', 'raw_id': 44, 'persist_flag': None, 'notes': '-'},
    {'index': 48, 'name': 'Otherworld Mall 1F Boutique - Hanger', 'vanilla': 'Hanger', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 45, 'persist_flag': None, 'notes': '-'},
    {'index': 49, 'name': 'Otherworld Mall 1F Boutique - Bulletproof Vest', 'vanilla': 'Bulletproof Vest', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 22, 'persist_flag': None, 'notes': '-'},
    {'index': 50, 'name': 'Otherworld Mall 2F Walkway Fast Travel', 'vanilla': '2nd Floor Walkway Fast Travel', 'requirements': 'Hanger', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 51, 'name': 'Otherworld Mall 2F Jewellery Store - Walnut', 'vanilla': 'Walnut', 'requirements': '-', 'classification': 'Progression', 'raw_id': 46, 'persist_flag': None, 'notes': '-'},
    {'index': 52, 'name': 'Otherworld Mall 2F Clothes Store - Handgun Bullets 3', 'vanilla': 'Handgun Bullets', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 950, 'notes': '-'},
    {'index': 53, 'name': 'Otherworld Mall 2F Clothes Store - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 952, 'notes': '-'},
    {'index': 54, 'name': 'Otherworld Mall 3F Restaurant - Cooked Key', 'vanilla': 'Cooked Key', 'requirements': '-', 'classification': 'Progression', 'raw_id': 47, 'persist_flag': None, 'notes': '-'},
    {'index': 55, 'name': 'Otherworld Mall 3F Restaurant - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': '-', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 955, 'notes': '-'},
    {'index': 56, 'name': 'Otherworld Mall 3F Restaurant - First-Aid Kit 2', 'vanilla': 'First-Aid Kit', 'requirements': '-', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': 958, 'notes': '-'},
    {'index': 57, 'name': 'Otherworld Mall 2F Café - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': 'Cooked Key', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 947, 'notes': '-'},
    {'index': 58, 'name': 'Otherworld Mall 2F Café - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': 'Cooked Key', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 948, 'notes': '-'},
    {'index': 59, 'name': 'Otherworld Mall 2F Café - Steel Pipe', 'vanilla': 'Steel Pipe', 'requirements': 'Cooked Key', 'classification': 'Useful', 'raw_id': 2, 'persist_flag': None, 'notes': '-'},
    {'index': 60, 'name': 'Otherworld Mall 2F Bakery - Detergent', 'vanilla': 'Detergent', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 48, 'persist_flag': None, 'notes': '-'},
    {'index': 61, 'name': 'Otherworld Mall 2F Supply Room - Handgun Bullets 1', 'vanilla': 'Handgun Bullets', 'requirements': 'Bleach AND Detergent', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 941, 'notes': '-'},
    {'index': 62, 'name': 'Otherworld Mall 2F Supply Room - Handgun Bullets 2', 'vanilla': 'Handgun Bullets', 'requirements': 'Bleach AND Detergent', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 942, 'notes': '-'},
    {'index': 63, 'name': 'Otherworld Mall 2F Supply Room - Handgun Bullets 3', 'vanilla': 'Handgun Bullets', 'requirements': 'Bleach AND Detergent', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 943, 'notes': '-'},
    {'index': 64, 'name': 'Otherworld Mall 2F Supply Room - Beef Jerky', 'vanilla': 'Beef Jerky', 'requirements': 'Bleach AND Detergent', 'classification': 'Filler', 'raw_id': 21, 'persist_flag': 945, 'notes': '-'},
    {'index': 65, 'name': 'Otherworld Mall 2F Sports Shop Fast Travel', 'vanilla': 'Sports Shop Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 66, 'name': 'Otherworld Mall 2F Sports Shop - Moonstone', 'vanilla': 'Moonstone', 'requirements': 'Walnut', 'classification': 'Progression', 'raw_id': 49, 'persist_flag': None, 'notes': '-'},
    {'index': 67, 'name': 'Split Worm', 'vanilla': 'Split Worm', 'requirements': 'Moonstone', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': 'Boss; all bosses are Progression.'},
    {'index': 68, 'name': 'Mall 1F Burger Shop - Handgun Bullets 1', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 924, 'notes': '-'},
    {'index': 69, 'name': 'Mall 1F Burger Shop - Handgun Bullets 2', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 925, 'notes': '-'},
    {'index': 70, 'name': 'Mall 1F Burger Shop - Handgun Bullets 3', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 926, 'notes': '-'},
    {'index': 71, 'name': 'Mall 1F Burger Shop - First-Aid Kit', 'vanilla': 'First-Aid Kit', 'requirements': '-', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': 922, 'notes': '-'},
    {'index': 72, 'name': 'Mall 1F Burger Shop - Beef Jerky', 'vanilla': 'Beef Jerky', 'requirements': '-', 'classification': 'Filler', 'raw_id': 21, 'persist_flag': 928, 'notes': '-'},
    {'index': 73, 'name': 'Mall 1F Burger Shop Fast Travel', 'vanilla': 'Burger Shop Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 74, 'name': 'Subway B1 - Subway Map', 'vanilla': 'Subway Map', 'requirements': '-', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Map.'},
    {'index': 75, 'name': 'Subway B2 Stairs Fast Travel', 'vanilla': 'Subway B2 Stairs Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 76, 'name': 'Subway B5 Platform 4 - Supply', 'vanilla': 'Supply', 'requirements': '-', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'One guaranteed adaptive healing slot.'},
    {'index': 77, 'name': 'Subway Platform 4 - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': 'Excluded from AP checks.'},
    {'index': 78, 'name': 'Subway B4 - Nutcracker', 'vanilla': 'Nutcracker', 'requirements': '-', 'classification': 'Progression', 'raw_id': 50, 'persist_flag': None, 'notes': '-'},
    {'index': 79, 'name': 'Subway B3 Platform 2 Carriage - Shotgun', 'vanilla': 'Shotgun', 'requirements': 'Nutcracker', 'classification': 'Useful', 'raw_id': 11, 'persist_flag': None, 'notes': '-'},
    {'index': 80, 'name': 'Subway B3 Platform 2 Carriage - Shotgun Shells 1', 'vanilla': 'Shotgun Shells', 'requirements': 'Flashlight AND Nutcracker', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': 962, 'notes': '-'},
    {'index': 81, 'name': 'Subway B3 Platform 2 Carriage - Shotgun Shells 2', 'vanilla': 'Shotgun Shells', 'requirements': 'Flashlight AND Nutcracker', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': 963, 'notes': '-'},
    {'index': 82, 'name': 'Subway B5 Train Fast Travel', 'vanilla': 'In the In The Train Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 83, 'name': 'Subway B5 Train - First-Aid Kit', 'vanilla': 'First-Aid Kit', 'requirements': '-', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': 972, 'notes': '-'},
    {'index': 84, 'name': 'Subway B5 Train - Shotgun Shells', 'vanilla': 'Shotgun Shells', 'requirements': '-', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': 973, 'notes': '-'},
    {'index': 85, 'name': 'Subway B5 Train - Handgun Bullets 1', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 974, 'notes': '-'},
    {'index': 86, 'name': 'Subway B5 Train - Handgun Bullets 2', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 975, 'notes': '-'},
    {'index': 87, 'name': 'Underpass Platform (Unknown Station) Fast Travel', 'vanilla': 'Platform (unknown station) Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 88, 'name': 'Underpass Locker Room - Underpass Map', 'vanilla': 'Underpass Map', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Map.'},
    {'index': 89, 'name': 'Underpass Locker Room - Maul', 'vanilla': 'Maul', 'requirements': 'Flashlight', 'classification': 'Useful', 'raw_id': 3, 'persist_flag': None, 'notes': '-'},
    {'index': 90, 'name': 'Underpass Locker Room - Supply', 'vanilla': 'Supply', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Adaptive slot; observed vanilla First-Aid Kit.'},
    {'index': 91, 'name': 'Underpass Wine Rack - Wine Bottle', 'vanilla': 'Wine Bottle', 'requirements': '-', 'classification': 'Progression', 'raw_id': 51, 'persist_flag': None, 'notes': '-'},
    {'index': 92, 'name': 'Underpass - Handgun Bullets 1', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 93, 'name': 'Underpass - Handgun Bullets 2', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 94, 'name': 'Underpass Wine Rack - Beef Jerky', 'vanilla': 'Beef Jerky', 'requirements': '-', 'classification': 'Filler', 'raw_id': 21, 'persist_flag': None, 'notes': '-'},
    {'index': 95, 'name': 'Underpass Dead End - Shotgun Shells', 'vanilla': 'Shotgun Shells', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': None, 'notes': '-'},
    {'index': 96, 'name': 'Underpass Underground Passage Office Fast Travel', 'vanilla': 'Underground Passage Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 97, 'name': 'Underpass Underground Passage Office - Oil-Filled Bottle', 'vanilla': 'Oil-Filled Bottle', 'requirements': 'Wine Bottle', 'classification': 'Progression', 'raw_id': 52, 'persist_flag': None, 'notes': '-'},
    {'index': 98, 'name': 'Underpass Underground Passage Office - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 99, 'name': 'Underpass Underground Passage Office - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 100, 'name': 'Underpass Underground Passage Office - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 101, 'name': 'Underpass Underground Passage Office - Shotgun Shells', 'vanilla': 'Shotgun Shells', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': None, 'notes': '-'},
    {'index': 102, 'name': 'Sewer Dump - Dryer', 'vanilla': 'Dryer', 'requirements': 'Oil-Filled Bottle AND Flashlight', 'classification': 'Progression', 'raw_id': 53, 'persist_flag': None, 'notes': '-'},
    {'index': 103, 'name': 'Sewer Dump - Ampoule', 'vanilla': 'Ampoule', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 20, 'persist_flag': None, 'notes': '-'},
    {'index': 104, 'name': 'Sewer Office Fast Travel', 'vanilla': 'Sewers Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 105, 'name': 'Sewer Office - Health Drink', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 989, 'notes': 'Flag 989 previously claimed; verify.'},
    {'index': 106, 'name': 'Sewer Fairy - Gold Pipe', 'vanilla': 'Gold Pipe', 'requirements': 'Dryer AND Steel Pipe', 'classification': 'Useful', 'raw_id': 7, 'persist_flag': None, 'notes': 'Separate live award; shared flag291 is metadata only. AP failed-answer retry preserves Steel Pipe.'},
    {'index': 107, 'name': 'Sewer Fairy - Silver Pipe', 'vanilla': 'Silver Pipe', 'requirements': 'Dryer AND Steel Pipe', 'classification': 'Useful', 'raw_id': 8, 'persist_flag': None, 'notes': 'Separate live award; shared flag291 is metadata only. AP failed-answer retry preserves Steel Pipe.'},
    {'index': 108, 'name': 'Construction Site Fast Travel', 'vanilla': 'Construction Site Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 109, 'name': 'Construction Site 5F - Health Drink', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 996, 'notes': '-'},
    {'index': 110, 'name': 'Construction Site 5F - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 998, 'notes': '-'},
    {'index': 111, 'name': 'Construction Site 5F Hidden Wall - Silencer', 'vanilla': 'Silencer', 'requirements': 'Flashlight AND any weapon other than Stun Gun or Flamethrower (Knife counts)', 'classification': 'Filler', 'raw_id': 24, 'persist_flag': None, 'notes': 'Any AP item is allowed. Exact pickup record and flag316 verified in the 085120 capture.'},
    {'index': 112, 'name': 'Office 3F Mannequin Room - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 1002, 'notes': '-'},
    {'index': 113, 'name': 'Office 3F Mannequin Room - Shotgun Shells', 'vanilla': 'Shotgun Shells', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': 1004, 'notes': '-'},
    {'index': 114, 'name': 'Office 3F Dance Studio Fast Travel', 'vanilla': 'Dance Hall Office Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 115, 'name': 'Office 3F Dance Studio - Office Building Map', 'vanilla': 'Office Building Map', 'requirements': '-', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Map.'},
    {'index': 116, 'name': 'Office 3F Locker Room - Supply 1', 'vanilla': 'Supply', 'requirements': '-', 'classification': 'Filler', 'raw_id': None, 'persist_flag': 1011, 'notes': 'Adaptive slot.'},
    {'index': 117, 'name': 'Office 3F Locker Room - Supply 2', 'vanilla': 'Supply', 'requirements': '-', 'classification': 'Filler', 'raw_id': None, 'persist_flag': 1012, 'notes': 'Adaptive slot.'},
    {'index': 118, 'name': 'Office 5F Art Storage - Katana', 'vanilla': 'Katana', 'requirements': 'Flashlight', 'classification': 'Useful', 'raw_id': 4, 'persist_flag': None, 'notes': '-'},
    {'index': 119, 'name': 'Office 5F Gallery of Fine Arts Hallway - Screwdriver', 'vanilla': 'Screwdriver', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 54, 'persist_flag': None, 'notes': '-'},
    {'index': 120, 'name': 'Office 5F KMN Auto Parts - Health Drink', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 1018, 'notes': '-'},
    {'index': 121, 'name': 'Office 5F KMN Auto Parts - Jack', 'vanilla': 'Jack', 'requirements': '-', 'classification': 'Progression', 'raw_id': 56, 'persist_flag': None, 'notes': '-'},
    {'index': 122, 'name': 'Office 3F Dance Studio - Rope', 'vanilla': 'Rope', 'requirements': 'Screwdriver', 'classification': 'Progression', 'raw_id': 55, 'persist_flag': None, 'notes': '-'},
    {'index': 123, 'name': 'Office 2F 2nd Floor Hall Fast Travel', 'vanilla': '2nd Floor Hall Fast Travel', 'requirements': 'Rope AND Jack', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 124, 'name': 'Office 2F ECHO Interiors - Beef Jerky', 'vanilla': 'Beef Jerky', 'requirements': '-', 'classification': 'Filler', 'raw_id': 21, 'persist_flag': 1000, 'notes': '-'},
    {'index': 125, 'name': 'Otherworld Office 2F Wheelchair Baby - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 1024, 'notes': 'Explicit exception: no Otherworld prefix.'},
    {'index': 126, 'name': 'Otherworld Office 2F Mental Health Clinic Fast Travel', 'vanilla': 'Mental Clinic Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 127, 'name': 'Otherworld Office 2F Mental Health Clinic - Oxydol', 'vanilla': 'Oxydol', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 57, 'persist_flag': 398, 'notes': 'Stable key SH3:FIXED:FLAG:398.'},
    {'index': 128, 'name': 'Otherworld Office 2F Mental Health Clinic - Supply 1', 'vanilla': 'Supply', 'requirements': 'Flashlight', 'classification': 'UNSET', 'raw_id': None, 'persist_flag': 1026, 'notes': 'Adaptive shelf slot.'},
    {'index': 129, 'name': 'Otherworld Office 2F Mental Health Clinic - Supply 2', 'vanilla': 'Supply', 'requirements': 'Flashlight', 'classification': 'UNSET', 'raw_id': None, 'persist_flag': 1027, 'notes': 'Adaptive shelf slot.'},
    {'index': 130, 'name': 'Otherworld Office 2F Mental Health Clinic - Supply 3', 'vanilla': 'Supply', 'requirements': 'Flashlight', 'classification': 'UNSET', 'raw_id': None, 'persist_flag': 1030, 'notes': 'Adaptive shelf slot.'},
    {'index': 131, 'name': 'Otherworld Office 1F Cafe - Shotgun Shells', 'vanilla': 'Shotgun Shells', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': 1021, 'notes': '-'},
    {'index': 132, 'name': 'Otherworld Office 1F Cafe - Pork Liver', 'vanilla': 'Pork Liver', 'requirements': '-', 'classification': 'Progression', 'raw_id': 58, 'persist_flag': None, 'notes': '-'},
    {'index': 133, 'name': 'Otherworld Office 5F KMN Auto Parts - Handgun Bullets 1', 'vanilla': 'Handgun Bullets', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 1037, 'notes': '-'},
    {'index': 134, 'name': 'Otherworld Office 5F KMN Auto Parts - Handgun Bullets 2', 'vanilla': 'Handgun Bullets', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 1038, 'notes': '-'},
    {'index': 135, 'name': 'Otherworld Office 5F KMN Auto Parts - Matchbook', 'vanilla': 'Matchbook', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 59, 'persist_flag': None, 'notes': '-'},
    {'index': 136, 'name': 'Otherworld Office 5F Gallery Fast Travel', 'vanilla': 'Gallery Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 137, 'name': 'Otherworld Office 4F Imports Bedroom - First-Aid Kit', 'vanilla': 'First-Aid Kit', 'requirements': 'Oxydol AND Pork Liver AND Matchbook', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': 1033, 'notes': '-'},
    {'index': 138, 'name': 'Otherworld Office 4F Imports Bedroom - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': 'Oxydol AND Pork Liver AND Matchbook', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 1035, 'notes': '-'},
    {'index': 139, 'name': 'Otherworld Office 4F Imports Office - Silver Coin', 'vanilla': 'Silver Coin', 'requirements': '-', 'classification': 'Progression', 'raw_id': 60, 'persist_flag': None, 'notes': '-'},
    {'index': 140, 'name': 'Otherworld Office 4F Imports Office - Life Insurance Key', 'vanilla': 'Life Insurance Key', 'requirements': 'Silver Coin', 'classification': 'Progression', 'raw_id': 61, 'persist_flag': None, 'notes': '-'},
    {'index': 141, 'name': 'Daisy Villa Apartments Fast Travel', 'vanilla': 'Apt. Hall Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': 'Walking access requires Life Insurance Key AND Flashlight; direct save access bypasses the entrance.'},
    {'index': 142, 'name': 'Missionary', 'vanilla': 'Missionary', 'requirements': 'House Key', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': 'Boss. Sequence auto-equips Handgun; test/fix if Handgun absent.'},
    {'index': 143, 'name': "Heather's Room - Stun Gun", 'vanilla': 'Stun Gun', 'requirements': '-', 'classification': 'Useful', 'raw_id': 9, 'persist_flag': None, 'notes': '-'},
    {'index': 144, 'name': "Heather's Room - Stun Gun Battery 1", 'vanilla': 'Stun Gun Battery', 'requirements': '-', 'classification': 'Filler', 'raw_id': 14, 'persist_flag': 1040, 'notes': '-'},
    {'index': 145, 'name': "Heather's Room - Stun Gun Battery 2", 'vanilla': 'Stun Gun Battery', 'requirements': '-', 'classification': 'Filler', 'raw_id': 14, 'persist_flag': 1041, 'notes': '-'},
    {'index': 146, 'name': 'Motel Fast Travel', 'vanilla': 'Motel Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 147, 'name': "Daisy Villa Apartments - Dad's Notebook", 'vanilla': "Dad's Notebook", 'requirements': '-', 'classification': 'Filler', 'raw_id': 62, 'persist_flag': None, 'notes': 'Automatic/story grant.'},
    {'index': 148, 'name': 'Daisy Villa Apartments - Silent Hill Map', 'vanilla': 'Silent Hill Map', 'requirements': '-', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Automatic/story grant; map.'},
    {'index': 149, 'name': "Heaven's Night - Shotgun Shells", 'vanilla': 'Shotgun Shells', 'requirements': '-', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': None, 'notes': '-'},
    {'index': 150, 'name': "Heaven's Night - First-Aid Kit", 'vanilla': 'First-Aid Kit', 'requirements': '-', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': None, 'notes': '-'},
    {'index': 151, 'name': "Heaven's Night - Beef Jerky", 'vanilla': 'Beef Jerky', 'requirements': '-', 'classification': 'Filler', 'raw_id': 21, 'persist_flag': None, 'notes': '-'},
    {'index': 152, 'name': 'Hospital 1F Office Fast Travel', 'vanilla': 'Hospital 1F Office Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 153, 'name': 'Hospital 1F Office - Health Drink', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 154, 'name': 'Hospital 1F Office - Hospital Map', 'vanilla': 'Hospital Map', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Map.'},
    {'index': 155, 'name': 'Hospital 1F Lounge Fridge - Health Drink', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 156, 'name': 'Hospital 2F Locker Room - Nail Polish Remover', 'vanilla': 'Nail Polish Remover', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 63, 'persist_flag': None, 'notes': '-'},
    {'index': 157, 'name': 'Hospital 2F Locker Room - Perfume', 'vanilla': 'Perfume', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 158, 'name': 'Hospital 2F M4 - Instant Camera', 'vanilla': 'Instant Camera', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 65, 'persist_flag': None, 'notes': '-'},
    {'index': 159, 'name': 'Hospital 2F M5 - First-Aid Kit', 'vanilla': 'First-Aid Kit', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': None, 'notes': '-'},
    {'index': 160, 'name': 'Hospital 1F C4 - Stairwell Key', 'vanilla': 'Stairwell Key', 'requirements': 'Nail Polish Remover', 'classification': 'Progression', 'raw_id': 64, 'persist_flag': None, 'notes': 'Stairwell Key can bypass carry-over Flashlight requirements caused only by needing the elevator; explicit FL checks remain hard.'},
    {'index': 161, 'name': 'Hospital BF - Submachine Gun Bullets', 'vanilla': 'Submachine Gun Bullets', 'requirements': 'Stairwell Key AND Flashlight', 'classification': 'Filler', 'raw_id': 17, 'persist_flag': None, 'notes': '-'},
    {'index': 162, 'name': 'Hospital BF - Submachine Gun', 'vanilla': 'Submachine Gun', 'requirements': 'Stairwell Key AND Flashlight', 'classification': 'Useful', 'raw_id': 12, 'persist_flag': None, 'notes': '-'},
    {'index': 163, 'name': 'Hospital 3F Store Room Fast Travel', 'vanilla': 'Hospital 3F Store Room Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 164, 'name': 'Hospital 3F Store Room - Stun Gun Battery', 'vanilla': 'Stun Gun Battery', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 14, 'persist_flag': None, 'notes': '-'},
    {'index': 165, 'name': 'Hospital 3F Store Room - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 166, 'name': 'Hospital 3F Store Room - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 167, 'name': 'Hospital RF Roof - Submachine Gun Bullets 1', 'vanilla': 'Submachine Gun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 17, 'persist_flag': None, 'notes': '-'},
    {'index': 168, 'name': 'Hospital RF Roof - Submachine Gun Bullets 2', 'vanilla': 'Submachine Gun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 17, 'persist_flag': None, 'notes': '-'},
    {'index': 169, 'name': 'Hospital 3F S1 - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': 'Flashlight AND Instant Camera', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 170, 'name': 'Hospital 3F S1 - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': 'Flashlight AND Instant Camera', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 171, 'name': 'Hospital 3F Hallway - Beef Jerky', 'vanilla': 'Beef Jerky', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 21, 'persist_flag': None, 'notes': '-'},
    {'index': 172, 'name': 'Otherworld Hospital 3F S03 Fast Travel', 'vanilla': 'Room S03 Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 173, 'name': 'Otherworld Hospital 3F S03 - Handgun Bullets 1', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 174, 'name': 'Otherworld Hospital 3F S03 - Handgun Bullets 2', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 175, 'name': 'Otherworld Hospital B3 Morgue - Cremated Key', 'vanilla': 'Cremated Key', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 66, 'persist_flag': None, 'notes': '-'},
    {'index': 176, 'name': 'Otherworld Hospital 2F Locker Room - Plastic Bag', 'vanilla': 'Plastic Bag', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 67, 'persist_flag': None, 'notes': '-'},
    {'index': 177, 'name': 'Otherworld Hospital 2F Locker Room - Health Drink', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 178, 'name': 'Otherworld Hospital 3F Exam Room 4 - Plastic Bag (With Blood)', 'vanilla': 'Plastic Bag (With Blood)', 'requirements': 'Plastic Bag', 'classification': 'Progression', 'raw_id': 68, 'persist_flag': None, 'notes': 'Plastic Bag / Cremated Key / Exam Room path can be done in any order; do not create an ordering dependency between those branches.'},
    {'index': 179, 'name': 'Otherworld Hospital 1F Exam Room Fast Travel', 'vanilla': 'Exam Room Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 180, 'name': 'Otherworld Hospital 1F Exam Room - Ampoule', 'vanilla': 'Ampoule', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 20, 'persist_flag': None, 'notes': '-'},
    {'index': 181, 'name': 'Otherworld Hospital 1F C4 Fast Travel', 'vanilla': 'Room C4 Fast Travel', 'requirements': 'Cremated Key', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 182, 'name': 'Leonard', 'vanilla': 'Leonard', 'requirements': 'Plastic Bag (With Blood)', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': 'Boss.'},
    {'index': 183, 'name': 'Otherworld Hospital 1F C4 - Talisman', 'vanilla': 'Talisman', 'requirements': 'Leonard', 'classification': 'Filler', 'raw_id': 27, 'persist_flag': None, 'notes': '-'},
    {'index': 184, 'name': 'Amusement Park Souvenir Shop - Healing Supply', 'vanilla': 'First-Aid Kit', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': None, 'notes': '-'},
    {'index': 185, 'name': 'Amusement Park Souvenir Shop - Beef Jerky', 'vanilla': 'Beef Jerky', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 21, 'persist_flag': None, 'notes': '-'},
    {'index': 186, 'name': 'Amusement Park Souvenir Shop - Roller Coaster Key', 'vanilla': 'Roller Coaster Key', 'requirements': 'Flashlight', 'classification': 'Progression', 'raw_id': 69, 'persist_flag': None, 'notes': '-'},
    {'index': 187, 'name': 'Amusement Park Souvenir Shop Fast Travel', 'vanilla': 'Souvenir Shop Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 188, 'name': 'Amusement Park Roller Coaster Control Room - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': 'Roller Coaster Key AND Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 189, 'name': 'Amusement Park Roller Coaster Control Room - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': 'Roller Coaster Key AND Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 190, 'name': 'Amusement Park Haunted Mansion Fast Travel', 'vanilla': 'Haunted Mansion Entrance Fast Travel', 'requirements': 'Roller Coaster Key', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 191, 'name': 'Amusement Park Theater - Chain', 'vanilla': 'Chain', 'requirements': '-', 'classification': 'Progression', 'raw_id': 71, 'persist_flag': None, 'notes': '-'},
    {'index': 192, 'name': 'Amusement Park Theater - Health Drink', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': None, 'notes': '-'},
    {'index': 193, 'name': 'Amusement Park Theater - Shotgun Shells', 'vanilla': 'Shotgun Shells', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': None, 'notes': '-'},
    {'index': 194, 'name': 'Amusement Park Theater - Red Shoe', 'vanilla': 'Red Shoe', 'requirements': 'Theater', 'classification': 'Progression', 'raw_id': 70, 'persist_flag': None, 'notes': '-'},
    {'index': 195, 'name': 'Amusement Park Swing Rocket Control Room - Ammo Supply', 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 196, 'name': "Amusement Park Fortuneteller - Douglas's Notebook", 'vanilla': "Douglas's Notebook", 'requirements': 'Chain', 'classification': 'Filler', 'raw_id': 72, 'persist_flag': None, 'notes': '-'},
    {'index': 197, 'name': 'Amusement Park Fortuneteller - Doll Head', 'vanilla': 'Doll Head', 'requirements': 'Fortuneteller', 'classification': 'Progression', 'raw_id': 73, 'persist_flag': None, 'notes': '-'},
    {'index': 198, 'name': 'Amusement Park Fortune Teller - Ampoule', 'vanilla': 'Ampoule', 'requirements': '-', 'classification': 'Filler', 'raw_id': 20, 'persist_flag': None, 'notes': '-'},
    {'index': 199, 'name': 'Amusement Park Fortuneteller Fast Travel', 'vanilla': 'Fortuneteller Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 200, 'name': 'Amusement Park Happy Carousel Stand - Stun Gun Battery 1', 'vanilla': 'Stun Gun Battery', 'requirements': 'Red Shoe AND Doll Head', 'classification': 'Filler', 'raw_id': 14, 'persist_flag': None, 'notes': '-'},
    {'index': 201, 'name': 'Amusement Park Happy Carousel Stand - Stun Gun Battery 2', 'vanilla': 'Stun Gun Battery', 'requirements': 'Red Shoe AND Doll Head', 'classification': 'Filler', 'raw_id': 14, 'persist_flag': None, 'notes': '-'},
    {'index': 202, 'name': 'Amusement Park Happy Carousel Bench - First-Aid Kit', 'vanilla': 'First-Aid Kit', 'requirements': '-', 'classification': 'Filler', 'raw_id': 19, 'persist_flag': None, 'notes': '-'},
    {'index': 203, 'name': 'Memory of Alessa', 'vanilla': 'Memory of Alessa', 'requirements': 'Red Shoe AND Doll Head', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': 'Boss. End-of-area cutscene also auto-equips Handgun; test/fix if Handgun absent.'},
    {'index': 204, 'name': 'Church 1F Podium - "Eye of the Night" Tarot Card', 'vanilla': '"Eye of the Night" Tarot Card', 'requirements': '-', 'classification': 'Progression', 'raw_id': 74, 'persist_flag': None, 'notes': '-'},
    {'index': 205, 'name': 'Church 1F Chapel Fast Travel', 'vanilla': 'Chapel Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 206, 'name': 'Church 1F - Church Map', 'vanilla': 'Church Map', 'requirements': '-', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Map.'},
    {'index': 207, 'name': "Church 1F Vincent's Room - Cassette Tape", 'vanilla': 'Cassette Tape', 'requirements': '-', 'classification': 'Filler', 'raw_id': 79, 'persist_flag': None, 'notes': '-'},
    {'index': 208, 'name': "Church 1F Vincent's Room - Handgun Bullets 1", 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 209, 'name': "Church 1F Vincent's Room - Handgun Bullets 2", 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 210, 'name': 'Church 1F Belfry Fast Travel', 'vanilla': 'Belfry Fast Travel', 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': '-'},
    {'index': 211, 'name': 'Church 1F Library - "Moon" Tarot Card', 'vanilla': '"Moon" Tarot Card', 'requirements': '-', 'classification': 'Progression', 'raw_id': 75, 'persist_flag': None, 'notes': '-'},
    {'index': 212, 'name': 'Church 1F Library - Book: Otherworld Laws', 'vanilla': 'Book: Otherworld Laws', 'requirements': '-', 'classification': 'Filler', 'raw_id': 76, 'persist_flag': None, 'notes': '-'},
    {'index': 213, 'name': "Church BF Alessa's Room - Brass Key", 'vanilla': 'Brass Key', 'requirements': "Alessa's Room", 'classification': 'Progression', 'raw_id': 78, 'persist_flag': None, 'notes': '-'},
    {'index': 214, 'name': "Church BF Alessa's Room Fast Travel", 'vanilla': "Alessa's Room Fast Travel", 'requirements': '-', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': 'Known from established 29-save Fast Travel list.'},
    {'index': 215, 'name': 'Church BF Alessa\'s Hospital Bed - "Fool" Tarot Card', 'vanilla': '"Fool" Tarot Card', 'requirements': '-', 'classification': 'Progression', 'raw_id': 81, 'persist_flag': None, 'notes': '-'},
    {'index': 216, 'name': "Church BF Alessa's Hospital Bed - Handgun Bullets", 'vanilla': 'Handgun Bullets', 'requirements': '-', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': None, 'notes': '-'},
    {'index': 217, 'name': "Church BF Alessa's Hospital Bed - Ampoule", 'vanilla': 'Ampoule', 'requirements': '-', 'classification': 'Filler', 'raw_id': 20, 'persist_flag': None, 'notes': '-'},
    {'index': 218, 'name': "Church BF Harry's Room - Stun Gun Battery 1", 'vanilla': 'Stun Gun Battery', 'requirements': '-', 'classification': 'Filler', 'raw_id': 14, 'persist_flag': None, 'notes': '-'},
    {'index': 219, 'name': "Church BF Harry's Room - Stun Gun Battery 2", 'vanilla': 'Stun Gun Battery', 'requirements': '-', 'classification': 'Filler', 'raw_id': 14, 'persist_flag': None, 'notes': '-'},
    {'index': 220, 'name': 'Church BF Morgue - "Hanged Man" Tarot Card', 'vanilla': '"Hanged Man" Tarot Card', 'requirements': '-', 'classification': 'Progression', 'raw_id': 77, 'persist_flag': None, 'notes': '-'},
    {'index': 221, 'name': 'Church BF Morgue - Shotgun Shells', 'vanilla': 'Shotgun Shells', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 16, 'persist_flag': None, 'notes': '-'},
    {'index': 222, 'name': 'Church 1F Claudia\'s Room - "High Priestess" Tarot Card', 'vanilla': '"High Priestess" Tarot Card', 'requirements': 'Brass Key', 'classification': 'Progression', 'raw_id': 80, 'persist_flag': None, 'notes': '-'},
    {'index': 223, 'name': 'God', 'vanilla': 'God', 'requirements': 'All 5 Tarot Cards AND Pendant', 'classification': 'Progression', 'raw_id': None, 'persist_flag': None, 'notes': 'Standard end condition / victory check.'},
)

LOCATION_NAME_TO_ID = {
    # Start-of-game AP locations. IDs mirror their gathered catalogue indices.
    # The intervening 0x03..0x0F range remains reserved for the other starting-item
    # catalogue entries if any of them later become real locations.
    'Starting Item - House Key': 0x53485001,
    'Starting Item - Pendant': 0x53485002,
    'Starting Item - Knife': 0x53485010,
    'Mall 1F Toilet Fast Travel': 0x53485011,
    'Mall 1F Alleyway - Unlimited Submachine Gun': 0x53485012,
    'Mall 1F Boutique - Handgun': 0x53485013,
    'Mall 1F Boutique - Handgun Bullets 1': 0x53485014,
    'Mall 1F Boutique - Handgun Bullets 2': 0x53485015,
    'Mall 1F Hallway - Shopping Mall Map': 0x53485016,
    'Mall 2F Bakery - Tongs': 0x53485017,
    'Mall 2F Supply Room - Beef Jerky': 0x53485018,
    'Mall 2F Storeroom - Health Drink 1': 0x53485019,
    'Mall 2F Storeroom - Health Drink 2': 0x5348501A,
    'Mall 2F Storeroom - Handgun Bullets': 0x5348501B,
    'Mall 2F Storeroom - Key Taken with Tongs': 0x5348501C,
    'Mall 2F Storeroom Fast Travel': 0x5348501D,
    'Mall 2F Hallway - Beam Saber': 0x5348501E,
    'Mall 2F Bakery - Flamethrower': 0x5348501F,
    'Mall 2F Bookstore - Handgun Bullets': 0x53485020,
    'Mall 2F Bookstore - Shakespeare Anthology 1': 0x53485021,
    'Mall 2F Bookstore - Shakespeare Anthology 2': 0x53485022,
    'Mall 2F Bookstore - Shakespeare Anthology 3': 0x53485023,
    'Mall 2F Bookstore - Shakespeare Anthology 4': 0x53485024,
    'Mall 2F Bookstore - Shakespeare Anthology 5': 0x53485025,
    'Mall 2F Elevator - Radio': 0x53485026,
    'Otherworld Mall 1F First Aid Room Fast Travel': 0x53485027,
    'Otherworld Mall 1F First Aid Room - Health Drink 1': 0x53485028,
    'Otherworld Mall 1F First Aid Room - Health Drink 2': 0x53485029,
    'Otherworld Mall 1F First Aid Room - Ampoule': 0x5348502A,
    'Otherworld Mall 1F Supply Room - Handgun Bullets 1': 0x5348502B,
    'Otherworld Mall 1F Supply Room - Handgun Bullets 2': 0x5348502C,
    'Otherworld Mall 1F Supply Room - First-Aid Kit': 0x5348502D,
    'Otherworld Mall 1F Supply Room - Flashlight': 0x5348502E,
    "Otherworld Mall 1F Ladies' Room - Bleach": 0x5348502F,
    'Otherworld Mall 1F Boutique - Hanger': 0x53485030,
    'Otherworld Mall 1F Boutique - Bulletproof Vest': 0x53485031,
    'Otherworld Mall 2F Walkway Fast Travel': 0x53485032,
    'Otherworld Mall 2F Jewellery Store - Walnut': 0x53485033,
    'Otherworld Mall 2F Clothes Store - Handgun Bullets 3': 0x53485034,
    'Otherworld Mall 2F Clothes Store - Health Drink 1': 0x53485035,
    'Otherworld Mall 3F Restaurant - Cooked Key': 0x53485036,
    'Otherworld Mall 3F Restaurant - Health Drink 2': 0x53485037,
    'Otherworld Mall 3F Restaurant - First-Aid Kit 2': 0x53485038,
    'Otherworld Mall 2F Café - Health Drink 1': 0x53485039,
    'Otherworld Mall 2F Café - Health Drink 2': 0x5348503A,
    'Otherworld Mall 2F Café - Steel Pipe': 0x5348503B,
    'Otherworld Mall 2F Bakery - Detergent': 0x5348503C,
    'Otherworld Mall 2F Supply Room - Handgun Bullets 1': 0x5348503D,
    'Otherworld Mall 2F Supply Room - Handgun Bullets 2': 0x5348503E,
    'Otherworld Mall 2F Supply Room - Handgun Bullets 3': 0x5348503F,
    'Otherworld Mall 2F Supply Room - Beef Jerky': 0x53485040,
    'Otherworld Mall 2F Sports Shop Fast Travel': 0x53485041,
    'Otherworld Mall 2F Sports Shop - Moonstone': 0x53485042,
    'Split Worm': 0x53485043,
    'Mall 1F Burger Shop - Handgun Bullets 1': 0x53485044,
    'Mall 1F Burger Shop - Handgun Bullets 2': 0x53485045,
    'Mall 1F Burger Shop - Handgun Bullets 3': 0x53485046,
    'Mall 1F Burger Shop - First-Aid Kit': 0x53485047,
    'Mall 1F Burger Shop - Beef Jerky': 0x53485048,
    'Mall 1F Burger Shop Fast Travel': 0x53485049,
    'Subway B1 - Subway Map': 0x5348504A,
    'Subway B2 Stairs Fast Travel': 0x5348504B,
    'Subway B5 Platform 4 - Supply': 0x5348504C,
    'Subway Platform 4 - Handgun Bullets': 0x5348504D,
    'Subway B4 - Nutcracker': 0x5348504E,
    'Subway B3 Platform 2 Carriage - Shotgun': 0x5348504F,
    'Subway B3 Platform 2 Carriage - Shotgun Shells 1': 0x53485050,
    'Subway B3 Platform 2 Carriage - Shotgun Shells 2': 0x53485051,
    'Subway B5 Train Fast Travel': 0x53485052,
    'Subway B5 Train - First-Aid Kit': 0x53485053,
    'Subway B5 Train - Shotgun Shells': 0x53485054,
    'Subway B5 Train - Handgun Bullets 1': 0x53485055,
    'Subway B5 Train - Handgun Bullets 2': 0x53485056,
    'Underpass Platform (Unknown Station) Fast Travel': 0x53485057,
    'Underpass Locker Room - Underpass Map': 0x53485058,
    'Underpass Locker Room - Maul': 0x53485059,
    'Underpass Locker Room - Supply': 0x5348505A,
    'Underpass Wine Rack - Wine Bottle': 0x5348505B,
    'Underpass - Handgun Bullets 1': 0x5348505C,
    'Underpass - Handgun Bullets 2': 0x5348505D,
    'Underpass Wine Rack - Beef Jerky': 0x5348505E,
    'Underpass Dead End - Shotgun Shells': 0x5348505F,
    'Underpass Underground Passage Office Fast Travel': 0x53485060,
    'Underpass Underground Passage Office - Oil-Filled Bottle': 0x53485061,
    'Underpass Underground Passage Office - Health Drink 1': 0x53485062,
    'Underpass Underground Passage Office - Health Drink 2': 0x53485063,
    'Underpass Underground Passage Office - Handgun Bullets': 0x53485064,
    'Underpass Underground Passage Office - Shotgun Shells': 0x53485065,
    'Sewer Dump - Dryer': 0x53485066,
    'Sewer Dump - Ampoule': 0x53485067,
    'Sewer Office Fast Travel': 0x53485068,
    'Sewer Office - Health Drink': 0x53485069,
    'Sewer Fairy - Gold Pipe': 0x5348506A,
    'Sewer Fairy - Silver Pipe': 0x5348506B,
    'Construction Site Fast Travel': 0x5348506C,
    'Construction Site 5F - Health Drink': 0x5348506D,
    'Construction Site 5F - Handgun Bullets': 0x5348506E,
    'Construction Site 5F Hidden Wall - Silencer': 0x5348506F,
    'Office 3F Mannequin Room - Handgun Bullets': 0x53485070,
    'Office 3F Mannequin Room - Shotgun Shells': 0x53485071,
    'Office 3F Dance Studio Fast Travel': 0x53485072,
    'Office 3F Dance Studio - Office Building Map': 0x53485073,
    'Office 3F Locker Room - Supply 1': 0x53485074,
    'Office 3F Locker Room - Supply 2': 0x53485075,
    'Office 5F Art Storage - Katana': 0x53485076,
    'Office 5F Gallery of Fine Arts Hallway - Screwdriver': 0x53485077,
    'Office 5F KMN Auto Parts - Health Drink': 0x53485078,
    'Office 5F KMN Auto Parts - Jack': 0x53485079,
    'Office 3F Dance Studio - Rope': 0x5348507A,
    'Office 2F 2nd Floor Hall Fast Travel': 0x5348507B,
    'Office 2F ECHO Interiors - Beef Jerky': 0x5348507C,
    'Otherworld Office 2F Wheelchair Baby - Handgun Bullets': 0x5348507D,
    'Otherworld Office 2F Mental Health Clinic Fast Travel': 0x5348507E,
    'Otherworld Office 2F Mental Health Clinic - Oxydol': 0x53484004,
    'Otherworld Office 2F Mental Health Clinic - Supply 1': 0x53484001,
    'Otherworld Office 2F Mental Health Clinic - Supply 2': 0x53484002,
    'Otherworld Office 2F Mental Health Clinic - Supply 3': 0x53484003,
    'Otherworld Office 1F Cafe - Shotgun Shells': 0x53485083,
    'Otherworld Office 1F Cafe - Pork Liver': 0x53485084,
    'Otherworld Office 5F KMN Auto Parts - Handgun Bullets 1': 0x53485085,
    'Otherworld Office 5F KMN Auto Parts - Handgun Bullets 2': 0x53485086,
    'Otherworld Office 5F KMN Auto Parts - Matchbook': 0x53485087,
    'Otherworld Office 5F Gallery Fast Travel': 0x53485088,
    'Otherworld Office 4F Imports Bedroom - First-Aid Kit': 0x53485089,
    'Otherworld Office 4F Imports Bedroom - Handgun Bullets': 0x5348508A,
    'Otherworld Office 4F Imports Office - Silver Coin': 0x5348508B,
    'Otherworld Office 4F Imports Office - Life Insurance Key': 0x5348508C,
    'Daisy Villa Apartments Fast Travel': 0x5348508D,
    'Missionary': 0x5348508E,
    "Heather's Room - Stun Gun": 0x5348508F,
    "Heather's Room - Stun Gun Battery 1": 0x53485090,
    "Heather's Room - Stun Gun Battery 2": 0x53485091,
    'Motel Fast Travel': 0x53485092,
    "Daisy Villa Apartments - Dad's Notebook": 0x53485093,
    'Daisy Villa Apartments - Silent Hill Map': 0x53485094,
    "Heaven's Night - Shotgun Shells": 0x53485095,
    "Heaven's Night - First-Aid Kit": 0x53485096,
    "Heaven's Night - Beef Jerky": 0x53485097,
    'Hospital 1F Office Fast Travel': 0x53485098,
    'Hospital 1F Office - Health Drink': 0x53485099,
    'Hospital 1F Office - Hospital Map': 0x5348509A,
    'Hospital 1F Lounge Fridge - Health Drink': 0x5348509B,
    'Hospital 2F Locker Room - Nail Polish Remover': 0x5348509C,
    'Hospital 2F Locker Room - Perfume': 0x5348509D,
    'Hospital 2F M4 - Instant Camera': 0x5348509E,
    'Hospital 2F M5 - First-Aid Kit': 0x5348509F,
    'Hospital 1F C4 - Stairwell Key': 0x534850A0,
    'Hospital BF - Submachine Gun Bullets': 0x534850A1,
    'Hospital BF - Submachine Gun': 0x534850A2,
    'Hospital 3F Store Room Fast Travel': 0x534850A3,
    'Hospital 3F Store Room - Stun Gun Battery': 0x534850A4,
    'Hospital 3F Store Room - Health Drink 1': 0x534850A5,
    'Hospital 3F Store Room - Health Drink 2': 0x534850A6,
    'Hospital RF Roof - Submachine Gun Bullets 1': 0x534850A7,
    'Hospital RF Roof - Submachine Gun Bullets 2': 0x534850A8,
    'Hospital 3F S1 - Health Drink 1': 0x534850A9,
    'Hospital 3F S1 - Health Drink 2': 0x534850AA,
    'Hospital 3F Hallway - Beef Jerky': 0x534850AB,
    'Otherworld Hospital 3F S03 Fast Travel': 0x534850AC,
    'Otherworld Hospital 3F S03 - Handgun Bullets 1': 0x534850AD,
    'Otherworld Hospital 3F S03 - Handgun Bullets 2': 0x534850AE,
    'Otherworld Hospital B3 Morgue - Cremated Key': 0x534850AF,
    'Otherworld Hospital 2F Locker Room - Plastic Bag': 0x534850B0,
    'Otherworld Hospital 2F Locker Room - Health Drink': 0x534850B1,
    'Otherworld Hospital 3F Exam Room 4 - Plastic Bag (With Blood)': 0x534850B2,
    'Otherworld Hospital 1F Exam Room Fast Travel': 0x534850B3,
    'Otherworld Hospital 1F Exam Room - Ampoule': 0x534850B4,
    'Otherworld Hospital 1F C4 Fast Travel': 0x534850B5,
    'Leonard': 0x534850B6,
    'Otherworld Hospital 1F C4 - Talisman': 0x534850B7,
    'Amusement Park Souvenir Shop - Healing Supply': 0x534850B8,
    'Amusement Park Souvenir Shop - Beef Jerky': 0x534850B9,
    'Amusement Park Souvenir Shop - Roller Coaster Key': 0x534850BA,
    'Amusement Park Souvenir Shop Fast Travel': 0x534850BB,
    'Amusement Park Roller Coaster Control Room - Health Drink 1': 0x534850BC,
    'Amusement Park Roller Coaster Control Room - Health Drink 2': 0x534850BD,
    'Amusement Park Haunted Mansion Fast Travel': 0x534850BE,
    'Amusement Park Theater - Chain': 0x534850BF,
    'Amusement Park Theater - Health Drink': 0x534850C0,
    'Amusement Park Theater - Shotgun Shells': 0x534850C1,
    'Amusement Park Theater - Red Shoe': 0x534850C2,
    'Amusement Park Swing Rocket Control Room - Ammo Supply': 0x534850C3,
    "Amusement Park Fortuneteller - Douglas's Notebook": 0x534850C4,
    'Amusement Park Fortuneteller - Doll Head': 0x534850C5,
    'Amusement Park Fortune Teller - Ampoule': 0x534850C6,
    'Amusement Park Fortuneteller Fast Travel': 0x534850C7,
    'Amusement Park Happy Carousel Stand - Stun Gun Battery 1': 0x534850C8,
    'Amusement Park Happy Carousel Stand - Stun Gun Battery 2': 0x534850C9,
    'Amusement Park Happy Carousel Bench - First-Aid Kit': 0x534850CA,
    'Memory of Alessa': 0x534850CB,
    'Church 1F Podium - "Eye of the Night" Tarot Card': 0x534850CC,
    'Church 1F Chapel Fast Travel': 0x534850CD,
    'Church 1F - Church Map': 0x534850CE,
    "Church 1F Vincent's Room - Cassette Tape": 0x534850CF,
    "Church 1F Vincent's Room - Handgun Bullets 1": 0x534850D0,
    "Church 1F Vincent's Room - Handgun Bullets 2": 0x534850D1,
    'Church 1F Belfry Fast Travel': 0x534850D2,
    'Church 1F Library - "Moon" Tarot Card': 0x534850D3,
    'Church 1F Library - Book: Otherworld Laws': 0x534850D4,
    "Church BF Alessa's Room - Brass Key": 0x534850D5,
    "Church BF Alessa's Room Fast Travel": 0x534850D6,
    'Church BF Alessa\'s Hospital Bed - "Fool" Tarot Card': 0x534850D7,
    "Church BF Alessa's Hospital Bed - Handgun Bullets": 0x534850D8,
    "Church BF Alessa's Hospital Bed - Ampoule": 0x534850D9,
    "Church BF Harry's Room - Stun Gun Battery 1": 0x534850DA,
    "Church BF Harry's Room - Stun Gun Battery 2": 0x534850DB,
    'Church BF Morgue - "Hanged Man" Tarot Card': 0x534850DC,
    'Church BF Morgue - Shotgun Shells': 0x534850DD,
    'Church 1F Claudia\'s Room - "High Priestess" Tarot Card': 0x534850DE,
    'God': 0x534850DF,
}

# Three vanilla inventory grants are modeled as unrestricted Archipelago locations.
START_LOCATION_NAMES = (
    'Starting Item - House Key',
    'Starting Item - Pendant',
    'Starting Item - Knife',
)
START_LOCATION_IDS = tuple(LOCATION_NAME_TO_ID[name] for name in START_LOCATION_NAMES)

# Existing four runtime-backed locations keep their original IDs exactly.
LOC_SHELF_SLOT_1 = 'Otherworld Office 2F Mental Health Clinic - Supply 1'
LOC_SHELF_SLOT_2 = 'Otherworld Office 2F Mental Health Clinic - Supply 2'
LOC_SHELF_SLOT_3 = 'Otherworld Office 2F Mental Health Clinic - Supply 3'
LOC_OXYDOL = 'Otherworld Office 2F Mental Health Clinic - Oxydol'

# Runtime-backed physical checks used by the APWorld. Persistent flags identify locations,
# but completion is accepted only from live native pickup/grant trace events; loading a save
# never completes a location merely because its persistent bit is already set.
PERSIST_FLAG_TO_LOCATION_ID = {
    398: LOCATION_NAME_TO_ID['Otherworld Office 2F Mental Health Clinic - Oxydol'],
    909: LOCATION_NAME_TO_ID['Mall 1F Boutique - Handgun Bullets 1'],
    910: LOCATION_NAME_TO_ID['Mall 1F Boutique - Handgun Bullets 2'],
    912: LOCATION_NAME_TO_ID['Mall 2F Bookstore - Handgun Bullets'],
    915: LOCATION_NAME_TO_ID['Mall 2F Storeroom - Health Drink 1'],
    916: LOCATION_NAME_TO_ID['Mall 2F Storeroom - Health Drink 2'],
    918: LOCATION_NAME_TO_ID['Mall 2F Storeroom - Handgun Bullets'],
    920: LOCATION_NAME_TO_ID['Mall 2F Supply Room - Beef Jerky'],
    922: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - First-Aid Kit'],
    924: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - Handgun Bullets 1'],
    925: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - Handgun Bullets 2'],
    926: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - Handgun Bullets 3'],
    928: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - Beef Jerky'],
    930: LOCATION_NAME_TO_ID['Otherworld Mall 1F First Aid Room - Health Drink 1'],
    931: LOCATION_NAME_TO_ID['Otherworld Mall 1F First Aid Room - Health Drink 2'],
    934: LOCATION_NAME_TO_ID['Otherworld Mall 1F First Aid Room - Ampoule'],
    936: LOCATION_NAME_TO_ID['Otherworld Mall 1F Supply Room - First-Aid Kit'],
    938: LOCATION_NAME_TO_ID['Otherworld Mall 1F Supply Room - Handgun Bullets 1'],
    939: LOCATION_NAME_TO_ID['Otherworld Mall 1F Supply Room - Handgun Bullets 2'],
    941: LOCATION_NAME_TO_ID['Otherworld Mall 2F Supply Room - Handgun Bullets 1'],
    942: LOCATION_NAME_TO_ID['Otherworld Mall 2F Supply Room - Handgun Bullets 2'],
    943: LOCATION_NAME_TO_ID['Otherworld Mall 2F Supply Room - Handgun Bullets 3'],
    945: LOCATION_NAME_TO_ID['Otherworld Mall 2F Supply Room - Beef Jerky'],
    947: LOCATION_NAME_TO_ID['Otherworld Mall 2F Café - Health Drink 1'],
    948: LOCATION_NAME_TO_ID['Otherworld Mall 2F Café - Health Drink 2'],
    950: LOCATION_NAME_TO_ID['Otherworld Mall 2F Clothes Store - Handgun Bullets 3'],
    952: LOCATION_NAME_TO_ID['Otherworld Mall 2F Clothes Store - Health Drink 1'],
    955: LOCATION_NAME_TO_ID['Otherworld Mall 3F Restaurant - Health Drink 2'],
    958: LOCATION_NAME_TO_ID['Otherworld Mall 3F Restaurant - First-Aid Kit 2'],
    962: LOCATION_NAME_TO_ID['Subway B3 Platform 2 Carriage - Shotgun Shells 1'],
    963: LOCATION_NAME_TO_ID['Subway B3 Platform 2 Carriage - Shotgun Shells 2'],
    972: LOCATION_NAME_TO_ID['Subway B5 Train - First-Aid Kit'],
    973: LOCATION_NAME_TO_ID['Subway B5 Train - Shotgun Shells'],
    974: LOCATION_NAME_TO_ID['Subway B5 Train - Handgun Bullets 1'],
    975: LOCATION_NAME_TO_ID['Subway B5 Train - Handgun Bullets 2'],
    996: LOCATION_NAME_TO_ID['Construction Site 5F - Health Drink'],
    998: LOCATION_NAME_TO_ID['Construction Site 5F - Handgun Bullets'],
    1000: LOCATION_NAME_TO_ID['Office 2F ECHO Interiors - Beef Jerky'],
    1002: LOCATION_NAME_TO_ID['Office 3F Mannequin Room - Handgun Bullets'],
    1004: LOCATION_NAME_TO_ID['Office 3F Mannequin Room - Shotgun Shells'],
    1011: LOCATION_NAME_TO_ID['Office 3F Locker Room - Supply 1'],
    1012: LOCATION_NAME_TO_ID['Office 3F Locker Room - Supply 2'],
    1018: LOCATION_NAME_TO_ID['Office 5F KMN Auto Parts - Health Drink'],
    1021: LOCATION_NAME_TO_ID['Otherworld Office 1F Cafe - Shotgun Shells'],
    1024: LOCATION_NAME_TO_ID['Otherworld Office 2F Wheelchair Baby - Handgun Bullets'],
    1026: LOCATION_NAME_TO_ID['Otherworld Office 2F Mental Health Clinic - Supply 1'],
    1027: LOCATION_NAME_TO_ID['Otherworld Office 2F Mental Health Clinic - Supply 2'],
    1030: LOCATION_NAME_TO_ID['Otherworld Office 2F Mental Health Clinic - Supply 3'],
    1033: LOCATION_NAME_TO_ID['Otherworld Office 4F Imports Bedroom - First-Aid Kit'],
    1035: LOCATION_NAME_TO_ID['Otherworld Office 4F Imports Bedroom - Handgun Bullets'],
    1037: LOCATION_NAME_TO_ID['Otherworld Office 5F KMN Auto Parts - Handgun Bullets 1'],
    1038: LOCATION_NAME_TO_ID['Otherworld Office 5F KMN Auto Parts - Handgun Bullets 2'],
    1040: LOCATION_NAME_TO_ID["Heather's Room - Stun Gun Battery 1"],
    1041: LOCATION_NAME_TO_ID["Heather's Room - Stun Gun Battery 2"],
}

# Gathered flags include excluded supplies. Only the active mapping above can
# report checks; loaded LOC snapshots are never accepted as acquisition events.
GATHERED_PERSIST_FLAG_TO_LOCATION_ID = {
    398: LOCATION_NAME_TO_ID['Otherworld Office 2F Mental Health Clinic - Oxydol'],
    909: LOCATION_NAME_TO_ID['Mall 1F Boutique - Handgun Bullets 1'],
    910: LOCATION_NAME_TO_ID['Mall 1F Boutique - Handgun Bullets 2'],
    912: LOCATION_NAME_TO_ID['Mall 2F Bookstore - Handgun Bullets'],
    915: LOCATION_NAME_TO_ID['Mall 2F Storeroom - Health Drink 1'],
    916: LOCATION_NAME_TO_ID['Mall 2F Storeroom - Health Drink 2'],
    918: LOCATION_NAME_TO_ID['Mall 2F Storeroom - Handgun Bullets'],
    920: LOCATION_NAME_TO_ID['Mall 2F Supply Room - Beef Jerky'],
    922: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - First-Aid Kit'],
    924: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - Handgun Bullets 1'],
    925: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - Handgun Bullets 2'],
    926: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - Handgun Bullets 3'],
    928: LOCATION_NAME_TO_ID['Mall 1F Burger Shop - Beef Jerky'],
    930: LOCATION_NAME_TO_ID['Otherworld Mall 1F First Aid Room - Health Drink 1'],
    931: LOCATION_NAME_TO_ID['Otherworld Mall 1F First Aid Room - Health Drink 2'],
    934: LOCATION_NAME_TO_ID['Otherworld Mall 1F First Aid Room - Ampoule'],
    936: LOCATION_NAME_TO_ID['Otherworld Mall 1F Supply Room - First-Aid Kit'],
    938: LOCATION_NAME_TO_ID['Otherworld Mall 1F Supply Room - Handgun Bullets 1'],
    939: LOCATION_NAME_TO_ID['Otherworld Mall 1F Supply Room - Handgun Bullets 2'],
    941: LOCATION_NAME_TO_ID['Otherworld Mall 2F Supply Room - Handgun Bullets 1'],
    942: LOCATION_NAME_TO_ID['Otherworld Mall 2F Supply Room - Handgun Bullets 2'],
    943: LOCATION_NAME_TO_ID['Otherworld Mall 2F Supply Room - Handgun Bullets 3'],
    945: LOCATION_NAME_TO_ID['Otherworld Mall 2F Supply Room - Beef Jerky'],
    947: LOCATION_NAME_TO_ID['Otherworld Mall 2F Café - Health Drink 1'],
    948: LOCATION_NAME_TO_ID['Otherworld Mall 2F Café - Health Drink 2'],
    950: LOCATION_NAME_TO_ID['Otherworld Mall 2F Clothes Store - Handgun Bullets 3'],
    952: LOCATION_NAME_TO_ID['Otherworld Mall 2F Clothes Store - Health Drink 1'],
    955: LOCATION_NAME_TO_ID['Otherworld Mall 3F Restaurant - Health Drink 2'],
    958: LOCATION_NAME_TO_ID['Otherworld Mall 3F Restaurant - First-Aid Kit 2'],
    962: LOCATION_NAME_TO_ID['Subway B3 Platform 2 Carriage - Shotgun Shells 1'],
    963: LOCATION_NAME_TO_ID['Subway B3 Platform 2 Carriage - Shotgun Shells 2'],
    972: LOCATION_NAME_TO_ID['Subway B5 Train - First-Aid Kit'],
    973: LOCATION_NAME_TO_ID['Subway B5 Train - Shotgun Shells'],
    974: LOCATION_NAME_TO_ID['Subway B5 Train - Handgun Bullets 1'],
    975: LOCATION_NAME_TO_ID['Subway B5 Train - Handgun Bullets 2'],
    989: LOCATION_NAME_TO_ID['Sewer Office - Health Drink'],
    996: LOCATION_NAME_TO_ID['Construction Site 5F - Health Drink'],
    998: LOCATION_NAME_TO_ID['Construction Site 5F - Handgun Bullets'],
    1000: LOCATION_NAME_TO_ID['Office 2F ECHO Interiors - Beef Jerky'],
    1002: LOCATION_NAME_TO_ID['Office 3F Mannequin Room - Handgun Bullets'],
    1004: LOCATION_NAME_TO_ID['Office 3F Mannequin Room - Shotgun Shells'],
    1011: LOCATION_NAME_TO_ID['Office 3F Locker Room - Supply 1'],
    1012: LOCATION_NAME_TO_ID['Office 3F Locker Room - Supply 2'],
    1018: LOCATION_NAME_TO_ID['Office 5F KMN Auto Parts - Health Drink'],
    1021: LOCATION_NAME_TO_ID['Otherworld Office 1F Cafe - Shotgun Shells'],
    1024: LOCATION_NAME_TO_ID['Otherworld Office 2F Wheelchair Baby - Handgun Bullets'],
    1026: LOCATION_NAME_TO_ID['Otherworld Office 2F Mental Health Clinic - Supply 1'],
    1027: LOCATION_NAME_TO_ID['Otherworld Office 2F Mental Health Clinic - Supply 2'],
    1030: LOCATION_NAME_TO_ID['Otherworld Office 2F Mental Health Clinic - Supply 3'],
    1033: LOCATION_NAME_TO_ID['Otherworld Office 4F Imports Bedroom - First-Aid Kit'],
    1035: LOCATION_NAME_TO_ID['Otherworld Office 4F Imports Bedroom - Handgun Bullets'],
    1037: LOCATION_NAME_TO_ID['Otherworld Office 5F KMN Auto Parts - Handgun Bullets 1'],
    1038: LOCATION_NAME_TO_ID['Otherworld Office 5F KMN Auto Parts - Handgun Bullets 2'],
    1040: LOCATION_NAME_TO_ID["Heather's Room - Stun Gun Battery 1"],
    1041: LOCATION_NAME_TO_ID["Heather's Room - Stun Gun Battery 2"],
}

ACTIVE_LOCATION_NAMES = (
    'Starting Item - House Key',
    'Starting Item - Pendant',
    'Starting Item - Knife',
    'Mall 1F Boutique - Handgun Bullets 1',
    'Mall 1F Boutique - Handgun Bullets 2',
    'Mall 2F Supply Room - Beef Jerky',
    'Mall 2F Storeroom - Health Drink 1',
    'Mall 2F Storeroom - Health Drink 2',
    'Mall 2F Storeroom - Handgun Bullets',
    'Mall 2F Bookstore - Handgun Bullets',
    'Otherworld Mall 1F First Aid Room - Health Drink 1',
    'Otherworld Mall 1F First Aid Room - Health Drink 2',
    'Otherworld Mall 1F First Aid Room - Ampoule',
    'Otherworld Mall 1F Supply Room - Handgun Bullets 1',
    'Otherworld Mall 1F Supply Room - Handgun Bullets 2',
    'Otherworld Mall 1F Supply Room - First-Aid Kit',
    'Otherworld Mall 2F Clothes Store - Handgun Bullets 3',
    'Otherworld Mall 2F Clothes Store - Health Drink 1',
    'Otherworld Mall 3F Restaurant - Health Drink 2',
    'Otherworld Mall 3F Restaurant - First-Aid Kit 2',
    'Otherworld Mall 2F Café - Health Drink 1',
    'Otherworld Mall 2F Café - Health Drink 2',
    'Otherworld Mall 2F Supply Room - Handgun Bullets 1',
    'Otherworld Mall 2F Supply Room - Handgun Bullets 2',
    'Otherworld Mall 2F Supply Room - Handgun Bullets 3',
    'Otherworld Mall 2F Supply Room - Beef Jerky',
    'Mall 1F Burger Shop - Handgun Bullets 1',
    'Mall 1F Burger Shop - Handgun Bullets 2',
    'Mall 1F Burger Shop - Handgun Bullets 3',
    'Mall 1F Burger Shop - First-Aid Kit',
    'Mall 1F Burger Shop - Beef Jerky',
    'Subway B3 Platform 2 Carriage - Shotgun Shells 1',
    'Subway B3 Platform 2 Carriage - Shotgun Shells 2',
    'Subway B5 Train - First-Aid Kit',
    'Subway B5 Train - Shotgun Shells',
    'Subway B5 Train - Handgun Bullets 1',
    'Subway B5 Train - Handgun Bullets 2',
    'Construction Site 5F - Health Drink',
    'Construction Site 5F - Handgun Bullets',
    'Office 3F Mannequin Room - Handgun Bullets',
    'Office 3F Mannequin Room - Shotgun Shells',
    'Office 3F Locker Room - Supply 1',
    'Office 3F Locker Room - Supply 2',
    'Office 5F KMN Auto Parts - Health Drink',
    'Office 2F ECHO Interiors - Beef Jerky',
    'Otherworld Office 2F Wheelchair Baby - Handgun Bullets',
    'Otherworld Office 2F Mental Health Clinic - Oxydol',
    'Otherworld Office 2F Mental Health Clinic - Supply 1',
    'Otherworld Office 2F Mental Health Clinic - Supply 2',
    'Otherworld Office 2F Mental Health Clinic - Supply 3',
    'Otherworld Office 1F Cafe - Shotgun Shells',
    'Otherworld Office 5F KMN Auto Parts - Handgun Bullets 1',
    'Otherworld Office 5F KMN Auto Parts - Handgun Bullets 2',
    'Otherworld Office 4F Imports Bedroom - First-Aid Kit',
    'Otherworld Office 4F Imports Bedroom - Handgun Bullets',
    "Heather's Room - Stun Gun Battery 1",
    "Heather's Room - Stun Gun Battery 2",
)
ACTIVE_LOCATION_NAME_TO_ID = {name: LOCATION_NAME_TO_ID[name] for name in ACTIVE_LOCATION_NAMES}

# Stable menu rows are independent of progressive ordering and native save IDs.
FAST_TRAVEL_MENU_LOCATIONS = ('Mall 1F Toilet Fast Travel', 'Mall 2F Storeroom Fast Travel', 'Mall 1F Burger Shop Fast Travel', 'Otherworld Mall 1F First Aid Room Fast Travel', 'Otherworld Mall 2F Walkway Fast Travel', 'Otherworld Mall 2F Sports Shop Fast Travel', 'Subway B2 Stairs Fast Travel', 'Subway B5 Train Fast Travel', 'Underpass Platform (Unknown Station) Fast Travel', 'Underpass Underground Passage Office Fast Travel', 'Sewer Office Fast Travel', 'Construction Site Fast Travel', 'Office 3F Dance Studio Fast Travel', 'Office 2F 2nd Floor Hall Fast Travel', 'Otherworld Office 2F Mental Health Clinic Fast Travel', 'Otherworld Office 5F Gallery Fast Travel', 'Daisy Villa Apartments Fast Travel', 'Motel Fast Travel', 'Hospital 1F Office Fast Travel', 'Hospital 3F Store Room Fast Travel', 'Otherworld Hospital 1F Exam Room Fast Travel', 'Otherworld Hospital 3F S03 Fast Travel', 'Otherworld Hospital 1F C4 Fast Travel', 'Amusement Park Souvenir Shop Fast Travel', 'Amusement Park Haunted Mansion Fast Travel', 'Amusement Park Fortuneteller Fast Travel', 'Church 1F Chapel Fast Travel', 'Church 1F Belfry Fast Travel', "Church BF Alessa's Room Fast Travel")
FAST_TRAVEL_PROGRESSIVE_ROWS = (0, 1, 3, 4, 5, 2, *range(6, 29))
SAVE_ID_TO_MENU_ROW = {2: 0, 3: 1, 1: 2, 4: 3, 5: 4, 6: 5, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11, 14: 12, 13: 13, 15: 14, 16: 15, 17: 16, 18: 17, 19: 18, 20: 19, 22: 20, 21: 21, 23: 22, 24: 23, 25: 24, 26: 25, 27: 26, 28: 27, 29: 28, 7: 6}
SAVE_ID_TO_LOCATION_ID = {
    native: LOCATION_NAME_TO_ID[FAST_TRAVEL_MENU_LOCATIONS[row]]
    for native, row in SAVE_ID_TO_MENU_ROW.items()
}
ACTIVE_FAST_TRAVEL_ROWS = tuple(row for row in FAST_TRAVEL_PROGRESSIVE_ROWS
                                if row in SAVE_ID_TO_MENU_ROW.values())
SAVE_LOCATION_NAMES = tuple(FAST_TRAVEL_MENU_LOCATIONS[row] for row in ACTIVE_FAST_TRAVEL_ROWS)
ITEM_PROGRESSIVE_FAST_TRAVEL = "Progressive Fast Travel"
# Travel items reuse the established location names; their item IDs occupy a new range.
FAST_TRAVEL_ITEM_TO_ROW = {
    0x53483100 + row: row for row in ACTIVE_FAST_TRAVEL_ROWS
}
for _row in ACTIVE_FAST_TRAVEL_ROWS:
    _name = FAST_TRAVEL_MENU_LOCATIONS[_row]
    ITEM_NAME_TO_ID[_name] = 0x53483100 + _row
    ITEM_CLASSIFICATION[_name] = "progression"
ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_FAST_TRAVEL] = 0x534831FF
ITEM_CLASSIFICATION[ITEM_PROGRESSIVE_FAST_TRAVEL] = "progression"
FAST_TRAVEL_ITEM_IDS = frozenset((*FAST_TRAVEL_ITEM_TO_ROW, 0x534831FF))
VIRTUAL_TRAVEL_RAW_ID = 254 # receipt only; NEVER a game inventory item
SAVE_TRAVEL_PROTOCOL = 2
ACTIVE_LOCATION_NAMES += SAVE_LOCATION_NAMES
ACTIVE_LOCATION_NAME_TO_ID.update({name: LOCATION_NAME_TO_ID[name] for name in SAVE_LOCATION_NAMES})

# Executable-verified live scripted acquisitions. Flags are catalogue metadata;
# the native event handlers, never loaded ownership/flag snapshots, report checks.
SCRIPTED_PROTOCOL = 8
SCRIPTED_CHECKS = ({'name': 'Mall 1F Alleyway - Unlimited Submachine Gun', 'raw': 13, 'flag': 145, 'bit': 0}, {'name': 'Mall 1F Boutique - Handgun', 'raw': 10, 'flag': 116, 'bit': 1}, {'name': 'Mall 2F Bakery - Tongs', 'raw': 37, 'flag': 137, 'bit': 2}, {'name': 'Mall 2F Storeroom - Key Taken with Tongs', 'raw': 38, 'flag': 42, 'bit': 3}, {'name': 'Mall 2F Hallway - Beam Saber', 'raw': 5, 'flag': 121, 'bit': 4}, {'name': 'Mall 2F Bakery - Flamethrower', 'raw': 6, 'flag': 139, 'bit': 5}, {'name': 'Mall 2F Bookstore - Shakespeare Anthology 1', 'raw': 39, 'flag': 127, 'bit': 6}, {'name': 'Mall 2F Bookstore - Shakespeare Anthology 2', 'raw': 40, 'flag': 128, 'bit': 7}, {'name': 'Mall 2F Bookstore - Shakespeare Anthology 3', 'raw': 41, 'flag': 129, 'bit': 8}, {'name': 'Mall 2F Bookstore - Shakespeare Anthology 4', 'raw': 42, 'flag': 130, 'bit': 9}, {'name': 'Mall 2F Bookstore - Shakespeare Anthology 5', 'raw': 43, 'flag': 131, 'bit': 10}, {'name': 'Mall 2F Elevator - Radio', 'raw': 31, 'flag': 199, 'bit': 11}, {'name': 'Otherworld Mall 1F Supply Room - Flashlight', 'raw': 34, 'flag': 170, 'bit': 12}, {'name': "Otherworld Mall 1F Ladies' Room - Bleach", 'raw': 44, 'flag': 173, 'bit': 13}, {'name': 'Otherworld Mall 1F Boutique - Hanger', 'raw': 45, 'flag': 171, 'bit': 14}, {'name': 'Otherworld Mall 1F Boutique - Bulletproof Vest', 'raw': 22, 'flag': 172, 'bit': 15}, {'name': 'Otherworld Mall 2F Jewellery Store - Walnut', 'raw': 46, 'flag': 181, 'bit': 16}, {'name': 'Otherworld Mall 3F Restaurant - Cooked Key', 'raw': 47, 'flag': 193, 'bit': 17}, {'name': 'Otherworld Mall 2F Café - Steel Pipe', 'raw': 2, 'flag': 183, 'bit': 18}, {'name': 'Otherworld Mall 2F Bakery - Detergent', 'raw': 48, 'flag': 184, 'bit': 19}, {'name': 'Otherworld Mall 2F Sports Shop - Moonstone', 'raw': 49, 'flag': 190, 'bit': 20}, {'name': 'Mall 1F Hallway - Shopping Mall Map', 'raw': 253, 'flag': 117, 'bit': 21}, {'name': 'Split Worm', 'raw': None, 'flag': 206, 'bit': 22})
# Defeat stores and the later Talisman grant verified against the boss capture.
SCRIPTED_CHECKS += ({'name': 'Missionary', 'raw': None, 'flag': 454, 'bit': 23}, {'name': 'Leonard', 'raw': None, 'flag': 657, 'bit': 24}, {'name': 'Memory of Alessa', 'raw': None, 'flag': 770, 'bit': 25}, {'name': 'God', 'raw': None, 'flag': 871, 'bit': 26}, {'name': 'Otherworld Hospital 1F C4 - Talisman', 'raw': 27, 'flag': 535, 'bit': 27})

SCRIPTED_CHECKS += ({'name': 'Subway B1 - Subway Map', 'raw': 252, 'flag': 230, 'bit': 28}, {'name': 'Subway B3 Platform 2 Carriage - Shotgun', 'raw': 11, 'flag': 232, 'bit': 29}, {'name': 'Underpass Locker Room - Underpass Map', 'raw': 251, 'flag': 271, 'bit': 30}, {'name': 'Underpass Locker Room - Maul', 'raw': 3, 'flag': 272, 'bit': 31}, {'name': 'Underpass Underground Passage Office - Oil-Filled Bottle', 'raw': 52, 'flag': 275, 'bit': 32}, {'name': 'Sewer Fairy - Gold Pipe', 'raw': 7, 'flag': 291, 'bit': 33}, {'name': 'Sewer Fairy - Silver Pipe', 'raw': 8, 'flag': 291, 'bit': 34}, {'name': 'Construction Site 5F Hidden Wall - Silencer', 'raw': 24, 'flag': 316, 'bit': 35}, {'name': 'Office 5F Art Storage - Katana', 'raw': 4, 'flag': 352, 'bit': 36}, {'name': 'Office 3F Dance Studio - Office Building Map', 'raw': 250, 'flag': 354, 'bit': 37})
SCRIPTED_CHECKS += ({'name': 'Otherworld Office 5F KMN Auto Parts - Matchbook', 'raw': 59, 'flag': 400, 'bit': 38}, {'name': 'Otherworld Office 1F Cafe - Pork Liver', 'raw': 58, 'flag': 396, 'bit': 39}, {'name': 'Otherworld Office 4F Imports Office - Silver Coin', 'raw': 60, 'flag': 399, 'bit': 40}, {'name': 'Otherworld Office 4F Imports Office - Life Insurance Key', 'raw': 61, 'flag': 401, 'bit': 41}, {'name': "Heather's Room - Stun Gun", 'raw': 9, 'flag': 457, 'bit': 42}, {'name': "Daisy Villa Apartments - Dad's Notebook", 'raw': 62, 'flag': 25, 'bit': 43}, {'name': 'Daisy Villa Apartments - Silent Hill Map', 'raw': 249, 'flag': 27, 'bit': 44}, {'name': 'Hospital 1F Office - Hospital Map', 'raw': 248, 'flag': 515, 'bit': 45}, {'name': 'Hospital 1F Lounge Fridge - Health Drink', 'raw': 18, 'flag': 588, 'bit': 46}, {'name': 'Hospital 2F Locker Room - Nail Polish Remover', 'raw': 63, 'flag': 516, 'bit': 47}, {'name': 'Hospital 2F Locker Room - Perfume', 'raw': 26, 'flag': 517, 'bit': 48}, {'name': 'Hospital 2F M4 - Instant Camera', 'raw': 65, 'flag': 518, 'bit': 49}, {'name': 'Hospital 1F C4 - Stairwell Key', 'raw': 64, 'flag': 521, 'bit': 50}, {'name': 'Hospital BF - Submachine Gun', 'raw': 12, 'flag': 519, 'bit': 51}, {'name': 'Subway B4 - Nutcracker', 'raw': 50, 'flag': 231, 'bit': 52}, {'name': 'Underpass Wine Rack - Wine Bottle', 'raw': 51, 'flag': 274, 'bit': 53}, {'name': 'Sewer Dump - Dryer', 'raw': 53, 'flag': 273, 'bit': 54}, {'name': 'Office 5F KMN Auto Parts - Jack', 'raw': 56, 'flag': 353, 'bit': 55}, {'name': 'Office 5F Gallery of Fine Arts Hallway - Screwdriver', 'raw': 54, 'flag': 350, 'bit': 56}, {'name': 'Office 3F Dance Studio - Rope', 'raw': 55, 'flag': 348, 'bit': 57}, {'name': 'Church BF Morgue - "Hanged Man" Tarot Card', 'raw': 77, 'flag': 827, 'bit': 58}, {'name': 'Church 1F Claudia\'s Room - "High Priestess" Tarot Card', 'raw': 80, 'flag': 830, 'bit': 59})
SCRIPTED_CHECKS += ({'name': 'Church 1F - Church Map', 'raw': 247, 'flag': 834, 'bit': 60},)
SCRIPTED_BIT_TO_LOCATION_ID = {r['bit']: LOCATION_NAME_TO_ID[r['name']] for r in SCRIPTED_CHECKS}
# Shared fairy flag291 cannot identify its two separate rewards.
SCRIPTED_FLAG_TO_LOCATION_ID = {r['flag']: LOCATION_NAME_TO_ID[r['name']] for r in SCRIPTED_CHECKS if r['flag'] != 291}
SCRIPTED_LOCATION_NAMES = tuple(r['name'] for r in SCRIPTED_CHECKS)
MALL_MAP_LOCATION = 'Mall 1F Hallway - Shopping Mall Map'
MALL_MAP_ITEM = "Shopping Mall Map"
BOSS_LOCATION = "Split Worm"
MAP_CHECK_ITEMS = {
    MALL_MAP_LOCATION: MALL_MAP_ITEM,
    'Subway B1 - Subway Map': "Subway Map",
    "Underpass Locker Room - Underpass Map": "Underpass Map",
    'Office 3F Dance Studio - Office Building Map': "Office Building Map",
    'Daisy Villa Apartments - Silent Hill Map': "Silent Hill Map",
    'Hospital 1F Office - Hospital Map': "Hospital Map",
    'Church 1F - Church Map': "Church Map",
}
MAP_RAW_TO_FLAG = {253: 1511, 252: 1512, 251: 1513, 250: 1514, 249: 1515, 248: 1516, 247: 1517}
MAP_RAW_ID = 253  # map-ownership flag1511 only; never an inventory raw ID
# Register every normal inventory raw ID already present in the user's catalogue.
# The executable's original grant function uses owned bits for all IDs outside
# 9..21; firearm/consumable quantities are handled by the native receiver.
# Do not invent IDs for Heather Beam or map/event entries with no normal raw ID.
_NEW_INVENTORY_ITEMS = {}
for _record in CHECK_CATALOGUE:
    if _record['name'] == 'Hospital 2F Locker Room - Perfume':
        _record['raw_id'] = 26
    _name, _raw = _record['vanilla'], _record['raw_id']
    if _raw is not None and _name not in ITEM_NAME_TO_ID:
        if _raw in ITEM_ID_TO_RAW.values():
            continue
        _item_id = 0x53483200 + _raw
        ITEM_NAME_TO_ID[_name] = _item_id
        ITEM_ID_TO_RAW[_item_id] = _raw
        ITEM_CLASSIFICATION[_name] = _record['classification'].lower()
        _NEW_INVENTORY_ITEMS[_name] = _raw
ITEM_NAME_TO_ID[MALL_MAP_ITEM] = 0x53483300
ITEM_ID_TO_RAW[ITEM_NAME_TO_ID[MALL_MAP_ITEM]] = MAP_RAW_ID
ITEM_CLASSIFICATION[MALL_MAP_ITEM] = 'filler'
# Only the newly activated mall pickups add these unique rewards to the pool.
# Other later-game normal items can be received/plandoed; their unverified
# locations remain inactive and do not have their vanilla grants suppressed.
MALL_ADDED_POOL_ITEMS = tuple(name for name, raw in _NEW_INVENTORY_ITEMS.items()
                            if raw in {20, 22, *range(39, 50)}) + (MALL_MAP_ITEM,)
for _n, _raw in enumerate((252, 251, 250, 249, 248, 247), 1):
    _name = list(MAP_CHECK_ITEMS.values())[_n]
    ITEM_NAME_TO_ID[_name] = 0x53483300 + _n
    ITEM_ID_TO_RAW[ITEM_NAME_TO_ID[_name]] = _raw
    ITEM_CLASSIFICATION[_name] = 'filler'
ITEM_NAME_TO_ID['Silencer'] = 0x53483218
ITEM_ID_TO_RAW[ITEM_NAME_TO_ID['Silencer']] = 24
ITEM_CLASSIFICATION['Silencer'] = 'filler'
POST_MALL_ADDED_POOL_ITEMS = ('Maul', 'Oil-Filled Bottle', 'Silencer', *list(MAP_CHECK_ITEMS.values())[1:4])
VERIFIED_ADDED_POOL_ITEMS = ('Church Map', 'Silver Coin', 'Life Insurance Key', "Dad's Notebook", 'Nail Polish Remover', 'Perfume', 'Instant Camera', 'Stairwell Key', 'Silent Hill Map', 'Hospital Map', 'Nutcracker', 'Wine Bottle', 'Dryer', 'Jack', 'Screwdriver', 'Rope', '"Hanged Man" Tarot Card', '"High Priestess" Tarot Card')
RECEIVE_RAW_IDS = frozenset(ITEM_ID_TO_RAW.values()) | {VIRTUAL_TRAVEL_RAW_ID}
ACTIVE_LOCATION_NAMES += SCRIPTED_LOCATION_NAMES
ACTIVE_LOCATION_NAME_TO_ID.update({name: LOCATION_NAME_TO_ID[name] for name in SCRIPTED_LOCATION_NAMES})
GATHERED_PERSIST_FLAG_TO_LOCATION_ID.update(SCRIPTED_FLAG_TO_LOCATION_ID)
for _record in CHECK_CATALOGUE:
    if _record['name'] in SCRIPTED_LOCATION_NAMES:
        _record['persist_flag'] = next(r['flag'] for r in SCRIPTED_CHECKS if r['name'] == _record['name'])

def active_locations(boss_checks=False):
    return {name: loc for name, loc in ACTIVE_LOCATION_NAME_TO_ID.items()
            if boss_checks or name not in BOSS_LOCATIONS}

# All five bosses have verified, one-shot live defeat handlers.
BOSS_LOCATIONS = ("Split Worm", "Missionary", "Leonard", "Memory of Alessa", "God")
SUPPORTED_BOSS_LOCATIONS = tuple(name for name in BOSS_LOCATIONS if name in SCRIPTED_LOCATION_NAMES)
BOSS_EVENT_ITEMS = {name: name + " defeated" for name in BOSS_LOCATIONS}
BOSS_GOAL_LOCATION_IDS = {name: LOCATION_NAME_TO_ID[name] for name in BOSS_LOCATIONS}
ITEM_TALISMAN = "Talisman"

def goal_location_ids(win_condition):
    if win_condition == "kill_god":
        return frozenset((BOSS_GOAL_LOCATION_IDS["God"],))
    if win_condition == "kill_all_bosses":
        return frozenset(BOSS_GOAL_LOCATION_IDS.values())
    raise ValueError("Unsupported SH3 win condition")

ITEM_SUBMACHINE_GUN = "Submachine Gun"
ITEM_SUBMACHINE_GUN_BULLETS = "Submachine Gun Bullets"
AMMO_WEAPON_PAIRS = (
    (ITEM_HANDGUN, ITEM_HANDGUN_BULLETS),
    (ITEM_SHOTGUN, ITEM_SHOTGUN_SHELLS),
    (ITEM_SUBMACHINE_GUN, ITEM_SUBMACHINE_GUN_BULLETS),
)
# Counts of pickup slots, not rounds. Source: the user's retained Normal-mode
# checklist. Include listed supplies even when their runtime check is pending.
AMMO_VANILLA_COUNTS = {
    ammo: sum(row['vanilla'] == ammo for row in CHECK_CATALOGUE)
    for _, ammo in AMMO_WEAPON_PAIRS
}
BOSS_WEAPONS = frozenset(name for name, item_id in ITEM_NAME_TO_ID.items()
                         if ITEM_ID_TO_RAW.get(item_id) in {2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13})
for _name in BOSS_WEAPONS:
    ITEM_CLASSIFICATION[_name] = "progression"

def boss_checks_enabled(win_condition, randomize_boss_checks=False):
    # Both goals use the same live boss-check catalogue so server progress
    # and tracker state remain consistent across reconnects and restarts.
    return True

# This active location has a verified live pickup handler. Its local
# wall requirement differs from bosses: Knife counts; Stun Gun and Flamethrower do not.
SILENCER_LOCATION = "Construction Site 5F Hidden Wall - Silencer"
SILENCER_WEAPONS = (BOSS_WEAPONS | frozenset((ITEM_KNIFE,))) - frozenset((ITEM_FLAMETHROWER,))

# Heather Beam is an ability, not a normal inventory bit. The existing virtual
# receipt advances the durable AP index; the game-thread beam controller derives
# ownership from the applied, session-bound AP prefix.
ITEM_HEATHER_BEAM = "Heather Beam"
ITEM_NAME_TO_ID[ITEM_HEATHER_BEAM] = 0x53483400
ITEM_CLASSIFICATION[ITEM_HEATHER_BEAM] = "progression"
ITEM_CLASSIFICATION["Transform Costume"] = "progression"
BOSS_WEAPON_COMBINATIONS = ((ITEM_HEATHER_BEAM, "Transform Costume"),)
ITEM_ID_TO_RAW[ITEM_NAME_TO_ID[ITEM_HEATHER_BEAM]] = VIRTUAL_TRAVEL_RAW_ID

# Virtual effects use the existing no-inventory receipt acknowledgement.
TRAP_NAMES = ("Damage", "Stumble", "Exhaustion", "Blackout", "Radio Static", "False Alarm")
TRAP_ITEM_IDS = {0x53483500 + i: name for i, name in enumerate(TRAP_NAMES)}
for _id, _name in TRAP_ITEM_IDS.items():
    ITEM_NAME_TO_ID[_name + " Trap"] = _id
    ITEM_CLASSIFICATION[_name + " Trap"] = "trap"
    ITEM_ID_TO_RAW[_id] = VIRTUAL_TRAVEL_RAW_ID

# Stable ground slots verified from live pickups and executable spawn filters.
# Existing IDs are retained; the newly catalogued NW subway slot gets index224.
LOCATION_NAME_TO_ID['Subway B5 Platform 3 - Supply'] = 0x534850E0
CHECK_CATALOGUE += ({'index':224,'name':'Subway B5 Platform 3 - Supply',
    'vanilla':'Health Drink','requirements':'Flashlight','classification':'Filler',
    'raw_id':18,'persist_flag':968,'notes':'Guaranteed Normal slot; recorded separately from SW flag969.'},)
VERIFIED_SUPPLIES_127 = ((969, 'Subway B5 Platform 4 - Supply', 18), (968, 'Subway B5 Platform 3 - Supply', 18), (984, 'Underpass Wine Rack - Beef Jerky', 21), (980, 'Underpass Dead End - Shotgun Shells', 16), (985, 'Underpass Underground Passage Office - Health Drink 1', 18), (986, 'Underpass Underground Passage Office - Health Drink 2', 18), (987, 'Underpass Underground Passage Office - Handgun Bullets', 15), (988, 'Underpass Underground Passage Office - Shotgun Shells', 16), (990, 'Sewer Dump - Ampoule', 20), (989, 'Sewer Office - Health Drink', 18), (1043, "Heaven's Night - Shotgun Shells", 16), (1045, "Heaven's Night - First-Aid Kit", 19), (1047, "Heaven's Night - Beef Jerky", 21), (1049, 'Hospital 1F Office - Health Drink', 18), (1061, 'Hospital 2F M5 - First-Aid Kit', 19), (1074, 'Hospital BF - Submachine Gun Bullets', 17), (1076, 'Hospital RF Roof - Submachine Gun Bullets 1', 17), (1077, 'Hospital RF Roof - Submachine Gun Bullets 2', 17), (1063, 'Hospital 3F Store Room - Stun Gun Battery', 14), (1066, 'Hospital 3F Store Room - Health Drink 1', 18), (1067, 'Hospital 3F Store Room - Health Drink 2', 18), (1071, 'Hospital 3F S1 - Health Drink 1', 18), (1072, 'Hospital 3F S1 - Health Drink 2', 18), (1069, 'Hospital 3F Hallway - Beef Jerky', 21))
for _flag, _name, _raw in VERIFIED_SUPPLIES_127:
    PERSIST_FLAG_TO_LOCATION_ID[_flag] = LOCATION_NAME_TO_ID[_name]
    GATHERED_PERSIST_FLAG_TO_LOCATION_ID[_flag] = LOCATION_NAME_TO_ID[_name]
    ACTIVE_LOCATION_NAME_TO_ID[_name] = LOCATION_NAME_TO_ID[_name]
    for _record in CHECK_CATALOGUE:
        if _record['name'] == _name:
            _record['persist_flag'] = _flag
            _record['raw_id'] = _raw
            _record['notes'] = 'Recorded live pickup; guaranteed uncollected ground slot on Normal action difficulty.'
ACTIVE_LOCATION_NAMES += tuple(n for _, n, _ in VERIFIED_SUPPLIES_127)

# Verified Otherworld Hospital pickups and grouped birthday gifts.
LOCATION_NAME_TO_ID['Otherworld Hospital 1F C1 - Birthday Gift 1'] = 0x534850E1
CHECK_CATALOGUE += ({'index': 225, 'name': 'Otherworld Hospital 1F C1 - Birthday Gift 1', 'vanilla': 'Supply', 'requirements': 'Cremated Key / Flashlight', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'First guaranteed birthday gift: Health Drink slot0 or Handgun Bullets slot9; answer telephone to open C1.'},)
LOCATION_NAME_TO_ID['Otherworld Hospital 1F C1 - Birthday Gift 2'] = 0x534850E2
CHECK_CATALOGUE += ({'index': 226, 'name': 'Otherworld Hospital 1F C1 - Birthday Gift 2', 'vanilla': 'Supply', 'requirements': 'Cremated Key / Flashlight', 'classification': 'Filler', 'raw_id': None, 'persist_flag': None, 'notes': 'Second guaranteed birthday gift: Health Drink slot1 or Handgun Bullets slot10.'},)
HOSPITAL_GROUND_129 = ((1101, 'Otherworld Hospital 3F S03 - Handgun Bullets 1', 15), (1102, 'Otherworld Hospital 3F S03 - Handgun Bullets 2', 15), (1099, 'Otherworld Hospital 2F Locker Room - Health Drink', 18), (1097, 'Otherworld Hospital 1F Exam Room - Ampoule', 20), (1079, 'Otherworld Hospital 1F C1 - Birthday Gift 1', 18), (1080, 'Otherworld Hospital 1F C1 - Birthday Gift 2', 18), (1088, 'Otherworld Hospital 1F C1 - Birthday Gift 1', 15), (1089, 'Otherworld Hospital 1F C1 - Birthday Gift 2', 15))
BIRTHDAY_GIFT_FLAGS = (1079, 1080, 1088, 1089)
for _flag, _name, _raw in HOSPITAL_GROUND_129:
    PERSIST_FLAG_TO_LOCATION_ID[_flag] = LOCATION_NAME_TO_ID[_name]
    GATHERED_PERSIST_FLAG_TO_LOCATION_ID[_flag] = LOCATION_NAME_TO_ID[_name]
    if _flag not in BIRTHDAY_GIFT_FLAGS:
        for _record in CHECK_CATALOGUE:
            if _record['name'] == _name:
                _record['persist_flag'] = _flag
                _record['notes'] = 'Recorded live pickup; guaranteed Normal ground slot.'
SCRIPTED_CHECKS += ({'name': 'Otherworld Hospital B3 Morgue - Cremated Key', 'raw': 66, 'flag': 689, 'bit': 61}, {'name': 'Otherworld Hospital 2F Locker Room - Plastic Bag', 'raw': 67, 'flag': 679, 'bit': 62}, {'name': 'Otherworld Hospital 3F Exam Room 4 - Plastic Bag (With Blood)', 'raw': 68, 'flag': 3167, 'bit': 63})
SCRIPTED_BIT_TO_LOCATION_ID = {r['bit']: LOCATION_NAME_TO_ID[r['name']] for r in SCRIPTED_CHECKS}
SCRIPTED_FLAG_TO_LOCATION_ID = {r['flag']: LOCATION_NAME_TO_ID[r['name']] for r in SCRIPTED_CHECKS if r['flag'] != 291}
SCRIPTED_LOCATION_NAMES = tuple(r['name'] for r in SCRIPTED_CHECKS)
GATHERED_PERSIST_FLAG_TO_LOCATION_ID.update(SCRIPTED_FLAG_TO_LOCATION_ID)
ACTIVE_LOCATION_NAMES += ('Otherworld Hospital 3F S03 - Handgun Bullets 1', 'Otherworld Hospital 3F S03 - Handgun Bullets 2', 'Otherworld Hospital 2F Locker Room - Health Drink', 'Otherworld Hospital 1F Exam Room - Ampoule', 'Otherworld Hospital 1F C1 - Birthday Gift 1', 'Otherworld Hospital B3 Morgue - Cremated Key', 'Otherworld Hospital 2F Locker Room - Plastic Bag', 'Otherworld Hospital 3F Exam Room 4 - Plastic Bag (With Blood)')
ACTIVE_LOCATION_NAME_TO_ID.update({n:LOCATION_NAME_TO_ID[n] for n in ('Otherworld Hospital 3F S03 - Handgun Bullets 1', 'Otherworld Hospital 3F S03 - Handgun Bullets 2', 'Otherworld Hospital 2F Locker Room - Health Drink', 'Otherworld Hospital 1F Exam Room - Ampoule', 'Otherworld Hospital 1F C1 - Birthday Gift 1', 'Otherworld Hospital B3 Morgue - Cremated Key', 'Otherworld Hospital 2F Locker Room - Plastic Bag', 'Otherworld Hospital 3F Exam Room 4 - Plastic Bag (With Blood)')})
VERIFIED_ADDED_POOL_ITEMS += ('Cremated Key', 'Plastic Bag', 'Plastic Bag (With Blood)')
next(r for r in CHECK_CATALOGUE if r['name']=='Otherworld Hospital B3 Morgue - Cremated Key')['persist_flag']=689
next(r for r in CHECK_CATALOGUE if r['name']=='Otherworld Hospital 2F Locker Room - Plastic Bag')['persist_flag']=679
next(r for r in CHECK_CATALOGUE if r['name']=='Otherworld Hospital 3F Exam Room 4 - Plastic Bag (With Blood)')['persist_flag']=3167

ACTIVE_LOCATION_NAMES += ('Otherworld Hospital 1F C1 - Birthday Gift 2',)
ACTIVE_LOCATION_NAME_TO_ID['Otherworld Hospital 1F C1 - Birthday Gift 2'] = LOCATION_NAME_TO_ID['Otherworld Hospital 1F C1 - Birthday Gift 2']

# Verified late-game pickups; scripted protocol7 supports128 event bits.
LATE_GROUND_131 = ((1112, 'Amusement Park Roller Coaster Control Room - Health Drink 1'), (1113, 'Amusement Park Roller Coaster Control Room - Health Drink 2'), (1116, 'Amusement Park Theater - Health Drink'), (1117, 'Amusement Park Theater - Shotgun Shells'), (1120, 'Amusement Park Happy Carousel Stand - Stun Gun Battery 1'), (1121, 'Amusement Park Happy Carousel Stand - Stun Gun Battery 2'), (1122, 'Amusement Park Happy Carousel Bench - First-Aid Kit'), (1132, "Church BF Harry's Room - Stun Gun Battery 1"), (1133, "Church BF Harry's Room - Stun Gun Battery 2"), (1135, 'Church BF Morgue - Shotgun Shells'), (1143, "Church BF Alessa's Hospital Bed - Handgun Bullets"), (1139, "Church BF Alessa's Hospital Bed - Ampoule"))
for _flag, _name in LATE_GROUND_131:
    PERSIST_FLAG_TO_LOCATION_ID[_flag] = LOCATION_NAME_TO_ID[_name]
    GATHERED_PERSIST_FLAG_TO_LOCATION_ID[_flag] = LOCATION_NAME_TO_ID[_name]
    next(r for r in CHECK_CATALOGUE if r['name']==_name)['persist_flag'] = _flag
SCRIPTED_CHECKS += ({'name': 'Amusement Park Souvenir Shop - Roller Coaster Key', 'raw': 69, 'flag': 747, 'bit': 64}, {'name': 'Amusement Park Theater - Red Shoe', 'raw': 70, 'flag': 751, 'bit': 65}, {'name': 'Amusement Park Theater - Chain', 'raw': 71, 'flag': 752, 'bit': 66}, {'name': "Amusement Park Fortuneteller - Douglas's Notebook", 'raw': 72, 'flag': 754, 'bit': 67}, {'name': 'Amusement Park Fortuneteller - Doll Head', 'raw': 73, 'flag': 753, 'bit': 68}, {'name': 'Church 1F Podium - "Eye of the Night" Tarot Card', 'raw': 74, 'flag': 813, 'bit': 69}, {'name': 'Church 1F Library - "Moon" Tarot Card', 'raw': 75, 'flag': 825, 'bit': 70}, {'name': 'Church 1F Library - Book: Otherworld Laws', 'raw': 76, 'flag': 826, 'bit': 71}, {'name': 'Church BF Alessa\'s Hospital Bed - "Fool" Tarot Card', 'raw': 81, 'flag': 831, 'bit': 72}, {'name': "Church BF Alessa's Room - Brass Key", 'raw': 78, 'flag': 828, 'bit': 73})
SCRIPTED_BIT_TO_LOCATION_ID = {r['bit']: LOCATION_NAME_TO_ID[r['name']] for r in SCRIPTED_CHECKS}
SCRIPTED_FLAG_TO_LOCATION_ID = {r['flag']: LOCATION_NAME_TO_ID[r['name']] for r in SCRIPTED_CHECKS if r['flag'] != 291}
SCRIPTED_LOCATION_NAMES = tuple(r['name'] for r in SCRIPTED_CHECKS)
GATHERED_PERSIST_FLAG_TO_LOCATION_ID.update(SCRIPTED_FLAG_TO_LOCATION_ID)
ACTIVE_LOCATION_NAMES += ('Amusement Park Roller Coaster Control Room - Health Drink 1', 'Amusement Park Roller Coaster Control Room - Health Drink 2', 'Amusement Park Theater - Health Drink', 'Amusement Park Theater - Shotgun Shells', 'Amusement Park Happy Carousel Stand - Stun Gun Battery 1', 'Amusement Park Happy Carousel Stand - Stun Gun Battery 2', 'Amusement Park Happy Carousel Bench - First-Aid Kit', "Church BF Harry's Room - Stun Gun Battery 1", "Church BF Harry's Room - Stun Gun Battery 2", 'Church BF Morgue - Shotgun Shells', "Church BF Alessa's Hospital Bed - Handgun Bullets", "Church BF Alessa's Hospital Bed - Ampoule", 'Amusement Park Souvenir Shop - Roller Coaster Key', 'Amusement Park Theater - Red Shoe', 'Amusement Park Theater - Chain', "Amusement Park Fortuneteller - Douglas's Notebook", 'Amusement Park Fortuneteller - Doll Head', 'Church 1F Podium - "Eye of the Night" Tarot Card', 'Church 1F Library - "Moon" Tarot Card', 'Church 1F Library - Book: Otherworld Laws', 'Church BF Alessa\'s Hospital Bed - "Fool" Tarot Card', "Church BF Alessa's Room - Brass Key")
ACTIVE_LOCATION_NAME_TO_ID.update({n:LOCATION_NAME_TO_ID[n] for n in ('Amusement Park Roller Coaster Control Room - Health Drink 1', 'Amusement Park Roller Coaster Control Room - Health Drink 2', 'Amusement Park Theater - Health Drink', 'Amusement Park Theater - Shotgun Shells', 'Amusement Park Happy Carousel Stand - Stun Gun Battery 1', 'Amusement Park Happy Carousel Stand - Stun Gun Battery 2', 'Amusement Park Happy Carousel Bench - First-Aid Kit', "Church BF Harry's Room - Stun Gun Battery 1", "Church BF Harry's Room - Stun Gun Battery 2", 'Church BF Morgue - Shotgun Shells', "Church BF Alessa's Hospital Bed - Handgun Bullets", "Church BF Alessa's Hospital Bed - Ampoule", 'Amusement Park Souvenir Shop - Roller Coaster Key', 'Amusement Park Theater - Red Shoe', 'Amusement Park Theater - Chain', "Amusement Park Fortuneteller - Douglas's Notebook", 'Amusement Park Fortuneteller - Doll Head', 'Church 1F Podium - "Eye of the Night" Tarot Card', 'Church 1F Library - "Moon" Tarot Card', 'Church 1F Library - Book: Otherworld Laws', 'Church BF Alessa\'s Hospital Bed - "Fool" Tarot Card', "Church BF Alessa's Room - Brass Key")})
VERIFIED_ADDED_POOL_ITEMS += ('Roller Coaster Key', 'Red Shoe', 'Chain', "Douglas's Notebook", 'Doll Head', '"Eye of the Night" Tarot Card', '"Moon" Tarot Card', 'Book: Otherworld Laws', '"Fool" Tarot Card', 'Brass Key')
next(r for r in CHECK_CATALOGUE if r['name']=='Amusement Park Souvenir Shop - Roller Coaster Key')['persist_flag']=747
next(r for r in CHECK_CATALOGUE if r['name']=='Amusement Park Theater - Red Shoe')['persist_flag']=751
next(r for r in CHECK_CATALOGUE if r['name']=='Amusement Park Theater - Chain')['persist_flag']=752
next(r for r in CHECK_CATALOGUE if r['name']=="Amusement Park Fortuneteller - Douglas's Notebook")['persist_flag']=754
next(r for r in CHECK_CATALOGUE if r['name']=='Amusement Park Fortuneteller - Doll Head')['persist_flag']=753
next(r for r in CHECK_CATALOGUE if r['name']=='Church 1F Podium - "Eye of the Night" Tarot Card')['persist_flag']=813
next(r for r in CHECK_CATALOGUE if r['name']=='Church 1F Library - "Moon" Tarot Card')['persist_flag']=825
next(r for r in CHECK_CATALOGUE if r['name']=='Church 1F Library - Book: Otherworld Laws')['persist_flag']=826
next(r for r in CHECK_CATALOGUE if r['name']=='Church BF Alessa\'s Hospital Bed - "Fool" Tarot Card')['persist_flag']=831
next(r for r in CHECK_CATALOGUE if r['name']=="Church BF Alessa's Room - Brass Key")['persist_flag']=828

# Condition17 means the real park visit(flag744), not an inventory condition.
LATE_GROUND_131 += ((1111, 'Amusement Park Souvenir Shop - Beef Jerky'),)
PERSIST_FLAG_TO_LOCATION_ID[1111] = LOCATION_NAME_TO_ID['Amusement Park Souvenir Shop - Beef Jerky']
GATHERED_PERSIST_FLAG_TO_LOCATION_ID[1111] = PERSIST_FLAG_TO_LOCATION_ID[1111]
ACTIVE_LOCATION_NAMES += ('Amusement Park Souvenir Shop - Beef Jerky',)
ACTIVE_LOCATION_NAME_TO_ID['Amusement Park Souvenir Shop - Beef Jerky'] = PERSIST_FLAG_TO_LOCATION_ID[1111]
next(r for r in CHECK_CATALOGUE if r['name']=='Amusement Park Souvenir Shop - Beef Jerky')['persist_flag'] = 1111

# Normal/Normal minimum-one alternative supply groups, plus recorded Church pickups.
LATE_GROUND_132 = ((1106, 'Amusement Park Souvenir Shop - Healing Supply'), (1107, 'Amusement Park Souvenir Shop - Healing Supply'), (1114, 'Amusement Park Swing Rocket Control Room - Ammo Supply'), (1115, 'Amusement Park Swing Rocket Control Room - Ammo Supply'), (1129, "Church 1F Vincent's Room - Handgun Bullets 1"), (1130, "Church 1F Vincent's Room - Handgun Bullets 2"))
for _flag, _name in LATE_GROUND_132:
    PERSIST_FLAG_TO_LOCATION_ID[_flag] = LOCATION_NAME_TO_ID[_name]
    GATHERED_PERSIST_FLAG_TO_LOCATION_ID[_flag] = LOCATION_NAME_TO_ID[_name]
    _row = next(r for r in CHECK_CATALOGUE if r['name']==_name)
    _row['persist_flag'] = _row.get('persist_flag') or _flag
SCRIPTED_CHECKS += ({'name': "Church 1F Vincent's Room - Cassette Tape", 'raw': 79, 'flag': 829, 'bit': 74},)
SCRIPTED_BIT_TO_LOCATION_ID = {r['bit']: LOCATION_NAME_TO_ID[r['name']] for r in SCRIPTED_CHECKS}
SCRIPTED_FLAG_TO_LOCATION_ID = {r['flag']: LOCATION_NAME_TO_ID[r['name']] for r in SCRIPTED_CHECKS if r['flag'] != 291}
SCRIPTED_LOCATION_NAMES = tuple(r['name'] for r in SCRIPTED_CHECKS)
GATHERED_PERSIST_FLAG_TO_LOCATION_ID.update(SCRIPTED_FLAG_TO_LOCATION_ID)
ACTIVE_LOCATION_NAMES += ('Amusement Park Souvenir Shop - Healing Supply', 'Amusement Park Swing Rocket Control Room - Ammo Supply', "Church 1F Vincent's Room - Handgun Bullets 1", "Church 1F Vincent's Room - Handgun Bullets 2", "Church 1F Vincent's Room - Cassette Tape")
ACTIVE_LOCATION_NAME_TO_ID.update({n:LOCATION_NAME_TO_ID[n] for n in ('Amusement Park Souvenir Shop - Healing Supply', 'Amusement Park Swing Rocket Control Room - Ammo Supply', "Church 1F Vincent's Room - Handgun Bullets 1", "Church 1F Vincent's Room - Handgun Bullets 2", "Church 1F Vincent's Room - Cassette Tape")})
VERIFIED_ADDED_POOL_ITEMS += ("Cassette Tape",)
next(r for r in CHECK_CATALOGUE if r["name"]=="Church 1F Vincent's Room - Cassette Tape")["persist_flag"]=829
next(r for r in CHECK_CATALOGUE if r["name"]=='Amusement Park Souvenir Shop - Healing Supply')["notes"]='One guaranteed pickup: First-Aid Kit or Ampoule. Optional extra kits/ammo remain vanilla.'
next(r for r in CHECK_CATALOGUE if r["name"]=='Amusement Park Swing Rocket Control Room - Ammo Supply')["notes"]='One guaranteed pickup: Handgun Bullets or Submachine Gun Ammo.'

# Only implemented locations are exposed to AP clients and option tools.
# Preserve all assigned IDs; conditional vanilla pickups remain untouched.
LOCATION_NAME_TO_ID = dict(ACTIVE_LOCATION_NAME_TO_ID)
CHECK_CATALOGUE = tuple(row for row in CHECK_CATALOGUE if row['name'] in LOCATION_NAME_TO_ID)

# Bundles use one AP stream entry and one atomic native inventory grant.
BUNDLED_ITEMS = {
    "Shakespeare Anthology": tuple(f"Shakespeare Anthology {i}" for i in range(1, 6)),
    "Tarot Cards": ('"Eye of the Night" Tarot Card', '"Moon" Tarot Card',
                    '"Fool" Tarot Card', '"Hanged Man" Tarot Card', '"High Priestess" Tarot Card'),
}
for _offset, _name in enumerate(BUNDLED_ITEMS):
    _id = 0x53483600 + _offset
    ITEM_NAME_TO_ID[_name] = _id
    ITEM_CLASSIFICATION[_name] = "progression"
    ITEM_ID_TO_RAW[_id] = 240 + _offset
RECEIVE_RAW_IDS = RECEIVE_RAW_IDS | {240, 241}
BUNDLE_ITEM_IDS = frozenset(ITEM_NAME_TO_ID[n] for n in BUNDLED_ITEMS)

# Fixed Normal/Normal Subway B4 pickups. New IDs append after all existing IDs.
SUBWAY_B4_CHECKS_157 = ({'index': 227, 'name': 'Subway B4 Supplies - Health Drink 1', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 964, 'notes': 'Verified fixed Normal-action room 52 pickup; condition 0. Conservative Flashlight access gate, matching the other dark Subway supply checks. Verified against the mapped Subway B4 pickup data.'}, {'index': 228, 'name': 'Subway B4 Supplies - Health Drink 2', 'vanilla': 'Health Drink', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 18, 'persist_flag': 965, 'notes': 'Verified fixed Normal-action room 52 pickup; condition 0. Conservative Flashlight access gate, matching the other dark Subway supply checks. Verified against the mapped Subway B4 pickup data.'}, {'index': 229, 'name': 'Subway B4 Supplies - Handgun Bullets', 'vanilla': 'Handgun Bullets', 'requirements': 'Flashlight', 'classification': 'Filler', 'raw_id': 15, 'persist_flag': 966, 'notes': 'Verified fixed Normal-action room 52 pickup; condition 0. Conservative Flashlight access gate, matching the other dark Subway supply checks. Verified against the mapped Subway B4 pickup data.'})
for _row in SUBWAY_B4_CHECKS_157:
    _name, _flag = _row['name'], _row['persist_flag']
    _location_id = 0x53485000 + _row['index']
    assert _name not in LOCATION_NAME_TO_ID and _location_id not in LOCATION_NAME_TO_ID.values()
    assert _flag not in PERSIST_FLAG_TO_LOCATION_ID
    CHECK_CATALOGUE += (_row,)
    LOCATION_NAME_TO_ID[_name] = _location_id
    ACTIVE_LOCATION_NAME_TO_ID[_name] = _location_id
    ACTIVE_LOCATION_NAMES += (_name,)
    PERSIST_FLAG_TO_LOCATION_ID[_flag] = _location_id
    GATHERED_PERSIST_FLAG_TO_LOCATION_ID[_flag] = _location_id
