import requests
import concurrent.futures
import argparse
import random
import string
import difflib
import re
import csv

regex_patterns = {
    'google_api'     : r'AIza[0-9A-Za-z-_]{35}',
	'firebase'  : r'AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140}',
	'google_captcha' : r'6L[0-9A-Za-z-_]{38}|^6[0-9a-zA-Z_-]{39}$',
	'google_oauth'   : r'ya29\.[0-9A-Za-z\-_]+',
	'amazon_aws_access_key_id' : r'A[SK]IA[0-9A-Z]{16}',
	'amazon_mws_auth_toke' : r'amzn\\.mws\\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
	'amazon_aws_url' : r's3\.amazonaws.com[/]+|[a-zA-Z0-9_-]*\.s3\.amazonaws.com',
	'amazon_aws_url2' : r"(" \
		   r"[a-zA-Z0-9-\.\_]+\.s3\.amazonaws\.com" \
		   r"|s3://[a-zA-Z0-9-\.\_]+" \
		   r"|s3-[a-zA-Z0-9-\.\_\/]+" \
		   r"|s3.amazonaws.com/[a-zA-Z0-9-\.\_]+" \
		   r"|s3.console.aws.amazon.com/s3/buckets/[a-zA-Z0-9-\.\_]+)",
	'facebook_access_token' : r'EAACEdEose0cBA[0-9A-Za-z]+',
	'authorization_basic' : r'basic [a-zA-Z0-9=:_\+\/-]{5,100}',
	'authorization_bearer' : r'bearer [a-zA-Z0-9_\-\.=:_\+\/]{5,100}',
	'mailgun_api_key' : r'key-[0-9a-zA-Z]{32}',
	'twilio_api_key' : r'SK[0-9a-fA-F]{32}',
	'twilio_account_sid' : r'AC[a-zA-Z0-9_\-]{32}',
	'twilio_app_sid' : r'AP[a-zA-Z0-9_\-]{32}',
	'paypal_braintree_access_token' : r'access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}',
	'square_oauth_secret' : r'sq0csp-[ 0-9A-Za-z\-_]{43}|sq0[a-z]{3}-[0-9A-Za-z\-_]{22,43}',
	'square_access_token' : r'sqOatp-[0-9A-Za-z\-_]{22}|EAAA[a-zA-Z0-9]{60}',
	'stripe_standard_api' : r'sk_live_[0-9a-zA-Z]{24}',
	'stripe_restricted_api' : r'rk_live_[0-9a-zA-Z]{24}',
	'github_access_token' : r'[a-zA-Z0-9_-]*:[a-zA-Z0-9_\-]+@github\.com*',
	'rsa_private_key' : r'-----BEGIN RSA PRIVATE KEY-----',
	'ssh_dsa_private_key' : r'-----BEGIN DSA PRIVATE KEY-----',
	'ssh_dc_private_key' : r'-----BEGIN EC PRIVATE KEY-----',
	'pgp_private_block' : r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
	'json_web_token' : r'ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$',
	'slack_token' : r"\"api_token\":\"(xox[a-zA-Z]-[a-zA-Z0-9-]+)\"",
	'SSH_privKey' : r"([-]+BEGIN [^\s]+ PRIVATE KEY[-]+[\s]*[^-]*[-]+END [^\s]+ PRIVATE KEY[-]+)",
	'Heroku API KEY' : r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
	'possible_Creds' : r'(?i)(" \
					r"password\s*[`=:\"]+\s*[^\s]+|" \
					r"password is\s*[`=:\"]*\s*[^\s]+|" \
					r"pwd\s*[`=:\"]*\s*[^\s]+|" \
					r"passwd\s*[`=:\"]+\s*[^\s]+)',
	'email': r"[\w\.-]+@[\w\.-]+\.\w+",
	'ip': r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
}

# ASCII Art for APIDetector
ascii_art = """
     \      _ \ _ _|      __ \   ____| __ __|  ____|   ___| __ __|  _ \    _ \  
    _ \    |   |  |       |   |  __|      |    __|    |        |   |   |  |   | 
   ___ \   ___/   |       |   |  |        |    |      |        |   |   |  __ <  
 _/    _\ _|    ___|     ____/  _____|   _|   _____| \____|   _|  \___/  _| \_\ 
                                     
                                        https://github.com/brinhosa/apidetector                                                                                                              
"""

# Function to test a single endpoint
def test_endpoint(url, error_content, verbose, user_agent, regex_patterns):
    headers = {'User-Agent': user_agent}
    found_secrets = []
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=False)
        if response.status_code == 200:
            # Calculate similarity with the error content
            similarity = difflib.SequenceMatcher(None, error_content, response.text).ratio()
            if similarity < 0.90:
                data = response.text
                matching_contents = []
                for line in data.split('\n'):
                    pattern_name, matched_content = check_regex(line, regex_patterns)
                    if pattern_name:
                        matching_contents.append((url, pattern_name, matched_content))
                found_secrets.extend(matching_contents)
    except requests.RequestException as e:
        pass
    return found_secrets



# Random string to test invalid paths
def generate_random_string(length=21):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Function to test all endpoints for a given subdomain
def test_subdomain_endpoints(subdomain, common_endpoints, mixed_mode, verbose, user_agent, regex_patterns):
    random_path = generate_random_string()
    protocols = ['https://', 'http://'] if mixed_mode else ['https://']
    valid_urls = []
    error_content = ""

    # Retrieve the error page content
    for protocol in protocols:
        error_url = f"{protocol}{subdomain}/{random_path}"
        try:
            error_response = requests.get(error_url, headers={'User-Agent': user_agent}, timeout=15)
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
#Second method of detection for false-positives             
    # Retrieve the error page content
    for protocol in protocols:
        error_url = f"{protocol}{subdomain}/{random_path}"
        try:
            error_response = requests.get(error_url, headers={'User-Agent': user_agent}, timeout=15)
            error_content = error_response.text
            break  # Assuming the same error content for all protocols
        except requests.RequestException:
            pass
             
    for protocol in protocols:
        for endpoint in common_endpoints:
            url = f"{protocol}{subdomain}{endpoint}"
            result = test_endpoint(url, error_content, verbose, user_agent)
            if result:
                valid_urls.append(result)
                if verbose:
                    print(f"Found: {url}")
    return valid_urls


def main(domain, input_file, output_file, num_threads, common_endpoints, mixed_mode, verbose, user_agent, output_secrets=None):
    subdomains = [domain] if domain else []

    if verbose:
        print("APIDetector - API Security Testing Tool\n" + ascii_art)

    if not domain:
        with open(input_file, 'r') as file:
            subdomains.extend(line.strip() for line in file)

    all_valid_urls = []
    all_found_secrets = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(test_subdomain_endpoints, subdomain, common_endpoints, mixed_mode, verbose, user_agent, regex_patterns) for subdomain in subdomains]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            all_valid_urls.extend([x[0] for x in result])
            all_found_secrets.extend(result)

    if all_valid_urls:
        if output_file:
            with open(output_file, 'w') as file:
                for url in sorted(set(all_valid_urls)):
                    file.write(url + '\n')
            if verbose:
                print(f"Completed. Valid URLs are saved in {output_file}")
    else:
        print("No exposed URLs found.")

    # Write found secrets to file if -oS is specified
    if output_secrets and all_found_secrets:
        with open(output_secrets, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['URL', 'Secret Type', 'Secret Details'])
            for secret in all_found_secrets:
                csvwriter.writerow(secret)
        if verbose:
            print(f"Secrets found are saved in {output_secrets}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APIDetector - API Security Testing Tool\n" + ascii_art,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-d", "--domain", help="Single domain to test")
    parser.add_argument("-i", "--input", help="Input file containing subdomains to test")
    parser.add_argument("-o", "--output", help="Output file to write valid URLs to")
    parser.add_argument("-oS", "--output-secrets", help="Output file to write found secrets to")
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

    main(args.domain, args.input, args.output, args.threads, common_endpoints, args.mixed_mode, verbose, args.user_agent, args.output_secrets)
