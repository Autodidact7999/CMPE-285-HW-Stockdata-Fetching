from flask import Flask, request, render_template
import datetime
import yfinance as yf

app = Flask(__name__)

def get_stock_info(symbol):
    
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        
        if hist.empty:
            raise ValueError("Invalid symbol: " + symbol)

        info = stock.info
        if not info:
            raise ValueError(f"No data available for symbol: {symbol}")


        # Current date and time
        current_time = datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y')

        # Full name of the company
        company_name = info.get('longName', "N/A")

        # Stock price
        current_price = info.get('currentPrice', 0)


        # Value changes
        previous_close = info.get('regularMarketPreviousClose', 0)
        value_change = current_price - previous_close
        
        value_change_sign = "+" if value_change >= 0 else "-"

        # Percentage changes
        percent_change = (value_change / previous_close) * 100 if previous_close else 0
        percent_change_sign = "+" if percent_change >= 0 else "-"

        return {
            'time': current_time,
            'name': company_name,
            'symbol': symbol,
            'price': f'{current_price:.2f}',
            'value_change': f'{value_change_sign}{abs(value_change):.2f}',
            'percent_change': f'{percent_change_sign}{abs(percent_change):.2f}%',
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