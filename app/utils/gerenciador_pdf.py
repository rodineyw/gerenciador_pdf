from PyPDF2 import PdfReader
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QFileDialog, QMessageBox, QProgressBar, QApplication, QLineEdit
)
from .pdf_utils import dividir_pdf, mesclar_pdfs, renomear_com_texto


class GerenciadorPdf(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setup_widgets()
        self.setWindowTitle("Gerenciador de Arquivos PDF")
        self.setGeometry(300, 300, 600, 400)

    def setup_widgets(self):
        self.lista_arquivos = QListWidget(self)
        self.layout.addWidget(self.lista_arquivos)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)
        
        self.label = QLabel("Número de Páginas: 0")
        self.layout.addWidget(self.label)

        self.botao_selecionar = QPushButton("Selecionar Arquivos", self)
        self.botao_selecionar.clicked.connect(self.selecionar_arquivos)
        self.layout.addWidget(self.botao_selecionar)

        self.pages_per_file_label = QLabel("Páginas por Arquivo:", self)
        self.layout.addWidget(self.pages_per_file_label)

        self.pages_per_file_input = QLineEdit(self)
        self.layout.addWidget(self.pages_per_file_input)

        self.botao_dividir = QPushButton("Dividir PDFs Selecionados", self)
        self.botao_dividir.clicked.connect(self.dividir_pdfs)
        self.layout.addWidget(self.botao_dividir)

        self.merge_button = QPushButton("Mesclar PDFs Selecionados", self)
        self.merge_button.clicked.connect(self.merge_pdfs)
        self.layout.addWidget(self.merge_button)

        self.botao_renomear_arquivos = QPushButton(
            "Renomear Arquivos com TXT", self)
        self.botao_renomear_arquivos.clicked.connect(self.renomear_arquivos)
        self.layout.addWidget(self.botao_renomear_arquivos)

        # self.botao_renomear_planilha = QPushButton(
        #     "Renomear com Planilha", self)
        # self.botao_renomear_planilha.clicked.connect(
        #     self.renomear_com_planilha)
        # self.layout.addWidget(self.botao_renomear_planilha)

    def selecionar_arquivos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar Arquivos", "", "All Files (*);;PDF Files (*.pdf)"
        )
        if files:
            self.lista_arquivos.clear()
            self.lista_arquivos.addItems(files)
            page_count = self.get_pdf_page_count(files[0])
            self.label.setText(f"Número de Páginas: {page_count}")
            
            
    def get_pdf_page_count(self, pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)
        

    def dividir_pdfs(self):
        pasta_saida = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta de Saída")
        if pasta_saida and self.lista_arquivos.count() > 0:
            total_files = self.lista_arquivos.count()
            self.progress_bar.setMaximum(total_files)
            try:
                paginas_por_arquivo = int(self.pages_per_file_input.text())
            except ValueError:
                QMessageBox.warning(
                    self, "Erro", "Páginas por arquivo deve ser um número inteiro!")
                return
            for index in range(total_files):
                caminho_arquivo = self.lista_arquivos.item(index).text()
                if caminho_arquivo.lower().endswith(".pdf"):
                    dividir_pdf(caminho_arquivo, pasta_saida,
                                paginas_por_arquivo)
                    self.progress_bar.setValue(index + 1)
            self.progress_bar.setValue(0)
            QMessageBox.information(
                self, "Sucesso", "Os PDFs foram divididos com sucesso!")

    def merge_pdfs(self):
        pasta_saida = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta de Saída")
        if pasta_saida and self.lista_arquivos.count() > 0:
            files = [self.lista_arquivos.item(
                i).text() for i in range(self.lista_arquivos.count())]
            arquivos_ignorados = mesclar_pdfs(files, pasta_saida)

            if arquivos_ignorados:
                mensagem_arquivos_ignorados = "\n".join(arquivos_ignorados)
                QMessageBox.warning(
                    self, "Atenção", f"Os seguintes arquivos foram ignorados:\n{
                        mensagem_arquivos_ignorados}"
                )

            QMessageBox.information(
                self, "Sucesso", "Os PDFs foram mesclados com sucesso!")

    def renomear_arquivos(self):
        arquivo_nomes, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Nomes", "", "Text Files (*.txt)")
        if arquivo_nomes:
            arquivos = [self.lista_arquivos.item(
                i).text() for i in range(self.lista_arquivos.count())]
            renomear_com_texto(arquivos, arquivo_nomes)
            self.lista_arquivos.clear()
            self.lista_arquivos.addItems(arquivos)
            QMessageBox.information(
                self, "Sucesso", "Os arquivos foram renomeados com sucesso!"
            )

    # def renomear_com_planilha(self):
    #     arquivo_planilha, _ = QFileDialog.getOpenFileName(
    #         self, "Selecionar Planilha", "", "Excel Files (*.xlsx)")
    #     if arquivo_planilha:
    #         pasta_saida = QFileDialog.getExistingDirectory(
    #             self, "Selecionar Pasta de Saída")
    #         if pasta_saida:
    #             arquivos = [self.lista_arquivos.item(
    #                 i).text() for i in range(self.lista_arquivos.count())]
    #             renomear_com_planilha(arquivos, arquivo_planilha, pasta_saida)
    #             QMessageBox.information(
    #                 self, "Sucesso", "Os arquivos foram renomeados conforme a planilha!"
    #             )


if __name__ == "__main__":
    app = QApplication([])
    window = GerenciadorPdf()
    window.show()
    app.exec()
