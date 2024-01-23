import subprocess
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
import threading
from tkinterdnd2 import TkinterDnD, DND_FILES

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频转换器")

        # 设置宽度和高度的比例为4:3
        width = 500
        height = int(width * 3 / 4)
        self.root.geometry(f"{width}x{height}")

        self.input_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()

        ttk.Label(root, text="选择文件或文件夹:", anchor='w').pack(pady=5, padx=int(width*0.05), fill='both')
        self.input_entry = tk.Entry(root, textvariable=self.input_var)
        self.input_entry.pack(pady=5, padx=int(width*0.05), fill='both', expand=True)
        self.input_entry.drop_target_register(DND_FILES)
        self.input_entry.dnd_bind('<<Drop>>', self.drop_input)

        ttk.Button(root, text="浏览", command=self.browse_input).pack(pady=5, padx=int(width*0.05), fill='both')

        ttk.Label(root, text="输出文件夹:", anchor='w').pack(pady=5, padx=int(width*0.05), fill='both')
        self.output_entry = ttk.Entry(root, textvariable=self.output_folder_var)
        self.output_entry.pack(pady=5, padx=int(width*0.05), fill='both', expand=True)
        self.output_entry.drop_target_register(DND_FILES)
        self.output_entry.dnd_bind('<<Drop>>', self.drop_output)

        ttk.Button(root, text="浏览", command=self.browse_output_folder).pack(pady=5, padx=int(width*0.05), fill='both')

        self.convert_button = ttk.Button(root, text="转换", command=self.start_conversion)
        self.convert_button.pack(pady=10, padx=int(width*0.05), fill='both')

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, mode='determinate', length=int(width*0.8))
        self.progress_bar.pack(pady=10, padx=int(width*0.05), fill='both')

        # 进度条文本标签
        self.progress_label_var = tk.StringVar()
        self.progress_label = ttk.Label(root, textvariable=self.progress_label_var)
        self.progress_label.pack(pady=5, padx=int(width*0.05), fill='both')

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.thread_lock = threading.Lock()

    def drop_input(self, event):
        # 处理拖放到输入框的事件
        input_path = event.data
        # 去除两边的大括号
        input_path = input_path.strip('{}')
        self.input_var.set(input_path)

    def drop_output(self, event):
        # 处理拖放到输出框的事件
        output_path = event.data
        # 去除两边的大括号
        output_path = output_path.strip('{}')
        self.output_folder_var.set(output_path)

    def browse_input(self):
        file_types = [
            ("视频文件", "*.mp4;*.avi;*.mkv;*.mov;*.wmv"),
            ("音频文件", "*.mp3;*.wav;*.flac"),
            ("所有文件", "*.*")
        ]
        input_path = filedialog.askopenfilename(initialdir="/", title="选择文件或文件夹", filetypes=file_types)

        if input_path:
            self.input_var.set(input_path)

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        self.output_folder_var.set(folder)

    def start_conversion(self):
        input_path = self.input_var.get()
        output_folder = self.output_folder_var.get()

        if not input_path or not output_folder:
            messagebox.showwarning("错误", "请选择输入文件或文件夹以及输出文件夹。")
            return

        try:
            self.convert_button.config(state='disabled')
            self.progress_bar["value"] = 0
            self.progress_var.set(0)

            os.makedirs(output_folder, exist_ok=True)

            future = self.executor.submit(self.convert, input_path, output_folder)
            future.add_done_callback(self.on_conversion_done)
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            self.convert_button.config(state='normal')

    def on_conversion_done(self, future):
        try:
            future.result()
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
        finally:
            with self.thread_lock:
                self.convert_button.config(state='normal')
                messagebox.showinfo("转换完成", "视频转换完成.")
                self.progress_label_var.set("转换完成")

    def convert(self, input_path, output_folder):
        if os.path.isdir(input_path):
            input_files = [f for f in os.listdir(input_path) if f.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mp3', '.wav', '.flac'))]
        elif os.path.isfile(input_path) and input_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.mp3', '.wav', '.flac')):
            input_files = [os.path.basename(input_path)]
            input_path = os.path.dirname(input_path)
        else:
            raise ValueError("不支持的文件类型，请选择文件或包含视频文件的文件夹。")

        total_files = len(input_files)

        for i, input_file in enumerate(input_files, start=1):
            input_file_path = os.path.join(input_path, input_file)
            output_file_prefix = os.path.join(output_folder, os.path.splitext(input_file)[0])
            convert_to_m3u8(input_file_path, output_file_prefix)

            progress = (i / total_files) * 100
            self.progress_var.set(progress)
            self.progress_label_var.set(f"转换中: {i}/{total_files}")

def convert_to_m3u8(input_file, output_file_prefix):
    output_m3u8_file = f'{output_file_prefix}.m3u8'

    if os.path.exists(output_m3u8_file):
        user_response = messagebox.askyesno("文件已存在", f"{output_m3u8_file} 已经存在。\n是否要覆盖？")
        if not user_response:
            return

    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-f', 'hls',
        '-hls_time', '3',
        '-hls_list_size', '0',
        '-hls_segment_filename', f'{output_file_prefix}_%02d.ts',
        output_m3u8_file
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = VideoConverterApp(root)
    root.mainloop()
