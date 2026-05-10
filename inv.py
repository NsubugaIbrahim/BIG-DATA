import pandas as pd

inventors = pd.read_csv(
    "g_inventor_not_disambiguated.tsv",
    sep="\t",
    nrows=5
)

print(inventors.columns.tolist())
print(inventors_clean['rawlocation_id'].head())
print(locations_clean['location_id'].head())