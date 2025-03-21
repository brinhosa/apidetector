#REQUIREMENTS:
#pip install playwright nest_asyncio
#EXECUTE:
#playwright install
## Legal Disclaimer
#The use of APIDetector should be limited to testing and educational purposes only. The developers of APIDetector assume no liability and are not responsible for any misuse or damage caused by this tool. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developers assume no responsibility for unauthorized or illegal use of this tool. Before using APIDetector, ensure you have permission to test the network or systems you intend to scan.

import nest_asyncio
import asyncio
from playwright.async_api import async_playwright
import argparse
import sys
import re
import os

nest_asyncio.apply()

def generate_output_filename(url):
    # Get domain from environment if available
    domain = os.environ.get('DOMAIN', '')
    
    # If domain is provided in environment, use it
    if domain:
        # Create a clean domain name
        clean_domain = re.sub(r'[^a-zA-Z0-9]', '_', domain)
        return f"{clean_domain}.png"
    
    # Otherwise extract domain from URL
    url_path = url.split('://')[-1]  # Remove protocol
    if '/' in url_path:
        # Get just the domain part
        domain = url_path.split('/', 1)[0]
    else:
        domain = url_path
    
    # Create a clean domain name
    clean_domain = re.sub(r'[^a-zA-Z0-9]', '_', domain)
    return f"{clean_domain}.png"

async def generate_poc_screenshot(url, output_file):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            # Wait for a specific element that indicates the page is fully loaded
            await page.wait_for_selector('#swagger-ui')

            # Check for the presence of the text "XSS"
            content = await page.content()
            if "XSS" in content:
                print(f"XSS was found, PoC image saved as \"{output_file}\".")
                # Take a screenshot
                await page.screenshot(path=output_file)
                # If this is a PoC generation, print a special message that can be detected
                if os.environ.get('GENERATE_POC') == 'true':
                    print("Screenshot saved successfully for PoC")
            else:
                print("XSS was not found.")

            await browser.close()
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="PoC Generator - Generates a screenshot of the Swagger UI page if XSS text is found.")
    parser.add_argument("url", help="The URL of the Swagger UI page.")
    parser.add_argument("-o", "--output", help="Output file for the screenshot.")
    args = parser.parse_args()

    if not args.url:
        print("URL is required.", file=sys.stderr)
        sys.exit(1)

    # Get output filename
    output_filename = args.output or generate_output_filename(args.url)
    
    # Check if SCREENSHOT_PATH environment variable is set
    screenshot_path = os.environ.get('SCREENSHOT_PATH')
    if screenshot_path:
        # Use the screenshots folder from environment variable
        output_file = os.path.join(screenshot_path, output_filename)
        # Ensure the directory exists
        os.makedirs(screenshot_path, exist_ok=True)
    else:
        # Use the current directory
        output_file = output_filename

    asyncio.run(generate_poc_screenshot(args.url, output_file))

if __name__ == "__main__":
    main()
