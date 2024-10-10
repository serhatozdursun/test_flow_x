import tkinter as tk
from tkinter import filedialog, messagebox
from src.jmx.jmx_creator import create_jmx_file
from src.postman.postman_json_creator import create_postman_collection
import webbrowser


def handle_conversion(source_ext, source_desc, dest_ext, dest_desc, conversion_func):
    """
    Handles the file selection and conversion process for a given conversion type.

    :param conversion_type: The selected conversion type.
    :param source_ext: The file extension for the source file.
    :param source_desc: The description for the source file type.
    :param dest_ext: The file extension for the destination file.
    :param dest_desc: The description for the destination file type.
    :param conversion_func: The function to perform the conversion.
    """
    source_file = filedialog.askopenfilename(title=f"Select {source_desc} file",
                                             filetypes=[(f"{source_desc} files", f"*.{source_ext}")])
    if source_file:
        destination_file = filedialog.asksaveasfilename(title=f"Save as {dest_desc} file",
                                                        defaultextension=f".{dest_ext}",
                                                        filetypes=[(f"{dest_desc} files", f"*.{dest_ext}")])
        if destination_file:
            conversion_func(source_file, destination_file)
            messagebox.showinfo("Success", f"Conversion to {dest_desc} completed successfully!")
        else:
            messagebox.showwarning("Input required", f"Please provide a {dest_desc} file.")
    else:
        messagebox.showwarning("Input required", f"Please select a {source_desc} file.")


def convert_files():
    conversion_type = conversion_var.get()

    conversion_mapping = {
        '1': lambda: handle_conversion('1', 'json', 'Postman Collection JSON', 'jmx', 'JMX', create_jmx_file),
        '2': lambda: handle_conversion('2', 'jmx', 'JMeter JMX', 'json', 'Postman Collection JSON',
                                       create_postman_collection)
    }

    unsupported_conversions = ['3', '4', '5', '6']

    if conversion_type in conversion_mapping:
        conversion_mapping[conversion_type]()
    elif conversion_type in unsupported_conversions:
        messagebox.showwarning("Feature not ready", "This feature is a WIP and currently unsupported.")
    else:
        messagebox.showerror("Error", "Invalid conversion type selected.")


def create_gui():
    root = tk.Tk()
    root.title("Test Flow X Converter")

    options = [
        "1. Postman Collection => JMX",
        "2. JMX => Postman Collection",
    #    "3. Postman Collection => K6 (unsupported feature, WIP)",
    #    "4. K6 => Postman Collection (unsupported feature, WIP)",
    #    "5. JMX => K6 (unsupported feature, WIP)",
    #    "6. K6 => JMX (unsupported feature, WIP)"
    ]

    tk.Label(root, text="Select Conversion Type", font=("Arial", 14)).pack(pady=10)

    global conversion_var
    conversion_var = tk.StringVar(value="1")

    # Add radio buttons for conversion options
    for option in options:
        tk.Radiobutton(root, text=option, variable=conversion_var, value=option[0], font=("Arial", 12)).pack(anchor="w",
                                                                                                             padx=20)

    convert_button = tk.Button(
        root,
        text="Convert",
        command=convert_files,
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
    webbrowser.open(url)


if __name__ == '__main__':
    create_gui()
