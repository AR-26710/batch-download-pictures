import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from util import download_images_from_gallery


class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片下载器")
        self.root.geometry("600x700")
        self.root.resizable(True, True)

        # 状态管理
        self.is_paused = False
        self.stop_download = False
        self.download_thread = None

        # 初始化UI
        self.setup_styles()
        self.create_main_layout()
        self.create_input_frame()
        self.create_advanced_frame()
        self.create_control_buttons()
        self.create_log_display()
        self.setup_grid_weights()

    def setup_styles(self):
        """配置UI样式"""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # 颜色方案
        self.bg_color = "#f5f5f5"
        self.frame_bg = "#ffffff"
        self.accent_color = "#4a86e8"
        self.text_color = "#333333"

        # 配置通用样式
        self.style.configure(
            "TLabel", 
            font=(".Microsoft YaHei UI", 10),
            padding=5,
            background=self.bg_color,
            foreground=self.text_color
        )
        self.style.configure(
            "TButton", 
            font=(".Microsoft YaHei UI", 10),
            padding=8,
            background=self.accent_color,
            foreground="white"
        )
        self.style.map(
            "TButton",
            background=[("active", "#3d70d5"), ("disabled", "#cccccc")]
        )
        self.style.configure(
            "TEntry", 
            font=(".Microsoft YaHei UI", 10),
            padding=5,
            fieldbackground=self.frame_bg
        )
        self.style.configure(
            "TCombobox", 
            font=(".Microsoft YaHei UI", 10),
            padding=5,
            fieldbackground=self.frame_bg
        )
        self.style.configure(
            "TLabelframe",
            background=self.bg_color,
            foreground=self.text_color,
            font=(".Microsoft YaHei UI", 10, "bold")
        )
        self.style.configure(
            "TLabelframe.Label",
            background=self.bg_color,
            foreground=self.text_color
        )

    def create_main_layout(self):
        """创建主框架"""
        self.main_frame = ttk.Frame(
            self.root, 
            padding="20 20 20 20", 
            style="TFrame"
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.configure(style="TFrame")

    def create_input_frame(self):
        """创建输入区域框架"""
        self.input_frame = ttk.LabelFrame(
            self.main_frame, 
            text="下载设置", 
            padding="15 15 15 15"
        )
        self.input_frame.pack(fill=tk.X, pady=(0, 15))

        # 目标URL
        ttk.Label(self.input_frame, text="目标 URL:").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.url_entry = ttk.Entry(self.input_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=8, columnspan=2, sticky="ew")

        # 选择器类型
        ttk.Label(self.input_frame, text="选择器类型:").grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.selector_type = ttk.Combobox(self.input_frame, values=["id", "class"], state="readonly", width=10)
        self.selector_type.grid(row=1, column=1, padx=5, pady=8, sticky="w")
        self.selector_type.set("id")

        # 选择器值
        ttk.Label(self.input_frame, text="选择器值:").grid(row=2, column=0, padx=5, pady=8, sticky="e")
        self.selector_entry = ttk.Entry(self.input_frame, width=50)
        self.selector_entry.grid(row=2, column=1, padx=5, pady=8, columnspan=2, sticky="ew")

        # 保存目录
        ttk.Label(self.input_frame, text="保存目录:").grid(row=3, column=0, padx=5, pady=8, sticky="e")
        self.save_dir_entry = ttk.Entry(self.input_frame, width=40)
        self.save_dir_entry.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        self.browse_button = ttk.Button(self.input_frame, text="浏览", command=self.browse_directory)
        self.browse_button.grid(row=3, column=2, padx=5, pady=8)

        # 命名方式
        ttk.Label(self.input_frame, text="命名方式:").grid(row=4, column=0, padx=5, pady=8, sticky="e")
        self.naming_option = ttk.Combobox(
            self.input_frame, 
            values=["original", "uuid", "timestamp", "custom"], 
            state="readonly",
            width=10
        )
        self.naming_option.grid(row=4, column=1, padx=5, pady=8, sticky="w")
        self.naming_option.set("original")

        # 自定义前缀
        ttk.Label(self.input_frame, text="自定义前缀:").grid(row=5, column=0, padx=5, pady=8, sticky="e")
        self.custom_prefix_entry = ttk.Entry(self.input_frame, width=50)
        self.custom_prefix_entry.grid(row=5, column=1, padx=5, pady=8, columnspan=2, sticky="ew")

    def create_advanced_frame(self):
        """创建高级设置框架"""
        self.advanced_frame = ttk.LabelFrame(
            self.main_frame, 
            text="高级设置", 
            padding="15 15 15 15"
        )
        self.advanced_frame.pack(fill=tk.X, pady=(0, 15))

        # 超时时间
        ttk.Label(self.advanced_frame, text="超时时间（秒）:").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.timeout_entry = ttk.Entry(self.advanced_frame, width=10)
        self.timeout_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        self.timeout_entry.insert(0, "15")

        # 最大重试次数
        ttk.Label(self.advanced_frame, text="最大重试次数:").grid(row=0, column=2, padx=5, pady=8, sticky="e")
        self.retries_entry = ttk.Entry(self.advanced_frame, width=10)
        self.retries_entry.grid(row=0, column=3, padx=5, pady=8, sticky="w")
        self.retries_entry.insert(0, "3")

        # 下载间隔（秒）
        ttk.Label(self.advanced_frame, text="下载间隔（秒）:").grid(row=1, column=0, padx=5, pady=8, sticky="e")
        self.interval_entry = ttk.Entry(self.advanced_frame, width=10)
        self.interval_entry.grid(row=1, column=1, padx=5, pady=8, sticky="w")
        self.interval_entry.insert(0, "0")

    def create_control_buttons(self):
        """创建控制按钮框架"""
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(0, 15))

        self.download_button = ttk.Button(self.button_frame, text="开始下载", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(self.button_frame, text="暂停", command=self.pause_download, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(self.button_frame, text="取消", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

    def create_log_display(self):
        """创建日志输出框架"""
        self.log_frame = ttk.LabelFrame(
            self.main_frame, 
            text="下载日志", 
            padding="15 15 15 15"
        )
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        # 添加日志滚动条
        self.log_scrollbar = ttk.Scrollbar(self.log_frame)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(
            self.log_frame, 
            height=10, 
            width=70, 
            yscrollcommand=self.log_scrollbar.set, 
            wrap=tk.WORD,
            font=(".Microsoft YaHei UI", 9),
            bg="#ffffff"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_scrollbar.config(command=self.log_text.yview)
        self.log_text.config(state=tk.DISABLED)

    def setup_grid_weights(self):
        """配置网格权重，使界面可调整大小"""
        # 配置输入框架列权重
        self.input_frame.columnconfigure(1, weight=1)
        # 配置高级设置框架列权重
        self.advanced_frame.columnconfigure(1, weight=1)
        self.advanced_frame.columnconfigure(3, weight=1)

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
            download_interval = float(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("错误", "超时时间、重试次数和下载间隔必须为数字！")
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
            args=(url, selector_value, selector_type, save_dir, naming_option, custom_prefix, timeout, max_retries, self.log_message, download_interval),
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
