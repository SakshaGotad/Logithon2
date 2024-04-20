from flask import Flask, render_template, request, jsonify
import requests
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import arrow

app = Flask(__name__)

# Initialize VADER sentiment analyzer
nltk.download('punkt')
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        
        weather_data = fetch_weather_data(latitude, longitude)
        sentiment_data = fetch_and_analyze_news(latitude, longitude)
        
        return render_template('F.html', weather_data=weather_data, sentiment_data=sentiment_data)
    
    return render_template('F.html', weather_data=None, sentiment_data=None)

def fetch_weather_data(latitude, longitude):
    api_key = '9a0986ea-f820-11ee-a75c-0242ac130002-9a098794-f820-11ee-a75c-0242ac130002'
    base_url = 'https://api.stormglass.io/v2/tide/sea-level/point'
    
    start = arrow.now().floor('day')
    end = arrow.now().shift(days=1).floor('day')

    params = {
        'lat': latitude,
        'lng': longitude,
        'start': start.to('UTC').timestamp(),
        'end': end.to('UTC').timestamp(),
    }
    headers = {
        'Authorization': api_key
    }
    
    response = requests.get(base_url, params=params, headers=headers)
    
    if response.status_code == 200:
        weather_data = response.json()
        return classify_weather(weather_data)
    else:
        return "Unknown"

def classify_weather(weather_data):
    # Extract tidal sea level data
    tidal_data = weather_data.get('data', [])

    # Define thresholds for tide levels
    thresholds = [i * (1 / 10) for i in range(10)]

    for entry in tidal_data:
        sea_level = entry.get('sg', 0)

        # Assign category based on tide level
        category = None
        for i, threshold in enumerate(thresholds):
            if sea_level <= threshold:
                category = f'Tide Level {i + 1}'
                break

        entry['Category'] = category

    return tidal_data

def fetch_and_analyze_news(latitude, longitude):
    api_key = '319b436cf8424ac3bb105e021bb966b1'
    base_url = 'https://newsapi.org/v2/everything'
    
    params = {
        'apiKey': api_key,
        'q': 'wion',
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 10,
        'lat': latitude,
        'lon': longitude,
        'radius': 50,
    }
    
    response = requests.get(base_url, params=params)
  
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data['articles']
        
        # Combine titles and descriptions of articles
        article_texts = [article['title'] + '. ' + article['description'] for article in articles]
        article_texts_combined = ' '.join(article_texts)
        
        # Analyze sentiment
        sentiment_score = sia.polarity_scores(article_texts_combined)['compound']
        sentiment = classify_sentiment(sentiment_score)
        
        return sentiment
    else:
        return "Unknown"

def classify_sentiment(score):
    if score >= 0.9:
        return "1"
    elif 0.7 <= score < 0.9:
        return "2"
    elif 0.4 <= score < 0.7:
        return "3"
    elif 0.1 <= score < 0.4:
        return "4"
    elif -0.1 < score < 0.1:
        return "5"
    elif -0.4 <= score < -0.1:
        return "6"
    elif -0.7 <= score < -0.4:
        return "7"
    elif -0.9 <= score < -0.7:
        return "8"
    elif score <= -0.9:
        return "9"
    else:
        return "Unknown"

if __name__ == '__main__':
    app.run(debug=True,port=8080)
