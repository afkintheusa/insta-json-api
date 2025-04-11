from flask import Flask, request, jsonify
import requests
import json
import re

app = Flask(__name__)

@app.route('/json', methods=['GET'])
def get_instagram_json():
    instagram_url = request.args.get("url")
    if not instagram_url or "instagram.com" not in instagram_url:
        return jsonify({"error": "Invalid or missing Instagram URL."}), 400

    try:
        # Step 1: Ask reeldown.io
        response = requests.post(
            "https://reeldown.io/reels/api/download/",
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/json',
            },
            data=json.dumps({"url": instagram_url})
        )

        error_message = response.json().get("error", "")

        graphql_url_match = re.search(r'(https?:\/\/www\.instagram\.com\/graphql\/[^\s"\']+|\/graphql\/[^\s"\']+)', error_message)

        if not graphql_url_match:
            return jsonify({"error": "Could not extract the GraphQL URL."}), 500

        graphql_url = graphql_url_match.group(1)

        # Fix missing domain if needed
        if graphql_url.startswith("/graphql"):
            graphql_url = "https://www.instagram.com" + graphql_url

        graphql_response = requests.get(graphql_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if graphql_response.status_code == 200:
            return jsonify(graphql_response.json())
        else:
            return jsonify({"error": f"Failed to fetch JSON from GraphQL URL. Status code: {graphql_response.status_code}"}), graphql_response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Instagram JSON API is live. Use /json?url=INSTAGRAM_URL"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
