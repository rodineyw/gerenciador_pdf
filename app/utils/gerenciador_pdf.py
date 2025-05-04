import os
import requests
import subprocess

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QFileDialog, QMessageBox, QProgressBar, QApplication, QLineEdit, QListWidgetItem, QInputDialog, QCheckBox, QSlider, QComboBox
)
from .pdf_utils import dividir_pdf, mesclar_pdfs, renomear_com_texto, comprimir_pdf_ghostscript


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
        # self.checkbox_reduzir_imagem = QCheckBox("Reduzir qualidade das imagens", self)
        # self.layout.addWidget(self.checkbox_reduzir_imagem)
        
        # # Slider para escolher a qualidade
        # self.slider_qualidade = QSlider(Qt.Orientation.Horizontal)
        # self.slider_qualidade.setMinimum(10)
        # self.slider_qualidade.setMaximum(95)
        # self.slider_qualidade.setValue(75)
        # self.slider_qualidade.setTickInterval(5)
        # self.slider_qualidade.setTickPosition(QSlider.TickPosition.TicksBelow)
        # self.layout.addWidget(QLabel("Qualidade das imagens (quanto menor, mais comprimido):"))
        # self.layout.addWidget(self.slider_qualidade)

        # Widgets de compressão com ghostscript
        self.layout.addWidget(QLabel("Opções de compressão:", self))
        
        # Presets ghostscript
        self.combo_preset_gs = QComboBox(self)
        
        self.combo_preset_gs.addItem("Tela (Menor Tamanho, Baixa Qualidade)", "/screen")
        self.combo_preset_gs.addItem("Ebook (Bom Equilíbrio)", "/ebook")
        self.combo_preset_gs.addItem("Impressão (Alta Qualidade)", "/printer")
        self.combo_preset_gs.addItem("Pré-impressão (Qualidade Máxima, Maior Tamanho)", "/prepress")
        self.combo_preset_gs.addItem("Padrão", "/default")
        # Define o 'Ebook' como padrão inicial
        self.combo_preset_gs.setCurrentIndex(1) # Índice 1 corresponde a '/ebook'
        self.layout.addWidget(self.combo_preset_gs)
        
        # Botão de compressão
        self.compress_button = QPushButton('Comprimir e Salvar PDF selecionado', self)
        self.compress_button.clicked.connect(self.compress_pdf)
        self.layout.addWidget(self.compress_button)

        # Botão renomear arquivo
        self.botao_renomear_arquivos = QPushButton(
            "Renomear Arquivos com TXT", self)
        self.botao_renomear_arquivos.clicked.connect(self.renomear_arquivos)
        self.layout.addWidget(self.botao_renomear_arquivos)
        
        self.botao_renomear_excel = QPushButton("Renomear Arquivos com Excel", self)
        self.botao_renomear_excel.clicked.connect(self.renomear_com_excel)
        self.layout.addWidget(self.botao_renomear_excel)
        
        # Botão para verificar atualizações
        self.botao_atualizar = QPushButton("Verificar Atualizações", self)
        self.botao_atualizar.clicked.connect(self.atualizar_se_disponivel)
        self.layout.addWidget(self.botao_atualizar)
        
    def atualizar_se_disponivel(self):
        VERSAO_ATUAL = "0.2"  # Atualize sempre que lançar nova versão
        URL_VERSAO = "https://raw.githubusercontent.com/rodineyw/gerenciador_pdf/main/gerenciadorpdf_version.txt"
        URL_INSTALADOR = "https://github.com/rodineyw/gerenciador_pdf/releases/download/v0.2/GerenciadorPDF-Setup.exe"

        try:
            resposta = requests.get(URL_VERSAO, timeout=5)
            versao_disponivel = resposta.text.strip()

            if versao_disponivel != VERSAO_ATUAL:
                resposta_user = QMessageBox.question(
                    self, "Atualização Disponível",
                    f"Nova versão {versao_disponivel} disponível.\nDeseja atualizar agora?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if resposta_user == QMessageBox.StandardButton.Yes:
                    from app.utils.autoatualizador import AutoAtualizador
                    self.atualizador = AutoAtualizador(URL_INSTALADOR, self)
                    self.atualizador.exec()
            else:
                QMessageBox.information(self, "Atualização", "Você já está usando a versão mais recente.")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao verificar atualização:\n{str(e)}")


    def baixar_e_instalar(self, url_instalador):
        try:
            resposta = requests.get(url_instalador, stream=True)
            instalador_path = os.path.join(os.getenv('TEMP'), "GerenciadorPDF-Setup.exe")

            with open(instalador_path, 'wb') as f:
                for chunk in resposta.iter_content(chunk_size=8192):
                    f.write(chunk)

            subprocess.Popen([instalador_path, "/silent"], shell=True)
            QMessageBox.information(self, "Atualização", "Atualizador iniciado. O aplicativo será fechado.")
            QApplication.quit()

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao baixar ou iniciar instalador:\n{str(e)}")


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

    """ Comprimir PDF (Agora usando Ghostscript) """
    def compress_pdf(self):
        # --- Validação inicial (igual antes) ---
        if self.lista_arquivos.count() == 0:
            QMessageBox.warning(self, "Atenção", "Nenhum PDF selecionado.")
            return
        selected_item = self.lista_arquivos.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Atenção", "Selecione um arquivo da lista.")
            return
        # ... (Validação do pdf_path - igual antes) ...
        pdf_path_data = selected_item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(pdf_path_data, tuple) or len(pdf_path_data) == 0:
             QMessageBox.critical(self, "Erro Interno", "Não foi possível obter o caminho do arquivo selecionado.")
             print(f"Erro: Dado inesperado para o item selecionado: {pdf_path_data}")
             return
        pdf_path = pdf_path_data[0]
        if not isinstance(pdf_path, str) or not pdf_path.lower().endswith(".pdf"):
             QMessageBox.critical(self, "Erro", f"O arquivo '{os.path.basename(str(pdf_path))}' não parece ser um PDF válido.")
             return

        # --- Diálogo de Salvar (igual antes) ---
        default_save_name = os.path.basename(pdf_path).replace(".pdf", "_comprimido_gs.pdf") # Mudei sufixo
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF Comprimido (Ghostscript)", default_save_name, "PDF Files (*.pdf)"
        )
        if not save_path:
            print("Salvamento cancelado pelo usuário.")
            return
        if not save_path.lower().endswith(".pdf"):
            save_path += ".pdf"

        # **** PEGA O PRESET DO GHOSTSCRIPT SELECIONADO ****
        selected_preset = self.combo_preset_gs.currentData() # Pega o dado interno ('/ebook', etc.)

        try:
            # --- Feedback Visual (igual antes) ---
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.progress_bar.setRange(0, 0) # Indeterminado, GS não dá progresso fácil

            print(f"Tentando comprimir com Ghostscript: {pdf_path}")
            print(f"Preset: {selected_preset}")
            print(f"Salvar em: {save_path}")

            # **** CHAMA A NOVA FUNÇÃO DO PDF_UTILS ****
            original, final = comprimir_pdf_ghostscript(
                file_path=pdf_path,
                output_path=save_path,
                quality_preset=selected_preset
            )

            # --- Restaura Feedback Visual (igual antes) ---
            QApplication.restoreOverrideCursor()
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)

            # --- Lógica de resultado (quase igual, ajusta mensagem se falhou) ---
            if final is not None: # Ghostscript retornou tamanho final (pode ter tido erro antes)
                 # Verifica se original também foi obtido (GS pode falhar antes de ler o original)
                if original is None:
                     QMessageBox.critical(self, "Erro",
                                         "Não foi possível ler o tamanho do arquivo original.")
                     return # Sai se não tem tamanho original

                original_mb = original / (1024 * 1024)
                final_mb = final / (1024 * 1024)

                if final >= original:
                    print(f"Compressão GS ineficaz ou aumentou tamanho. Original: {original_mb:.2f} MB, Final: {final_mb:.2f} MB")
                    QMessageBox.warning(
                        self, "Compressão Ineficaz",
                        f"A compressão com Ghostscript (preset: {selected_preset}) "
                        f"não reduziu o tamanho do arquivo (ou até aumentou!).\n"
                        f"Tamanho original: {original_mb:.2f} MB\n"
                        f"Tamanho final: {final_mb:.2f} MB\n\n"
                        f"O arquivo maior foi descartado."
                    )
                    try:
                        os.remove(save_path)
                        print(f"Arquivo maior descartado: {save_path}")
                    except OSError as e:
                        print(f"Erro ao tentar deletar arquivo maior '{save_path}': {e}")
                        QMessageBox.critical(self, "Erro", f"Não foi possível deletar arquivo maior gerado:\n{save_path}\n\nErro: {e}")
                else:
                    diff = original_mb - final_mb
                    reduction_percent = ((original - final) / original * 100) if original > 0 else 0
                    print(f"Compressão GS bem-sucedida! Redução: {diff:.2f} MB")
                    QMessageBox.information(
                        self, "Sucesso!",
                        f"PDF comprimido com Ghostscript (preset: {selected_preset})!\n"
                        f"Tamanho original: {original_mb:.2f} MB\n"
                        f"Tamanho final: {final_mb:.2f} MB\n"
                        f"Redução: {diff:.2f} MB ({reduction_percent:.1f}%)\n\n"
                        f"Salvo em: {save_path}"
                    )
            else:
                 # Se final é None, significa que comprimir_pdf_ghostscript falhou
                 error_msg = "Ocorreu um erro durante a compressão com Ghostscript.\n"
                 error_msg += "Verifique se o Ghostscript está instalado e acessível (no PATH).\n"
                 error_msg += "Consulte o console/terminal para mensagens de erro detalhadas do Ghostscript."
                 QMessageBox.critical(self, "Erro na Compressão (Ghostscript)", error_msg)
                 # Tenta limpar arquivo de saída incompleto
                 if os.path.exists(save_path):
                     try: os.remove(save_path)
                     except OSError: pass

        except Exception as e: # Erro geral no Python
            QApplication.restoreOverrideCursor()
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)
            print(f"Erro GERAL Python ao chamar compress_pdf (gerenciador_pdf.py): {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro Inesperado Python", f"Ocorreu um erro inesperado:\n{str(e)}")
            if 'save_path' in locals() and os.path.exists(save_path):
                 try: os.remove(save_path)
                 except OSError: pass
                 
                                
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
                
    def renomear_com_excel(self):
        from .pdf_utils import renomear_com_excel
        renomear_com_excel(self, [self.lista_arquivos.item(i) for i in range(self.lista_arquivos.count())])



if __name__ == "__main__":
    app = QApplication([])
    window = GerenciadorPdf()
    window.show()
    app.exec()
