from flask import Flask, request, jsonify
import requests
import json
import re
import subprocess

app = Flask(__name__)

@app.route('/json', methods=['GET'])
def get_instagram_json():
    instagram_url = request.args.get("url")
    if not instagram_url or "instagram.com" not in instagram_url:
        return jsonify({"error": "Invalid or missing Instagram URL."}), 400

    try:
        # Step 1: Try using instaloader to fetch post info
        cmd = ["instaloader", "--no-captions", "--no-pictures", "--no-videos", "--no-metadata-json", "--no-compress-json", "--", instagram_url]
        process = subprocess.run(cmd, capture_output=True, text=True)

        error_output = process.stderr

        # First check for full GraphQL URL
        graphql_url_match = re.search(r'(https?://www\.instagram\.com/graphql/query\?[^ ]+)', error_output)
        if not graphql_url_match:
            # Fallback: Try to extract partial /graphql/query... URL and prepend domain
            partial_match = re.search(r'(/graphql/query\?[^ ]+)', error_output)
            if partial_match:
                graphql_url = "https://www.instagram.com" + partial_match.group(1)
            else:
                return jsonify({"error": "Could not extract GraphQL URL from error."}), 500
        else:
            graphql_url = graphql_url_match.group(1)

        # Step 2: Fetch JSON from that GraphQL URL
        graphql_response = requests.get(graphql_url, headers={'User-Agent': 'Mozilla/5.0'})

        if graphql_response.status_code == 200:
            return jsonify(graphql_response.json())
        else:
            return jsonify({
                "error": f"Failed to fetch JSON from GraphQL URL.",
                "status_code": graphql_response.status_code
            }), graphql_response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Instagram JSON API is live. Use /json?url=INSTAGRAM_URL"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
