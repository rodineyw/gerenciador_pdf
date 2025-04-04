import os

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QFileDialog, QMessageBox, QProgressBar, QApplication, QLineEdit, QListWidgetItem, QInputDialog, QCheckBox, QSlider
)
from .pdf_utils import dividir_pdf, mesclar_pdfs, renomear_com_texto, comprimir_pdf


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

        
        # Checkbox para reduzir imagem
        self.checkbox_reduzir_imagem = QCheckBox("Reduzir qualidade das imagens", self)
        self.layout.addWidget(self.checkbox_reduzir_imagem)
        
        # Slider para escolher a qualidade
        self.slider_qualidade = QSlider(Qt.Orientation.Horizontal)
        self.slider_qualidade.setMinimum(10)
        self.slider_qualidade.setMaximum(95)
        self.slider_qualidade.setValue(75)
        self.slider_qualidade.setTickInterval(5)
        self.slider_qualidade.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.layout.addWidget(QLabel("Qualidade das imagens (quanto menor, mais comprimido):"))
        self.layout.addWidget(self.slider_qualidade)

        
        # Botão de compressão
        self.compress_button = QPushButton('Comprimir e Salvar', self)
        self.compress_button.clicked.connect(self.compress_pdf)
        self.layout.addWidget(self.compress_button)

        # Botão renomear arquivo
        self.botao_renomear_arquivos = QPushButton(
            "Renomear Arquivos com TXT", self)
        self.botao_renomear_arquivos.clicked.connect(self.renomear_arquivos)
        self.layout.addWidget(self.botao_renomear_arquivos)

    """ Selecionar arquivos """
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

    """ Função para obter o número de páginas de um PDF """
    def get_pdf_page_count(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as f:
                pdf = PdfReader(f)
                return len(pdf.pages)
        except PdfReadError:
            print(f"Aviso: PyPDF2 falhou ao ler {pdf_path}. Tentando com FItz...")
            try:
                import fitz
                doc = fitz.open(pdf_path)
                count = len(doc)
                doc.close()
                return count
            except Exception as e:
                print(f"Erro ao contar páginas de {pdf_path} com Fitz: {e}")
                return 0
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado {pdf_path}")
            return 0
        except Exception as e:
            print(f"Erro inesperado ao contar páginas de {pdf_path}: {e}")
            return 0

    """ Comprimir PDF """
    def compress_pdf(self):
        if self.lista_arquivos.count() == 0:
            QMessageBox.warning(self, "Atenção", "Nenhum PDF selecionado.")
            return

        selected_item = self.lista_arquivos.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Atenção", "Selecione um arquivo PDF da lista.")
            return

        pdf_path, _ = selected_item.data(Qt.ItemDataRole.UserRole)[0]
        
        # garante que é um PDF antes de prosseguir
        if not pdf_path.lower().endswith(".pdf"):
            QMesssageBox.critical(self, "Erro", f"O arquivo '{os.path.basename(pdf_path)}' não parece ser um PDF válido.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF Comprimido como...", os.path.basename(pdf_path).replace(".pdf", "_comprimido.pdf"), "PDF Files (*.pdf)"
        )

        if not save_path:
            QMessageBox.warning(self, "Cancelado", "Salvamento cancelado pelo usuário.")
            return
        
        # Garante que o nome de saída também tenha .pdf
        if not save_path.lower().endswith(".pdf"):
            save_path += ".pdf"

        reduzir = self.checkbox_reduzir_imagem.isChecked()
        qualidade_img = self.slider_qualidade.value()

        try:
            # Mostra uma indicação de que está trabalhando
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.progress_bar.setRange(0, 0)
            
            print(f"Tentando comprimir: {pdf_path}")
            print(f"Salvar em: {save_path}")
            print(f"Reduzir imagens: {reduzir}, Qualidade: {qualidade_img}")
            
            # Chama a função de compressão do pdf_utils.py
            original, final = comprimir_pdf(
                file_path=pdf_path,
                output_path=save_path,
                reduzir_imagem=reduzir,
                qualidade=qualidade_img
            )
            
            # Restaura o cursor e a barra de progresso
            QApplication.restoreOverrideCursor()
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)

            if final is not None:
                original_mb = original / (1024 * 1024)
                final_mb = final / (1024 * 1024)
                
                if final >= original:
                    print(f"Compressão ineficaz ou aumentou o tamanho. Original: {original_mb:.2f} MB, Final: {final_mb:.2f} MB")
                    QMessageBox.warning(
                        self, "Compressão Ineficaz",
                        f"A compressão não reduziu o tamanho do arquivo (ou até aumentou).\n"
                        f"Tamanho original: {original_mb:.2f} MB\n"
                        f"Tamanho 'comprimido': {final_mb:.2f} MB\n\n"
                        f"O arquivo maior foi descartado. Nenhuma alteração foi salva."
                    )
                    
                    try:
                        os.remove(save_path)
                        print(f"Arquivo maior descartado: {save_path}")
                    except OSError as e:
                        print(f"Erro ao tentar deletar o arquivo maior '{save_path}': {e}")
                        QMessageBox.critical(self, "Erro", f"Não foi possivel deletar o arquivo maior gerado:\n{save_path}\n\nErro: {e}")
                else:
                    diff = original_mb - final_mb
                    print(f"Compressão bem-sucedida! Redução: {diff:.2f} MB")
                    QMessageBox.information(
                        self, "Sucesso",
                        f"PDF comprimido e salvo com sucesso!\n"
                        f"Tamanho original: {original_mb:.2f} MB\n"
                        f"Tamanho final: {final_mb:.2f} MB\n"
                        f"Redução: {diff:.2f} MB"
                        f"Salvo em: {save_path}"
                    )
            else:
                QMessageBox.critical(self, "Erro na compressão",
                                     "Ocorreu um erro interno durante a tentativa de compressão. Veja o console para detalhes.\n"
                                     f"O arquivo de saída '{save_path}' pode não ter sido criado ou estar incmpleto.")
                if os.path.exists(save_path):
                    try:
                        os.remove(save_path)
                    except OSError:
                        pass
        except Exception as e:
            QApplecation.restoreOverrideCursor()
            self.progress_bar.setRange(0, 1)
            self.progress_barsetValue(0)
            print(f"Erro GERAL na função compress_pdf (gerenciador_pdf.py): {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro inesperado ao tentar comprimir:\n{str(e)}")
            if 'save_path' in locals() and os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except OSError:
                    pass
                                
    """ Remover Paginas """
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

    """ Dividir PDFs"""
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

    """ Mesclar PDFs """
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

    """ Renomear PDFs """
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
