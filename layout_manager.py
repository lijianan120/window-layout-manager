import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import subprocess
import threading
import time

try:
    import win32gui
    import win32con
    import win32process
    import psutil
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False

class SimpleLayoutManager:
    def __init__(self, root):
        self.root = root
        self.root.title("副屏窗口布局管理器 v1.0")
        self.root.geometry("550x650")
        self.config_file = "layout_config.json"
        self.config = self.load_config()
        self.create_ui()
    
    def load_config(self):
        default = {
            "windows": [
                {"name": "微信", "exe": "WeChat.exe", "path": "", "x": 0, "y": 0, "w": 720, "h": 1280},
                {"name": "Telegram", "exe": "Telegram.exe", "path": "", "x": 720, "y": 0, "w": 720, "h": 1280},
                {"name": "浏览器", "exe": "chrome.exe", "path": "", "x": 0, "y": 1280, "w": 720, "h": 1280},
                {"name": "TradingView", "exe": "TradingView.exe", "path": "", "x": 720, "y": 1280, "w": 720, "h": 1280}
            ]
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def save_config(self):
        config = self.get_ui_values()
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("保存成功", f"配置已保存")
    
    def get_ui_values(self):
        windows = []
        for widgets in self.window_widgets:
            windows.append({
                "name": widgets["name"].get(),
                "exe": widgets["exe"].get(),
                "path": widgets["path"].get(),
                "x": int(widgets["x"].get() or 0),
                "y": int(widgets["y"].get() or 0),
                "w": int(widgets["w"].get() or 720),
                "h": int(widgets["h"].get() or 1280)
            })
        return {"windows": windows}
    
    def create_ui(self):
        tk.Label(self.root, text="📐 副屏窗口布局管理器", font=("Microsoft YaHei", 14, "bold")).pack(pady=10)
        
        list_frame = tk.LabelFrame(self.root, text="窗口配置")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        headers = ["名称", "程序路径", "X", "Y", "宽", "高", ""]
        for i, h in enumerate(headers):
            tk.Label(list_frame, text=h, font=("Microsoft YaHei", 9, "bold")).grid(row=0, column=i, padx=2)
        
        self.window_widgets = []
        for i, win in enumerate(self.config.get("windows", [])[:4]):
            self.create_window_row(list_frame, i+1, win)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="💾 保存配置", command=self.save_config, bg="#4CAF50", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🚀 应用布局", command=self.apply_layout, bg="#2196F3", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="❌ 退出", command=self.root.quit, width=10).pack(side="right", padx=5)
    
    def create_window_row(self, parent, row, win):
        name = tk.Entry(parent, width=10)
        name.insert(0, win.get("name", ""))
        name.grid(row=row, column=0, padx=2, pady=2)
        
        path_frame = tk.Frame(parent)
        path_frame.grid(row=row, column=1, padx=2, pady=2, sticky="w")
        
        path = tk.Entry(path_frame, width=30)
        path.pack(side="left")
      path.insert(0, win.get("path", ""))
        
        exe = tk.Entry(path_frame, width=12)
        exe.pack(side="left", padx=2)
        exe.insert(0, win.get("exe", ""))
        
        tk.Button(path_frame, text="浏览", command=lambda p=path: self.browse_path(p)).pack(side="left")
        
        x = tk.Entry(parent, width=6)
        x.insert(0, str(win.get("x", 0)))
        x.grid(row=row, column=2, padx=2)
        
        y = tk.Entry(parent, width=6)
        y.insert(0, str(win.get("y", 0)))
        y.grid(row=row, column=3, padx=2)
        
        w = tk.Entry(parent, width=6)
        w.insert(0, str(win.get("w", 720)))
        w.grid(row=row, column=4, padx=2)
        
        h = tk.Entry(parent, width=6)
        h.insert(0, str(win.get("h", 1280)))
        h.grid(row=row, column=5, padx=2)
        
        tk.Button(parent, text="测试", command=lambda r=row-1: self.test_window(r)).grid(row=row, column=6)
        
        self.window_widgets.append({"name": name, "path": path, "exe": exe, "x": x, "y": y, "w": w, "h": h})
    
    def browse_path(self, entry):
        path = filedialog.askopenfilename(filetypes=[("程序", "*.exe")])
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)
    
    def find_window(self, exe_name):
        if not WINDOWS_API_AVAILABLE:
            return None
        exe_lower = exe_name.lower()
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    if exe_lower in proc.name().lower():
                        extra.append(hwnd)
                        return False
                except:
                    pass
            return True
        handles = []
        win32gui.EnumWindows(callback, handles)
        return handles[0] if handles else None
    
    def move_window(self, hwnd, x, y, w, h):
        if not WINDOWS_API_AVAILABLE:
            return
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, w, h, win32con.SWP_SHOWWINDOW)
    
    def launch_app(self, path):
        if os.path.exists(path):
            subprocess.Popen(path, shell=True)
            return True
        return False
    
    def apply_layout(self):
        def do_it():
            config = self.get_ui_values()
            for win in config["windows"]:
                hwnd = self.find_window(win["exe"])
                if not hwnd and win["path"]:
                    self.launch_app(win["path"])
                    time.sleep(3)
                    hwnd = self.find_window(win["exe"])
                if hwnd:
                    self.move_window(hwnd, win["x"], win["y"], win["w"], win["h"])
                    time.sleep(0.5)
            messagebox.showinfo("完成", "布局已应用！")
        threading.Thread(target=do_it, daemon=True).start()
    
    def test_window(self, index):
        widgets = self.window_widgets[index]
        win = {"exe": widgets["exe"].get(), "path": widgets["path"].get(),
               "x": int(widgets["x"].get() or 0), "y": int(widgets["y"].get() or 0),
               "w": int(widgets["w"].get() or 720), "h": int(widgets["h"].get() or 1280)}
        hwnd = self.find_window(win["exe"])
        if not hwnd and win["path"]:
            if self.launch_app(win["path"]):
                time.sleep(3)
                hwnd = self.find_window(win["exe"])
        if hwnd:
            self.move_window(hwnd, win["x"], win["y"], win["w"], win["h"])

def main():
    root = tk.Tk()
    app = SimpleLayoutManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()

