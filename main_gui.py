import tkinter as tk
from tkinter import filedialog, messagebox
from jmx.jmx_creator import create_jmx_file


def convert_files():
    conversion_type = conversion_var.get()

    if conversion_type == '1':
        # Prompt to select a Postman Collection file
        source_file = filedialog.askopenfilename(title="Select Postman Collection JSON",
                                                 filetypes=[("JSON files", "*.json")])
        if source_file:
            # Prompt to save as a JMX file
            destination_file = filedialog.asksaveasfilename(title="Save as JMX file", defaultextension=".jmx",
                                                            filetypes=[("JMX files", "*.jmx")])
            if destination_file:
                create_jmx_file(source_file, destination_file)
                messagebox.showinfo("Success", "Conversion to JMX completed successfully!")
        else:
            messagebox.showwarning("Input required", "Please select a Postman Collection JSON file.")

    elif conversion_type == '2':
        messagebox.showwarning("Feature not ready", "JMX to Postman Collection conversion is a WIP.")

    elif conversion_type == '3':
        messagebox.showwarning("Feature not ready", "Postman Collection to K6 conversion is a WIP.")

    elif conversion_type == '4':
        messagebox.showwarning("Feature not ready", "K6 to Postman Collection conversion is a WIP.")

    elif conversion_type == '5':
        messagebox.showwarning("Feature not ready", "JMX to K6 conversion is a WIP.")

    elif conversion_type == '6':
        messagebox.showwarning("Feature not ready", "K6 to JMX conversion is a WIP.")


def create_gui():
    root = tk.Tk()
    root.title("Test Flow X Converter")

    # Conversion options
    options = [
        "1 -> Postman Collection -> JMX",
        "2 -> JMX -> Postman Collection (unsupported feature, WIP)",
        "3 -> Postman Collection -> K6 (unsupported feature, WIP)",
        "4 -> K6 -> Postman Collection (unsupported feature, WIP)",
        "5 -> JMX -> K6 (unsupported feature, WIP)",
        "6 -> K6 -> JMX (unsupported feature, WIP)"
    ]

    tk.Label(root, text="Select Conversion Type", font=("Arial", 14)).pack(pady=10)

    global conversion_var
    conversion_var = tk.StringVar(value="1")

    # Radio buttons for conversion options
    for option in options:
        tk.Radiobutton(root, text=option, variable=conversion_var, value=option[0], font=("Arial", 12)).pack(anchor="w",
                                                                                                             padx=20)

    convert_button = tk.Button(
        root,
        text="Convert",
        command=convert_files,
        font=("Arial", 12),
        bg="green",  # Set initial button background color
        fg="black",  # Set initial text color
        activebackground="lightgreen",  # Background color when clicked
        activeforeground="black",  # Text color when clicked
        highlightthickness=0,  # Remove highlight border
        borderwidth=0  # Remove button border
    )
    convert_button.pack(pady=20)

    root.geometry("500x400")
    root.mainloop()


if __name__ == '__main__':
    create_gui()