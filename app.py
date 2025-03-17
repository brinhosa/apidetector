from flask import Flask, render_template, request, jsonify, send_file
import concurrent.futures
import os
import sys
import asyncio
import json
import tempfile
import argparse
from pathlib import Path

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import apidetectorv2
import pocgenerator

# Common Swagger/OpenAPI endpoints to test
common_endpoints = [
    '/swagger-ui.html', '/openapi.json', '/v2/api-docs', '/v3/api-docs',
    '/swagger.json', '/api-docs', '/docs', '/swagger-ui/', '/swagger-ui/index.html',
    '/api/swagger.json', '/api/swagger-ui.html', '/swagger.yaml', '/swagger.yml',
    '/api/swagger.yaml', '/api/swagger.yml', '/swagger-resources',
    '/swagger-resources/configuration/ui', '/swagger-resources/configuration/security',
    '/api/swagger-resources', '/api/v2/swagger.json', '/api/v3/swagger.json',
    '/api/v1/documentation', '/api/v2/documentation', '/api/v3/documentation',
    '/api/v1/api-docs', '/api/v2/api-docs', '/api/v3/api-docs',
    '/api/swagger', '/api/docs', '/api/swagger-ui', '/api.json', '/api.yaml',
    '/api.yml', '/api.html', '/documentation/swagger.json', '/documentation/swagger.yaml',
    '/documentation/swagger.yml', '/documentation/swagger-ui.html',
    '/documentation/swagger-ui', '/swagger/index.html', '/swagger-ui.html/v2/api-docs',
    '/swagger-ui.html/v3/api-docs', '/swagger/v2/api-docs', '/swagger/v3/api-docs',
    '/api/swagger/v2/api-docs', '/api/swagger/v3/api-docs', '/classicapi/doc/'
]

app = Flask(__name__)

# Create a temporary directory for screenshots
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'apidetector_screenshots')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        domain = data.get('domain')
        mixed_mode = data.get('mixedMode', False)
        thread_count = min(int(data.get('threadCount', 30)), 50)  # Limit to 50 threads
        user_agent = data.get('userAgent', 'Mozilla/5.0')

        if not domain:
            return jsonify({'error': 'Domain is required'}), 400

        found_urls = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            try:
                future = executor.submit(
                    apidetectorv2.test_subdomain_endpoints,
                    domain,
                    common_endpoints,
                    mixed_mode,
                    True,
                    user_agent
                )
                found_urls = future.result()
            except Exception as e:
                app.logger.error(f"Error during scan: {str(e)}")
                return jsonify({'error': str(e)}), 500

        return jsonify({'urls': found_urls})

    except Exception as e:
        app.logger.error(f"Error during scan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            mimetype='image/png'
        )
    except Exception as e:
        app.logger.error(f"Error serving screenshot: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='APIDetector Web Interface')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='Port to run the web interface on (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host to run the web interface on (default: 127.0.0.1)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Run in debug mode (default: False)')
    
    args = parser.parse_args()
    
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Print startup message
    print(f"\nAPIDetector Web Interface")
    print(f"=======================")
    print(f"Starting server at: http://{args.host}:{args.port}")
    print(f"Press Ctrl+C to quit\n")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
