import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


class KrakenDataProvider:
    def __init__(self):
        self.base_url = "https://api.kraken.com/0/public"

    def get_first_trade_date(self, pair):
        # Отримання першої дати торгів для пари
        df = self.get_ohlc_data(
            pair, "21600"
        )  # Використовуємо максимальний інтервал для ефективності
        if not df.empty:
            return df["timestamp"].min()
        return None

    def get_trading_pairs(self):
        # Отримання списку всіх торгових пар з USD
        pairs = self.get_asset_pairs()
        # Фільтруємо тільки пари з USD

        filtered_pairs = {}
        for key in pairs.keys():
            if key.endswith("USD"):
                filtered_pairs[pairs[key]["base"]] = key

        return filtered_pairs

    def get_asset_pairs(self):
        # Отримання доступних торгових пар
        response = requests.get(f"{self.base_url}/AssetPairs")
        if response.status_code == 200:
            return response.json()["result"]
        return {}

    def get_ohlc_data(self, pair, interval="1440"):
        # Отримання OHLC даних interval у хвилинах: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600
        params = {
            "pair": pair,
            "interval": interval,
            "since": int((datetime.now() - timedelta(days=365 * 10)).timestamp()),
        }
        response = requests.get(f"{self.base_url}/OHLC", params=params)
        if response.status_code != 200:
            raise Exception("Помилка під час отримання даних")

        data = response.json()["result"][pair]

        print(data[0])

        # Перетворення даних у DataFrame
        df = pd.DataFrame(
            data,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "vwap",
                "volume",
                "count",
            ],
        )

        # Конвертація типів даних
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        for col in ["open", "high", "low", "close", "vwap", "volume"]:
            df[col] = df[col].astype(float)

        return df

    def create_visualization(self, pair, interval="1440", days_back=30):
        # Створення візуалізації з графіком ціни та обсягу
        # Отримання даних
        df = self.get_ohlc_data(pair, interval)

        # Створення графіка з підграфіком
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f"Price {pair}", "Trading volume"),
            row_heights=[0.7, 0.3],
        )

        focus_start = datetime.now() - timedelta(days=days_back)
        focus_end = datetime.now()

        fig.update_xaxes(range=[focus_start, focus_end])

        # Додавання графіка ціни
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["close"],
                mode="lines",
                name="Close date",
                line=dict(color="blue"),
            ),
            row=1,
            col=1,
        )

        # Додавання графіка обсягу
        fig.add_trace(
            go.Bar(
                x=df["timestamp"],
                y=df["volume"],
                name="Volume",
                marker_color="rgba(0,0,255,0.3)",
            ),
            row=2,
            col=1,
        )

        # Налаштування макета
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"Chart of {pair} for the last {days_back} days",
            xaxis_rangeslider_visible=False,
        )

        return fig
