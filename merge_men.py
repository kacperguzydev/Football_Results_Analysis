import pandas as pd

# Load raw results data
df = pd.read_csv("data/men/results.csv")
print(f" Loaded {len(df)} rows.")

# Convert 'date' column to datetime
print(" Converting 'date' column")
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Drop rows with invalid or missing dates
invalid_dates = df['date'].isnull().sum()
if invalid_dates > 0:
    print(f" Found {invalid_dates} rows with invalid dates")
    df = df.dropna(subset=['date'])

# Add 'gender' column to label data
df['gender'] = 'M'

# Data quality checks
neg_scores = df[(df['home_score'] < 0) | (df['away_score'] < 0)]
if not neg_scores.empty:
    print(f" Found {len(neg_scores)} rows with negative scores")
    df = df[(df['home_score'] >= 0) & (df['away_score'] >= 0)]

# Remove duplicate rows (same date, teams, tournament)
duplicates = df.duplicated(subset=['date', 'home_team', 'away_team', 'tournament'])
if duplicates.sum() > 0:
    print(f" Found {duplicates.sum()} duplicate rows .")
    df = df[~duplicates]

# Save cleaned data
output_path = "data/men/men_cleaned.csv"
df.to_csv(output_path, index=False)
print(f" Cleaned men dataset saved to {output_path} ({len(df)} rows).")
