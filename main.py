# Flask app
from flask import Flask, jsonify, render_template, request
import arrow
import requests
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app = Flask(__name__)

# Initialize VADER sentiment analyzer
nltk.download('punkt')
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Define your API keys and endpoints
sea_level_url = 'https://api.stormglass.io/v2/tide/sea-level/point'
news_base_url = 'https://newsapi.org/v2/everything'

# Function to fetch weather data from API
def fetch_weather_data(latitude, longitude):
    start = arrow.now().floor('day')
    end = arrow.now().shift(days=1).floor('day')

    params = {
        'lat': latitude,
        'lng': longitude,
        'start': start.to('UTC').timestamp(),
        'end': end.to('UTC').timestamp(),
    }
    # Fetch weather data from API
    response = requests.get(sea_level_url, params=params)
    weather_data = response.json()

    return weather_data

# Function to fetch news articles and perform sentiment analysis
def fetch_and_analyze_news(latitude, longitude):
    params = {
        'q': 'wion',  # Search keyword to find news related to ports
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 10,
        'lat': latitude,
        'lon': longitude,
        'radius': 50,
    }
    # Fetch news data from API
    response = requests.get(news_base_url, params=params)
    news_data = response.json()

    # Perform sentiment analysis
    sentiment_data = sia.polarity_scores(str(news_data))

    return sentiment_data

# Route to render HTML template with form
@app.route('/', methods=['GET', 'POST'])
def display_form():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        weather_data = fetch_weather_data(latitude, longitude)
        sentiment_data = fetch_and_analyze_news(latitude, longitude)
        return render_template('F.html', weather_data=weather_data, sentiment_data=sentiment_data)
    else:
        return render_template('F.html', weather_data=None, sentiment_data=None)

if __name__ == '__main__':
    app.run(debug=True)