import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QFileDialog, 
                             QLabel, QMessageBox, QGroupBox, QTextEdit, 
                             QRadioButton, QButtonGroup, QAbstractItemView, QInputDialog, QLineEdit)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

# Try to set up ffmpeg from imageio-ffmpeg if available (fixes pydub RuntimeWarning)
try:
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    # Configure pydub to use the specific ffmpeg executable
    try:
        from pydub import AudioSegment
        AudioSegment.converter = ffmpeg_path
    except ImportError:
        pass
except ImportError:
    pass

# Try to import MarkItDown
try:
    # Assuming we are in the root of the repo and markitdown package is available
    # Use src/markitdown to ensure we load the local modified version
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "markitdown", "src"))
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None

class ConversionThread(QThread):
    progress_update = pyqtSignal(str) # Log message
    file_finished = pyqtSignal(str, bool) # filename, success
    all_finished = pyqtSignal()

    def __init__(self, files, output_dir=None):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.running = True

    def run(self):
        if not MarkItDown:
            self.progress_update.emit("错误: 无法导入 'markitdown' 库。请确保已安装该库或在项目根目录下运行。")
            self.all_finished.emit()
            return

        try:
            # Set up a requests session with a browser-like User-Agent
            import requests
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            md = MarkItDown(requests_session=session)
        except Exception as e:
            self.progress_update.emit(f"初始化 MarkItDown 失败: {str(e)}")
            self.all_finished.emit()
            return
        
        for file_path in self.files:
            if not self.running:
                break
            
            # Skip if directory (unless we want to support dir recursion later)
            if os.path.isdir(file_path):
                self.progress_update.emit(f"跳过文件夹: {file_path}")
                continue

            try:
                self.progress_update.emit(f"正在转换: {os.path.basename(file_path)}...")
                
                # Check if it's a URL or file
                if file_path.startswith("http://") or file_path.startswith("https://"):
                    # URL processing
                    result = md.convert(file_path)
                    base_name = "url_content"
                    # Try to guess a name from URL
                    import urllib.parse
                    path_part = urllib.parse.urlparse(file_path).path
                    if path_part and path_part != "/":
                        base_name = os.path.splitext(os.path.basename(path_part))[0]
                    if not base_name:
                         base_name = "downloaded_content"
                else:
                    # File processing
                    result = md.convert(file_path)
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                
                # Determine output path
                if self.output_dir:
                    out_dir = self.output_dir
                else:
                    if os.path.exists(file_path):
                        out_dir = os.path.dirname(file_path)
                    else:
                        out_dir = os.getcwd() # Fallback for URLs
                
                # Ensure output directory exists
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)

                out_path = os.path.join(out_dir, f"{base_name}.md")
                
                # Handle filename collision
                counter = 1
                while os.path.exists(out_path):
                    out_path = os.path.join(out_dir, f"{base_name}_{counter}.md")
                    counter += 1
                
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(result.text_content)
                
                self.progress_update.emit(f"成功: {out_path}")
                self.file_finished.emit(file_path, True)
                
            except Exception as e:
                self.progress_update.emit(f"失败 {os.path.basename(file_path)}: {str(e)}")
                self.file_finished.emit(file_path, False)
        
        self.all_finished.emit()

    def stop(self):
        self.running = False

class FileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            f = url.toLocalFile()
            # If it's a local file
            if f and os.path.exists(f):
                existing_items = [self.item(i).text() for i in range(self.count())]
                if f not in existing_items:
                    self.addItem(f)
            else:
                # If it's a remote URL (e.g. dragged from browser)
                str_url = url.toString()
                if str_url.startswith("http"):
                    existing_items = [self.item(i).text() for i in range(self.count())]
                    if str_url not in existing_items:
                        self.addItem(str_url)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkItDown GUI - 全能Markdown转换工具")
        self.resize(900, 700)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Header / Instructions
        title_label = QLabel("MarkDown 转换器")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(title_label)

        desc_label = QLabel("将各类文档转换为 Markdown 格式，便于 LLM 使用。")
        layout.addWidget(desc_label)
        
        # Supported formats
        formats_text = (
            "支持格式：\n"
            "• 办公文档: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx)\n"
            "• 多媒体: 音频 (.mp3, .wav)\n"
            "• 网络: HTML, Wikipedia, YouTube, Bing搜索结果, RSS\n"
            "• 数据/电子书: CSV, JSON, XML, ZIP, EPUB"
        )
        format_group = QGroupBox("支持的转换类型")
        format_layout = QVBoxLayout()
        format_label = QLabel(formats_text)
        format_label.setStyleSheet("color: #444; font-size: 12px;")
        format_layout.addWidget(format_label)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # File List Area
        list_label = QLabel("文件列表 (支持拖拽文件):")
        layout.addWidget(list_label)

        self.file_list = FileListWidget()
        layout.addWidget(self.file_list)
        
        # Buttons area
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ 添加文件")
        self.btn_add.clicked.connect(self.add_files)
        self.btn_add_url = QPushButton("🌐 添加 URL")
        self.btn_add_url.clicked.connect(self.add_url)
        self.btn_remove = QPushButton("➖ 移除选中")
        self.btn_remove.clicked.connect(self.remove_files)
        self.btn_clear = QPushButton("🗑️ 清空列表")
        self.btn_clear.clicked.connect(self.file_list.clear)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_add_url)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)
        
        # Output Options
        opt_group = QGroupBox("输出设置")
        opt_layout = QHBoxLayout()
        
        self.radio_source = QRadioButton("保存在原文件同级目录")
        self.radio_custom = QRadioButton("指定输出目录")
        self.radio_source.setChecked(True)
        
        self.btn_browse = QPushButton("浏览...")
        self.btn_browse.setEnabled(False)
        self.btn_browse.clicked.connect(self.browse_output)
        
        self.custom_path_label = QLabel("")
        self.custom_path_label.setStyleSheet("color: gray; font-style: italic;")
        
        self.output_group = QButtonGroup()
        self.output_group.addButton(self.radio_source)
        self.output_group.addButton(self.radio_custom)
        self.output_group.buttonToggled.connect(self.toggle_output_options)
        
        opt_layout.addWidget(self.radio_source)
        opt_layout.addWidget(self.radio_custom)
        opt_layout.addWidget(self.btn_browse)
        opt_layout.addWidget(self.custom_path_label)
        opt_layout.addStretch()
        opt_group.setLayout(opt_layout)
        layout.addWidget(opt_group)
        
        # Convert Button
        self.btn_convert = QPushButton("🚀 开始转换")
        self.btn_convert.setStyleSheet("font-size: 16px; padding: 12px; font-weight: bold; background-color: #0078D4; color: white; border-radius: 5px;")
        self.btn_convert.clicked.connect(self.start_conversion)
        layout.addWidget(self.btn_convert)
        
        # Log Area
        log_label = QLabel("转换日志:")
        layout.addWidget(log_label)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        self.log_area.setPlaceholderText("准备就绪...")
        layout.addWidget(self.log_area)
        
        self.thread = None

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        if files:
            existing_items = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            for f in files:
                if f not in existing_items:
                    self.file_list.addItem(f)

    def add_url(self):
        text, ok = QInputDialog.getText(self, "添加 URL", "请输入要转换的网址 (如网页链接、维基百科等):", QLineEdit.Normal, "")
        if ok and text:
            url = text.strip()
            if url:
                 existing_items = [self.file_list.item(i).text() for i in range(self.file_list.count())]
                 if url not in existing_items:
                    self.file_list.addItem(url)

    def remove_files(self):
        # Must collect items first because indices change when removing
        items = self.file_list.selectedItems()
        if not items:
            return
        for item in items:
            self.file_list.takeItem(self.file_list.row(item))

    def toggle_output_options(self, btn, checked):
        if checked:
            is_custom = (btn == self.radio_custom)
            self.btn_browse.setEnabled(is_custom)
            if not is_custom:
                self.custom_path_label.setText("")

    def browse_output(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if d:
            self.custom_path_label.setText(d)

    def start_conversion(self):
        count = self.file_list.count()
        if count == 0:
            QMessageBox.warning(self, "提示", "请先添加文件！")
            return
            
        files = [self.file_list.item(i).text() for i in range(count)]
        output_dir = None
        if self.radio_custom.isChecked():
            output_dir = self.custom_path_label.text()
            if not output_dir:
                QMessageBox.warning(self, "提示", "请选择输出目录！")
                return
        
        self.btn_convert.setEnabled(False)
        self.btn_convert.setText("正在转换...")
        self.log_area.append("\n=== 开始任务 ===")
        
        self.thread = ConversionThread(files, output_dir)
        self.thread.progress_update.connect(self.log_area.append)
        self.thread.all_finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self):
        self.log_area.append("=== 任务完成 ===")
        self.btn_convert.setEnabled(True)
        self.btn_convert.setText("🚀 开始转换")
        QMessageBox.information(self, "完成", "转换任务已结束，请查看日志获取详情。")

if __name__ == "__main__":
    if not MarkItDown:
        print("警告: 未找到 'markitdown' 模块。GUI 将无法执行转换。")
    
    app = QApplication(sys.argv)
    
    # Optional: Set style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
