import pandas as pd
import matplotlib.pyplot as plt

# Read yearly average goals data
df = pd.read_csv("output/yearly_avg_goals.csv")
print(f"Loaded {len(df)} rows from yearly_avg_goals.csv")

# Calculate 5-year rolling averages by gender
df['rolling_avg'] = df.groupby('gender')['avg_goals'].transform(
    lambda x: x.rolling(window=5, min_periods=1).mean()
)

# Create the plot
plt.figure(figsize=(12, 6))
for gender, group in df.groupby('gender'):
    plt.plot(group['year'], group['avg_goals'], alpha=0.3, label=f"{gender} yearly average")
    plt.plot(group['year'], group['rolling_avg'], label=f"{gender} 5-year rolling avg")

plt.title("Scoring Trends Over Time")
plt.xlabel("Year")
plt.ylabel("Average Goals per Match")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the plot
output_file = "output/scoring_trends.png"
plt.savefig(output_file)
print(f"Plot saved to {output_file}")

plt.show()
