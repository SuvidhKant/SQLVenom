import requests
import tkinter as tk
from tkinter import ttk, messagebox
from core import requester, extractor, crawler
from urllib.parse import unquote

payloads_dict = {
    "Generic SQL Injection": "payloads/payloadsgeneric_sql_injection.txt",
    "Generic Error Based": "payloads/payloadsgeneric_error_based.txt",
    "Generic Time Based SQL": "payloads/payloadsgeneric_time_based_sql.txt",
    "Auth Bypass": "payloads/payloadsauth_bypass.txt",
    "Generic Union Select": "payloads/payloadsgeneric_Union_Select.txt"
}

def concatenate_list_data(lst, result):
    for element in lst:
        result = result + "\n" + str(element)
    return result

def get_injection_type(font):
    # You can customize this function based on your requirements
    return 'standard'

class SQLVenomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Venom GUI")

        # Add a frame for better organization
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.domain_label = ttk.Label(self.main_frame, text="Domain:")
        self.domain_entry = ttk.Entry(self.main_frame)

        self.subs_var = tk.BooleanVar()
        self.subs_check = ttk.Checkbutton(self.main_frame, text="Include Subdomains", variable=self.subs_var)

        self.font_label = ttk.Label(self.main_frame, text="Choose PyFiglet Font:")
        self.font_combobox = ttk.Combobox(self.main_frame, values=["standard", "slant"])
        self.font_combobox.set("standard")

        self.payload_label = ttk.Label(self.main_frame, text="Select Payload Type:")
        self.payload_combobox = ttk.Combobox(self.main_frame, values=["Generic SQL Injection", "Generic Error Based", "Generic Time Based SQL", "Auth Bypass", "Generic Union Select"])
        self.payload_combobox.set("Select Payload")

        self.start_button = ttk.Button(self.main_frame, text="Start SQL Injection Scan", command=self.start_scan)

        # Arrange widgets using grid
        self.domain_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.domain_entry.grid(row=0, column=1, padx=10, pady=5)

        self.subs_check.grid(row=1, column=0, columnspan=2, pady=5)

        self.font_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.font_combobox.grid(row=2, column=1, padx=10, pady=5)

        self.payload_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.payload_combobox.grid(row=3, column=1, padx=10, pady=5)

        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Add some padding to all widgets in the frame
        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def start_scan(self):
        domain = self.domain_entry.get()
        subs = self.subs_var.get()
        font = self.font_combobox.get()
        payload_type = self.payload_combobox.get()

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

        messagebox.showinfo("Scan Complete", "The scan has been completed successfully")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLVenomGUI(root)
    root.mainloop()
