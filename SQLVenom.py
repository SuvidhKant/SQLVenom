import messagebox
import requests
import argparse
import pyfiglet
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tk_messagebox
from colorama import init, Fore, Style
from core import requester
from core import extractor
from core import crawler
from urllib.parse import unquote

payloads_dict = {
    "Generic SQL Injection": "payloads/payloadsgeneric_sql_injection.txt",
    "Generic Error Based": "payloads/payloadsgeneric_error_based.txt",
    "Generic Time Based SQL": "payloads/payloadsgeneric_time_based_sql.txt",
    "Auth Bypass": "payloads/payloadsauth_bypass.txt",
    "Generic Union Select": "payloads/payloadsgeneric_Union_Select.txt"
}

def display_banner():
    # Generate the SQLVenom banner using PyFiglet
    sqlvenom_banner = pyfiglet.figlet_format("SQL Venom", font="big")
    
    # Get the size of the terminal window
    terminal_size = os.get_terminal_size()
    terminal_width = terminal_size.columns
    terminal_height = terminal_size.lines

    # Calculate the horizontal and vertical padding
    horizontal_padding = (terminal_width - len(sqlvenom_banner.split('\n')[0])) // 2
    vertical_padding = (terminal_height - len(sqlvenom_banner.split('\n'))) // 2

    init()  # Initialize colorama

    # Print red underline above the banner
    print(Fore.RED + '-' * terminal_width)
    print(Fore.RED + '-' * terminal_width)

    print()
    print()

    # Print the banner with centered padding
    for line in sqlvenom_banner.split('\n'):
        print(Fore.BLUE + ' ' * horizontal_padding + line + Style.RESET_ALL)

    # print two lines of hyphens above and below the banner with red color
    print(Fore.RED + '-' * terminal_width)
    print(Fore.RED + '-' * terminal_width)

def concatenate_list_data(lst, result):
    for element in lst:
        result = result + "\n" + str(element)
    return result

def get_injection_type(font):
    # Customize this function based on requirements
    return 'standard'

class SQLVenomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Venom GUI")

        self.domain_label = ttk.Label(root, text="Domain:")
        self.domain_entry = ttk.Entry(root)

        self.subs_var = tk.BooleanVar()
        self.subs_check = ttk.Checkbutton(root, text="Include Subdomains", variable=self.subs_var)

        self.font_label = ttk.Label(root, text="Choose PyFiglet Font:")
        self.font_combobox = ttk.Combobox(root, values=["Standard", "Slant"])
        self.font_combobox.set("Font")

        # Add a label and combobox for selecting payload type
        self.payload_label = ttk.Label(root, text="Select Payload Type:")
        self.payload_combobox = ttk.Combobox(root, values=["Generic SQL Injection", "Generic Error Based", "Generic Time Based SQL", "Auth Bypass", "Generic Union Select"])
        self.payload_combobox.set("Select Payload")

        self.start_button = ttk.Button(root, text="Start SQL Injection Scan", command=self.start_scan)

        # Arrange widgets using grid
        self.domain_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.domain_entry.grid(row=0, column=1, padx=10, pady=5)

        self.subs_check.grid(row=1, column=0, columnspan=2, pady=5)

        self.font_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.font_combobox.grid(row=2, column=1, padx=10, pady=5)

        # Add payload label and combobox to the grid
        self.payload_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.payload_combobox.grid(row=3, column=1, padx=10, pady=5)

        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

    def start_scan(self):
        domain = self.domain_entry.get()
        subs = self.subs_var.get()
        font = self.font_combobox.get()
        payload_type = self.payload_combobox.get()  # Get the selected payload type

        if not domain:
            messagebox.showerror("Error", "Please enter a domain.")
            return

        url = f"http://web.archive.org/cdx/search/cdx?url={'*.' if subs else ''}{domain}/*&output=txt&fl=original&collapse=urlkey&page=/"
        response = requester.connector(url)

        crawled_urls = crawler.spider(f"http://{domain}", 10)
        response = concatenate_list_data(crawled_urls, response)

        if response == False:
            return

        response = unquote(response)

        exclude = ['woff', 'js', 'ttf', 'otf', 'eot', 'svg', 'png', 'jpg']
        injection_type = get_injection_type(font)
        final_uris = extractor.param_extract(response, injection_type, exclude, "")

        # Use the selected payload type in your scan logic
        file_name = payloads_dict[payload_type]
        with open(file_name, 'r') as file:
            payloads = file.readlines()

        vulnerable_urls = []

        for uri in final_uris:
            for payload in payloads:
                final_url = uri + payload.strip()

                try:
                    req = requests.get("{}".format(final_url))
                    res = req.text
                    if 'SQL' in res or 'sql' in res or 'Sql' in res:
                        messagebox.showinfo("SQL Injection Detected", f"SQL Injection found at: {final_url}")
                        break
                except:
                    pass
        # Display a message before closing the window
        messagebox.showinfo("Scan Complete", "The scan has been completed successfully")

        # Close the GUI window
        self.root.destroy()

if __name__ == "__main__":
    display_banner()
    root = tk.Tk()
    app = SQLVenomGUI(root)
    root.mainloop()

