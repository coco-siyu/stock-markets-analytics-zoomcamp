# import yfinance as yf
# import pandas as pd

# # Step 1: download just the close column as Series
# close_series = yf.download("^GSPC", start="1950-01-01")["Close"]
# close_series.index = pd.to_datetime(close_series.index)

# # Step 2: get ATHs
# all_time_highs = close_series.cummax()
# ath_dates = close_series[close_series == all_time_highs].index

# # Step 3: loop through corrections
# corrections = []

# for i in range(len(ath_dates) - 1):
#     start_date = ath_dates[i]
#     end_date = ath_dates[i + 1]
#     interim = close_series[start_date:end_date]

#     if interim.empty:
#         continue

#     trough_price = interim.min()
#     trough_date = interim.idxmin()

#     nearest_date = close_series.index.asof(start_date)
#     if pd.isna(nearest_date):
#         continue

#     peak_price = close_series.loc[nearest_date]  # guaranteed to be float (Series)

#     # drawdown = (peak_price - trough_price) / peak_price * 100
#     drawdown = (float(peak_price) - float(trough_price)) / float(peak_price) * 100


#     if drawdown >= 5:
#         duration = (end_date - start_date).days
#         corrections.append({
#             "Start": start_date,
#             "End": end_date,
#             "Bottom": trough_date,
#             "Drawdown (%)": round(drawdown, 2),
#             "Duration (days)": duration
#         })

# # Step 4: results
# df = pd.DataFrame(corrections)
# print(df)

# print("\n📊 Correction Duration Percentiles (in days):")
# print(df["Duration (days)"].quantile([0.25, 0.5, 0.75]))


import pandas as pd
import yfinance as yf

# Step 1: Load earnings data
earnings_df = pd.read_csv("ha1_Amazon.csv", delimiter=";")
earnings_df["date"] = pd.to_datetime(earnings_df["date"])
earnings_df = earnings_df[earnings_df["actual"] > earnings_df["estimate"]].sort_values("date").reset_index(drop=True)

# Step 2: Download historical prices
price_df = yf.download("AMZN", start="2005-01-01")["Close"]
price_df = price_df.to_frame().reset_index().rename(columns={"Date": "date", "Close": "close"})
price_df["date"] = pd.to_datetime(price_df["date"])

# Step 3: Calculate 2-day return: Close_day3 / Close_day1 - 1
price_df["return_2d"] = price_df["close"].shift(-2) / price_df["close"] - 1

# Step 4: Match earnings dates
earnings_returns = []
for e_date in earnings_df["date"]:
    idx = price_df[price_df["date"] >= e_date].index.min()
    if pd.notna(idx) and idx + 2 < len(price_df):
        earnings_returns.append(price_df.loc[idx, "return_2d"])

# Step 5: Median return of earnings surprises
earnings_returns_series = pd.Series(earnings_returns).dropna()
median_surprise_return = earnings_returns_series.median() * 100  # percent

# Step 6: Compare to overall median
overall_median_return = price_df["return_2d"].median() * 100

print("✅ Median 2-day return after positive surprises: {:.2f}%".format(median_surprise_return))
print("📊 Median 2-day return overall: {:.2f}%".format(overall_median_return))
