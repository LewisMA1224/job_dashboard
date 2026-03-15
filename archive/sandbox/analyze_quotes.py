import pandas as pd

# Load the CSV file
df = pd.read_csv("quotes.csv")

# Show the first few rows
print(df.head())

author_counts = df["author"].value_counts()

print(author_counts)

einstein_quotes = df[df["author"] == "Albert Einstein"]

print(einstein_quotes)

df["quote_length"] = df["quote"].apply(len)

print(df.head())


longest = df.loc[df["quote_length"].idxmax()]

print("\nLongest Quote:")
print(longest)
df.to_csv("processed_quotes.csv", index=False)
