from src.jmx.jmx_creator import create_jmx_file
from src.postman.postman_json_creator import generate_postman_collection, save_json

# ANSI escape codes for colored text
YELLOW_TEXT = '\033[93m'
RED_TEXT = '\033[91m'
GREEN_TEXT = '\033[92m'
RESET_TEXT = '\033[0m'


def print_hi():
    """Displays an initial greeting message."""
    print('Store your file to convert under the file_to_convert directory')


def get_file_name(prompt, extension):
    """Prompts the user for a file name and removes the extension if included."""
    file_name = input(f"{YELLOW_TEXT}{prompt}{RESET_TEXT}")
    return file_name.replace(extension, "") if extension in file_name else file_name


def convert_postman_to_jmx():
    """Handles conversion from Postman Collection to JMX."""
    source_file = get_file_name(
        "Enter the Postman Collection JSON file name (without .json extension) from the file_to_convert folder: ", ".json")
    destination_file = get_file_name(
        "Enter the desired JMX file name (without .jmx extension) to save in the file_to_convert folder: ", ".jmx")
    create_jmx_file(source_file, destination_file)
    print(f"{GREEN_TEXT}Conversion from Postman Collection to JMX completed successfully!{RESET_TEXT}")


def convert_jmx_to_postman():
    """Handles conversion from JMX to Postman Collection."""
    source_file = get_file_name(
        "Enter the Jmeter Suite JMX file name (without .jmx extension) from the file_to_convert folder: ", ".jmx")
    destination_file = get_file_name(
        "Enter the desired Postman Collection JSON file name (without .json extension) to save in the file_to_convert folder: ", ".json")
    collection = generate_postman_collection(source_file)
    save_json(destination_file, collection)
    print(f"{GREEN_TEXT}Conversion from JMX suite to Postman Collection completed successfully!{RESET_TEXT}")


def unsupported_conversion():
    """Displays a message for unsupported conversion types."""
    print(f"{RED_TEXT}This conversion type is not supported yet.{RESET_TEXT}")


def main():
    """Main function to handle conversion based on user input."""
    print_hi()

    conversion_type = input(f"{YELLOW_TEXT}Please select one of the supported conversion types:\n"
                            "1 -> Postman Collection -> JMX\n"
                            "2 -> JMX -> Postman Collection\n"
                        #    "3 -> Postman Collection -> K6 (unsupported feature, WIP)\n"
                        #    "4 -> K6 -> Postman Collection (unsupported feature, WIP)\n"
                        #    "5 -> JMX -> K6 (unsupported feature, WIP)\n"
                        #    "6 -> K6 -> JMX (unsupported feature, WIP)\n"
                            f"{RESET_TEXT}{YELLOW_TEXT}>>> {RESET_TEXT}")

    conversion_actions = {
        '1': convert_postman_to_jmx,
        '2': convert_jmx_to_postman
    }

    # Call the appropriate conversion function or notify for unsupported types
    conversion_actions.get(conversion_type, unsupported_conversion)()


if __name__ == '__main__':
    main()
