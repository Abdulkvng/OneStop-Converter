import requests

alpha_vantage_api_key = 
coingecko_api_key = 
exchange_rate_api_key =   # Your actual API key

def get_stock_price(symbol):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'apikey': alpha_vantage_api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'Note' in data:
        raise ValueError("API limit reached, please try again later.")
    
    time_series = data.get('Time Series (1min)')
    if not time_series:
        raise ValueError("Invalid stock symbol or no data available.")
    
    latest_timestamp = sorted(time_series.keys())[-1]
    latest_data = time_series[latest_timestamp]
    return float(latest_data['1. open'])

def get_crypto_price(crypto_id):
    url = f'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': crypto_id,
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if crypto_id not in data:
        raise ValueError("Invalid cryptocurrency ID or no data available.")
    return float(data[crypto_id]['usd'])

def get_exchange_rate(from_currency, to_currency):
    url = f'https://v6.exchangerate-api.com/v6/{exchange_rate_api_key}/pair/{from_currency}/{to_currency}'
    response = requests.get(url)
    data = response.json()
    
    if data['result'] != 'success':
        raise ValueError("Error fetching exchange rate data.")
    
    return data['conversion_rate']

def convert_assets(from_asset, to_asset, amount):
    from_price = 0
    to_price = 0
    from_asset_type = ''
    to_asset_type = ''
    is_from_crypto = from_asset.startswith('crypto:')
    is_to_crypto = to_asset.startswith('crypto:')
    is_from_currency = from_asset.startswith('currency:')
    is_to_currency = to_asset.startswith('currency:')

    if is_from_crypto:
        from_price = get_crypto_price(from_asset.replace('crypto:', ''))
        from_asset_type = 'cryptocurrency'
    elif is_from_currency:
        from_price = 1  # Currency conversion does not need a price, handled separately
        from_currency = from_asset.replace('currency:', '')
        from_asset_type = 'currency'
    else:
        from_price = get_stock_price(from_asset)
        from_asset_type = 'stock'
    
    if is_to_crypto:
        to_price = get_crypto_price(to_asset.replace('crypto:', ''))
        to_asset_type = 'cryptocurrency'
    elif is_to_currency:
        to_price = 1  # Currency conversion does not need a price, handled separately
        to_currency = to_asset.replace('currency:', '')
        to_asset_type = 'currency'
    else:
        to_price = get_stock_price(to_asset)
        to_asset_type = 'stock'

    if is_from_currency and is_to_currency:
        exchange_rate = get_exchange_rate(from_currency, to_currency)
        converted_amount = amount * exchange_rate
        print(f"Converting {amount} {from_currency} to {to_currency}:")
        print(f"Exchange rate: 1 {from_currency} = {exchange_rate:.4f} {to_currency}")
        return converted_amount
    elif is_from_currency and not is_to_currency:
        exchange_rate = get_exchange_rate(from_currency, 'usd')
        amount_in_usd = amount * exchange_rate
        converted_amount = amount_in_usd / to_price
        print(f"Converting {amount} of {from_asset_type} ({from_asset}):")
        print(f"Current price of {from_asset}: {exchange_rate:.2f} USD/{from_currency}")
        print(f"Total value in USD: ${amount_in_usd:.2f}")
        print(f"Current price of {to_asset}: ${to_price:.2f}")
        print(f"Conversion rate: 1 {from_currency} = {to_price / exchange_rate:.4f} {to_asset}")
        return converted_amount
    elif not is_from_currency and is_to_currency:
        exchange_rate = get_exchange_rate('usd', to_currency)
        total_value_in_usd = amount * from_price
        converted_amount = total_value_in_usd * exchange_rate
        print(f"Converting {amount} of {from_asset_type} ({from_asset}):")
        print(f"Current price of {from_asset}: ${from_price:.2f}")
        print(f"Total value in USD: ${total_value_in_usd:.2f}")
        print(f"Current price of {to_asset}: {exchange_rate:.2f} {to_currency}/USD")
        print(f"Conversion rate: 1 {from_asset} = {exchange_rate * from_price:.4f} {to_asset}")
        return converted_amount
    else:
        total_value_in_from_asset = amount * from_price
        converted_amount = total_value_in_from_asset / to_price
        print(f"Converting {amount} of {from_asset_type} ({from_asset}):")
        print(f"Current price of {from_asset}: ${from_price:.2f}")
        print(f"Total value: ${total_value_in_from_asset:.2f}")
        print(f"Current price of {to_asset}: ${to_price:.2f}")
        print(f"Conversion rate: 1 {from_asset} = {to_price/from_price:.4f} {to_asset}")
        return converted_amount

try:
    from_asset = input("Enter the asset symbol to convert from (e.g., AAPL, crypto:bitcoin, or currency:USD): ").lower()
    to_asset = input("Enter the asset symbol to convert to (e.g., NVDA, crypto:ethereum, or currency:EUR): ").lower()
    amount = float(input("Enter the amount to convert: "))

    converted_amount = convert_assets(from_asset, to_asset, amount)
    
    print(f"{amount} of {from_asset} is equal to {converted_amount:.4f} of {to_asset}")
except ValueError as e:
    print(e)
except Exception as e:
    print(f"An error occurred: {e}")
