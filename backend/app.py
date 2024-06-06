from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import csv
import os

app = Flask(__name__)
CORS(app)

class PriceComparison:
    def __init__(self):
        self.results = []
        self.headers = {
            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

    def fetch(self, url):
        response = requests.get(url, headers=self.headers)
        return response

    def parseMobile(self, response):
        content = BeautifulSoup(response.text, 'lxml')
        deck = content.find('ul', {'class': 'sctn prdct-grid prdct-grid--s prdct-grid--list prdct-grid--prdct-s prdct-grid--spcftn-4 prdct-grid--spcftn-4-cmpr clearfix'})
        if deck:
            for card in deck.find_all('li', {'class': 'prdct-item clearfix card prdt-item-other'}):
                name = card.find('div', {'class': 'prdct-item__img-wrpr js-open-link ga_event_cls'}).find('img')['alt']
                details = card.find('ul', {'class': 'prdct-item__spcftn-clmn'}).text
                ratings = card.find('div', {'class': 'specs_rate algn-left'})
                rating = ratings.find_next('span').text.strip() if ratings else "N/A"
                amazon_span = card.find('span', text='Amazon')
                amazon_price = amazon_span.find_next('div').text.strip() if amazon_span else "N/A"
                croma_span = card.find('span', text='Croma')
                croma_price = croma_span.find_next('div').text.strip() if croma_span else "N/A"
                flipkart_span = card.find('span', text='Flipkart')
                flipkart_price = flipkart_span.find_next('div').text.strip() if flipkart_span else "N/A"
                self.results.append({
                    'name': name,
                    'Details': details,
                    'Ratings': rating,
                    'AmazonPrice': amazon_price,
                    'ChromaPrice': croma_price,
                    'FlipkartPrice': flipkart_price
                })

    def parseLaptop(self, response):
        content = BeautifulSoup(response.text, 'lxml')
        deck = content.find('ul', {'class': 'sctn prdct-grid prdct-grid--s prdct-grid--list prdct-grid--prdct-s prdct-grid--spcftn-4 prdct-grid--spcftn-4-cmpr clearfix'})
        if deck:
            for card in deck.find_all('li', {'class': 'prdct-item clearfix card prdt-item-other msp_othr_items'}):
                name = card.find('div', {'class': 'prdct-item__img-wrpr js-open-link ga_event_cls'}).find('img')['alt']
                details = card.find('ul', {'class': 'prdct-item__spcftn-clmn exp_lists'}).text
                ratings = card.find('div', {'class': 'specs_rate algn-left'})
                rating = ratings.find_next('span').text.strip() if ratings else "N/A"
                amazon_span = card.find('span', text='Amazon')
                amazon_price = amazon_span.find_next('div').text.strip() if amazon_span else "N/A"
                croma_span = card.find('span', text='Croma')
                croma_price = croma_span.find_next('div').text.strip() if croma_span else "N/A"
                flipkart_span = card.find('span', text='Flipkart')
                flipkart_price = flipkart_span.find_next('div').text.strip() if flipkart_span else "N/A"
                self.results.append({
                    'name': name,
                    'Details': details,
                    'Ratings': rating,
                    'AmazonPrice': amazon_price,
                    'ChromaPrice': croma_price,
                    'FlipkartPrice': flipkart_price
                })


    def to_csv(self, filename):
        with open(filename, 'w', newline='') as csv_file:
            if self.results:
                writer = csv.DictWriter(csv_file, fieldnames=self.results[0].keys())
                writer.writeheader()
                for row in self.results:
                    writer.writerow(row)
            else:
                raise ValueError("No data available to write to CSV")

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    scraper = PriceComparison()
    response = scraper.fetch(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch the URL'}), 400

    scraper.parse(response)
    try:
        scraper.to_csv('scraped_data.csv')
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Scraping completed', 'filename': 'scraped_data.csv'}), 200

@app.route('/download', methods=['GET'])
def download():
    filename = 'scraped_data.csv'
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
