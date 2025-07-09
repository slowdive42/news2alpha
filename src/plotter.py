import os
import yaml
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_signals(
    final_features_path: str, 
    output_html_path: str, 
    ticker: str
):
    """
    Creates an interactive plot of market price, sentiment, and news volume.
    """
    df = pd.read_csv(final_features_path, index_col='Date', parse_dates=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                          vertical_spacing=0.1, 
                          subplot_titles=(f'{ticker} Price', 'Sentiment and News Volume'),
                          row_heights=[0.7, 0.3])

    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close Price'), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['sentiment_mean'], name='Mean Sentiment', 
                               line=dict(color='orange')), row=2, col=1)
    
    fig.add_trace(go.Bar(x=df.index, y=df['news_count'], name='News Volume', 
                           marker=dict(color='lightblue'), opacity=0.5), row=2, col=1)

    fig.update_layout(
        title_text=f'Crypto Alpha Signals: {ticker}',
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Sentiment", row=2, col=1)

    fig.write_html(output_html_path)
    print(f"Successfully created and saved plot to {output_html_path}")

def _load_config_for_main():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
    if not os.path.exists(config_path):
        config_path = 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    config = _load_config_for_main()
    news_config = config['news']
    market_config = config['market']

    FROM_DATE = str(news_config['from_date'])
    TO_DATE = str(news_config['to_date'])
    SYMBOL = market_config['symbol']

    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, '..', 'data')
    final_features_dir = os.path.join(data_dir, 'final_features')

    INPUT_PATH = os.path.join(
        final_features_dir,
        f"final_{SYMBOL}_{FROM_DATE}_{TO_DATE}.csv"
    )

    OUTPUT_DIR = final_features_dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_HTML_PATH = os.path.join(OUTPUT_DIR, f"plot_{SYMBOL}_{FROM_DATE}_{TO_DATE}.html")

    if not os.path.exists(INPUT_PATH):
        print(f"Input file not found: {INPUT_PATH}")
    else:
        plot_signals(INPUT_PATH, OUTPUT_HTML_PATH, SYMBOL)
