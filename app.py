from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/store_session', methods=['POST'])
def store_session():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.json
        text = data.get('text')
        title = data.get('title')
        tags = data.get('tags', [])
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        print(f"Received session: {title}")  # Debug logging
        
        return jsonify({
            'success': True,
            'received': {
                'text': text[:100] + '...' if len(text) > 100 else text,
                'title': title,
                'tags': tags
            }
        })
            
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
