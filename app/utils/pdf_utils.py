import os
import fitz
import subprocess
import shutil
import platform
import pandas as pd

from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

def dividir_pdf(caminho_arquivo, pasta_saida, paginas_por_arquivo=2):
    try:
        # Log para verificar início da função
        print(f"Iniciando divisão do arquivo: {caminho_arquivo}")
        with open(caminho_arquivo, "rb") as arquivo_pdf:
            leitor_pdf = PdfReader(arquivo_pdf)
            num_paginas = len(leitor_pdf.pages)
            # Log do número de páginas
            print(f"Total de páginas no PDF: {num_paginas}")

            for i in range(0, num_paginas, paginas_por_arquivo):
                escritor_pdf = PdfWriter()
                for j in range(paginas_por_arquivo):
                    if i + j < num_paginas:
                        # Log para cada página adicionada
                        print(f"Adicionando página {i + j + 1}")
                        escritor_pdf.add_page(leitor_pdf.pages[i + j])

                nome_arquivo_saida = f"{os.path.splitext(os.path.basename(caminho_arquivo))[
                    0]}_parte_{i // paginas_por_arquivo + 1}.pdf"
                caminho_completo = os.path.join(
                    pasta_saida, nome_arquivo_saida)
                # Log do caminho de saída
                print(f"Salvando parte em: {caminho_completo}")

                with open(caminho_completo, "wb") as arquivo_saida:
                    escritor_pdf.write(arquivo_saida)

                # Log para confirmar que o arquivo foi salvo
                print(f"Arquivo salvo: {caminho_completo}")
    except Exception as e:
        print(f"Erro ao dividir PDF: {e}")


def mesclar_pdfs(lista_arquivos, pasta_saida):
    pdf_writer = PdfWriter()
    arquivos_ignorados = []

    for caminho_do_pdf in lista_arquivos:
        try:
            print(f"Processando: {caminho_do_pdf}")  # Log para depuração

            if not os.path.exists(caminho_do_pdf):
                print(f"Arquivo não encontrado: {caminho_do_pdf}")
                arquivos_ignorados.append(caminho_do_pdf)
                continue

            if os.path.getsize(caminho_do_pdf) == 0:
                print(f"Arquivo vazio: {caminho_do_pdf}")
                arquivos_ignorados.append(caminho_do_pdf)
                continue

            with open(caminho_do_pdf, 'rb') as f:
                pdf_reader = PdfReader(f)
                if len(pdf_reader.pages) == 0:
                    print(f"Arquivo sem páginas válidas: {caminho_do_pdf}")
                    arquivos_ignorados.append(caminho_do_pdf)
                    continue

                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

        except EmptyFileError:
            print(f"Erro de arquivo vazio: {caminho_do_pdf}")
            arquivos_ignorados.append(caminho_do_pdf)
        except Exception as e:
            print(f"Erro ao processar {caminho_do_pdf}: {e}")
            arquivos_ignorados.append(caminho_do_pdf)

    if len(pdf_writer.pages) > 0:
        caminho_saida = os.path.join(pasta_saida, "Documento_Mesclado.pdf")
        try:
            with open(caminho_saida, "wb") as f_out:
                pdf_writer.write(f_out)
            print(f"PDF mesclado salvo em: {caminho_saida}")
        except Exception as e:
            print(f"Erro ao salvar PDF mesclado: {e}")
            arquivos_ignorados.append(caminho_saida)

    return arquivos_ignorados


def renomear_com_texto(lista_arquivos, arquivo_nomes):
    try:
        with open(arquivo_nomes, "r", encoding="utf-8") as file:
            novos_nomes = file.read().splitlines()

        total_files = len(novos_nomes)
        if total_files == len(lista_arquivos):
            for index, novo_nome in enumerate(novos_nomes):
                caminho_arquivo_original = lista_arquivos[index].data(
                    Qt.ItemDataRole.UserRole)[0]
                novo_caminho_arquivo = os.path.join(os.path.dirname(
                    caminho_arquivo_original), novo_nome + os.path.splitext(caminho_arquivo_original)[1])
                os.rename(caminho_arquivo_original, novo_caminho_arquivo)
                lista_arquivos[index] = novo_caminho_arquivo
    except Exception as e:
        print(f"Erro ao renomear arquivos: {str(e)}")
        
        

def renomear_com_excel(widget, lista_arquivos):
    # Seleciona o arquivo Excel
    caminho_excel, _ = QFileDialog.getOpenFileName(
        widget, "Selecionar Arquivo Excel", "", "Excel Files (*.xlsx *.xls)")

    if not caminho_excel:
        return

    try:
        df = pd.read_excel(caminho_excel, engine="openpyxl")

        if df.empty:
            QMessageBox.warning(widget, "Erro", "O arquivo Excel está vazio.")
            return

        colunas = list(df.columns)
        coluna_selecionada, ok = QInputDialog.getItem(
            widget,
            "Selecionar Coluna",
            "Escolha a coluna com os nomes desejados:",
            colunas,
            0,
            False
        )

        if not ok or not coluna_selecionada:
            return

        novos_nomes = df[coluna_selecionada].dropna().astype(str).tolist()

        if len(novos_nomes) != len(lista_arquivos):
            QMessageBox.warning(
                widget,
                "Erro",
                "O número de nomes na coluna não corresponde ao número de arquivos selecionados."
            )
            return

        for index, novo_nome in enumerate(novos_nomes):
            item = lista_arquivos[index]
            caminho_arquivo_original = item.data(Qt.ItemDataRole.UserRole)[0]
            novo_caminho_arquivo = os.path.join(
                os.path.dirname(caminho_arquivo_original),
                novo_nome + os.path.splitext(caminho_arquivo_original)[1]
            )
            os.rename(caminho_arquivo_original, novo_caminho_arquivo)

            # Atualiza o dado na lista
            item.setData(Qt.ItemDataRole.UserRole, (novo_caminho_arquivo, item.data(Qt.ItemDataRole.UserRole)[1]))

        QMessageBox.information(widget, "Sucesso", "Arquivos renomeados com sucesso!")

    except Exception as e:
        QMessageBox.critical(widget, "Erro", f"Erro ao renomear com Excel:\n{str(e)}")


def comprimir_pdf_ghostscript(file_path, output_path, quality_preset='/ebook'):
    """
    Comprime um PDF usando Ghostscript.

    Args:
        file_path (str): Caminho do PDF original.
        output_path (str): Caminho para salvar o PDF comprimido.
        quality_preset (str): Preset de qualidade do Ghostscript.
                               Opções comuns: '/screen', '/ebook', '/printer', '/prepress'.
                               '/ebook' é um bom equilíbrio padrão.

    Returns:
        tuple: (tamanho_original, tamanho_final) se sucesso, (tamanho_original, None) se erro.
               Retorna (None, None) se o arquivo de entrada for inválido.
    """
    tamanho_original = None
    gs_executable = None

    try:
        # --- Validação do Arquivo de Entrada ---
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            print(f"[ERRO GS] Arquivo de entrada não encontrado ou vazio: {file_path}")
            return None, None
        tamanho_original = os.path.getsize(file_path)
        print(f"Tamanho original: {tamanho_original} bytes")

        # --- Encontrar o Executável do Ghostscript ---
        system = platform.system()
        if system == "Windows":
            # Tenta encontrar gswin64c.exe (64 bits) ou gswin32c.exe (32 bits) no PATH
            gs_executable = shutil.which("gswin64c.exe") or shutil.which("gswin32c.exe")
            if not gs_executable:
                 # Se não estiver no PATH, tenta caminhos comuns (AJUSTE SE NECESSÁRIO)
                 common_paths = [
                     "C:\\Program Files\\gs\\gs10.05.0\\bin\\gswin64c.exe", # Exemplo, versão pode mudar!
                     "C:\\Program Files (x86)\\gs\\gs10.05.0\\bin\\gswin32c.exe" # Exemplo
                 ]
                 for path in common_paths:
                     if os.path.exists(path):
                         gs_executable = path
                         break
        else: # Linux ou macOS
            gs_executable = shutil.which("gs")

        if not gs_executable:
            print("[ERRO GS] Executável do Ghostscript não encontrado.")
            print("Verifique se o Ghostscript está instalado e no PATH do sistema.")
            # Retorna erro, mas com tamanho original pra interface poder comparar depois se quiser
            return tamanho_original, None

        print(f"Usando Ghostscript: {gs_executable}")
        print(f"Preset de qualidade: {quality_preset}")

        # --- Montar o Comando Ghostscript ---
        # Referência: https://ghostscript.readthedocs.io/en/latest/Use.html#pdfwrite-parameters
        command = [
            gs_executable,
            "-sDEVICE=pdfwrite",         # Saída será PDF
            "-dCompatibilityLevel=1.4",  # Nível de compatibilidade (pode ajustar)
            f"-dPDFSETTINGS={quality_preset}", # Preset de qualidade/compressão
            "-dNOPAUSE",                 # Não pausar entre páginas
            "-dBATCH",                   # Sair após processar o arquivo
            "-dQUIET",                   # Suprimir mensagens normais (erros ainda aparecem)
            # "-dDetectDuplicateImages=true", # Tenta detectar e compartilhar imagens duplicadas (pode ajudar)
            # "-dCompressFonts=true",       # Tenta comprimir fontes
            # "-dDownsampleColorImages=true", # Habilita downsampling (controlado pelo PDFSETTINGS)
            # "-dColorImageResolution=150", # Exemplo: define resolução se downsampling ativo (padrão varia com preset)
            f"-sOutputFile={output_path}", # Arquivo de saída
            file_path                    # Arquivo de entrada
        ]

        print(f"Executando comando: {' '.join(command)}") # Mostra o comando no console

        # --- Executar o Comando ---
        # Usamos Popen para ter mais controle e capturar stdout/stderr se necessário
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate() # Espera o processo terminar

        # --- Verificar Resultado ---
        if process.returncode == 0:
            # Sucesso! Verifica o tamanho final
            if os.path.exists(output_path):
                tamanho_final = os.path.getsize(output_path)
                print(f"Ghostscript finalizado com sucesso. Tamanho final: {tamanho_final} bytes")
                return tamanho_original, tamanho_final
            else:
                print("[ERRO GS] Ghostscript finalizou sem erros, mas o arquivo de saída não foi encontrado.")
                return tamanho_original, None
        else:
            # Erro! Imprime a saída de erro do Ghostscript
            print(f"[ERRO GS] Ghostscript falhou com código de saída: {process.returncode}")
            if stderr:
                print("--- Saída de Erro do Ghostscript ---")
                print(stderr)
                print("------------------------------------")
            if stdout: # Às vezes infos úteis vão pro stdout mesmo com -dQUIET
                 print("--- Saída Padrão do Ghostscript ---")
                 print(stdout)
                 print("-----------------------------------")
            return tamanho_original, None # Indica falha

    except Exception as e:
        print(f"[ERRO FATAL Python] Falha ao tentar usar Ghostscript: {e}")
        import traceback
        traceback.print_exc()
        # Retorna None no final para indicar erro fatal, mas mantém original se já foi lido
        return tamanho_original if tamanho_original is not None else None, None

    # Não deveria chegar aqui, mas por segurança:
    return tamanho_original, None