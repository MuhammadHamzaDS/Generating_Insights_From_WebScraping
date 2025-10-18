import requests
from bs4 import BeautifulSoup
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================
# 🧠 STEP 1: MySQL CONNECTION
# ==============================
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # <-- agar tumhara username kuch aur hai to badlo
    password="lenovo&9090",
)
cursor = conn.cursor()

# Create database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS quotes_db")
cursor.execute("USE quotes_db")

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quote TEXT,
    author VARCHAR(255),
    tags VARCHAR(255)
)
""")

# ==============================
# 🕸️ STEP 2: WEB SCRAPING
# ==============================
base_url = "https://quotes.toscrape.com/page/{}/"

for page in range(1, 6):
    res = requests.get(base_url.format(page))
    soup = BeautifulSoup(res.text, "html.parser")

    for quote_block in soup.select(".quote"):
        quote = quote_block.select_one(".text").get_text(strip=True)
        author = quote_block.select_one(".author").get_text(strip=True)
        tags = ", ".join([t.get_text(strip=True) for t in quote_block.select(".tags .tag")])

        cursor.execute(
            "INSERT INTO quotes (quote, author, tags) VALUES (%s, %s, %s)",
            (quote, author, tags)
        )

    print(f"✅ Page {page} scraped successfully")

conn.commit()
print("✅ All data saved to MySQL!")

# ==============================
# 📊 STEP 3: DATA ANALYSIS
# ==============================
# Reconnect using pandas (important: use database now)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="lenovo&9090",
    database="quotes_db"
)

# 1️⃣ Top Authors by Quote Count
query1 = """
SELECT author, COUNT(*) AS total_quotes
FROM quotes
GROUP BY author
ORDER BY total_quotes DESC
LIMIT 10;
"""
df_authors = pd.read_sql(query1, conn)

plt.figure(figsize=(10,6))
sns.barplot(x="total_quotes", y="author", data=df_authors, palette="viridis")
plt.title("Top 10 Authors by Number of Quotes")
plt.xlabel("Total Quotes")
plt.ylabel("Author")
plt.tight_layout()
plt.show()

# 2️⃣ Quotes with 'life' and 'love'
query2 = """
SELECT
  SUM(CASE WHEN quote LIKE '%life%' THEN 1 ELSE 0 END) AS life_quotes,
  SUM(CASE WHEN quote LIKE '%love%' THEN 1 ELSE 0 END) AS love_quotes
FROM quotes;
"""
df_keywords = pd.read_sql(query2, conn)

plt.figure(figsize=(6,5))
sns.barplot(x=df_keywords.columns, y=df_keywords.iloc[0], palette="cool")
plt.title("Quotes Containing 'Life' vs 'Love'")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# 3️⃣ Most Common Tags
query3 = "SELECT tags FROM quotes;"
df_tags = pd.read_sql(query3, conn)

all_tags = []
for tags in df_tags["tags"]:
    if tags:
        all_tags.extend([t.strip() for t in tags.split(",")])

tag_series = pd.Series(all_tags).value_counts().head(10)

plt.figure(figsize=(10,6))
sns.barplot(x=tag_series.values, y=tag_series.index, palette="mako")
plt.title("Top 10 Most Common Tags")
plt.xlabel("Frequency")
plt.ylabel("Tag")
plt.tight_layout()
plt.show()

conn.close()
print("✅ Visualization Completed Successfully!")
