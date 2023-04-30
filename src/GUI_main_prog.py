import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox
from src.parsing_ch10.parser_1553 import parser_c10, parser_json
# from src.Exalt_File.Make_RPF import rpf_process
from src.Exalt_File.RPF import rpf_process


class UI:
    def __init__(self):
        # tkinter screen root
        self.root = tk.Tk()
        self.root.geometry("500x500")
        self.root.title('CH10 -> RPF / JSON -> RPF')
        self.root.configure(bg='#DAF7A6')

        # select file label
        self.path_label = tk.Label(self.root, text="Select File:", font=("Arial", 14, "bold"),
                                   fg="white", bg="#2980b9", bd=2, relief="solid", padx=10, pady=5)
        self.path_label.place(relx=0.5, rely=0.4, anchor="center")

        # text box for entering file path
        self.path_entry = tk.Entry(self.root, width=50, bg='white', fg='black', bd=2, relief="solid")
        self.path_entry.place(relx=0.5, rely=0.5, anchor="center")

        # browse button
        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_file,
                                       fg='white', bd=5, bg='#2980b9',
                                       font='Arial')
        self.browse_button.place(relx=0.4, rely=0.6, anchor="center")
        self.browse_button_ttp = tk.Label(self.root, text="Browse File", bg='#f0f0f0', font='Arial 10 italic')
        self.browse_button_ttp.place(relx=0.4, rely=0.7, anchor="center")

        # submit button
        self.submit_button = tk.Button(self.root, text="Process", command=self.submit_file,
                                       fg='white', bd=5, bg='#2980b9',
                                       font='Arial')

        self.submit_button.place(relx=0.6, rely=0.6, anchor="center")
        self.submit_button_ttp = tk.Label(self.root, text="Process File", bg='#f0f0f0', font='Arial 10 italic')
        self.submit_button_ttp.place(relx=0.6, rely=0.7, anchor="center")

        # exit button
        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit,
                                     fg='white', bd=5, bg='#c0392b', font='Arial')
        self.exit_button.place(relx=0.5, rely=0.8, anchor="center")
        self.exit_button_ttp = tk.Label(self.root, text="Exit Application", bg='#f0f0f0', font='Arial 10 italic')
        self.exit_button_ttp.place(relx=0.5, rely=0.9, anchor="center")

        # tkinter main loop
        self.root.mainloop()

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=(("JSON Files", "*.json"), ("C10 Files", "*.c10"), ("JSON and C10 Files", "*.json;*.c10")))
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, file_path)

    def submit_file(self):
        file_path = self.path_entry.get()
        self.process_file(file_path)

    def process_file(self, file_path):
        file_extension = os.path.splitext(file_path)[1]
        if file_extension == '.c10':
            self.c10_to_rpf(file_path)
        elif file_extension == '.json':
            self.json_to_rpf(file_path)
        else:
            messagebox.showinfo("Process File", f"File path: {file_path}\nfile extension is unknown")

    @staticmethod
    def c10_to_rpf(file_path):
        num_of_msgs, adapters_list = parser_c10(file_path)

        rpf_process(
            Path().absolute().parent / 'output_files' / (os.path.splitext(os.path.basename(file_path))[0] + '.json'),
            os.path.splitext(os.path.basename(file_path))[0],
            num_of_msgs,
            adapters_list,
            int(os.path.getctime(file_path))
        )

    @staticmethod
    def json_to_rpf(file_path):
        num_of_msgs, adapters_list = parser_json(file_path)

        rpf_process(
            file_path,
            os.path.splitext(os.path.basename(file_path))[0],
            num_of_msgs,
            adapters_list,
            int(os.path.getctime(file_path))
        )


def main():
    UI()


if __name__ == '__main__':
    main()
