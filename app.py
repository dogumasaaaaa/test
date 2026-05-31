from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Fake browser headers to ensure the banned site thinks a real person is watching
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.redgifs.com/",
    "Origin": "https://www.redgifs.com"
}

@app.route('/stream')
def stream_video():
    # Pass the actual video URL as a parameter: /stream?url=https://...
    target_url = request.args.get('url')
    if not target_url:
        return "Missing video URL target", 400

    try:
        # Stream the content from the destination server through this US host
        req = requests.get(target_url, headers=HEADERS, stream=True)
        
        # Exclude internal transfer headers that might break the connection
        exclude_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in req.raw.headers.items()
                   if name.lower() not in exclude_headers]

        # Force Cross-Origin Resource Sharing (CORS) so your local browser can read it
        headers.append(('Access-Control-Allow-Origin', '*'))

        # Pipe the chunks sequentially to the user's browser in real-time
        def generate():
            for chunk in req.iter_content(chunk_size=4096):
                yield chunk

        return Response(generate(), status=req.status_code, headers=headers)

    except Exception as e:
        return f"Proxy connection failure: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
