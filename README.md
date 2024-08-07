# APIDetector

APIDetector is a powerful and efficient tool designed for testing exposed Swagger endpoints in various subdomains with unique smart capabilities to detect false-positives. It's particularly useful for security professionals and developers who are engaged in API testing and vulnerability scanning.

## New in Version 2

APIDetector v2, launched at Blackhat Arsenal, automatically detects vulnerable Swagger versions with XSS and creates a proof of concept (PoC). The `apidetectorv2.py` file has been added to the repository to support this new feature.

### Requirements

To use the new version, install the required packages:

```bash
pip install playwright nest_asyncio
```

Then, install Playwright:

```bash
playwright install
```

## Features

- **Flexible Input**: Accepts a single domain or a list of subdomains from a file.
- **Multiple Protocols**: Option to test endpoints over both HTTP and HTTPS.
- **Concurrency**: Utilizes multi-threading for faster scanning.
- **Customizable Output**: Save results to a file or print to stdout.
- **Verbose and Quiet Modes**: Default verbose mode for detailed logs, with an option for quiet mode.
- **Custom User-Agent**: Ability to specify a custom User-Agent for requests.
- **Smart Detection of False-Positives**: Ability to detect most false-positives.
- **Automatic PoC Generation**: Detects vulnerable Swagger versions and generates a PoC image automatically.

## Getting Started

### Prerequisites

Before running APIDetector, ensure you have Python 3.x and pip installed on your system. You can download Python [here](https://www.python.org/downloads/).

### Installation

Clone the APIDetector repository to your local machine using:

```bash
git clone https://github.com/brinhosa/apidetector.git
cd apidetector
pip install requests
```

### Usage

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
- Denis Lourenço
- Bruno Francisco Cardoso

## Legal Disclaimer

The use of APIDetector should be limited to testing and educational purposes only. The developers of APIDetector assume no liability and are not responsible for any misuse or damage caused by this tool. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developers assume no responsibility for unauthorized or illegal use of this tool. Before using APIDetector, ensure you have permission to test the network or systems you intend to scan.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Thanks to all the contributors who have helped with testing, suggestions, and improvements.
- Author: Rafael B. Brinhosa  - https://www.linkedin.com/in/brinhosa/
