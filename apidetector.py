import requests
import concurrent.futures
import argparse
import random
import string
import difflib


# ASCII Art for APIDetector
ascii_art = """
     \      _ \ _ _|      __ \   ____| __ __|  ____|   ___| __ __|  _ \    _ \  
    _ \    |   |  |       |   |  __|      |    __|    |        |   |   |  |   | 
   ___ \   ___/   |       |   |  |        |    |      |        |   |   |  __ <  
 _/    _\ _|    ___|     ____/  _____|   _|   _____| \____|   _|  \___/  _| \_\ 
                                     
                                        https://github.com/brinhosa/apidetector                                                                                                              
"""

# Function to test a single endpoint
def test_endpoint(url, error_content, verbose, user_agent, xss_check):
    headers = {'User-Agent': user_agent}
    xss_vulnerable = False
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=False)
        if response.status_code == 200:
            similarity = difflib.SequenceMatcher(None, error_content, response.text).ratio()
            if similarity < 0.90:
                if xss_check:
                    xss_response = requests.get(url + "?configUrl=https://raw.githubusercontent.com/brinhosa/payloads/master/testswagger.json", headers=headers, timeout=30)
                    if "<img onerror=\"alert('XSS')\" src=\"1\">" in xss_response.text:
                        print(f"Found XSS in the URL: {url}")
                        xss_vulnerable = True
                return url, xss_vulnerable
    except requests.RequestException as e:
        pass

    return None, xss_vulnerable


# Random string to test invalid paths
def generate_random_string(length=21):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to test all endpoints for a given subdomain
def test_subdomain_endpoints(subdomain, common_endpoints, mixed_mode, verbose, user_agent, xss_check):
    random_path = generate_random_string()
    protocols = ['https://', 'http://'] if mixed_mode else ['https://']
    valid_urls = []
    error_content = ""
    xss_urls = []

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
            result, is_xss = test_endpoint(url, error_content, verbose, user_agent, xss_check)
            if result:
                valid_urls.append(result)
                if is_xss:
                    xss_urls.append(result)
                if verbose:
                    print(f"Found: {url}")

    return valid_urls, xss_urls


def main(domain, input_file, output_file, num_threads, common_endpoints, mixed_mode, verbose, user_agent, xss_check):
    subdomains = [domain] if domain else []

    if verbose:
        print("APIDetector - API Security Testing Tool\n" + ascii_art)

    if not domain:
        with open(input_file, 'r') as file:
            subdomains.extend(line.strip() for line in file)

    all_valid_urls, all_xss_urls = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(test_subdomain_endpoints, subdomain, common_endpoints, mixed_mode, verbose, user_agent) for subdomain in subdomains]
        for future in concurrent.futures.as_completed(futures):
            valid_urls, xss_urls = future.result()
            all_valid_urls.extend(valid_urls)
            all_xss_urls.extend(xss_urls)     

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

    if all_xss_urls and xss_check:
        xss_output_file = f"{output_file}_xss.txt" if output_file else "xss_results.txt"
        with open(xss_output_file, 'w') as file:
            for url in sorted(set(all_xss_urls)):
                file.write(url + '\n')
        if verbose:
            print(f"XSS vulnerabilities saved in {xss_output_file}")            


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
    parser.add_argument("-xss", "--xss-check", action='store_true', help="Enable XSS vulnerability checking")
 

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

    main(args.domain, args.input, args.output, args.threads, common_endpoints, args.mixed_mode, verbose, args.user_agent, args.xss_check)
