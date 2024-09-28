from jmx.jmx_creator import create_jmx_file

# ANSI escape codes for colored text
YELLOW_TEXT = '\033[93m'
RED_TEXT = '\033[91m'
GREEN_TEXT = '\033[92m'
RESET_TEXT = '\033[0m'


def print_hi(name):
    """Prints a greeting message."""
    print(f'Hi, {name}')


# Main execution block
if __name__ == '__main__':
    print_hi('Store your file to convert under the file_to_convert directory')

    conversion_type = input(f"{YELLOW_TEXT}Please select one of the supported conversion types:\n"
                            "1 -> Postman Collection -> JMX\n"
                            "2 -> JMX -> Postman Collection\n"
                            "3 -> Postman Collection -> K6 (unsupported feature, WIP)\n"
                            "4 -> K6 -> Postman Collection (unsupported feature, WIP)\n"
                            "5 -> JMX -> K6 (unsupported feature, WIP)\n"
                            f"6 -> K6 -> JMX (unsupported feature, WIP)\n{RESET_TEXT}")

    if conversion_type == '1':
        source_file = input(
            f"{YELLOW_TEXT}Enter the Postman Collection JSON file name (without .json extension): {RESET_TEXT}")
        if '.json' in source_file:
            source_file = source_file.replace(".json", "")
        destination_file = input(f"{YELLOW_TEXT}Enter the desired JMX file name (without .jmx extension): {RESET_TEXT}")
        if '.jmx' in destination_file:
            destination_file = source_file.replace(".jmx", "")
        create_jmx_file(source_file, destination_file)
        print(f"{GREEN_TEXT}Conversion from Postman Collection to JMX completed successfully!{RESET_TEXT}")

    elif conversion_type == '2':
        source_file = input(f"{YELLOW_TEXT}Enter the JMX file name (with .jmx extension): {RESET_TEXT}")
        destination_file = input(
            f"{YELLOW_TEXT}Enter the desired Postman Collection JSON file name (with .json extension): {RESET_TEXT}")
        print(f"{RED_TEXT}This feature is not ready yet. It will be available soon.{RESET_TEXT}")

    else:
        print(f"{RED_TEXT}This conversion type is not supported yet.{RESET_TEXT}")
