# Tesla Stock Price vs Revenue Analysis
# Goal: compare Tesla's share price with its quarterly revenue.
# Tip: each chart opens in a window. Close the window to continue the program.

import os
import pandas as pd
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup

# Folder to save the charts (used later in the README)
os.makedirs("images", exist_ok=True)

# ---------------------------------------------------------
# Step 1: Get Tesla share price data (from Yahoo Finance)
# ---------------------------------------------------------
tesla = yf.Ticker("TSLA")
stock = tesla.history(period="max")
stock = stock.reset_index()

# Remove the time zone so dates are easy to compare
stock["Date"] = pd.to_datetime(stock["Date"]).dt.tz_localize(None)

print("Share price data:")
print(stock[["Date", "Open", "Close", "Volume"]].head())

# ---------------------------------------------------------
# Step 2: Get Tesla revenue data (scraped from a web page)
# ---------------------------------------------------------
url = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/revenue.htm"
)
html_data = requests.get(url).text
soup = BeautifulSoup(html_data, "html.parser")

# Find the table and read the date and revenue from each row
table = soup.find("table")
rows = []
for row in table.find_all("tr"):
    cells = row.find_all("td")
    if len(cells) >= 2:
        date = cells[0].text.strip()
        revenue_text = cells[1].text.strip()
        rows.append({"Date": date, "Revenue": revenue_text})

revenue = pd.DataFrame(rows)

# ---------------------------------------------------------
# Step 3: Clean the revenue data
# ---------------------------------------------------------
# Remove "$" and "," so revenue becomes a number
revenue["Revenue"] = revenue["Revenue"].str.replace(r"[,$]", "", regex=True)

# Remove empty rows
revenue = revenue[revenue["Revenue"] != ""]

# Change the data types
revenue["Revenue"] = revenue["Revenue"].astype(float)
revenue["Date"] = pd.to_datetime(revenue["Date"])

print("\nRevenue data (last 5 rows):")
print(revenue.tail())

# ---------------------------------------------------------
# Step 4: Keep the same time period in both datasets
# The revenue data ends in 2021, so we cut the share price data there too.
# ---------------------------------------------------------
stock = stock[stock["Date"] <= "2021-06-14"]
revenue = revenue[revenue["Date"] <= "2021-04-30"]

# ---------------------------------------------------------
# Step 5: Chart 1 - share price (top) and revenue (bottom)
# ---------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

axes[0].plot(stock["Date"], stock["Close"], color="blue")
axes[0].set_ylabel("Price (US$)")
axes[0].set_title("Tesla - Historical Share Price")

axes[1].plot(revenue["Date"], revenue["Revenue"], color="green")
axes[1].set_ylabel("Revenue (US$ Millions)")
axes[1].set_xlabel("Date")
axes[1].set_title("Tesla - Historical Revenue")

plt.tight_layout()
plt.savefig("images/tesla_price_vs_revenue.png", dpi=150)
plt.show()

# ---------------------------------------------------------
# Step 6: Compare price and revenue quarter by quarter
# Revenue is reported every quarter, but price changes every day.
# So we take the average price of each quarter to compare them fairly.
# ---------------------------------------------------------
stock["Quarter"] = stock["Date"].dt.to_period("Q")
revenue["Quarter"] = revenue["Date"].dt.to_period("Q")

average_price = stock.groupby("Quarter")["Close"].mean()
quarterly_revenue = revenue.groupby("Quarter")["Revenue"].last()

# Keep only the quarters that exist in both
combined = pd.concat([average_price, quarterly_revenue], axis=1, join="inner")
combined.columns = ["Average Price", "Revenue"]

correlation = combined["Average Price"].corr(combined["Revenue"])
print("\nNumber of quarters compared:", len(combined))
print("Correlation between average price and revenue:", round(correlation, 2))
print("(Close to 1 = they rise together. It does not prove one causes the other.)")

# ---------------------------------------------------------
# Step 7: Chart 2 - average price vs revenue
# ---------------------------------------------------------
sns.regplot(x="Revenue", y="Average Price", data=combined)
plt.xlabel("Quarterly Revenue (US$ Millions)")
plt.ylabel("Average Share Price (US$)")
plt.title("Tesla - Revenue vs Average Share Price (each dot = one quarter)")
plt.savefig("images/tesla_revenue_vs_price.png", dpi=150)
plt.show()
