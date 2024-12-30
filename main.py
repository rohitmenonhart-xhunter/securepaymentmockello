from flask import Flask, render_template, request, redirect, url_for, Response
import hashlib
import random
import time
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Temporary storage to hold the generated links (In-memory or can use Redis/SQLite)
redirect_links = {}

# Allowed URL and Key for link generation
ALLOWED_URL = "https://paymentpage-q42y.onrender.com/"
SECRET_KEY = "rohitmenonhart1209v77"


# Function to generate a unique token
def generate_token():
    return hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    key = request.form.get('key')

    # Check if the key is correct
    if key != SECRET_KEY:
        return "Invalid key provided!", 400

    links = []

    # Generate 10 unique, self-destructing links for the fixed URL
    for _ in range(10):
        token = generate_token()
        expiration_time = time.time() + 600  # Link expires in 10 minutes (unused, but can be used if needed)
        redirect_links[token] = {'url': ALLOWED_URL, 'expires': expiration_time}

        secure_link = url_for('redirect_link', token=token, _external=True)
        links.append(secure_link)

    # Return the links as a list that is easy to copy
    return render_template('links.html', links=links)


@app.route('/<token>')
def redirect_link(token):
    if token not in redirect_links:
        return "Invalid or expired link", 404

    link_info = redirect_links[token]

    # Remove the link after it has been accessed (expire it immediately)
    del redirect_links[token]

    # Forward the request to the actual URL without showing it in the browser
    try:
        response = requests.get(link_info['url'])

        # Forward the response from the actual URL to the user
        return Response(response.content, status=response.status_code, content_type=response.headers['Content-Type'])
    except requests.exceptions.RequestException as e:
        return str(e), 500


if __name__ == "__main__":
    # Get the port from the environment variable (default to 5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
