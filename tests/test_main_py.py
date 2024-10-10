import pytest

from src.main import (
    print_hi,
    get_file_name,
    convert_postman_to_jmx,
    convert_jmx_to_postman,
    unsupported_conversion,
    main, RED_TEXT
)

# ANSI escape codes for colored text
YELLOW_TEXT = '\033[93m'
GREEN_TEXT = '\033[92m'
RESET_TEXT = '\033[0m'


# Test for print_hi function
def test_print_hi(mocker):
    mock_print = mocker.patch('builtins.print')
    print_hi()
    mock_print.assert_called_once_with('Store your file to convert under the file_to_convert directory')


# Test for get_file_name function
@pytest.mark.parametrize("input_value, expected_output", [
    ("test_file.json", "test_file"),
    ("test_file_without_extension", "test_file_without_extension"),
])
def test_get_file_name(mocker, input_value, expected_output):
    mock_input = mocker.patch('builtins.input', return_value=input_value)
    result = get_file_name("Enter file name: ", ".json")
    assert result == expected_output
    mock_input.assert_called_once_with(f"{YELLOW_TEXT}Enter file name: {RESET_TEXT}")


# Test for convert_postman_to_jmx function
def test_convert_postman_to_jmx(mocker):
    mock_get_file_name = mocker.patch('src.main.get_file_name', side_effect=["source_file", "destination_file"])
    mock_create_jmx_file = mocker.patch('src.main.create_jmx_file')
    mock_print = mocker.patch('builtins.print')

    convert_postman_to_jmx()

    mock_get_file_name.assert_any_call(
        "Enter the Postman Collection JSON file name (without .json extension) from the file_to_convert folder: ",
        ".json"
    )
    mock_get_file_name.assert_any_call(
        "Enter the desired JMX file name (without .jmx extension) to save in the file_to_convert folder: ",
        ".jmx"
    )
    mock_create_jmx_file.assert_called_once_with("source_file", "destination_file")
    mock_print.assert_called_once_with(f"{GREEN_TEXT}Conversion from Postman Collection to JMX completed successfully!{RESET_TEXT}")


# Test for convert_jmx_to_postman function
def test_convert_jmx_to_postman(mocker):
    mock_get_file_name = mocker.patch('src.main.get_file_name', side_effect=["source_jmx_file", "destination_json_file"])
    mock_generate_postman_collection = mocker.patch('src.main.generate_postman_collection', return_value="mock_collection")
    mock_save_json = mocker.patch('src.main.save_json')
    mock_print = mocker.patch('builtins.print')

    convert_jmx_to_postman()

    mock_get_file_name.assert_any_call(
        "Enter the Jmeter Suite JMX file name (without .jmx extension) from the file_to_convert folder: ",
        ".jmx"
    )
    mock_get_file_name.assert_any_call(
        "Enter the desired Postman Collection JSON file name (without .json extension) to save in the file_to_convert folder: ",
        ".json"
    )
    mock_generate_postman_collection.assert_called_once_with("source_jmx_file")
    mock_save_json.assert_called_once_with("destination_json_file", "mock_collection")
    mock_print.assert_called_once_with(f"{GREEN_TEXT}Conversion from JMX suite to Postman Collection completed successfully!{RESET_TEXT}")


# Test for unsupported_conversion function
def test_unsupported_conversion(mocker):
    mock_print = mocker.patch('builtins.print')
    unsupported_conversion()
    mock_print.assert_called_once_with(f"{RED_TEXT}This conversion type is not supported yet.{RESET_TEXT}")


# Test for main function with valid input for Postman to JMX
def test_main_postman_to_jmx(mocker):
    mock_print_hi = mocker.patch('src.main.print_hi')
    mock_input = mocker.patch('builtins.input', return_value='1')
    mock_convert_postman_to_jmx = mocker.patch('src.main.convert_postman_to_jmx')

    main()

    mock_print_hi.assert_called_once()
    mock_input.assert_called_once_with(f"{YELLOW_TEXT}Please select one of the supported conversion types:\n"
                                       "1 -> Postman Collection -> JMX\n"
                                       "2 -> JMX -> Postman Collection\n"
                                       f"{RESET_TEXT}{YELLOW_TEXT}>>> {RESET_TEXT}")
    mock_convert_postman_to_jmx.assert_called_once()


# Test for main function with valid input for JMX to Postman
def test_main_jmx_to_postman(mocker):
    mock_print_hi = mocker.patch('src.main.print_hi')
    mock_input = mocker.patch('builtins.input', return_value='2')
    mock_convert_jmx_to_postman = mocker.patch('src.main.convert_jmx_to_postman')

    main()

    mock_print_hi.assert_called_once()
    mock_input.assert_called_once_with(f"{YELLOW_TEXT}Please select one of the supported conversion types:\n"
                                       "1 -> Postman Collection -> JMX\n"
                                       "2 -> JMX -> Postman Collection\n"
                                       f"{RESET_TEXT}{YELLOW_TEXT}>>> {RESET_TEXT}")
    mock_convert_jmx_to_postman.assert_called_once()


# Test for main function with invalid input (unsupported conversion)
def test_main_unsupported_conversion(mocker):
    mock_print_hi = mocker.patch('src.main.print_hi')
    mock_input = mocker.patch('builtins.input', return_value='3')
    mock_unsupported_conversion = mocker.patch('src.main.unsupported_conversion')

    main()

    mock_print_hi.assert_called_once()
    mock_input.assert_called_once_with(f"{YELLOW_TEXT}Please select one of the supported conversion types:\n"
                                       "1 -> Postman Collection -> JMX\n"
                                       "2 -> JMX -> Postman Collection\n"
                                       f"{RESET_TEXT}{YELLOW_TEXT}>>> {RESET_TEXT}")
    mock_unsupported_conversion.assert_called_once()
