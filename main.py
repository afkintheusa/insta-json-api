from flask import Flask, request, jsonify
import requests
import re
import json

app = Flask(__name__)

@app.route('/json', methods=['GET'])
def get_instagram_json():
    instagram_url = request.args.get('url')
    
    if not instagram_url or "instagram.com" not in instagram_url:
        return jsonify({"error": "Please provide a valid Instagram URL."}), 400

    try:
        # Step 1: Query reeldown.io to get GraphQL URL
        response = requests.post(
            "https://reeldown.io/reels/api/download/",
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/json',
            },
            data=json.dumps({"url": instagram_url})
        )
        
        error_message = response.json().get("error", "")
        graphql_url_match = re.search(r'when accessing (https?://[^\s]+)', error_message)

        if not graphql_url_match:
            return jsonify({"error": "Failed to extract GraphQL URL from reeldown.io."}), 500

        graphql_url = graphql_url_match.group(1)

        # Step 2: Fetch JSON from GraphQL URL
        try:
            graphql_response = requests.get(graphql_url, headers={'User-Agent': 'Mozilla/5.0'})
            json_data = graphql_response.json()
            return jsonify(json_data), 200

        except requests.exceptions.SSLError as ssl_error:
            # Fallback: Reconstruct URL if SSL fails
            fallback_match = re.search(r"(/graphql/query\?[^'\s]+)", str(ssl_error))
            if fallback_match:
                rebuilt_url = "https://www.instagram.com" + fallback_match.group(1)
                graphql_response = requests.get(rebuilt_url, headers={'User-Agent': 'Mozilla/5.0'})
                return jsonify(graphql_response.json()), 200
            else:
                return jsonify({"error": "SSL error and URL reconstruction failed."}), 500

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)