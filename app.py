from flask import Flask, render_template, request, jsonify, send_file, Response
import concurrent.futures
import os
import sys
import asyncio
import json
import tempfile
import argparse
import re
import time
import uuid
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

# Domain validation regex pattern
domain_pattern = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$'
)

# Store active scans
active_scans = {}

@app.route('/scan', methods=['POST'])
def scan():
    try:
        # Check if JSON or form data
        if request.is_json:
            data = request.get_json()
            domain = data.get('domain')
            domains = [domain] if domain else []
            mixed_mode = data.get('mixedMode', False)
            thread_count = min(int(data.get('threadCount', 10)), 50)  # Limit to 50 threads
            user_agent = data.get('userAgent', 'Mozilla/5.0')
        else:
            # Handle form data with file upload
            domain = request.form.get('domain', '')
            domains = [domain] if domain and domain.strip() else []
            mixed_mode = request.form.get('mixedMode') == 'on'
            thread_count = min(int(request.form.get('threadCount', 10)), 50)
            user_agent = request.form.get('userAgent', 'Mozilla/5.0')
            
            # Handle file upload if present
            if 'domainFile' in request.files:
                domain_file = request.files['domainFile']
                if domain_file.filename != '':
                    content = domain_file.read().decode('utf-8')
                    file_domains = [line.strip() for line in content.splitlines() if line.strip()]
                    domains.extend(file_domains)
        
        # Validate domains
        valid_domains = []
        for d in domains:
            if domain_pattern.match(d):
                valid_domains.append(d)
        
        if not valid_domains:
            return jsonify({'error': 'No valid domains provided'}), 400
        
        # Generate a unique scan ID
        scan_id = str(uuid.uuid4())
        active_scans[scan_id] = {
            'domains': valid_domains,
            'results': [],
            'status': 'running',
            'current_domain': '',
            'progress': 0,
            'start_time': time.time()
        }
        
        # Start scan in a separate thread
        def run_scan():
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                    futures = []
                    for domain in valid_domains:
                        active_scans[scan_id]['current_domain'] = domain
                        futures.append(
                            executor.submit(
                                apidetectorv2.test_subdomain_endpoints,
                                domain,
                                common_endpoints,
                                mixed_mode,
                                True,
                                user_agent
                            )
                        )
                    
                    total = len(futures)
                    for i, future in enumerate(concurrent.futures.as_completed(futures)):
                        try:
                            results = future.result()
                            if results:
                                active_scans[scan_id]['results'].extend(results)
                        except Exception as e:
                            app.logger.error(f"Error scanning domain: {str(e)}")
                        
                        # Update progress
                        active_scans[scan_id]['progress'] = int(((i + 1) / total) * 100)
                
                active_scans[scan_id]['status'] = 'completed'
                active_scans[scan_id]['end_time'] = time.time()
            except Exception as e:
                app.logger.error(f"Error during scan: {str(e)}")
                active_scans[scan_id]['status'] = 'error'
                active_scans[scan_id]['error'] = str(e)
        
        # Start the scan in a background thread
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(run_scan)
        
        return jsonify({
            'scan_id': scan_id,
            'message': f'Scan started for {len(valid_domains)} domain(s)',
            'valid_domains': valid_domains
        })

    except Exception as e:
        app.logger.error(f"Error during scan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/scan-status/<scan_id>', methods=['GET'])
def scan_status(scan_id):
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan_data = active_scans[scan_id]
    return jsonify({
        'status': scan_data['status'],
        'progress': scan_data['progress'],
        'current_domain': scan_data['current_domain'],
        'results': scan_data['results'],
        'total_domains': len(scan_data['domains']),
        'domains_scanned': int((scan_data['progress'] / 100) * len(scan_data['domains']))
    })

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
