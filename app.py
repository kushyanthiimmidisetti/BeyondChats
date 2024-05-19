import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

API_URL = "https://devapi.beyondchats.com/api/get_message_with_sources"

def fetch_data(url):
    data = []
    while url:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch data: {response.status_code}")
                break
            response_json = response.json()
            if 'results' not in response_json or 'next' not in response_json:
                print("Unexpected response structure:", response_json)
                break
            data.extend(response_json['results'])
            url = response_json.get('next')
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return data

def find_citations(response, sources):
    citations = []
    for source in sources:
        if source['context'] in response:
            citations.append({
                "id": source['id'],
                "link": source.get('link', '')
            })
    return citations

@app.route('/')
def index():
    data = fetch_data(API_URL)
    results = []
    for item in data:
        response_text = item.get('response', '')
        sources = item.get('sources', [])
        citations = find_citations(response_text, sources)
        results.append({
            "response": response_text,
            "citations": citations
        })
    return jsonify(results)

@app.route('/ui')
def ui():
    data = fetch_data(API_URL)
    results = []
    for item in data:
        response_text = item.get('response', '')
        sources = item.get('sources', [])
        citations = find_citations(response_text, sources)
        results.append({
            "response": response_text,
            "citations": citations
        })
    return render_template_string("""
    <!doctype html>
    <html>
        <head>
            <title>API Citations</title>
        </head>
        <body>
            <h1>API Citations</h1>
            <ul>
            {% for item in results %}
                <li>
                    <p><strong>Response:</strong> {{ item.response }}</p>
                    <p><strong>Citations:</strong></p>
                    <ul>
                    {% for citation in item.citations %}
                        <li>
                            <p>ID: {{ citation.id }}</p>
                            <p>Link: <a href="{{ citation.link }}">{{ citation.link }}</a></p>
                        </li>
                    {% endfor %}
                    </ul>
                </li>
            {% endfor %}
            </ul>
        </body>
    </html>
    """, results=results)

if __name__ == '__main__':
    app.run(debug=True)
