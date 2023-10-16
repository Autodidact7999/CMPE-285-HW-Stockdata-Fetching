from flask import Flask, request, render_template
import datetime
import yfinance as yf
import plotly.graph_objs as go
import plotly.offline as pyo
import pandas as pd
import requests

app = Flask(__name__)

def get_company_logo(company_name):
    response = requests.get(f"https://logo.clearbit.com/{company_name}")
    if response.status_code == 200:
        return response.url
    else:
        return None

def get_stock_info(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1mo")  # get 1 month's data

    if hist.empty:
        raise ValueError("Invalid symbol: " + symbol)

    info = stock.info
    if not info:
        raise ValueError(f"No data available for symbol: {symbol}")

    current_time = datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y')
    company_name = info.get('longName', "N/A")
    logo_url = get_company_logo(company_name)
    current_price = info.get('currentPrice', 0)
    previous_close = info.get('regularMarketPreviousClose', 0)
    value_change = current_price - previous_close
    value_change_sign = "+" if value_change >= 0 else "-"
    percent_change = (value_change / previous_close) * 100 if previous_close else 0
    percent_change_sign = "+" if percent_change >= 0 else "-"

    # process data for plotting
    hist = hist.reset_index()
    fig = go.Figure(data=[go.Candlestick(x=hist['Date'],
                                         open=hist['Open'], high=hist['High'],
                                         low=hist['Low'], close=hist['Close'])])
    fig.update_layout(title='Stock Price', xaxis_rangeslider_visible=False)
    plot_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)

    return {
        'time': current_time,
        'name': company_name,
        'symbol':symbol,
        'price': f'{current_price:.2f}',
        'value_change': f'{value_change_sign}{abs(value_change):.2f}',
        'percent_change': f'{percent_change_sign}{abs(percent_change):.2f}%',
        'plot_div': plot_div,
        'logo_url': logo_url
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    data = None
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        try:
            data = get_stock_info(symbol)
        except ValueError as e:
            error = str(e)

    return render_template('index.html', error=error, data=data)


if __name__ == "__main__":
    app.run(debug=True)