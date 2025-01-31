import os
import requests
from bs4 import BeautifulSoup
import tweepy
from deepseek import DeepSeek
from datetime import datetime, timedelta

# Fetch latest stock results from Moneycontrol
def get_latest_stock_results():
    url = "https://www.moneycontrol.com/india/stockpricequote/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    stocks = []
    for row in soup.select('table.tblchart tr'):
        columns = row.find_all('td')
        if len(columns) > 1:
            stock_name = columns[0].text.strip()
            result_type = columns[1].text.strip()  # Quarterly/Half-Yearly/Yearly
            result_date = columns[2].text.strip()
            stocks.append({
                'name': stock_name,
                'type': result_type,
                'date': result_date
            })

    # Filter stocks with results in the last 24 hours
    now = datetime.now()
    recent_stocks = [
        stock for stock in stocks
        if now - datetime.strptime(stock['date'], '%Y-%m-%d') < timedelta(days=1)
    ]

    return recent_stocks

# Generate X post using DeepSeek R1
def generate_post(stock_data):
    deepseek = DeepSeek(api_key=os.getenv('DEEPSEEK_API_KEY'))
    prompt = f"Generate a concise and engaging X post about the latest {stock_data['type']} results for {stock_data['name']}."
    response = deepseek.generate(prompt)
    return response['choices'][0]['text']

# Post on X using Tweepy
def post_on_x(content):
    auth = tweepy.OAuth1UserHandler(
        os.getenv('API_KEY'), os.getenv('API_SECRET_KEY'),
        os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET')
    )
    api = tweepy.API(auth)
    api.update_status(content)

# Main function
def main():
    stocks = get_latest_stock_results()
    for stock in stocks:
        post_content = generate_post(stock)
        post_on_x(post_content)
        print(f"Posted: {post_content}")

if __name__ == "__main__":
    main()