import os
from PyPDF2 import PdfReader, PdfWriter
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QFileDialog, QMessageBox, QProgressBar, QApplication, QLineEdit, QListWidgetItem, QInputDialog
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

        self.botao_selecionar = QPushButton("Selecionar Arquivos", self)
        self.botao_selecionar.clicked.connect(self.selecionar_arquivos)
        self.layout.addWidget(self.botao_selecionar)

        self.remove_page_button = QPushButton("Remover Página", self)
        self.remove_page_button.clicked.connect(self.remove_page)
        self.layout.addWidget(self.remove_page_button)

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

        # Botão para comprimir o PDF
        self.compress_button = QPushButton('Comprimir e Salvar', self)
        self.compress_button.clicked.connect(self.compress_pdf)
        self.layout.addWidget(self.compress_button)

        self.botao_renomear_arquivos = QPushButton(
            "Renomear Arquivos com TXT", self)
        self.botao_renomear_arquivos.clicked.connect(self.renomear_arquivos)
        self.layout.addWidget(self.botao_renomear_arquivos)

    def selecionar_arquivos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar Arquivos", "", "All Files (*);;PDF Files (*.pdf)"
        )
        if files:
            self.lista_arquivos.clear()
            for file in files:
                page_count = self.get_pdf_page_count(file)
                item_text = f"{os.path.basename(file)} - Páginas: {page_count}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, (file, page_count))
                self.lista_arquivos.addItem(item)

    def get_pdf_page_count(self, pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)

    def compress_pdf(self):
        # Verifica se há arquivos selecionados
        if self.lista_arquivos.count() == 0:
            QMessageBox.warning(self, "Erro", "Nenhum PDF selecionado.")
            return

        # Seleciona o arquivo PDF da lista
        selected_item = self.lista_arquivos.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self, "Erro", "Selecione um arquivo PDF da lista.")
            return

        pdf_path = selected_item.data(Qt.ItemDataRole.UserRole)[0]

        # Seleciona o local para salvar o arquivo comprimido
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF Comprimido", "", "PDF Files (*.pdf)"
        )

        if save_path:
            try:
                # Comprimir o PDF (reescrever para reduzir o tamanho)
                reader = PdfReader(pdf_path)
                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                # Salvar o arquivo comprimido
                with open(save_path, 'wb') as f:
                    writer.write(f)

                QMessageBox.information(
                    self, "Sucesso", f"PDF comprimido salvo em: {save_path}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Falha ao comprimir o PDF: {str(e)}")
        else:
            QMessageBox.warning(self, "Cancelado",
                                "Ação de salvar foi cancelada.")

    def remove_page(self):
        selected_item = self.lista_arquivos.currentItem()
        if selected_item:
            file_path, page_count = selected_item.data(
                Qt.ItemDataRole.UserRole)
            self.remove_page_from_pdf(file_path)

    def remove_page_from_pdf(self, file_path):
        reader = PdfReader(file_path)
        writer = PdfWriter()

        pages_to_keep = list(range(len(reader.pages)))

        # Solicitar as páginas para remover
        pages_to_remove, ok = QInputDialog.getText(
            self, "Remover Páginas", "Número das páginas que deseja remover (separadas por vírgula):"
        )

        if ok and pages_to_remove:
            try:
                # Converter a string de entrada em uma lista de números de página
                pages_to_remove = [
                    int(page.strip()) - 1 for page in pages_to_remove.split(",")]

                # Remover as páginas especificadas
                pages_to_keep = [
                    i for i in pages_to_keep if i not in pages_to_remove]

                for i in pages_to_keep:
                    writer.add_page(reader.pages[i])

                new_file_path = file_path.replace(".pdf", "_editado.pdf")
                with open(new_file_path, "wb") as f:
                    writer.write(f)

                QMessageBox.information(self, "Sucesso", f"As páginas {
                                        pages_to_remove} foram removidas com sucesso!\nNovo arquivo salvo como {new_file_path}")

            except ValueError:
                QMessageBox.warning(
                    self, "Erro", "Por favor, insira números de página válidos separados por vírgula.")

    def dividir_pdfs(self):
        print("Função dividir PDF foi chamada...")
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
                item = self.lista_arquivos.item(index)
                caminho_arquivo = item.data(Qt.ItemDataRole.UserRole)[0]
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
                i).data(Qt.ItemDataRole.UserRole)[0]
                for i in range(self.lista_arquivos.count())]
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
            try:
                with open(arquivo_nomes, 'r', encoding="utf-8") as file:
                    novos_nomes = file.read().splitlines()

                total_files = len(novos_nomes)
                if total_files == self.lista_arquivos.count():
                    for index in range(total_files):
                        item = self.lista_arquivos.item(index)
                        caminho_arquivo_original = item.data(
                            Qt.ItemDataRole.UserRole)[0]
                        novo_nome = novos_nomes[index]
                        novo_caminho_arquivo = os.path.join(
                            os.path.dirname(caminho_arquivo_original),
                            novo_nome +
                            os.path.splitext(caminho_arquivo_original)[1]
                        )
                        os.rename(caminho_arquivo_original,
                                  novo_caminho_arquivo)
                        item.setData(Qt.ItemDataRole.UserRole, (novo_caminho_arquivo, item.data(
                            Qt.ItemDataRole.UserRole)[1]))
                    QMessageBox.information(
                        self, "Sucesso", "Os arquivos foram renomeados com sucesso!"
                    )
                else:
                    QMessageBox.Warning(
                        self, "Erro", "O número de nomes no arquivo não corresponde ao número de arquivos selecionados."
                    )
            except Exception as e:
                QMessageBox.warning(
                    self, "Erro", f"Ocorreu um erro ao renomear os arquivos: {str(e)}")


if __name__ == "__main__":
    app = QApplication([])
    window = GerenciadorPdf()
    window.show()
    app.exec()
