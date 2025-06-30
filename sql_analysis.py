import pandas as pd
from sqlalchemy import create_engine
from config import POSTGRES

# database connection
conn_str = (
    f"postgresql://{POSTGRES['user']}:{POSTGRES['password']}"
    f"@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['database']}"
)
engine = create_engine(conn_str)
print("Connected to the database.")

# Yearly average goals by gender
query_yearly_avg = """
WITH yearly_avg AS (
    SELECT
        EXTRACT(YEAR FROM date::DATE) AS year,
        gender,
        AVG(home_score + away_score) AS avg_goals
    FROM (
        SELECT * FROM matches_men
        UNION ALL
        SELECT * FROM matches_women
    ) combined
    GROUP BY gender, EXTRACT(YEAR FROM date::DATE)
)
SELECT
    year,
    gender,
    avg_goals
FROM yearly_avg
ORDER BY gender, year;
"""
df_yearly = pd.read_sql(query_yearly_avg, engine)
df_yearly['year'] = df_yearly['year'].astype('Int64')
df_yearly['avg_goals'] = df_yearly['avg_goals'].round().astype('Int64')
df_yearly.to_csv("output/yearly_avg_goals.csv", index=False)
print("Saved: output/yearly_avg_goals.csv")

# Tournament scoring averages
query_tournament = """
SELECT
    tournament,
    gender,
    COUNT(*) AS match_count,
    AVG(home_score + away_score) AS avg_goals
FROM (
    SELECT * FROM matches_men
    UNION ALL
    SELECT * FROM matches_women
) combined
GROUP BY gender, tournament
HAVING COUNT(*) > 10
ORDER BY avg_goals DESC;
"""
df_tournament = pd.read_sql(query_tournament, engine)
df_tournament['avg_goals'] = df_tournament['avg_goals'].apply(
    lambda x: f"{x:.2f}" if pd.notnull(x) else ""
)
df_tournament.to_csv("output/tournament_avg_goals.csv", index=False)
print("Saved: output/tournament_avg_goals.csv")

# Home vs. away scoring averages
query_home_away = """
SELECT
    gender,
    AVG(home_score) AS avg_home_goals,
    AVG(away_score) AS avg_away_goals
FROM (
    SELECT * FROM matches_men
    UNION ALL
    SELECT * FROM matches_women
) combined
GROUP BY gender;
"""
df_home_away = pd.read_sql(query_home_away, engine)
df_home_away['avg_home_goals'] = df_home_away['avg_home_goals'].apply(
    lambda x: f"{x:.2f}" if pd.notnull(x) else ""
)
df_home_away['avg_away_goals'] = df_home_away['avg_away_goals'].apply(
    lambda x: f"{x:.2f}" if pd.notnull(x) else ""
)
df_home_away.to_csv("output/home_away_bias.csv", index=False)
print("Saved: output/home_away_bias.csv")
