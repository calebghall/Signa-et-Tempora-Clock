import json

# Configuration
input_file = 'cities500.txt' 
tier1_file = 'tier1.json'
tier2_file = 'tier2.json'
attribution_str = "Data (c) GeoNames.org | CC BY 4.0"

print(f"Processing {input_file}...")

raw_data = []

# 1. Read TSV
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        columns = line.split('\t')
        try:
            pop = int(columns[14])
            if pop < 10000:
                continue
            
            raw_data.append({
                'n': columns[1],
                'lat': columns[4],
                'lon': columns[5],
                'c': columns[8],
                's': columns[10],
                'pop': pop
            })
        except (IndexError, ValueError):
            continue

# 2. Sort by population descending 
raw_data.sort(key=lambda x: x['pop'], reverse=True)

strings = []
string_to_id = {}

def get_id(s):
    s = str(s or "").strip()
    if s not in string_to_id:
        string_to_id[s] = len(strings)
        strings.append(s)
    return string_to_id[s]

# Define Tiers ONCE with the attribution key included
tier1 = {"a": attribution_str, "m": strings, "r": [], "k": {}}
tier2 = {"a": attribution_str, "m": strings, "r": [], "k": {}}

# 3. Build Tiers
for item in raw_data:
    name = item['n']
    country = item['c'].lower()
    state = str(item['s'] or "")
    pop = item['pop']

    # Coordinate optimization
    lat = round(float(item['lat']), 2)
    lon = round(float(item['lon']), 2)
    lat = int(lat) if lat.is_integer() else lat
    lon = int(lon) if lon.is_integer() else lon

    # Tiering Logic
    is_us = (country == 'us')
    target = tier1 if (is_us or pop >= 50000) else tier2

    # Record format: [CountryID, StateID, Lat, Lon]
    rec_idx = len(target["r"])
    target["r"].append([get_id(country.upper()), get_id(state), lat, lon])

    # Search Keys
    n_low = name.lower().strip()
    s_low = state.lower().strip()
    c_low = country.lower().strip()

    # 1. Generic Key: "paris"
    if n_low not in target["k"]:
        target["k"][n_low] = rec_idx
    
    # 2. State Key: "cordova|tn" (Matches if state is provided)
    if s_low:
        target["k"][f"{n_low}|{s_low}"] = rec_idx

    # 3. Country Key: "paris|fr" <-- ADD THIS
    if c_low:
        target["k"][f"{n_low}|{c_low}"] = rec_idx
            
    # 4. Full Key: "cordova|tn|us" or "paris|11|fr"
    if s_low and c_low:
        target["k"][f"{n_low}|{s_low}|{c_low}"] = rec_idx

# 4. Save Tier Files
with open(tier1_file, 'w', encoding='utf-8') as f:
    json.dump(tier1, f, separators=(',', ':'), ensure_ascii=False)

with open(tier2_file, 'w', encoding='utf-8') as f:
    json.dump(tier2, f, separators=(',', ':'), ensure_ascii=False)

print(f"Finished! Tier 1: {len(tier1['r'])} | Tier 2: {len(tier2['r'])}")
