import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def plot_signals(
    final_features_path: str, 
    output_html_path: str, 
    ticker: str
):
    """
    Creates an interactive plot of market price, sentiment, and news volume.

    Args:
        final_features_path (str): Path to the final feature table CSV.
        output_html_path (str): Path to save the interactive HTML plot.
        ticker (str): The ticker symbol for labeling.
    """
    # Load the final data
    df = pd.read_csv(final_features_path, index_col='Date', parse_dates=True)

    # Create a figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                          vertical_spacing=0.1, 
                          subplot_titles=(f'{ticker} Price', 'Sentiment and News Volume'),
                          row_heights=[0.7, 0.3])

    # --- Plot 1: Price ---
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close Price'), row=1, col=1)

    # --- Plot 2: Sentiment and Volume ---
    # Sentiment Score
    fig.add_trace(go.Scatter(x=df.index, y=df['sentiment_mean'], name='Mean Sentiment', 
                               line=dict(color='orange')), row=2, col=1)
    
    # News Volume (on a secondary y-axis)
    fig.add_trace(go.Bar(x=df.index, y=df['news_count'], name='News Volume', 
                           marker=dict(color='lightblue'), opacity=0.5), row=2, col=1)

    # --- Layout and Formatting ---
    fig.update_layout(
        title_text=f'Crypto Alpha Signals: {ticker}',
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Sentiment", row=2, col=1)

    # Save to HTML
    fig.write_html(output_html_path)
    print(f"Successfully created and saved plot to {output_html_path}")

if __name__ == '__main__':
    # Example usage
    TICKER = 'BTC-USD'
    FROM_DATE = '2024-06-08'
    TO_DATE = '2024-07-08'

    # Input path
    INPUT_PATH = os.path.join(
        '..', '..', 'data', 'final_features',
        f"final_{TICKER}_{FROM_DATE}_{TO_DATE}.csv"
    )

    # Output path
    OUTPUT_DIR = os.path.join('..', '..', 'data', 'final_features')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_HTML_PATH = os.path.join(OUTPUT_DIR, f"plot_{TICKER}_{FROM_DATE}_{TO_DATE}.html")

    if not os.path.exists(INPUT_PATH):
        print(f"Input file not found: {INPUT_PATH}")
        print("Please run the main.py script first to generate the final features.")
    else:
        plot_signals(INPUT_PATH, OUTPUT_HTML_PATH, TICKER)
