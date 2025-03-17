# APIDetector

APIDetector is a powerful and efficient tool designed for testing exposed Swagger endpoints in various subdomains with unique smart capabilities to detect false-positives. It's particularly useful for security professionals and developers who are engaged in API testing and vulnerability scanning.

Presented at BlackHat Arsenal 2024 ([Link](https://www.blackhat.com/us-24/arsenal/schedule/index.html#apidetector-advanced-swagger-endpoint-detection-and-vulnerability-analysis-39649))

![APIDetector Web Interface](docs/images/web-interface.png)

## Version History

### New in Version 3 (Current)

- **Modern Web Interface**: User-friendly interface for easy API endpoint scanning
- **Real-time Results**: Live updates of discovered endpoints and vulnerabilities
- **Interactive Dashboard**: Clean and responsive UI using Tailwind CSS and Alpine.js
- **File Upload Support**: Scan multiple domains/subdomains at once by uploading a text file
- **Domain Validation**: Input validation with regex pattern matching
- **Flexible Configuration**: Easy-to-use form for scan settings with improved defaults
- **Visual Results**: Improved presentation of scan results and PoCs
- **Screenshot Management**: Automatically captures and displays screenshots of vulnerable endpoints (one per subdomain)
- **Targeted PoC Generation**: Generates proof of concept only for `/swagger-ui/index.html` endpoints
- **Responsive Design**: Optimized for all screen sizes from mobile to desktop
- **Error Handling**: Enhanced error feedback and logging
- **Accessibility Improvements**: Better keyboard navigation and screen reader support

### Version 2 Features

- **Automatic XSS Detection**: Identifies vulnerable Swagger versions
- **Visual PoC Generation**: Creates proof of concepts for vulnerabilities
- **Enhanced Error Handling**: Better feedback and logging
- **Improved Performance**: Optimized scanning algorithms

### Core Features

- **Flexible Input**: Accept single domains or lists of subdomains
- **Multiple Protocols**: Test endpoints over both HTTP and HTTPS
- **Concurrency**: Multi-threaded scanning for faster results
- **Smart Detection**: Advanced false-positive detection capabilities
- **Customizable Settings**: Configure threads, user-agent, and more

## Requirements

APIDetector v3 requires Python 3.x and the following packages:

```bash
flask         # Web framework
requests      # HTTP client
playwright    # Browser automation for screenshots
nest_asyncio  # Async IO support
```

All dependencies are listed in `requirements.txt` and can be installed automatically during setup.

### First-time Setup

After installing the required packages, you need to install the Playwright browsers:

```bash
python -m playwright install
```

This is required for the screenshot functionality to work properly.



## Getting Started

### Prerequisites

- Python 3.x ([Download](https://www.python.org/downloads/))
- pip (Python package installer)
- Git (for cloning the repository)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/brinhosa/apidetector.git
cd apidetector
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install browser automation:
```bash
playwright install
```

### Web Interface (Version 3)

1. Start the web server:
```bash
python app.py
```

2. By default, the server runs on http://127.0.0.1:5000. You can specify a different port or host:
```bash
python app.py --port 8080 --host 0.0.0.0
```

3. Open your browser and navigate to the URL shown in the terminal.

4. Using the web interface:
   - Enter a single domain or upload a file with multiple domains (one per line)
   - Configure scan options (thread count, mixed mode, user agent)
   - Click 'Start Scan' to begin
   - View real-time results as they appear
   - Screenshots of vulnerable endpoints will be displayed automatically

5. The screenshots are saved in the `screenshots` directory for future reference.

## Usage

APIDetector v3 offers two ways to interact with the tool: a modern web interface (new in v3) and a traditional command-line interface (original).

### Web Interface

1. Start the web server:
```bash
python app.py [options]
```

Available options:
| Option | Description | Default |
|--------|-------------|----------|
| `-p`, `--port` | Port number | 5000 |
| `--host` | Host address | 127.0.0.1 |
| `-d`, `--debug` | Enable debug mode | False |

Examples:
```bash
# Run on default settings (localhost:5000)
python app.py

# Run on custom port
python app.py -p 8080

# Allow external access
python app.py --host 0.0.0.0

# Run in debug mode
python app.py -d
```

2. Access the web interface:
   - Open your browser and navigate to the displayed URL
   - Enter the target domain OR upload a file with multiple domains (one per line)
   - Configure scan options:
     - HTTP/HTTPS mode
     - Number of threads (default: 10)
     - Custom User-Agent
   - Click "Start Scan"

3. View Results:
   - Discovered API endpoints are displayed in real-time with progress tracking
   - Vulnerable endpoints are automatically tested
   - PoC screenshots are generated for confirmed vulnerabilities
   - Results can be viewed while the scan is still in progress

### Command Line Interface

Run APIDetector using the command line. Here are some usage examples:

- Common usage, scan with 30 threads a list of subdomains using a Chrome user-agent and save the results in a file:
  ```bash
  python apidetector.py -i list_of_company_subdomains.txt -o results_file.txt -t 30 -ua "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
  ```

- To scan a single domain:

  ```bash
  python apidetector.py -d example.com
  ```

- To scan multiple domains from a file:

  ```bash
  python apidetector.py -i input_file.txt
  ```

- To specify an output file:

  ```bash
  python apidetector.py -i input_file.txt -o output_file.txt
  ```

- To use a specific number of threads:

  ```bash
  python apidetector.py -i input_file.txt -t 20
  ```

- To scan with both HTTP and HTTPS protocols:

  ```bash
  python apidetector.py -m -d example.com
  ```

- To run the script in quiet mode (suppress verbose output):

  ```bash
  python apidetector.py -q -d example.com
  ```

- To run the script with a custom user-agent:

  ```bash
  python apidetector.py -d example.com -ua "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
  ```
If you are using APIDetector v2, replace the commands by apidetectorv2.py.

### Options

- `-d`, `--domain`: Single domain to test.
- `-i`, `--input`: Input file containing subdomains to test.
- `-o`, `--output`: Output file to write valid URLs to.
- `-t`, `--threads`: Number of threads to use for scanning (default is 10).
- `-m`, `--mixed-mode`: Test both HTTP and HTTPS protocols.
- `-q`, `--quiet`: Disable verbose output (default mode is verbose).
- `-ua`, `--user-agent`: Custom User-Agent string for requests.

### Risk Details of Each Endpoint APIDetector Finds

Exposing Swagger or OpenAPI documentation endpoints can present various risks, primarily related to information disclosure. Here's an ordered list based on potential risk levels, with similar endpoints grouped together APIDetector scans:

#### 1. High-Risk Endpoints (Direct API Documentation):
- **Endpoints**: 
  - `'/swagger-ui.html'`, `'/swagger-ui/'`, `'/swagger-ui/index.html'`, `'/api/swagger-ui.html'`, `'/documentation/swagger-ui.html'`, `'/swagger/index.html'`, `'/api/docs'`, `'/docs'`, `'/api/swagger-ui'`, `'/documentation/swagger-ui'`
- **Risk**: 
  - These endpoints typically serve the Swagger UI interface, which provides a complete overview of all API endpoints, including request formats, query parameters, and sometimes even example requests and responses. 
  - **Risk Level**: High. Exposing these gives potential attackers detailed insights into your API structure and potential attack vectors.

#### 2. Medium-High Risk Endpoints (API Schema/Specification):
- **Endpoints**:
  - `'/openapi.json'`, `'/swagger.json'`, `'/api/swagger.json'`, `'/swagger.yaml'`, `'/swagger.yml'`, `'/api/swagger.yaml'`, `'/api/swagger.yml'`, `'/api.json'`, `'/api.yaml'`, `'/api.yml'`, `'/documentation/swagger.json'`, `'/documentation/swagger.yaml'`, `'/documentation/swagger.yml'`
- **Risk**: 
  - These endpoints provide raw Swagger/OpenAPI specification files. They contain detailed information about the API endpoints, including paths, parameters, and sometimes authentication methods.
  - **Risk Level**: Medium-High. While they require more interpretation than the UI interfaces, they still reveal extensive information about the API.

#### 3. Medium Risk Endpoints (API Documentation Versions):
- **Endpoints**:
  - `'/v2/api-docs'`, `'/v3/api-docs'`, `'/api/v2/swagger.json'`, `'/api/v3/swagger.json'`, `'/api/v1/documentation'`, `'/api/v2/documentation'`, `'/api/v3/documentation'`, `'/api/v1/api-docs'`, `'/api/v2/api-docs'`, `'/api/v3/api-docs'`, `'/swagger/v2/api-docs'`, `'/swagger/v3/api-docs'`, `'/swagger-ui.html/v2/api-docs'`, `'/swagger-ui.html/v3/api-docs'`, `'/api/swagger/v2/api-docs'`, `'/api/swagger/v3/api-docs'`
- **Risk**: 
  - These endpoints often refer to version-specific documentation or API descriptions. They reveal information about the API's structure and capabilities, which could aid an attacker in understanding the API's functionality and potential weaknesses.
  - **Risk Level**: Medium. These might not be as detailed as the complete documentation or schema files, but they still provide useful information for attackers.

#### 4. Lower Risk Endpoints (Configuration and Resources):
- **Endpoints**:
  - `'/swagger-resources'`, `'/swagger-resources/configuration/ui'`, `'/swagger-resources/configuration/security'`, `'/api/swagger-resources'`, `'/api.html'`
- **Risk**: 
  - These endpoints often provide auxiliary information, configuration details, or resources related to the API documentation setup.
  - **Risk Level**: Lower. They may not directly reveal API endpoint details but can give insights into the configuration and setup of the API documentation.

### Summary:
- **Highest Risk**: Directly exposing interactive API documentation interfaces.
- **Medium-High Risk**: Exposing raw API schema/specification files.
- **Medium Risk**: Version-specific API documentation.
- **Lower Risk**: Configuration and resource files for API documentation.

### Recommendations:
- **Access Control**: Ensure that these endpoints are not publicly accessible or are at least protected by authentication mechanisms.
- **Environment-Specific Exposure**: Consider exposing detailed API documentation only in development or staging environments, not in production.
- **Monitoring and Logging**: Monitor access to these endpoints and set up alerts for unusual access patterns.

## Contributing

Contributions to APIDetector are welcome! Feel free to fork the repository, make changes, and submit pull requests.
Special thanks to the contributing members who helped with testing and features suggestions:
- Filipi Pires (Ambassador) - https://www.linkedin.com/in/filipipires/
- Denis Lourenço -  https://www.linkedin.com/in/🚲denis-lourenço-18b07a128/
- Bruno Francisco Cardoso - https://www.linkedin.com/in/bruno-francisco-cardoso-27445953/

## Legal Disclaimer

The APIDetector tool is strictly intended for testing and educational purposes only. The developers of APIDetector assume no liability and disclaim all responsibility for any misuse, unintended consequences, or damage caused by the use of this tool. Any unauthorized, illegal, or otherwise harmful use of APIDetector is expressly prohibited. The end user bears full responsibility for ensuring compliance with all relevant local, state, federal, and international laws. By using this tool, the user acknowledges that they hold the necessary authorizations to test the networks or systems they intend to scan and agrees to indemnify the developers against any and all claims arising from its use.
The end user is solely responsible for ensuring that their use of this tool does not violate any legal restrictions or terms of service governing the networks or systems under test.

**Disclaimer: APIDetector Tool Usage**
The APIDetector tool is exclusively designed for lawful testing and educational purposes. It is provided on an "as-is" basis without warranties of any kind, express or implied. The developers and distributors of APIDetector explicitly disclaim any liability for misuse, unintended consequences, or damages resulting from the use of this tool.
**Important Legal Notice:** Unauthorized, illegal, or unethical use of APIDetector is strictly prohibited. Users are solely responsible for adhering to all applicable local, state, federal, and international laws, as well as any terms of service governing the networks or systems they engage with. By using APIDetector, users affirm that they possess the necessary authorizations to test the targeted networks or systems. 
**Assumption of Risk and Indemnification:** By downloading, installing, or using APIDetector, the user assumes full responsibility for any legal repercussions associated with its usage. The developers and distributors of APIDetector shall not be held liable for any legal consequences, damages, or third-party claims arising from its use. Users agree to indemnify and hold harmless the developers and distributors against any claims, legal fees, or liabilities associated with their actions.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Thanks to all the contributors who have helped with testing, suggestions, and improvements.
- Author: Rafael B. Brinhosa  - https://www.linkedin.com/in/brinhosa/

