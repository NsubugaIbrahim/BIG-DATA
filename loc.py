import pandas as pd

print("Loading datasets...")

inventors = pd.read_csv(
    "g_inventor_not_disambiguated.tsv",
    sep="\t",
    usecols=[
        'inventor_id',
        'patent_id',
        'raw_inventor_name_first',
        'raw_inventor_name_last',
        'rawlocation_id'
    ],
    low_memory=False
)

locations = pd.read_csv(
    "g_location_disambiguated.tsv",
    sep="\t",
    usecols=[
        'location_id',
        'disambig_country'
    ],
    low_memory=False
)

print("Datasets loaded!")

# -----------------------------
# CHECK RAW VALUES
# -----------------------------

print("\nINVENTOR LOCATION IDS:")
print(inventors['rawlocation_id'].head(10))

print("\nLOCATION TABLE IDS:")
print(locations['location_id'].head(10))

# -----------------------------
# FORCE STRING TYPES
# -----------------------------

inventors['rawlocation_id'] = (
    inventors['rawlocation_id']
    .astype(str)
    .str.strip()
)

locations['location_id'] = (
    locations['location_id']
    .astype(str)
    .str.strip()
)

# -----------------------------
# MERGE
# -----------------------------

merged = inventors.merge(
    locations,
    left_on='rawlocation_id',
    right_on='location_id',
    how='left'
)

# -----------------------------
# RESULTS
# -----------------------------

print("\nTOTAL ROWS:")
print(len(merged))

print("\nMATCHED COUNTRIES:")
print(merged['disambig_country'].notna().sum())

print("\nTOP COUNTRIES:")
print(
    merged['disambig_country']
    .value_counts()
    .head(10)
)