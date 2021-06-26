import tkinter as tk
from client import Client
from tkinter import messagebox
from tkinter import ttk


class Login:
    def __init__(self, master):
        self.master = master
        self.master.bind('<Return>', self.login)
        self.master.title('SSH Connect')
        self.center_window()
        self.validate_num_wrapper = (self.master.register(self.validate_num), '%P', '%d')
        self.init_ui()

    def init_ui(self):
        hostname_label = ttk.Label(self.master, text='Hostname:')
        self.hostname_field = ttk.Entry(self.master, width=30)
        self.hostname_field.focus()

        port_label = ttk.Label(self.master, text='Port:')
        self.port_field = ttk.Entry(self.master, width=30, validate='key', validatecommand=self.validate_num_wrapper)
        self.port_field.insert(0, 22)

        username_label = ttk.Label(self.master, text='Username:')
        self.username_field = ttk.Entry(self.master, width=30)

        password_label = ttk.Label(self.master, text='Password:')
        self.password_field = ttk.Entry(self.master, width=30, show='*')

        login_button = ttk.Button(self.master, text='Connect...', command=self.login)
        exit_button = ttk.Button(self.master, text='Quit...', command=self.master.quit)
        clear_button = ttk.Button(self.master, text='Clear...', command=self.clear)

        hostname_label.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.hostname_field.grid(row=0, column=1, columnspan=2, sticky='we', padx=5, pady=5)

        port_label.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.port_field.grid(row=1, column=1, columnspan=2, sticky='we', padx=5, pady=5)

        username_label.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.username_field.grid(row=2, column=1, columnspan=2, sticky='we', padx=5, pady=5)

        password_label.grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.password_field.grid(row=3, column=1, columnspan=2, sticky='we', padx=5, pady=5)

        clear_button.grid(row=4, column=0, sticky='we', padx=5, pady=5)
        login_button.grid(row=4, column=1, sticky='we', padx=5, pady=5)
        exit_button.grid(row=4, column=2, sticky='we', padx=5, pady=5)

        self.error_label = ttk.Label(self.master, text='')
        self.error_label.grid(row=5, column=0, columnspan=3, sticky='we', padx=5, pady=5)

    def clear(self):
        self.hostname_field.delete(0, 'end')
        self.port_field.delete(0, 'end')
        self.username_field.delete(0, 'end')
        self.password_field.delete(0, 'end')

    def login(self, event=None):
        username = self.username_field.get()
        port = self.port_field.get()
        hostname = self.hostname_field.get()
        password = self.password_field.get()

        if len(username) == 0 or len(hostname) == 0 or len(password) == 0 or len(port) == 0:
            messagebox.showerror(title='Field Errors', message='There seems to have been a field left blank.',
                                 detail='Fill them all out and try again.', icon='error')
        else:
            c = Client(hostname, username, password, port)
            result = c.connect()
            if result == 0:
                from main import Main
                self.master.withdraw()
                toplevel = tk.Toplevel(self.master)
                main = Main(toplevel, c)
            elif result == 1:
                messagebox.showerror(title='Host key exception', message='There was a problem with the host keys.',
                                     detail='Ensure host keys are accurate and try again')
            elif result == 2:
                messagebox.showerror(title='Authentication Error', message='There was a problem with credentials.',
                                     detail='Check the credentials and try again')
            elif result == 3:
                messagebox.showerror(title='Connection Error', message='There was a problem establishing a connection',
                                     detail=f"Ensure '{hostname}' is accurate and reachable and try again")
            elif result == 4:
                messagebox.showerror(title='Socket Error', message='There was a problem with the sockets')

    def validate_num(self, val, action):
        if val == '' or action == ' ':
            return True
        try:
            port = int(val)
            if 0 <= port <= 65353:
                return True
            else:
                self.error_label.configure(text='The number you were going to enter would be out of the port range. '
                                                'Range: 0 - 65353', wraplength=250, justify=tk.CENTER)
                return False
        except ValueError:
            self.error_label.configure(text='Enter numbers only for \'Port\' field')
            return False

    def center_window(self):
        width = 300
        height = 200
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.master.geometry(f'{width}x{height}+{x}+{y}')


def main():
    root = tk.Tk()
    app = Login(root)
    root.mainloop()


if __name__ == '__main__':
    main()
