[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=serhatozdursun_test_flow_x)](https://sonarcloud.io/summary/new_code?id=serhatozdursun_test_flow_x) </br>
[![CodeQL Static Code Analysis](https://github.com/serhatozdursun/test_flow_x/actions/workflows/codeql.yml/badge.svg)](https://github.com/serhatozdursun/test_flow_x/actions/workflows/codeql.yml) </br>
[![Python Tests](https://github.com/serhatozdursun/test_flow_x/actions/workflows/python-tests.yml/badge.svg)](https://github.com/serhatozdursun/test_flow_x/actions/workflows/python-tests.yml)

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

Also, you should python-tk installed in you local

## Usage

You can use the application in two modes: Command-line or Graphical User Interface (GUI).

### Command-line Mode
Run the script to select a conversion type and follow the prompts:

```bash
python -m src.main_gui
```
You will be presented with the following conversion options:

## Postman Collection -> JMX
* JMX -> Postman Collection
* Postman Collection -> JMX

### GUI Mode
If you prefer a graphical interface, you can run the application with a user-friendly GUI:
```bash
python python -m src.main_gui
```
After running the command, a window will appear allowing you to choose the conversion type using radio buttons. Select a conversion type and click "Convert". You can use the GUI to select files for conversion or automatically save them to the default directories if a destination is not provided.

Steps for GUI:
1. Choose the conversion type (e.g., Postman Collection -> JMX).
2. Click "Convert" and select the source file for conversion.
3. Provide a destination file name or let the program use the default path.
4. The conversion result will be displayed, or you will be notified if the feature is not yet supported.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
