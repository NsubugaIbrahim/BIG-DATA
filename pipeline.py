import pandas as pd
from sqlalchemy import create_engine
import json
import os

# =========================================================
# PATENT ANALYTICS PIPELINE (ROBUST VERSION)
# =========================================================

print("=" * 60)
print("PATENT ANALYTICS PIPELINE STARTED")
print("=" * 60)

# =========================================================
# 1. LOAD DATASETS
# =========================================================

print("\n[1/10] Loading datasets...")

patents_raw = pd.read_csv("g_patent.tsv", sep="\t", low_memory=False)
abstracts = pd.read_csv("g_patent_abstract.tsv", sep="\t", low_memory=False)
assignees = pd.read_csv("g_assignee_disambiguated.tsv", sep="\t", low_memory=False)
inventors = pd.read_csv("g_inventor_disambiguated.tsv", sep="\t", low_memory=False)
locations = pd.read_csv("g_location_disambiguated.tsv", sep="\t", low_memory=False)

print("Datasets loaded successfully!")

# =========================================================
# 2. CLEAN PATENTS
# =========================================================

print("\n[2/10] Cleaning patents...")

patents = patents_raw[['patent_id', 'patent_title', 'patent_date']].copy()

patents = patents.merge(
    abstracts[['patent_id', 'patent_abstract']],
    on='patent_id',
    how='left'
)

patents.rename(columns={
    'patent_title': 'title',
    'patent_abstract': 'abstract',
    'patent_date': 'filing_date'
}, inplace=True)

patents['filing_date'] = pd.to_datetime(patents['filing_date'], errors='coerce')
patents['year'] = patents['filing_date'].dt.year
patents = patents.dropna(subset=['patent_id'])

print(f"Patents cleaned: {len(patents):,}")

# =========================================================
# 3. CLEAN LOCATIONS
# =========================================================

print("\n[3/10] Cleaning locations...")

locations_clean = locations.copy()

# safe column mapping
rename_map = {
    'disambig_country': 'country',
    'disambig_state': 'state',
    'disambig_city': 'city'
}

locations_clean.rename(columns={k: v for k, v in rename_map.items() if k in locations_clean.columns}, inplace=True)

keep_cols = [c for c in [
    'location_id', 'country', 'state', 'city', 'latitude', 'longitude'
] if c in locations_clean.columns]

locations_clean = locations_clean[keep_cols]

print(f"Locations cleaned: {len(locations_clean):,}")

# =========================================================
# 4. CLEAN INVENTORS 
# =========================================================

print("\n[4/10] Cleaning inventors...")

# ---- detect name columns safely ----
def find_col(df, keywords):
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            return col
    return None

first_col = find_col(inventors, ["first"])
last_col = find_col(inventors, ["last"])
name_col = find_col(inventors, ["name"])

if first_col and last_col:
    inventors['name'] = (
        inventors[first_col].fillna('') + " " +
        inventors[last_col].fillna('')
    ).str.strip()
elif name_col:
    inventors['name'] = inventors[name_col]
else:
    inventors['name'] = "UNKNOWN"

# safe column selection
inventor_keep = [c for c in [
    'inventor_id', 'patent_id', 'location_id', 'name'
] if c in inventors.columns]

inventors_clean = inventors[inventor_keep].copy()

# merge locations (only if location_id exists)
if 'location_id' in inventors_clean.columns:
    inventors_clean = inventors_clean.merge(
        locations_clean,
        on='location_id',
        how='left'
    )

inventors_clean = inventors_clean.dropna(subset=['inventor_id', 'patent_id'])

print(f"Inventors cleaned: {len(inventors_clean):,}")

# =========================================================
# 5. CLEAN COMPANIES
# =========================================================

print("\n[5/10] Cleaning companies...")

assignees['name'] = assignees.get('disambig_assignee_organization', None)

companies = assignees[[c for c in [
    'assignee_id', 'patent_id'
] if c in assignees.columns]].copy()

companies['name'] = assignees['name']

companies.rename(columns={'assignee_id': 'company_id'}, inplace=True)
companies = companies.dropna(subset=['company_id', 'patent_id'])

print(f"Companies cleaned: {len(companies):,}")

# =========================================================
# 6. RELATIONSHIPS
# =========================================================

print("\n[6/10] Building relationships...")

relationships = pd.merge(
    inventors_clean[['inventor_id', 'patent_id']],
    companies[['company_id', 'patent_id']],
    on='patent_id',
    how='inner'
).drop_duplicates()

print(f"Relationships built: {len(relationships):,}")

# =========================================================
# 7. SAMPLE REDUCTION
# =========================================================

print("\n[7/10] Reducing dataset size...")

MAX_ROWS = 100000

def safe_sample(df):
    return df.sample(MAX_ROWS, random_state=42) if len(df) > MAX_ROWS else df

patents = safe_sample(patents)
inventors_clean = safe_sample(inventors_clean)
companies = safe_sample(companies)
relationships = safe_sample(relationships)

print("Dataset reduction complete!")

# =========================================================
# 8. EXPORT CSVs
# =========================================================

print("\n[8/10] Exporting CSVs...")

patents.to_csv("clean_patents.csv", index=False)
inventors_clean.to_csv("clean_inventors.csv", index=False)
companies.to_csv("clean_companies.csv", index=False)
locations_clean.to_csv("clean_locations.csv", index=False)
relationships.to_csv("relationships.csv", index=False)

print("CSV export complete!")

# =========================================================
# 9. DATABASE
# =========================================================

print("\n[9/10] Creating SQLite database...")

if os.path.exists("patents.db"):
    os.remove("patents.db")

engine = create_engine("sqlite:///patents.db")

patents.to_sql("patents", engine, if_exists="replace", index=False)
inventors_clean.to_sql("inventors", engine, if_exists="replace", index=False)
companies.to_sql("companies", engine, if_exists="replace", index=False)
locations_clean.to_sql("locations", engine, if_exists="replace", index=False)
relationships.to_sql("relationships", engine, if_exists="replace", index=False)

print("Database created!")

# =========================================================
# 10. SCHEMA EXPORT
# =========================================================

print("\n[10/10] Generating schema...")

schema = pd.read_sql("SELECT sql FROM sqlite_master WHERE type='table';", engine)

with open("schema.sql", "w", encoding="utf-8") as f:
    for stmt in schema["sql"]:
        if stmt:
            f.write(stmt + ";\n\n")

print("schema.sql generated!")

# =========================================================
# ANALYTICS
# =========================================================

print("\nRunning analytics...")

top_inventors = pd.read_sql("""
SELECT name, COUNT(*) as patent_count
FROM inventors
GROUP BY name
ORDER BY patent_count DESC
LIMIT 10
""", engine)

top_companies = pd.read_sql("""
SELECT name, COUNT(*) as patent_count
FROM companies
GROUP BY name
ORDER BY patent_count DESC
LIMIT 10
""", engine)

top_countries = pd.read_sql("""
SELECT country, COUNT(*) as patent_count
FROM inventors
WHERE country IS NOT NULL AND country != ''
GROUP BY country
ORDER BY patent_count DESC
LIMIT 10
""", engine)

year_trends = pd.read_sql("""
SELECT year, COUNT(*) as total_patents
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year
""", engine)

# =========================================================
# EXPORT REPORTS
# =========================================================

top_inventors.to_csv("top_inventors.csv", index=False)
top_companies.to_csv("top_companies.csv", index=False)
top_countries.to_csv("top_countries.csv", index=False)
year_trends.to_csv("year_trends.csv", index=False)

report = {
    "total_patents": len(patents),
    "total_inventors": len(inventors_clean),
    "total_companies": len(companies),
    "top_inventors": top_inventors.to_dict(orient="records"),
    "top_companies": top_companies.to_dict(orient="records"),
    "top_countries": top_countries.to_dict(orient="records"),
    "year_trends": year_trends.to_dict(orient="records")
}

with open("report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=4)

# =========================================================
# FINAL OUTPUT
# =========================================================

print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)

print(f"Patents: {len(patents):,}")
print(f"Inventors: {len(inventors_clean):,}")
print(f"Companies: {len(companies):,}")
print(f"Relationships: {len(relationships):,}")

print("\nTOP INVENTORS")
print(top_inventors)

print("\nTOP COMPANIES")
print(top_companies)

print("\nTOP COUNTRIES")
print(top_countries)

print("\nYEAR TRENDS")
print(year_trends.head(20))

print("\nDONE 🚀")