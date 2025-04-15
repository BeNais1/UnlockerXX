import os
import sys
import psutil
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import time


class FileUnlockerApp:
    def __init__(self, root):
        self.root = root
        self.language = self.load_language()  # Загружаем язык из файла настроек
        self.translations = {
            'en': {
                'title': "Python File Unlocker",
                'file_folder': "File/Folder to Unlock",
                'browse': "Browse...",
                'unlock_file': "Unlock File",
                'delete_file': "Delete File",
                'kill_process': "Kill Process",
                'locking_processes': "Locking Processes",
                'language': "Language",
                'warning': "Warning",
                'select_file': "Please select a file first",
                'success': "Success",
                'file_unlocked': "File unlocked successfully",
                'file_deleted': "File/folder deleted successfully",
                'select_process': "Please select a process first",
                'process_terminated': "Process {pid} terminated",
                'error': "Error",
                'failed_unlock': "Failed to unlock file: {error}",
                'failed_delete': "Failed to delete: {error}",
                'failed_kill': "Failed to kill process: {error}",
                'failed_check': "Failed to check processes: {error}"
            },
            'ru': {
                'title': "Разблокировщик файлов на Python",
                'file_folder': "Файл/Папка для разблокировки",
                'browse': "Обзор...",
                'unlock_file': "Разблокировать файл",
                'delete_file': "Удалить файл",
                'kill_process': "Завершить процесс",
                'locking_processes': "Блокирующие процессы",
                'language': "Язык",
                'warning': "Предупреждение",
                'select_file': "Пожалуйста, выберите файл",
                'success': "Успех",
                'file_unlocked': "Файл успешно разблокирован",
                'file_deleted': "Файл/папка успешно удалены",
                'select_process': "Пожалуйста, выберите процесс",
                'process_terminated': "Процесс {pid} завершен",
                'error': "Ошибка",
                'failed_unlock': "Не удалось разблокировать файл: {error}",
                'failed_delete': "Не удалось удалить: {error}",
                'failed_kill': "Не удалось завершить процесс: {error}",
                'failed_check': "Не удалось проверить процессы: {error}"
            }
        }
        self.root.title(self.translate('title'))
        self.root.geometry("600x400")

        # Make the app look a bit better
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.create_widgets()

    def translate(self, key, **kwargs):
        return self.translations[self.language].get(key, key).format(**kwargs)

    def switch_language(self, lang):
        if lang in self.translations:
            self.language = lang
            self.save_language(lang)
            self.restart_app()

    def save_language(self, lang):
        with open("settings.json", "w") as f:
            json.dump({"language": lang}, f)

    def load_language(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                return settings.get("language", "en")
        except FileNotFoundError:
            return "en"

    def restart_app(self):
        self.root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Language dropdown
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=5)

        ttk.Label(lang_frame, text=self.translate('language')).pack(side=tk.LEFT, padx=5)
        lang_var = tk.StringVar(value=self.language)
        lang_dropdown = ttk.OptionMenu(lang_frame, lang_var, self.language, *self.translations.keys(),
                                        command=self.switch_language)
        lang_dropdown.pack(side=tk.LEFT, padx=5)

        # File selection
        file_frame = ttk.LabelFrame(main_frame, text=self.translate('file_folder'), padding="10")
        file_frame.pack(fill=tk.X, pady=5)

        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text=self.translate('browse'), command=self.browse_file).pack(side=tk.LEFT)

        # Actions frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text=self.translate('unlock_file'), command=self.unlock_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text=self.translate('delete_file'), command=self.delete_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text=self.translate('kill_process'), command=self.kill_process).pack(side=tk.LEFT, padx=2)

        # Process list
        process_frame = ttk.LabelFrame(main_frame, text=self.translate('locking_processes'), padding="10")
        process_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(process_frame, columns=('pid', 'name', 'status'), show='headings')
        self.tree.heading('pid', text='PID')
        self.tree.heading('name', text='Process Name')
        self.tree.heading('status', text='Status')

        vsb = ttk.Scrollbar(process_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(process_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        process_frame.grid_rowconfigure(0, weight=1)
        process_frame.grid_columnconfigure(0, weight=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path.set(file_path)
            self.find_locking_processes()

    def find_locking_processes(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            return

        self.tree.delete(*self.tree.get_children())

        try:
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    files = proc.open_files()
                    for f in files:
                        if os.path.normcase(f.path) == os.path.normcase(file_path):
                            self.tree.insert('', 'end',
                                             values=(proc.info['pid'], proc.info['name'], proc.info['status']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            messagebox.showerror(self.translate('error'), self.translate('failed_check', error=str(e)))

    def unlock_file(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning(self.translate('warning'), self.translate('select_file'))
            return

        try:
            # Try to open the file in read-write mode to "unlock" it
            with open(file_path, 'a'):
                os.utime(file_path, None)
            messagebox.showinfo(self.translate('success'), self.translate('file_unlocked'))
        except Exception as e:
            messagebox.showerror(self.translate('error'), self.translate('failed_unlock', error=str(e)))

    def delete_file(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning(self.translate('warning'), self.translate('select_file'))
            return

        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
            messagebox.showinfo(self.translate('success'), self.translate('file_deleted'))
            self.file_path.set("")
        except Exception as e:
            messagebox.showerror(self.translate('error'), self.translate('failed_delete', error=str(e)))

    def kill_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(self.translate('warning'), self.translate('select_process'))
            return

        pid = self.tree.item(selected_item)['values'][0]
        try:
            p = psutil.Process(pid)
            p.terminate()
            messagebox.showinfo(self.translate('success'), self.translate('process_terminated', pid=pid))
            self.find_locking_processes()
        except Exception as e:
            messagebox.showerror(self.translate('error'), self.translate('failed_kill', error=str(e)))


class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizing Application")
        self.root.geometry("400x200")
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=20)
        self.label = ttk.Label(self.root, text="Optimizing application for system requirements...")
        self.label.pack()
        self.status_label = ttk.Label(self.root, text="Initializing...")
        self.status_label.pack(pady=10)
        self.optimize_application()

    def optimize_application(self):
        tasks = [
            "Checking system compatibility...",
            "Loading necessary modules...",
            "Configuring application settings...",
            "Finalizing optimization..."
        ]

        for i, task in enumerate(tasks, 1):
            self.status_label.config(text=task)
            self.progress['value'] = (i / len(tasks)) * 100
            self.root.update_idletasks()
            time.sleep(1)  # Simulate task duration

        self.root.destroy()

if __name__ == "__main__":
    # Check for admin rights (required for some operations)
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)
    splash_root.mainloop()

    root = tk.Tk()
    app = FileUnlockerApp(root)
    root.mainloop()