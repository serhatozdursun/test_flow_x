# Test Flow X

## Description

Test Flow X is a Python project designed for converting various types of performance test files, including Postman collections and JMX files. The goal is to facilitate the testing workflow by providing easy conversion options among different file formats.

## Features

- Convert Postman Collection JSON files to JMX files.
- Convert JMX files to Postman Collection JSON files.
- Additional support for K6 conversions (WIP).

## Installation

To install the necessary dependencies, create a `requirements.txt` file as described below and run:

```bash
pip install -r requirements.txt
```

## Usage

Run the script to select a conversion type and follow the prompts:

```bash
python main.py
```

You will be presented with the following conversion options:

## Postman Collection -> JMX
* JMX -> Postman Collection
* Postman Collection -> K6 (unsupported feature, WIP)
* K6 -> Postman Collection (unsupported feature, WIP)
* JMX -> K6 (unsupported feature, WIP)
* K6 -> JMX (unsupported feature, WIP)


## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
