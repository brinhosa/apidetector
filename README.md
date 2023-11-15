# APIDetector

APIDetector is a powerful and efficient tool designed for testing exposed Swagger endpoints in various subdomains. It's particularly useful for security professionals and developers who are engaged in API testing and vulnerability scanning.

## Features

- **Flexible Input**: Accepts a single domain or a list of subdomains from a file.
- **Multiple Protocols**: Option to test endpoints over both HTTP and HTTPS.
- **Concurrency**: Utilizes multi-threading for faster scanning.
- **Customizable Output**: Save results to a file or print to stdout.

## Getting Started

### Prerequisites

Before running APIDetector, ensure you have Python 3.x installed on your system. You can download Python [here](https://www.python.org/downloads/).

### Installation

Clone the APIDetector repository to your local machine using:

```bash
git clone https://github.com/[your-username]/APIDetector.git
cd APIDetector
```

### Usage

Run APIDetector using the command line. Here are some usage examples:

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

### Options

- `-d`, `--domain`: Single domain to test.
- `-i`, `--input`: Input file containing subdomains to test.
- `-o`, `--output`: Output file to write valid URLs to.
- `-t`, `--threads`: Number of threads to use for scanning (default is 10).
- `-m`, `--mixed-mode`: Test both HTTP and HTTPS protocols.

## Contributing

Contributions to APIDetector are welcome! Feel free to fork the repository, make changes, and submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Thanks to all the contributors who have helped with testing, suggestions, and improvements.
- Author: Rafael Brinhosa  - https://www.linkedin.com/in/brinhosa/

## Legal Disclaimer

The use of APIDetector should be limited to testing and educational purposes only. The developers of APIDetector assume no liability and are not responsible for any misuse or damage caused by this tool. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developers assume no responsibility for unauthorized or illegal use of this tool. Before using APIDetector, ensure you have permission to test the network or systems you intend to scan.