import plotly.graph_objects as go
import requests
import pandas as pd
import time
from datetime import datetime, timedelta


# Ініціалізація програми
class CoinCapProvider:
    def __init__(self):
        self.base_url = "https://api.coincap.io/v2"

    def get_historical_data(self, asset_id, days):
        end = int(time.time() * 1000)
        start = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        try:
            response = requests.get(
                f"{self.base_url}/assets/{asset_id}/history",
                params={"interval": "d1", "start": start, "end": end},
            )
            if response.status_code == 200:
                data = response.json()["data"]
                df = pd.DataFrame(data)
                df["priceUsd"] = pd.to_numeric(df["priceUsd"])
                return df
            return None
        except Exception as e:
            print(f"Error getting data for {asset_id}: {e}")
            return None

    def calculate_price_change(self, df, days):
        if df is None or len(df) < days:
            return None

        start_price = df["priceUsd"].iloc[0]
        end_price = df["priceUsd"].iloc[-1]
        return ((end_price - start_price) / start_price) * 100

    def get_top_assets_changes(self, limit=10):
        try:
            response = requests.get(f"{self.base_url}/assets", params={"limit": limit})
            if response.status_code != 200:
                raise Exception("Error getting asset list")

            assets = response.json()["data"]
            changes_data = []

            for asset in assets:
                asset_id = asset["id"]
                symbol = asset["symbol"]
                name = asset["name"]

                hist_data = self.get_historical_data(asset_id, 90)
                if hist_data is None:
                    continue

                changes = {
                    "Symbol": symbol,
                    "Name": name,
                    "24h": float(asset["changePercent24Hr"]),
                    "7d": self.calculate_price_change(hist_data.tail(7), 7),
                    "30d": self.calculate_price_change(hist_data.tail(30), 30),
                    "60d": self.calculate_price_change(hist_data.tail(60), 60),
                }
                changes_data.append(changes)

            return pd.DataFrame(changes_data)
        except Exception as e:
            print(f"Error getting data: {e}")
            return None

    def create_stacked_bar_chart(self):
        df = self.get_top_assets_changes()
        if df is None:
            return go.Figure()

        periods = ["60d", "30d", "7d", "24h"]
        colors = ["#FF9999", "#FFB366", "#99FF99", "#66B3FF", "#FF99CC"]

        fig = go.Figure()

        for period, color in zip(periods, colors):
            fig.add_trace(
                go.Bar(name=period, x=df["Symbol"], y=df[period], marker_color=color)
            )

        fig.update_layout(
            title={
                "text": "Cryptocurrency Price Changes Over Different Periods",
                "y": 0.95,
                "x": 0.5,
                "xanchor": "left",
                "yanchor": "top",
            },
            xaxis_title="Cryptocurrency",
            yaxis_title="Price Change (%)",
            barmode="group",
            height=600,
            showlegend=True,
            legend_title="Period",
            hovermode="x unified",
        )

        return fig

    def get_market_data(self):
        # Отримання даних про ринок криптовалют
        try:
            response = requests.get(f"{self.base_url}/assets", params={"limit": 250})
            if response.status_code != 200:
                raise Exception("Помилка під час отримання даних")
            data = response.json()["data"]
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Помилка під час отримання даних: {e}")
            return None

    def create_market_cap_figure(self):
        # Створення кругової діаграми капіталізації
        df = self.get_market_data()
        if df is None:
            return go.Figure()

        # Перетворення строкових значень у числові
        df["marketCapUsd"] = pd.to_numeric(df["marketCapUsd"], errors="coerce")
        df["priceUsd"] = pd.to_numeric(df["priceUsd"], errors="coerce")
        df["changePercent24Hr"] = pd.to_numeric(
            df["changePercent24Hr"], errors="coerce"
        )

        # Підготовка даних для топ-10 + others
        top_10 = df.head(10)
        others_market_cap = df[10:]["marketCapUsd"].sum()

        labels = list(top_10["symbol"].str.upper()) + ["OTHERS"]
        values = list(top_10["marketCapUsd"]) + [others_market_cap]

        # Підготовка тексту для спливаючих підказок
        hover_text = []
        for idx, row in top_10.iterrows():
            market_cap_billions = float(row["marketCapUsd"]) / 1_000_000_000
            price = float(row["priceUsd"])
            change_24h = float(row["changePercent24Hr"])
            volume = float(row["volumeUsd24Hr"]) / 1_000_000

            hover_text.append(
                f"Name: {row['name']}<br>"
                + f"Market Cap: ${market_cap_billions:.2f}B<br>"
                + f"Price: ${price:.2f}<br>"
                + f"24h Change: {change_24h:.2f}%<br>"
                + f"24h Volume: ${volume:.2f}M"
            )

        others_billions = others_market_cap / 1_000_000_000
        hover_text.append(
            f"Other Cryptocurrencies<br>Total Market Cap: ${others_billions:.2f}B"
        )

        # Створення кругової діаграми
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,
                    hovertext=hover_text,
                    hoverinfo="text",
                    textposition="inside",
                    textinfo="label+percent",
                    showlegend=True,
                )
            ]
        )

        total_market_cap = sum(values) / 1_000_000_000
        fig.update_layout(
            title={
                "text": f"Розподіл капіталізації криптовалют<br>Загальна капіталізація: ${total_market_cap:.2f}B",
                "y": 0.95,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            annotations=[
                dict(
                    text=f'Топ 10 + Others<br>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    x=0.5,
                    y=0.5,
                    font_size=12,
                    showarrow=False,
                )
            ],
        )

        return fig

    def create_market_table(self):
        # Створення таблиці з даними топ-10 криптовалют
        df = self.get_market_data()
        if df is None:
            return []

        top_10 = df.head(10).copy()

        # Перетворення даних
        top_10["marketCapUsd"] = (
            pd.to_numeric(top_10["marketCapUsd"], errors="coerce") / 1_000_000_000
        )
        top_10["priceUsd"] = pd.to_numeric(top_10["priceUsd"], errors="coerce")
        top_10["changePercent24Hr"] = pd.to_numeric(
            top_10["changePercent24Hr"], errors="coerce"
        )
        top_10["volumeUsd24Hr"] = (
            pd.to_numeric(top_10["volumeUsd24Hr"], errors="coerce") / 1_000_000
        )

        # Форматування даних
        formatted_data = []
        for _, row in top_10.iterrows():
            formatted_data.append(
                {
                    "Rank": row["rank"],
                    "Symbol": row["symbol"].upper(),
                    "Name": row["name"],
                    "Price (USD)": f"${row['priceUsd']:.2f}",
                    "Market Cap (B)": f"${row['marketCapUsd']:.2f}B",
                    "Volume 24h (M)": f"${row['volumeUsd24Hr']:.2f}M",
                    "Change 24h (%)": f"{row['changePercent24Hr']:.2f}%",
                }
            )

        return formatted_data
