import os
import sys
import requests
import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton

class DownloaderThread(QThread):
    progress = pyqtSignal(int)
    speed = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, output_path):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self._is_cancelled = False

    def run(self):
        try:
            with requests.get(self.url, stream=True, timeout=10) as r:
                r.raise_for_status()
                total_length = int(r.headers.get('content-length', 0))
                downloaded = 0
                start_time = self.msecs_since_start()

                with open(self.output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if self._is_cancelled:
                            self.error.emit("Download cancelado.")
                            return

                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percent = int((downloaded / total_length) * 100)
                            self.progress.emit(percent)

                            elapsed = self.msecs_since_start() - start_time
                            if elapsed > 0:
                                speed_kbps = (downloaded / elapsed) * 1000 / 1024
                                self.speed.emit(f"{speed_kbps:.2f} KB/s")
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._is_cancelled = True

    def msecs_since_start(self):
        import time
        return int(time.time() * 1000)

class AutoAtualizador(QDialog):
    def __init__(self, url_instalador, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Atualizando Gerenciador PDF...")
        self.setFixedSize(400, 150)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.layout = QVBoxLayout(self)

        self.label_status = QLabel("Baixando nova versão...", self)
        self.layout.addWidget(self.label_status)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)

        self.label_speed = QLabel("Velocidade: 0 KB/s", self)
        self.layout.addWidget(self.label_speed)

        self.cancel_button = QPushButton("Cancelar", self)
        self.cancel_button.clicked.connect(self.cancelar_download)
        self.layout.addWidget(self.cancel_button)

        temp_dir = os.getenv('TEMP') or "/tmp"
        self.output_path = os.path.join(temp_dir, "GerenciadorPDF-Setup.exe")

        self.thread = DownloaderThread(url_instalador, self.output_path)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.speed.connect(self.label_speed.setText)
        self.thread.finished.connect(self.instalador_baixado)
        self.thread.error.connect(self.erro_download)
        self.thread.start()

    def cancelar_download(self):
        self.thread.cancel()
        self.close()

    def instalador_baixado(self, path):
        self.label_status.setText("Download concluído!")
        subprocess.Popen([path, "/silent"], shell=True)
        self.close()
        QApplication.quit()

    def erro_download(self, mensagem):
        self.label_status.setText(f"Erro: {mensagem}")
        self.cancel_button.setText("Fechar")
