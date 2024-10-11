import pytest
from unittest.mock import MagicMock
from src.main_gui import handle_conversion, perform_conversion


# Mock the tkinter file dialogs
@pytest.fixture
def mock_filedialog(mocker):
    mock_open = mocker.patch("tkinter.filedialog.askopenfilename")
    mock_save = mocker.patch("tkinter.filedialog.asksaveasfilename")
    return mock_open, mock_save


# Mock messagebox to check for alerts
@pytest.fixture
def mock_messagebox(mocker):
    return {
        "showerror": mocker.patch("src.main_gui.messagebox.showerror"),
        "showwarning": mocker.patch("src.main_gui.messagebox.showwarning"),
        "showinfo": mocker.patch("src.main_gui.messagebox.showinfo"),
    }


# Test case for handle_conversion
def test_handle_conversion(mock_filedialog, mock_messagebox):
    mock_open, mock_save = mock_filedialog
    mock_showinfo = mock_messagebox["showinfo"]

    # Mock the file dialog responses
    mock_open.return_value = "source_file.json"
    mock_save.return_value = "destination_file.jmx"

    # Mock conversion function
    mock_conversion_func = MagicMock()

    # Call the function
    handle_conversion("json", "Postman Collection", "jmx", "JMX", mock_conversion_func)

    # Check if the conversion function was called
    mock_conversion_func.assert_called_once_with("source_file.json", "destination_file.jmx")

    # Check that the correct info message was shown
    mock_showinfo.assert_called_once_with("Success", "Conversion to JMX completed successfully!")


# Test case where source file is not selected
def test_handle_conversion_no_source(mock_filedialog, mock_messagebox):
    mock_open, mock_save = mock_filedialog
    mock_showwarning = mock_messagebox["showwarning"]

    # Simulate no source file selected
    mock_open.return_value = ""
    mock_save.return_value = "destination_file.jmx"

    mock_conversion_func = MagicMock()

    handle_conversion("json", "Postman Collection", "jmx", "JMX", mock_conversion_func)

    # Check that warning was shown
    mock_showwarning.assert_called_once_with("Input required", "Please select a Postman Collection file.")


# Test case where destination file is not selected
def test_handle_conversion_no_destination(mock_filedialog, mock_messagebox):
    mock_open, mock_save = mock_filedialog
    mock_showwarning = mock_messagebox["showwarning"]

    # Simulate selecting source file but not the destination file
    mock_open.return_value = "source_file.json"
    mock_save.return_value = ""

    mock_conversion_func = MagicMock()

    handle_conversion("json", "Postman Collection", "jmx", "JMX", mock_conversion_func)

    # Check that warning was shown
    mock_showwarning.assert_called_once_with("Input required", "Please provide a JMX file.")


# Test perform_conversion for a valid conversion
def test_perform_conversion_valid(mock_filedialog, mock_messagebox, mocker):
    mock_open, mock_save = mock_filedialog
    mock_showinfo = mock_messagebox["showinfo"]

    # Mock the file dialog responses
    mock_open.return_value = "source_file.json"
    mock_save.return_value = "destination_file.jmx"

    # Mock the conversion functions
    mock_create_jmx = mocker.patch("src.main_gui.create_jmx_file")

    # Test for valid Postman to JMX conversion
    perform_conversion('1')

    mock_create_jmx.assert_called_once_with("source_file.json", "destination_file.jmx")
    mock_showinfo.assert_called_once_with("Success", "Conversion to JMX completed successfully!")


# Test perform_conversion for unsupported conversion type
def test_perform_conversion_unsupported(mock_messagebox):
    mock_showwarning = mock_messagebox["showwarning"]

    # Test for an unsupported conversion type
    perform_conversion('3')

    mock_showwarning.assert_called_once_with("Feature not ready", "This feature is a WIP and currently unsupported.")


# Test perform_conversion for invalid conversion type
def test_perform_conversion_invalid(mock_messagebox):
    showerror = mock_messagebox["showerror"]

    # Test for an invalid conversion type
    perform_conversion('invalid')

    showerror.assert_called_once_with("Error", "Invalid conversion type selected.")
