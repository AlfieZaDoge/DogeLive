from flask import Flask, jsonify
import requests
import json
import os

app = Flask(__name__)

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config.json'))

with open(config_path, 'r') as f:
    config = json.load(f)

API_KEY = config.get('API_KEY')
CHANNEL_ID = config.get('CHANNEL_ID')

@app.route('/DogeStreaming', methods=['GET'])
def doge_streaming():
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'channelId': CHANNEL_ID,
        'eventType': 'live',
        'type': 'video',
        'key': API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        video = data['items'][0]
        video_id = video['id']['videoId']
        title = video['snippet']['title']
        live_url = f"https://www.youtube.com/watch?v={video_id}"
        return jsonify({
            'answer': True,
            'StreamURL': live_url,
            'Length': len(live_url),
            'Title': title
        })
    else:
        return jsonify({
            'answer': False,
            'StreamURL': None,
            'Length': None,
            'Title': None
        })

if __name__ == '__main__':
    port = 3231
    print(f"DogeStreaming API is running on http://127.0.0.1:{port}/DogeStreaming")
    app.run(host='0.0.0.0', port=port)
