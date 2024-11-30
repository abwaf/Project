from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
from datetime import datetime
from KrakenAPI import KrakenDataProvider
from CoinAPI import CoinCapProvider

# Константи з LineChartHistoryDate
PERIOD_VALUES = {
    "15m": (15, 7),
    "30m": (30, 15),
    "1h": (60, 30),
    "4h": (240, 90),
    "1d": (1440, 365),
    "1w": (10080, 365 * 3),
    "all": (21600, None),
}


class CombinedDashboard:
    def __init__(self):
        self.app = Dash(__name__)
        self.coin_cap = CoinCapProvider()
        self.kraken = KrakenDataProvider()
        self.symbol_ticker = self.kraken.get_trading_pairs()
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        self.app.layout = html.Div(
            [
                html.H1("Cryptocurrency Dashboard", style={"textAlign": "left"}),
                # Controls Section
                html.Div(
                    [
                        html.Button(
                            "Refresh All Data",
                            id="refresh-button",
                            style={"margin": "10px", "padding": "10px"},
                        ),
                        html.Div(
                            id="last-update-time",
                            style={"textAlign": "left", "margin": "10px"},
                        ),
                    ]
                ),
                # Line Chart Section
                html.Div(
                    [
                        html.H2("Price History", style={"textAlign": "left"}),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Label("Period"),
                                        dcc.Dropdown(
                                            id="period",
                                            options=list(PERIOD_VALUES.keys()),
                                            value="1d",
                                            clearable=False,
                                        ),
                                    ],
                                    style={"padding": 10, "flex": 1},
                                ),
                                html.Div(
                                    children=[
                                        html.Label("Symbol"),
                                        dcc.Dropdown(
                                            id="symbol",
                                            options=list(self.symbol_ticker.keys()),
                                            value="XXBT",
                                            clearable=False,
                                        ),
                                    ],
                                    style={"padding": 10, "flex": 1},
                                ),
                            ],
                            style={"display": "flex", "flexDirection": "row"},
                        ),
                        dcc.Graph(id="line-chart"),
                    ],
                    style={"marginBottom": "40px"},
                ),
                # Volume Chart Top-10
                html.Div(
                    [
                        html.H2("Volume Chart Top-10 Crypto", style={"textAlign": "left"}),
                        dcc.Graph(id="volume-chart"),
                    ],
                ),
                # Bar Chart Section
                html.Div(
                    [
                        html.H2("Price Changes Diagram", style={"textAlign": "left"}),
                        dcc.Graph(id="changes-chart"),
                        # Changes Table
                        html.Div(
                            [
                                html.H3(
                                    "Detailed Changes Data", style={"textAlign": "left"}
                                ),
                                dash_table.DataTable(
                                    id="changes-table",
                                    columns=[
                                        {"name": "Symbol", "id": "Symbol"},
                                        {"name": "Name", "id": "Name"},
                                        {"name": "24h (%)", "id": "24h"},
                                        {"name": "7d (%)", "id": "7d"},
                                        {"name": "30d (%)", "id": "30d"},
                                        {"name": "60d (%)", "id": "60d"},
                                    ],
                                    style_table={"overflowX": "auto"},
                                    style_cell={
                                        "textAlign": "left",
                                        "padding": "10px",
                                        "minWidth": "100px",
                                    },
                                    style_header={
                                        "backgroundColor": "rgb(230, 230, 230)",
                                        "fontWeight": "bold",
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {
                                                "filter_query": "{24h} < 0 || {7d} < 0 || {30d} < 0 || {60d} < 0"
                                            },
                                            "color": "red",
                                        },
                                        {
                                            "if": {
                                                "filter_query": "{24h} > 0 || {7d} > 0 || {30d} > 0 || {60d} > 0"
                                            },
                                            "color": "green",
                                        },
                                    ],
                                ),
                            ],
                            style={"margin": "20px"},
                        ),
                    ],
                    style={"marginBottom": "40px"},
                ),
                # Market Cap Section
                html.Div(
                    [
                        html.H2("Market Cap Distribution", style={"textAlign": "left"}),
                        dcc.Graph(id="market-cap-pie"),
                        # Crypto Table
                        html.Div(
                            [
                                html.H3(
                                    "Top 10 Cryptocurrencies",
                                    style={"textAlign": "left"},
                                ),
                                dash_table.DataTable(
                                    id="crypto-table",
                                    columns=[
                                        {"name": "Rank", "id": "Rank"},
                                        {"name": "Symbol", "id": "Symbol"},
                                        {"name": "Name", "id": "Name"},
                                        {"name": "Price (USD)", "id": "Price (USD)"},
                                        {
                                            "name": "Market Cap (B)",
                                            "id": "Market Cap (B)",
                                        },
                                        {
                                            "name": "Volume 24h (M)",
                                            "id": "Volume 24h (M)",
                                        },
                                        {
                                            "name": "Change 24h (%)",
                                            "id": "Change 24h (%)",
                                        },
                                    ],
                                    style_table={"overflowX": "auto"},
                                    style_cell={
                                        "textAlign": "left",
                                        "padding": "10px",
                                        "minWidth": "100px",
                                    },
                                    style_header={
                                        "backgroundColor": "rgb(230, 230, 230)",
                                        "fontWeight": "bold",
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {
                                                "filter_query": '{Change 24h (%)} contains "-"',
                                                "column_id": "Change 24h (%)",
                                            },
                                            "color": "red",
                                        },
                                        {
                                            "if": {
                                                "filter_query": '{Change 24h (%)} > "0"',
                                                "column_id": "Change 24h (%)",
                                            },
                                            "color": "green",
                                        },
                                    ],
                                ),
                            ],
                            style={"margin": "20px"},
                        ),
                    ]
                ),
                # Interval component for auto-refresh
                dcc.Interval(
                    id="interval-component",
                    interval=60 * 1000,  # refresh every minute
                    n_intervals=0,
                ),
            ]
        )

    def setup_callbacks(self):
        @self.app.callback(
            Output("line-chart", "figure"),
            [
                Input("symbol", "value"),
                Input("period", "value"),
                Input("refresh-button", "n_clicks"),
            ],
        )
        def update_line_chart(symbol, period, n_clicks):

            interval, days = PERIOD_VALUES.get(period)
            ticker = self.symbol_ticker.get(symbol)
            # Якщо обрано період «all», обчислюємо кількість днів з першої торгівлі
            if period == "all":
                first_date = self.kraken.get_first_trade_date(ticker)
                if first_date:
                    days = (pd.Timestamp.now() - first_date).days
                else:
                    days = (
                        365 * 8
                    )  # Fallback на 8 років якщо не вдалося отримати першу дату
            return self.kraken.create_visualization(ticker, interval, days)

        @self.app.callback(
            [
                Output("market-cap-pie", "figure"),
                Output("crypto-table", "data"),
                Output("volume-chart", "figure"),
                Output("changes-chart", "figure"),
                Output("changes-table", "data"),
                Output("last-update-time", "children"),
            ],
            [
                Input("refresh-button", "n_clicks"),
                Input("interval-component", "n_intervals"),
            ],
        )
        def update_all_data(n_clicks, n_intervals):
            # Get market cap and table data
            market_cap_figure = self.coin_cap.create_market_cap_figure()
            table_data = self.coin_cap.create_market_table()
            volume_chart = self.coin_cap.create_volume_chart()

            # Get changes data
            changes_figure = self.coin_cap.create_stacked_bar_chart()
            changes_df = self.coin_cap.get_top_assets_changes()
            changes_table_data = (
                changes_df.round(2).to_dict("records") if changes_df is not None else []
            )

            update_time = (
                f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            return (
                market_cap_figure,
                table_data,
                volume_chart,
                changes_figure,
                changes_table_data,
                update_time,
            )

    def run_server(self, debug=True, host="0.0.0.0", port=8050):
        self.app.run_server(debug=debug, host=host, port=port)


if __name__ == "__main__":
    dashboard = CombinedDashboard()
    dashboard.run_server()
