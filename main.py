import requests
import json
import re
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to extract the GraphQL URL from reeldown.io
def get_graphql_url(instagram_url):
    url = "https://reeldown.io/reels/api/download/"
    payload = json.dumps({"url": instagram_url})
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Content-Type': 'application/json',
        'Origin': 'https://reeldown.io',
        'Connection': 'keep-alive',
        'Referer': 'https://reeldown.io/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0'
    }

    response = requests.post(url, headers=headers, data=payload)
    error_message = response.text

    # Extract the GraphQL URL from the response
    graphql_url_match = re.search(r'when accessing (https?://[^\s]+)', error_message)
    
    if graphql_url_match:
        return graphql_url_match.group(1)
    else:
        return None

# Function to fetch JSON data from the extracted GraphQL URL
def fetch_json_from_graphql_url(graphql_url):
    if graphql_url:
        response = requests.get(graphql_url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data from GraphQL URL. Status code: {response.status_code}"}
    else:
        return {"error": "No GraphQL URL found."}

# API endpoint to get JSON data from Instagram link
@app.route('/json', methods=['GET'])
def get_instagram_json():
    instagram_url = request.args.get('url')
    
    if not instagram_url:
        return jsonify({"error": "Instagram URL is required."}), 400
    
    # Step 1: Extract GraphQL URL from the reeldown.io response
    graphql_url = get_graphql_url(instagram_url)
    
    # Step 2: Fetch JSON data from GraphQL URL
    json_data = fetch_json_from_graphql_url(graphql_url)
    
    return jsonify(json_data)

# Run the Flask app with the correct port (needed for Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use the port from the environment or default to 5000
    app.run(host="0.0.0.0", port=port)
