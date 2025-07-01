import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from util import (
    download_images_from_gallery
)

# GUI特有的全局变量
pause_event = threading.Event()


class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片下载器")
        self.root.geometry("600x500")

        # 全局状态
        self.is_paused = False
        self.stop_download = False
        self.download_thread = None

        # 输入框和标签
        tk.Label(root, text="目标 URL:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="选择器类型:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.selector_type = ttk.Combobox(root, values=["id", "class"])
        self.selector_type.grid(row=1, column=1, padx=5, pady=5)
        self.selector_type.set("id")

        tk.Label(root, text="选择器值:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.selector_entry = tk.Entry(root, width=50)
        self.selector_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(root, text="保存目录:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.save_dir_entry = tk.Entry(root, width=50)
        self.save_dir_entry.grid(row=3, column=1, padx=5, pady=5)
        self.browse_button = tk.Button(root, text="浏览", command=self.browse_directory)
        self.browse_button.grid(row=3, column=2, padx=5, pady=5)

        tk.Label(root, text="命名方式:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.naming_option = ttk.Combobox(root, values=["original", "uuid", "timestamp", "custom"])
        self.naming_option.grid(row=4, column=1, padx=5, pady=5)
        self.naming_option.set("original")

        tk.Label(root, text="自定义前缀:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.custom_prefix_entry = tk.Entry(root, width=50)
        self.custom_prefix_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(root, text="超时时间（秒）:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.timeout_entry = tk.Entry(root, width=10)
        self.timeout_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        self.timeout_entry.insert(0, "15")

        tk.Label(root, text="最大重试次数:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.retries_entry = tk.Entry(root, width=10)
        self.retries_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        self.retries_entry.insert(0, "3")

        # 控制按钮
        self.download_button = tk.Button(root, text="开始下载", command=self.start_download)
        self.download_button.grid(row=8, column=0, pady=10)

        self.pause_button = tk.Button(root, text="暂停", command=self.pause_download, state=tk.DISABLED)
        self.pause_button.grid(row=8, column=1, pady=10)

        self.cancel_button = tk.Button(root, text="取消", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_button.grid(row=8, column=2, pady=10)

        # 日志输出
        self.log_text = tk.Text(root, height=10, width=70)
        self.log_text.grid(row=9, column=0, columnspan=3, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)

    def browse_directory(self):
        """选择保存目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, directory)

    def log_message(self, message):
        """在日志框中显示消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_download(self):
        """启动下载任务"""
        import util
        util.is_paused = False
        util.stop_download = False

        url = self.url_entry.get()
        selector_type = self.selector_type.get()
        selector_value = self.selector_entry.get()
        save_dir = self.save_dir_entry.get() if self.save_dir_entry.get() else None
        naming_option = self.naming_option.get()
        custom_prefix = self.custom_prefix_entry.get()

        try:
            timeout = int(self.timeout_entry.get())
            max_retries = int(self.retries_entry.get())
        except ValueError:
            messagebox.showerror("错误", "超时时间和重试次数必须为整数！")
            return

        if not url or not selector_value:
            messagebox.showerror("错误", "请输入目标 URL 和选择器值！")
            return

        self.log_message("开始下载...")
        self.download_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)

        # 启动下载线程
        self.download_thread = threading.Thread(
            target=download_images_from_gallery,
            args=(url, selector_value, selector_type, save_dir, naming_option, custom_prefix, timeout, max_retries, self.log_message),
            daemon=True
        )
        self.download_thread.start()

        # 检查线程是否完成
        self.root.after(100, self.check_thread)

    def pause_download(self):
        """暂停或继续下载"""
        import util
        util.is_paused = not util.is_paused
        if util.is_paused:
            self.pause_button.config(text="继续")
            self.log_message("下载已暂停")
        else:
            self.pause_button.config(text="暂停")
            self.log_message("下载已继续")

    def cancel_download(self):
        """取消下载"""
        import util
        util.stop_download = True
        self.download_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="暂停")
        self.cancel_button.config(state=tk.DISABLED)
        self.log_message("下载已取消")

    def check_thread(self):
        """检查下载线程是否完成"""
        if self.download_thread.is_alive():
            self.root.after(100, self.check_thread)
        else:
            self.download_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED, text="暂停")
            self.cancel_button.config(state=tk.DISABLED)
            self.log_message("下载完成！")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()
