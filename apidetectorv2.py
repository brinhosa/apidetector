#REQUIREMENTS:
#pip install playwright nest_asyncio
#EXECUTE:
#playwright install
## Legal Disclaimer
#The use of APIDetector should be limited to testing and educational purposes only. The developers of APIDetector assume no liability and are not responsible for any misuse or damage caused by this tool. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developers assume no responsibility for unauthorized or illegal use of this tool. Before using APIDetector, ensure you have permission to test the network or systems you intend to scan.

import requests
import concurrent.futures
import argparse
import random
import string
import difflib
import subprocess
import os

# ASCII Art for APIDetector
ascii_art = """
     \      _ \ _ _|      __ \   ____| __ __|  ____|   ___| __ __|  _ \    _ \  
    _ \    |   |  |       |   |  __|      |    __|    |        |   |   |  |   | 
   ___ \   ___/   |       |   |  |        |    |      |        |   |   |  __ <  
 _/    _\ _|    ___|     ____/  _____|   _|   _____| \____|   _|  \___/  _| \_\ 
                                     
                                        https://github.com/brinhosa/apidetector                                                                                                              
"""

# Function to test a single endpoint
def test_endpoint(url, error_content, verbose, user_agent, poc_already_generated=False):
    headers = {'User-Agent': user_agent}
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=False)
        if response.status_code == 200 and "Page Not Found".lower() not in response.text.lower():
            # Calculate similarity with the error content
            similarity = difflib.SequenceMatcher(None, error_content, response.text).ratio()
            if similarity < 0.90:
                # Extract the domain from the URL for use in the filename
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                
                # Check if this is specifically /swagger-ui/index.html
                is_swagger_ui_index = '/swagger-ui/index.html' in url
                
                # Check for other Swagger/OpenAPI endpoints (for reporting purposes)
                swagger_patterns = ['/swagger-ui', '/api-docs', '/openapi', '/swagger.', '/swagger-resources']
                is_swagger = any(pattern in url for pattern in swagger_patterns)
                
                # Only generate PoC if:
                # 1. We haven't already generated one for this domain AND
                # 2. This is specifically the /swagger-ui/index.html endpoint
                if is_swagger_ui_index and not poc_already_generated:
                    print(f"Calling PoC generator for {url}")
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    pocgenerator_path = os.path.join(current_dir, 'pocgenerator.py')
                    
                    # Add configUrl parameter for Swagger UI endpoints
                    endpoint_url = url + "?configUrl=https://raw.githubusercontent.com/brinhosa/payloads/master/testswagger.json"
                    
                    # Pass the SCREENSHOT_PATH environment variable if it exists
                    env = os.environ.copy()
                    # Add domain information to help with filename generation
                    env['DOMAIN'] = domain
                    # Add a flag to indicate this is a PoC generation
                    env['GENERATE_POC'] = 'true'
                    
                    # Run the PoC generator and capture the result
                    result = subprocess.run(['python3', pocgenerator_path, endpoint_url], env=env, capture_output=True, text=True)
                    
                    # Check if the screenshot was successfully created
                    if 'Screenshot saved' in result.stdout:
                        # Set a flag in the environment to indicate a successful screenshot
                        os.environ[f'SCREENSHOT_CREATED_{domain.replace('.', '_')}'] = 'true'
                
                return url
    except requests.RequestException as e:
        pass
    return None

# Random string to test invalid paths
def generate_random_string(length=21):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to test all endpoints for a given subdomain
def test_subdomain_endpoints(subdomain, common_endpoints, mixed_mode, verbose, user_agent):
    random_path = generate_random_string()
    protocols = ['https://', 'http://'] if mixed_mode else ['https://']
    valid_urls = []
    error_content = ""

    # Retrieve the error page content
    for protocol in protocols:
        error_url = f"{protocol}{subdomain}/{random_path}"
        try:
            error_response = requests.get(error_url, headers={'User-Agent': user_agent}, timeout=15)
            if error_response.status_code == 404 or "Page Not Found".lower() in error_response.text.lower():
                error_content = error_response.text
                break  # Assuming the same error content for all protocols
        except requests.RequestException:
            pass

    # Test for false-positives
    for protocol in protocols:
        test_url1 = f"{protocol}{subdomain}/api/swagger/v3/api-docs"
        test_url2 = f"{protocol}{subdomain}/api/swagger/v2/api-docs"
        try:
            response1 = requests.get(test_url1, headers={'User-Agent': user_agent}, timeout=15)
            response2 = requests.get(test_url2, headers={'User-Agent': user_agent}, timeout=15)
    
            if response1.status_code == 200 and response2.status_code == 200:
                # Calculate similarity
                similarity = difflib.SequenceMatcher(None, response1.text, response2.text).ratio()
                if similarity > 0.70:
                    print(f"{subdomain} not valid to test, returns success for any API version with high similarity of {similarity}.")
                    return valid_urls
                else:
                    print(f"{subdomain} valid for testing, API versions are not highly similar.")
        except requests.RequestException:
            pass

    # Flag to track if we've already generated a PoC for this domain
    poc_generated = False
    
    for protocol in protocols:
        for endpoint in common_endpoints:
            url = f"{protocol}{subdomain}{endpoint}"
            result = test_endpoint(url, error_content, verbose, user_agent, poc_generated)
            if result:
                valid_urls.append(result)
                # If this is a Swagger/OpenAPI endpoint, mark that we've generated a PoC
                swagger_patterns = ['/swagger-ui', '/api-docs', '/openapi', '/swagger.', '/swagger-resources']
                if any(pattern in url for pattern in swagger_patterns):
                    poc_generated = True
                if verbose:
                    print(f"Found: {url}")
    return valid_urls

def main(domain, input_file, output_file, num_threads, common_endpoints, mixed_mode, verbose, user_agent):
    subdomains = [domain] if domain else []

    if verbose:
        print("APIDetector - API Security Testing Tool\n" + ascii_art)

    if not domain:
        with open(input_file, 'r') as file:
            subdomains.extend(line.strip() for line in file)

    all_valid_urls = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(test_subdomain_endpoints, subdomain, common_endpoints, mixed_mode, verbose, user_agent) for subdomain in subdomains]
        for future in concurrent.futures.as_completed(futures):
            all_valid_urls.extend(future.result())

    if all_valid_urls:
        if output_file:
            with open(output_file, 'w') as file:
                for url in sorted(set(all_valid_urls)):
                    file.write(url + '\n')
            if verbose:
                print(f"Completed. Valid URLs are saved in {output_file}")
        else:
            if verbose:
                print("All results found in alphabetic order:")
            for url in sorted(set(all_valid_urls)):
                print(url)
    else:
        print("No exposed URLs found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APIDetector - API Security Testing Tool\n" + ascii_art,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-d", "--domain", help="Single domain to test")
    parser.add_argument("-i", "--input", help="Input file containing subdomains to test")
    parser.add_argument("-o", "--output", help="Output file to write valid URLs to")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use for scanning")
    parser.add_argument("-m", "--mixed-mode", action='store_true', help="Test both HTTP and HTTPS protocols")
    parser.add_argument("-q", "--quiet", action='store_true', help="Disable verbose output")
    parser.add_argument("-ua", "--user-agent", default="APIDetector", help="Custom User-Agent string for requests")

    args = parser.parse_args()

    if not args.domain and not args.input:
        parser.error("Either --domain or --input must be specified")

    # Determine verbose mode based on the quiet flag
    verbose = not args.quiet

    # List of common Swagger/OpenAPI endpoints
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
    common_endpoints_big = [
        '/swagger-ui.html', '/api-docs', '/swagger.json', '/docs',
        '/swagger-ui/', '/swagger-ui/index.html', '/api/swagger.json',
        '/api/swagger-ui.html', '/swagger.yaml', '/swagger.yml',
        '/api/swagger.yaml', '/api/swagger.yml', '/swagger-resources',
        '/swagger-resources/configuration/ui', '/swagger-resources/configuration/security',
        '/api/swagger-resources', '/api/v2/swagger.json', '/api/v3/swagger.json',
        '/api/v1/documentation', '/api/v2/documentation', '/api/v3/documentation',
        '/api/v1/api-docs', '/api/v2/api-docs', '/api/v3/api-docs',
        '/api/swagger', '/api/docs', '/api/swagger-ui', '/api.json',
        '/api.yaml', '/api.yml', '/api.html', '/documentation/swagger.json',
        '/documentation/swagger.yaml', '/documentation/swagger.yml',
        '/documentation/swagger-ui.html', '/documentation/swagger-ui',
        '/swagger/index.html', '/swagger-ui.html/v2/api-docs',
        '/swagger-ui.html/v3/api-docs', '/swagger/v2/api-docs', '/swagger/v3/api-docs',
        '/api/swagger/v2/api-docs', '/api/swagger/v3/api-docs', '/classicapi/doc/',
        '/api-doc', '/api/package_search/v4/documentation', '/api/2/explore/',
        '/apidoc', '/apidocs', '/application', '/backoffice/v1/ui',
        '/build/reference/web-api/explore', '/core/latest/swagger-ui/index.html',
        '/csp/gateway/slc/api/swagger-ui.html', '/doc', '/internal/docs',
        '/rest/v1', '/rest/v3/doc', '/swagger', '/swaggerui', '/ui',
        '/ui/', '/v1', '/v1.0', '/v1.1', '/v2', '/v2.0', '/v3',
        '/v1.x/swagger-ui.html', '/swagger/swagger-ui.html', '/swagger/index.html'
    ]

    main(args.domain, args.input, args.output, args.threads, common_endpoints, args.mixed_mode, verbose, args.user_agent)
