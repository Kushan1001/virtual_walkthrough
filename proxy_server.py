from flask import Flask, request, Response
import requests
import re

app = Flask(__name__)

# The base URL where Marzipano files are hosted
TARGET_BASE = "https://videoserver.nvli.in/nvli/360video/Qutb_Minar/app-files"

@app.route("/proxy_page")
def proxy_page():
    try:
        resp = requests.get(f"{TARGET_BASE}/index.html")
        html = resp.text

        html = re.sub(
                r'(src|href)=["\'](?!https?:\/\/|\/proxy\/|javascript:|mailto:)([^"\']+)["\']',
                r'\1="/proxy/\2"',
                html
        )


        return Response(html, content_type="text/html")
    except Exception as e:
        return f"Error loading page: {e}", 500


@app.route("/proxy/<path:subpath>")
def proxy_asset(subpath):
    try:
        target_url = f"{TARGET_BASE}/{subpath}"
        print(f"Fetching asset: {target_url}")
        r = requests.get(target_url, stream=True)

        excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'x-frame-options']
        headers = [(k, v) for k, v in r.raw.headers.items() if k.lower() not in excluded]

        return Response(r.content, headers=headers, content_type=r.headers.get("Content-Type", "application/octet-stream"))
    except Exception as e:
        return f"Error fetching asset: {e}", 500

@app.route("/<path:subpath>")
def fallback_proxy(subpath):
    try:
        if subpath.startswith("proxy/"):
            return "Invalid path", 404

        target_url = f"{TARGET_BASE}/{subpath}"
        print(f"Fallback fetch: {target_url}")
        r = requests.get(target_url, stream=True)

        excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'x-frame-options']
        headers = [(k, v) for k, v in r.raw.headers.items() if k.lower() not in excluded]

        return Response(r.content, headers=headers, content_type=r.headers.get("Content-Type", "application/octet-stream"))
    except Exception as e:
        return f"Error fetching asset: {e}", 500

@app.route("/tiles/<path:subpath>")
@app.route("/Keymap/<path:subpath>")
def proxy_tiles(subpath):
    try:
        target_url = f"{TARGET_BASE}/tiles/{subpath}" if 'tiles' in request.path else f"{TARGET_BASE}/Keymap/{subpath}"
        print(f"Fetching asset: {target_url}")
        r = requests.get(target_url, stream=True)

        excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'x-frame-options']
        headers = [(k, v) for k, v in r.raw.headers.items() if k.lower() not in excluded]

        return Response(r.content, headers=headers, content_type=r.headers.get("Content-Type", "application/octet-stream"))
    except Exception as e:
        return f"Error fetching asset: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
