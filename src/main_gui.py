import tkinter as tk
from tkinter import filedialog, messagebox
from src.jmx.jmx_creator import create_jmx_file
from src.postman.postman_json_creator import create_postman_collection
import webbrowser


def select_source_file(source_desc, source_ext):
    """
    Opens a file dialog to select the source file for conversion.

    :param source_desc: Description of the source file.
    :param source_ext: File extension of the source file.
    :return: Selected source file path or None.
    """
    return filedialog.askopenfilename(
        title=f"Select {source_desc} file",
        filetypes=[(f"{source_desc} files", f"*.{source_ext}")]
    )


def select_destination_file(dest_desc, dest_ext):
    """
    Opens a file dialog to specify the destination file path.

    :param dest_desc: Description of the destination file.
    :param dest_ext: File extension of the destination file.
    :return: Destination file path or None.
    """
    return filedialog.asksaveasfilename(
        title=f"Save as {dest_desc} file",
        defaultextension=f".{dest_ext}",
        filetypes=[(f"{dest_desc} files", f"*.{dest_ext}")]
    )


def handle_conversion(source_ext, source_desc, dest_ext, dest_desc, conversion_func):
    """
    Handles the file selection and conversion process for a given conversion.

    :param source_ext: The file extension for the source file.
    :param source_desc: The description for the source file type.
    :param dest_ext: The file extension for the destination file.
    :param dest_desc: The description for the destination file type.
    :param conversion_func: The function to perform the conversion.
    """
    source_file = select_source_file(source_desc, source_ext)
    if source_file:
        destination_file = select_destination_file(dest_desc, dest_ext)
        if destination_file:
            conversion_func(source_file, destination_file)
            messagebox.showinfo("Success", f"Conversion to {dest_desc} completed successfully!")
        else:
            messagebox.showwarning("Input required", f"Please provide a {dest_desc} file.")
    else:
        messagebox.showwarning("Input required", f"Please select a {source_desc} file.")


def perform_conversion(conversion_id):
    """
    Executes the conversion based on the selected conversion ID.

    :param conversion_id: ID representing the conversion type.
    """
    conversion_mapping = {
        '1': lambda: handle_conversion('json', 'Postman Collection JSON', 'jmx', 'JMX', create_jmx_file),
        '2': lambda: handle_conversion('jmx', 'JMeter JMX', 'json', 'Postman Collection JSON', create_postman_collection)
    }

    unsupported_conversions = ['3', '4', '5', '6']

    if conversion_id in conversion_mapping:
        conversion_mapping[conversion_id]()
    elif conversion_id in unsupported_conversions:
        messagebox.showwarning("Feature not ready", "This feature is a WIP and currently unsupported.")
    else:
        messagebox.showerror("Error", "Invalid conversion type selected.")


def create_gui():
    """
    Creates the main graphical user interface for the converter application.
    """
    root = tk.Tk()
    root.title("Test Flow X Converter")

    options = [
        "1. Postman Collection => JMX",
        "2. JMX => Postman Collection",
    ]

    tk.Label(root, text="Select Conversion Type", font=("Arial", 14)).pack(pady=10)

    global conversion_var
    conversion_var = tk.StringVar(value="1")

    # Add radio buttons for conversion options
    for option in options:
        tk.Radiobutton(
            root,
            text=option,
            variable=conversion_var,
            value=option[0],
            font=("Arial", 12)
        ).pack(anchor="w", padx=20)

    convert_button = tk.Button(
        root,
        text="Convert",
        command=lambda: perform_conversion(conversion_var.get()),
        font=("Arial", 12),
        bg="green",
        fg="black",
        activebackground="lightgreen",
        activeforeground="black",
        highlightthickness=0,
        borderwidth=0
    )
    convert_button.pack(pady=20)

    # Additional GUI elements (creator label, website link)
    tk.Label(root, text="Created by: Mehmet Serhat Özdursun", font=("Arial", 10)).pack(pady=5)

    website_link = tk.Label(root, text="Website", fg="blue", cursor="hand2")
    website_link.pack(pady=5)
    website_link.bind("<Button-1>", lambda e: open_link("https://serhatozdursun.com/"))

    root.geometry("400x250")
    root.mainloop()


def open_link(url):
    """
    Opens the given URL in the default web browser.

    :param url: URL to open.
    """
    webbrowser.open(url)


if __name__ == '__main__':
    create_gui()
