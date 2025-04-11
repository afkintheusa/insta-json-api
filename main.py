from flask import Flask, request, jsonify
import instaloader
import requests
import re

app = Flask(__name__)

@app.route('/json', methods=['GET'])
def get_instagram_json():
    instagram_url = request.args.get("url")
    if not instagram_url or "instagram.com" not in instagram_url:
        return jsonify({"error": "Invalid or missing Instagram URL."}), 400

    shortcode_match = re.search(r"/(p|reel|tv)/([^/?]+)", instagram_url)
    if not shortcode_match:
        return jsonify({"error": "Could not extract shortcode from URL."}), 400

    shortcode = shortcode_match.group(2)

    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        return jsonify(post._asdict())  # contains all the metadata
    except Exception as e:
        # Fallback: Try to extract GraphQL URL from the error message
        error_str = str(e)
        graphql_match = re.search(r'(\/graphql\/query\?[^\'\"\s]+)', error_str)
        if graphql_match:
            graphql_url = graphql_match.group(1)
            if not graphql_url.startswith("http"):
                graphql_url = "https://instagram.com" + graphql_url

            try:
                json_response = requests.get(graphql_url, headers={"User-Agent": "Mozilla/5.0"})
                return jsonify(json_response.json()), json_response.status_code
            except Exception as e2:
                return jsonify({"error": f"Failed to fetch GraphQL URL: {str(e2)}"}), 500

        return jsonify({"error": f"Instaloader failed: {error_str}"}), 500

@app.route('/')
def home():
    return "Instagram JSON API using Instaloader is live."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
