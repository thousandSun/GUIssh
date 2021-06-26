import os
from posixpath import split
import tkinter as tk
from client import Client
from tkinter import ttk
from tkinter import messagebox


class Main:
    def __init__(self, master, cl=None):
        self.client = cl
        self.remote_curr_path = ''
        self.remote_file_path = ''
        self.local_curr_path = ''
        self.local_file_path = ''
        self.master = master
        self.master.title("SSH Client")
        self.center_window()
        self.init_ui()

    def init_ui(self):
        frame = ttk.LabelFrame(self.master, text='SSH Options')

        host_label = ttk.Label(frame, text='Host: ')
        user_label = ttk.Label(frame, text='Username: ')
        port_label = ttk.Label(frame, text='Port: ')

        hostname_label = ttk.Label(frame, text=f'{self.client.get_host()}')
        username_label = ttk.Label(frame, text=f'{self.client.get_username()}')
        port_number_label = ttk.Label(frame, text=f'{self.client.get_port()}')

        host_label.grid(row=0, column=0, sticky='ne')
        hostname_label.grid(row=0, column=1, sticky='nw')
        user_label.grid(row=1, column=0, sticky='ne')
        username_label.grid(row=1, column=1, sticky='nw')
        port_label.grid(row=2, column=0, sticky='ne')
        port_number_label.grid(row=2, column=1, sticky='nw')

        frame.grid(row=0, column=0, padx=5, pady=5, sticky='nw')

        self.init_remote_section()
        self.init_local_section()
        self.init_button_section()

    def init_remote_section(self):
        _, stdout, _ = self.client.run_command('pwd')
        path = stdout.read().decode().strip()
        if self.client.get_username() in path:
            self.remote_curr_path = '~'
        else:
            self.remote_curr_path = path

        self.remote_frame = ttk.LabelFrame(self.master, text=f'{self.remote_curr_path}')

        self.remote_listbox = tk.Listbox(self.remote_frame, width=40, height=15)
        self.remote_listbox.bind('<FocusIn>', self.enable_download)
        self.remote_listbox.bind('<Double-1>', self.remote_cd)
        self.remote_listbox.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        self.remote_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nw')

        self.populate_remote_listbox()

    def init_local_section(self):
        self.local_curr_path = os.getcwd()
        path_to_display = os.path.relpath(self.local_curr_path)
        self.local_frame = ttk.LabelFrame(self.master, text=f'{path_to_display}')

        self.local_listbox = tk.Listbox(self.local_frame, width=40, height=15)
        self.local_listbox.bind('<FocusIn>', self.enable_upload)
        self.local_listbox.bind('<Double-1>', self.local_cd)
        self.local_listbox.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        self.local_frame.grid(row=1, column=1, padx=5, pady=5, sticky='nw')

        self.populate_local_listbox()

    def init_button_section(self):
        frame = ttk.LabelFrame(self.master, text="Action Buttons")

        self.upload_button = ttk.Button(frame, text='Upload Selected...', width=22, state=tk.DISABLED, command=self.upload_selected)
        self.download_button = ttk.Button(frame, text='Download Selected...', width=22, state=tk.DISABLED, command=self.download_selected)
        self.disconnect_button = ttk.Button(frame, text='Disconnect...', width=22, command=self.logout)

        self.upload_button.grid(row=0, column=0, padx=15, pady=5, sticky='nsew')
        self.download_button.grid(row=0, column=1, padx=15, pady=5, sticky='nsew')
        self.disconnect_button.grid(row=0, column=2, padx=15, pady=5, sticky='nsew')

        frame.grid(row=2, column=0, padx=5, pady=5, columnspan=2, sticky='nwe')

    def populate_remote_listbox(self):
        self.remote_listbox.delete(0, tk.END)
        self.remote_listbox.insert(tk.END, '..')
        self.remote_listbox.itemconfig(tk.END, {'fg': 'blue'})
        _, stdout, _ = self.client.run_command(f'ls -l --group-directories-first {self.remote_curr_path}')
        first = True
        for line in stdout:
            if first:
                first = False
                continue
            line = line.split()
            if line[0].startswith('d'):
                insert = line[8]
                self.remote_listbox.insert(tk.END, insert)
                self.remote_listbox.itemconfig(tk.END, {'fg': 'blue'})
            else:
                insert = line[8]
                self.remote_listbox.insert(tk.END, insert)

    def remote_cd(self, event):
        selected = self.remote_listbox.curselection()
        try:
            index = selected[0]
            color = self.remote_listbox.itemcget(index, 'foreground')
            if color == 'blue':
                path_to_cd = f'{self.remote_curr_path}/{self.remote_listbox.get(index)}'
                _, stdout, stderr = self.client.run_command(f'cd {path_to_cd} && pwd')

                error = stderr.read().decode().strip()
                if not error:
                    self.rename_remote_frame(stdout)
                else:
                    messagebox.showerror(title='Permission Denied', message='Cannot change into selected directory')
        except IndexError:
            pass

    def rename_remote_frame(self, stdout):
        path = stdout.read().decode().strip()
        if self.client.get_username() in path:
            path = path.split('/')
            username_index = path.index(self.client.get_username()) + 1
            path_variable = path[username_index:]
            if not path_variable:
                self.remote_curr_path = '~'
            else:
                self.remote_curr_path = f"~/{'/'.join(path_variable)}"
        else:
            self.remote_curr_path = path

        if len(self.remote_curr_path) >= 40:
            split_path = self.remote_curr_path.split('/')
            half = (len(split_path) // 2) + 1
            path_to_display = f"~/.../{'/'.join(split_path[half:])}"
            if len(path_to_display) >= 40:
                split_path1 = path_to_display.split('/')
                half1 = (len(split_path1) // 2) + 1
                path_to_display1 = f"~/.../{'/'.join(split_path1[half1:])}"
                self.remote_frame.configure(text=f'{path_to_display1}')
            else:
                self.remote_frame.configure(text=f'{path_to_display}')
        else:
            self.remote_frame.configure(text=f'{self.remote_curr_path}')
        self.populate_remote_listbox()

    def populate_local_listbox(self):
        self.local_listbox.delete(0, tk.END)
        self.local_listbox.insert(tk.END, '..')
        self.local_listbox.itemconfig(tk.END, {'fg': 'blue'})
        contents = os.listdir(self.local_curr_path)
        formatted = self.format_contents(contents)
        for insert in formatted:
            if os.path.isdir(insert):
                self.local_listbox.insert(tk.END, insert)
                self.local_listbox.itemconfig(tk.END, {'fg': 'blue'})
            else:
                self.local_listbox.insert(tk.END, insert)

    def rename_local_frame(self):
        user = os.path.expanduser('~')
        curr_path = os.getcwd()
        if user in curr_path:
            path_var = curr_path.split(user)[1:]
            if not path_var:
                self.local_curr_path = '~'
            else:
                self.local_curr_path = os.path.join('~', path_var)
        else:
            self.local_curr_path = curr_path
        
        if len(self.local_curr_path) > 40:
            split_path = self.local_curr_path.split(os.path.sep)
            half = (len(split_path) // 2) + 1
            path_to_display = f'~\\...\\{os.path.sep.join(split_path[half:])}'
            if len(path_to_display) > 40:
                split_path1 = path_to_display.split(os.path.sep)
                half1 = (len(split_path1) // 2) + 1
                path_to_display1 = f'~\\...\\{os.path.sep.join(split_path1[half:])}'
                self.local_frame.configure(text=f'{path_to_display1}')
            else:
                self.local_frame.configure(text=f'{path_to_display}')
        else:
            self.local_frame.configure(text=f'{self.local_curr_path}')
        self.populate_local_listbox()

    @staticmethod
    def format_contents(content):
        formatted = []
        for file in content:
            if file.startswith('.'):
                continue
            if os.path.isdir(file):
                formatted.append(file)
        for file in content:
            if file.startswith('.') or os.path.isdir(file):
                continue
            formatted.append(file)
        return formatted

    def local_cd(self, event):
        selected = self.local_listbox.curselection()
        try:
            index = selected[0]
            color = self.local_listbox.itemcget(index, 'foreground')
            if color == 'blue':
                path_to_cd = f'{self.local_curr_path}/{self.local_listbox.get(index)}'
                try:
                    os.chdir(path_to_cd)
                    self.rename_local_frame()
                except OSError:
                    messagebox.showerror(title='Permission Denied', message='Cannot change into selected directory')

        except IndexError:
            pass

    def logout(self):
        from connect import Login
        self.client.close_client()
        self.master.withdraw()
        top = tk.Toplevel(self.master)
        login = Login(top)

    def upload_selected(self):
        selected_item = self.local_listbox.get(self.local_listbox.curselection())
        self.local_file_path = os.path.sep.join([self.local_curr_path, selected_item])
        self.client.set_local_path(self.local_file_path)
        self.client.set_remote_path(self.remote_curr_path)
        self.client.upload()
        self.populate_remote_listbox()

    def download_selected(self):
        selected_item = self.remote_listbox.get(self.remote_listbox.curselection())
        self.remote_file_path = f'{self.remote_curr_path}/{selected_item}'
        self.client.set_remote_path(self.remote_file_path)
        self.client.set_local_path(self.local_curr_path)
        self.client.download()
        self.populate_local_listbox()

    def enable_upload(self, event):
        self.upload_button.configure(state=tk.NORMAL)
        self.download_button.configure(state=tk.DISABLED)

    def enable_download(self, event):
        self.download_button.configure(state=tk.NORMAL)
        self.upload_button.configure(state=tk.DISABLED)

    def center_window(self):
        width = 550
        height = 500
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.master.geometry(f'{width}x{height}+{x}+{y}')


def main():
    root = tk.Tk()
    cl = Client()
    app = Main(root, cl)
    root.mainloop()


if __name__ == '__main__':
    main()
