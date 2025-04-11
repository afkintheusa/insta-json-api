import requests
import json
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to extract the GraphQL URL from reeldown.io
def get_graphql_url(instagram_url):
    url = "https://reeldown.io/reels/api/download/"
    payload = json.dumps({"url": instagram_url})
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': 'https://reeldown.io',
        'Referer': 'https://reeldown.io/',
    }

    response = requests.post(url, headers=headers, data=payload)
    error_message = response.text

    # Extract the GraphQL URL from the response
    graphql_url_match = re.search(r'when accessing (https?://[^\s]+)', error_message)
    
    if graphql_url_match:
        return graphql_url_match.group(1)
    else:
        return None

# API endpoint to get GraphQL URL from Instagram link
@app.route('/json', methods=['GET'])
def get_graphql_json_link():
    instagram_url = request.args.get('url')
    
    if not instagram_url:
        return jsonify({"error": "Instagram URL is required."}), 400
    
    graphql_url = get_graphql_url(instagram_url)
    
    if graphql_url:
        return jsonify({
            "graphql_url": graphql_url,
            "note": "Copy this link and open it in your browser to view the full JSON data."
        })
    else:
        return jsonify({"error": "GraphQL URL could not be extracted."}), 500

# Run the Flask app
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
