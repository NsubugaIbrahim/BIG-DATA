import pandas as pd
from sqlalchemy import create_engine
import json

# =========================
# 1. LOAD DATA
# =========================

print("Loading data...")

patents_raw = pd.read_csv("g_patent.tsv", sep="\t", low_memory=False)
abstracts = pd.read_csv("g_patent_abstract.tsv", sep="\t", low_memory=False)
assignees = pd.read_csv("g_assignee_disambiguated.tsv", sep="\t", low_memory=False)
inventors = pd.read_csv("g_inventor_not_disambiguated.tsv", sep="\t", low_memory=False)

print("Data loaded!")

# =========================
# 2. CLEAN PATENTS
# =========================

print("Cleaning patents...")

patents = patents_raw[['patent_id', 'patent_title', 'patent_date']].copy()

# Merge abstracts
patents = patents.merge(
    abstracts[['patent_id', 'patent_abstract']],
    on='patent_id',
    how='left'
)

# Rename columns
patents.rename(columns={
    'patent_title': 'title',
    'patent_abstract': 'abstract',
    'patent_date': 'filing_date'
}, inplace=True)

# Convert date
patents['filing_date'] = pd.to_datetime(patents['filing_date'], errors='coerce')

# Extract year
patents['year'] = patents['filing_date'].dt.year

# Drop missing IDs
patents = patents.dropna(subset=['patent_id'])

# =========================
# 3. CLEAN INVENTORS
# =========================

print("Cleaning inventors...")

inventors['name'] = (
    inventors['raw_inventor_name_first'].fillna('') + " " +
    inventors['raw_inventor_name_last'].fillna('')
).str.strip()

inventors_clean = inventors[['inventor_id', 'patent_id', 'name']].dropna()

# =========================
# 4. CLEAN COMPANIES
# =========================

print("Cleaning companies...")

assignees['name'] = assignees['disambig_assignee_organization']

companies = assignees[['assignee_id', 'patent_id', 'name']].dropna()
companies.rename(columns={'assignee_id': 'company_id'}, inplace=True)

# =========================
# 5. RELATIONSHIPS TABLE
# =========================

print("Building relationships...")

relationships = pd.merge(
    inventors_clean[['inventor_id', 'patent_id']],
    companies[['company_id', 'patent_id']],
    on='patent_id',
    how='inner'
)

# =========================
# 6. SAVE CLEAN FILES
# =========================

print("Saving cleaned CSVs...")

patents.to_csv("clean_patents.csv", index=False)
inventors_clean.to_csv("clean_inventors.csv", index=False)
companies.to_csv("clean_companies.csv", index=False)

# =========================
# 7. STORE IN DATABASE
# =========================

print("Creating database...")

engine = create_engine("sqlite:///patents.db")

patents.to_sql("patents", engine, if_exists="replace", index=False)
inventors_clean.to_sql("inventors", engine, if_exists="replace", index=False)
companies.to_sql("companies", engine, if_exists="replace", index=False)
relationships.to_sql("relationships", engine, if_exists="replace", index=False)

print("Database ready!")

# =========================
# 8. ANALYSIS QUERIES
# =========================

print("Running analysis...")

# Q1: Top Inventors
top_inventors = pd.read_sql("""
SELECT name, COUNT(*) as patent_count
FROM inventors
GROUP BY name
ORDER BY patent_count DESC
LIMIT 10
""", engine)

# Q2: Top Companies
top_companies = pd.read_sql("""
SELECT name, COUNT(*) as patent_count
FROM companies
GROUP BY name
ORDER BY patent_count DESC
LIMIT 10
""", engine)

# Q3: Countries (we skip unless you add location dataset)

# Q4: Trends Over Time
year_trends = pd.read_sql("""
SELECT year, COUNT(*) as total_patents
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year
""", engine)

# Q5: JOIN Query
joined = pd.read_sql("""
SELECT p.patent_id, i.name AS inventor, c.name AS company
FROM relationships r
JOIN patents p ON r.patent_id = p.patent_id
JOIN inventors i ON r.inventor_id = i.inventor_id
JOIN companies c ON r.company_id = c.company_id
LIMIT 20
""", engine)

# Q6: CTE Query
cte_query = pd.read_sql("""
WITH inventor_counts AS (
    SELECT name, COUNT(*) as cnt
    FROM inventors
    GROUP BY name
)
SELECT * FROM inventor_counts
WHERE cnt > 50
ORDER BY cnt DESC
LIMIT 10
""", engine)

# Q7: Ranking Query
ranking = pd.read_sql("""
SELECT name,
       COUNT(*) as patent_count,
       RANK() OVER (ORDER BY COUNT(*) DESC) as rank
FROM inventors
GROUP BY name
LIMIT 10
""", engine)

# =========================
# 9. EXPORT REPORTS
# =========================

print("Exporting reports...")

top_inventors.to_csv("top_inventors.csv", index=False)
top_companies.to_csv("top_companies.csv", index=False)
year_trends.to_csv("country_trends.csv", index=False)

# JSON report
report = {
    "total_patents": int(len(patents)),
    "top_inventors": top_inventors.to_dict(orient="records"),
    "top_companies": top_companies.to_dict(orient="records"),
    "year_trends": year_trends.to_dict(orient="records")
}

with open("report.json", "w") as f:
    json.dump(report, f, indent=4)

# =========================
# 10. CONSOLE REPORT
# =========================

print("\n================= PATENT REPORT =================")
print(f"Total Patents: {len(patents)}\n")

print("Top Inventors:")
print(top_inventors.to_string(index=False))

print("\nTop Companies:")
print(top_companies.to_string(index=False))

print("\nPatent Trends:")
print(year_trends.head().to_string(index=False))

print("\nDone!")