import pandas as pd
from sqlalchemy import create_engine
from config import POSTGRES
from scipy import stats

# Connect to database
conn_str = (
    f"postgresql://{POSTGRES['user']}:{POSTGRES['password']}"
    f"@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['database']}"
)
engine = create_engine(conn_str)
print("Connected to the database.")

# Overall comparison: men vs. women total goals per match
query_men = "SELECT (home_score + away_score) AS total_goals FROM matches_men;"
query_women = "SELECT (home_score + away_score) AS total_goals FROM matches_women;"

goals_men = pd.read_sql(query_men, engine)['total_goals'].dropna()
goals_women = pd.read_sql(query_women, engine)['total_goals'].dropna()

u_stat, p_val = stats.mannwhitneyu(goals_men, goals_women, alternative='two-sided')
print(f"\nOverall Mann-Whitney U: U={u_stat:.0f}, p-value={p_val:.4e}")

# Year-by-year hypothesis tests
query_years = """
SELECT DISTINCT EXTRACT(YEAR FROM date::DATE)::int AS year
FROM (
    SELECT date FROM matches_men
    UNION ALL
    SELECT date FROM matches_women
) combined
ORDER BY year;
"""
years = pd.read_sql(query_years, engine)['year']

results = []

for year in years:
    # Pull matches for the given year
    query_men_year = f"""
        SELECT (home_score + away_score) AS total_goals
        FROM matches_men
        WHERE EXTRACT(YEAR FROM date::DATE) = {year};
    """
    query_women_year = f"""
        SELECT (home_score + away_score) AS total_goals
        FROM matches_women
        WHERE EXTRACT(YEAR FROM date::DATE) = {year};
    """
    goals_men_year = pd.read_sql(query_men_year, engine)['total_goals'].dropna()
    goals_women_year = pd.read_sql(query_women_year, engine)['total_goals'].dropna()

    # Skip years with too little data
    if len(goals_men_year) < 10 or len(goals_women_year) < 10:
        continue

    # Run Mann-Whitney test for each year
    u, p = stats.mannwhitneyu(goals_men_year, goals_women_year, alternative='two-sided')

    # Store results
    results.append({
        'year': year,
        'men_matches': len(goals_men_year),
        'women_matches': len(goals_women_year),
        'avg_men_goals': goals_men_year.mean(),
        'avg_women_goals': goals_women_year.mean(),
        'p_value': p
    })

# Save yearly results to CSV
df_results = pd.DataFrame(results)
df_results.to_csv("output/yearly_goal_difference.csv", index=False)
print("Saved year-by-year hypothesis test results to output/yearly_goal_difference.csv")
