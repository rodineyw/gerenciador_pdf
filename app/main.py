import os
import sys
import traceback
from PyQt6.QtWidgets import QApplication

# Adicionar o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.gerenciador_pdf import GerenciadorPdf

VERSAO_ATUAL = "1.0.4"  # Atualize aqui sempre que lançar


def main():
    app = QApplication([])
    window = GerenciadorPdf()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("erro_log.txt", "w") as f:
            f.write("Ocorreu um erro inesperado:\n")
            traceback.print_exc(file=f)
        print(f"Erro inesperado: {e}")
