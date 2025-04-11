from flask import Flask, request, jsonify
import json
import requests
import re
from urllib.parse import unquote

app = Flask(__name__)

def get_instagram_graphql_data(instagram_url):
    reeldown_url = "https://reeldown.io/reels/api/download/"
    payload = json.dumps({"url": instagram_url})
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.post(reeldown_url, headers=headers, data=payload)
        error_data = response.json()
        
        if 'error' not in error_data:
            return {"error": "Unexpected response from Reeldown"}
        
        error_message = error_data['error']
        url_pattern = r'https://www\.instagram\.com/graphql/query\?[^\s]+'
        match = re.search(url_pattern, error_message)
        
        if not match:
            return {"error": "Could not extract GraphQL URL"}
        
        graphql_url = match.group(0)
        decoded_url = unquote(graphql_url)
        
        graphql_response = requests.get(decoded_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0'
        })
        
        if graphql_response.status_code != 200:
            return {"error": f"Failed to fetch GraphQL data (status {graphql_response.status_code})"}
        
        return graphql_response.json()
        
    except Exception as e:
        return {"error": str(e)}

@app.route('/extract', methods=['GET'])
def extract_data():
    instagram_url = request.args.get('url')
    if not instagram_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    
    result = get_instagram_graphql_data(instagram_url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)