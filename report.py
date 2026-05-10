import pandas as pd
import json

# =========================
# LOAD DATA (LIGHTWEIGHT)
# =========================

top_inventors = pd.read_csv("top_inventors.csv")
top_companies = pd.read_csv("top_companies.csv")
trends = pd.read_csv("country_trends.csv")

# =========================
# DERIVED INSIGHTS
# =========================

total_patents = trends['total_patents'].sum()

# Growth calculation
trends = trends.sort_values("year")
trends['growth_rate'] = trends['total_patents'].pct_change() * 100

latest_year = trends.iloc[-1]['year']
latest_value = trends.iloc[-1]['total_patents']

peak_year = trends.loc[trends['total_patents'].idxmax()]

# Top inventor insight
top_inventor = top_inventors.iloc[0]

# Top company insight
top_company = top_companies.iloc[0]

# =========================
# TEXT REPORT (HUMAN READABLE)
# =========================

print("\n================= ADVANCED PATENT REPORT =================\n")

print(f"📊 Total patents analyzed: {int(total_patents):,}")
print(f"📅 Latest year: {int(latest_year)} with {int(latest_value):,} patents")

print(f"\n🔥 Peak innovation year: {int(peak_year['year'])} "
      f"({int(peak_year['total_patents']):,} patents)")

print("\n🏆 Top Inventor:")
print(f"   {top_inventor['name']} with {int(top_inventor['patent_count']):,} patents")

print("\n🏢 Top Company:")
print(f"   {top_company['name']} with {int(top_company['patent_count']):,} patents")

print("\n📈 Growth trend (recent years):")
print(trends.tail(5).to_string(index=False))

# =========================
# JSON REPORT (STRUCTURED)
# =========================

report = {
    "summary": {
        "total_patents": int(total_patents),
        "latest_year": int(latest_year),
        "latest_value": int(latest_value),
        "peak_year": int(peak_year['year'])
    },
    "top_inventor": top_inventor.to_dict(),
    "top_company": top_company.to_dict(),
    "recent_trends": trends.tail(5).to_dict(orient="records")
}

with open("advanced_report.json", "w") as f:
    json.dump(report, f, indent=4)

print("\n✅ Advanced report generated: advanced_report.json")