import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
import os
import re
import webview


class WebPageCreator(ThemedTk):
    def __init__(self):
        super().__init__(theme="breeze")
        self.title("SiteForge")
        self.geometry("1000x700")
        self.iconbitmap('assets/program-icon.ico')

        self.components = self.load_components()
        self.selected_components = []
        self.styles = []
        self.scripts = []

        self.create_widgets()

    def load_components(self):
        components = {}
        components_dir = 'components'
        if not os.path.exists(components_dir):
            os.makedirs(components_dir)
        for filename in os.listdir(components_dir):
            if filename.endswith('.html'):
                component_name = os.path.splitext(filename)[0]
                with open(os.path.join(components_dir, filename), 'r') as file:
                    components[component_name] = file.read()
        return components

    def extract_styles(self, component_html):
        styles = re.findall(r'<style.*?>(.*?)</style>', component_html, re.DOTALL)
        return styles

    def extract_scripts(self, component_html):
        scripts = re.findall(r'<script.*?>(.*?)</script>', component_html, re.DOTALL)
        return scripts

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_component_list)

        self.component_listbox = tk.Listbox(left_frame, height=20, width=30)
        self.update_component_list()
        self.component_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.component_listbox.bind("<<ListboxSelect>>", self.display_component_preview)

        scrollbar = ttk.Scrollbar(left_frame, command=self.component_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.component_listbox['yscrollcommand'] = scrollbar.set

        self.add_button = ttk.Button(left_frame, text="Add Component", command=self.add_component)
        self.add_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.remove_button = ttk.Button(left_frame, text="Remove Component", command=self.remove_component)
        self.remove_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.generate_button = ttk.Button(left_frame, text="Generate HTML", command=self.generate_html)
        self.generate_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.preview_button = ttk.Button(left_frame, text="Preview Page", command=self.preview_page)
        self.preview_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        preview_label = ttk.Label(right_frame, text="HTML Preview")
        preview_label.pack(side=tk.TOP, padx=5, pady=5)

        self.preview_text = tk.Text(right_frame, wrap=tk.WORD)
        self.preview_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(right_frame, command=self.preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text['yscrollcommand'] = scrollbar.set

        component_preview_frame = ttk.Frame(left_frame)
        component_preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        preview_label = ttk.Label(component_preview_frame, text="Component Preview")
        preview_label.pack(side=tk.TOP, padx=5, pady=5)

        self.component_preview_text = tk.Text(component_preview_frame, wrap=tk.WORD, height=10)
        self.component_preview_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(component_preview_frame, command=self.component_preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.component_preview_text['yscrollcommand'] = scrollbar.set

    def update_component_list(self, event=None):
        search_term = self.search_var.get().lower()
        self.component_listbox.delete(0, tk.END)
        for component in self.components:
            if search_term in component.lower():
                self.component_listbox.insert(tk.END, component)

    def display_component_preview(self, event):
        selected_component = self.component_listbox.get(tk.ACTIVE)
        if selected_component:
            component_html = self.components[selected_component]
            self.component_preview_text.delete("1.0", tk.END)
            self.component_preview_text.insert(tk.END, component_html)

    def add_component(self):
        selected_component = self.component_listbox.get(tk.ACTIVE)
        if selected_component:
            component_html = self.components[selected_component]
            self.selected_components.append((selected_component, component_html))

            # Extract and store styles
            self.styles.extend(self.extract_styles(component_html))

            # Extract and store scripts
            self.scripts.extend(self.extract_scripts(component_html))

            # Update HTML preview
            self.update_html_preview()

    def remove_component(self):
        selected_component = self.component_listbox.get(tk.ACTIVE)
        if selected_component:
            self.selected_components = [comp for comp in self.selected_components if comp[0] != selected_component]

            # Rebuild styles and scripts
            self.styles = []
            self.scripts = []
            for _, component_html in self.selected_components:
                self.styles.extend(self.extract_styles(component_html))
                self.scripts.extend(self.extract_scripts(component_html))

            # Update HTML preview
            self.update_html_preview()

    def update_html_preview(self):
        combined_html = "<!DOCTYPE html>\n<html>\n<head>\n<title>My Web Page</title>\n"

        # Add combined styles
        if self.styles:
            combined_html += "<style>\n" + "\n".join(self.styles) + "\n</style>\n"

        combined_html += "</head>\n<body>\n"
        for _, component in self.selected_components:
            component_html_no_styles_scripts = re.sub(r'<(style|script).*?>.*?</\1>', '', component, flags=re.DOTALL)
            combined_html += component_html_no_styles_scripts + "\n"
        combined_html += "</body>\n"

        # Add combined scripts
        if self.scripts:
            combined_html += "<script>\n" + "\n".join(self.scripts) + "\n</script>\n"

        combined_html += "</html>"

        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, combined_html)

    def generate_html(self):
        html_content = self.preview_text.get("1.0", tk.END)

        file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(html_content)
            messagebox.showinfo("Success", f"HTML file saved as {file_path}")

    def preview_page(self):
        html_content = self.preview_text.get("1.0", tk.END)
        temp_file_path = os.path.join(os.getcwd(), "temp_preview.html")
        with open(temp_file_path, 'w') as file:
            file.write(html_content)

        webview.create_window("Preview", temp_file_path)
        webview.start()


if __name__ == "__main__":
    app = WebPageCreator()
    app.mainloop()
''