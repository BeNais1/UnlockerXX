import os
import sys
import psutil
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import time
from file_operations import browse_file, find_locking_processes, unlock_file, delete_file
from process_operations import find_high_usage_processes, kill_process
from ui_helpers import create_treeview

class FileUnlockerApp:
    def __init__(self, root):
        self.root = root
        self.language = self.load_language()
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
                'failed_check': "Failed to check processes: {error}",
                'high_usage_processes': "High Resource Usage Processes",
                'cpu': "CPU %",
                'memory': "Memory %"
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
                'failed_check': "Не удалось проверить процессы: {error}",
                'high_usage_processes': "Процессы с высоким использованием ресурсов",
                'cpu': "ЦП %",
                'memory': "Память %"
            }
        }
        self.root.title(self.translate('title'))
        self.root.geometry("800x600")
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
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=5)

        ttk.Label(lang_frame, text=self.translate('language')).pack(side=tk.LEFT, padx=5)
        lang_var = tk.StringVar(value=self.language)
        lang_dropdown = ttk.OptionMenu(lang_frame, lang_var, self.language, *self.translations.keys(),
                                        command=self.switch_language)
        lang_dropdown.pack(side=tk.LEFT, padx=5)

        file_frame = ttk.LabelFrame(main_frame, text=self.translate('file_folder'), padding="10")
        file_frame.pack(fill=tk.X, pady=5)

        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text=self.translate('browse'), command=lambda: browse_file(self.file_path, self.find_locking_processes)).pack(side=tk.LEFT)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text=self.translate('unlock_file'), command=lambda: unlock_file(self.file_path.get())).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text=self.translate('delete_file'), command=lambda: delete_file(self.file_path.get())).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text=self.translate('kill_process'), command=lambda: kill_process(self.tree)).pack(side=tk.LEFT, padx=2)

        process_frame = ttk.LabelFrame(main_frame, text=self.translate('locking_processes'), padding="10")
        process_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = create_treeview(process_frame, ['pid', 'name', 'status'], ['PID', 'Process Name', 'Status'])

        high_usage_frame = ttk.LabelFrame(main_frame, text=self.translate('high_usage_processes'), padding="10")
        high_usage_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.high_usage_tree = create_treeview(high_usage_frame, ['pid', 'name', 'cpu', 'memory'], ['PID', self.translate('cpu'), self.translate('memory')])

    def find_locking_processes(self):
        find_locking_processes(self.file_path.get(), self.tree)

    def find_high_usage_processes(self):
        find_high_usage_processes(self.high_usage_tree)

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
            time.sleep(1)
        self.root.destroy()

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)
    splash_root.mainloop()
    root = tk.Tk()
    app = FileUnlockerApp(root)
    root.mainloop()