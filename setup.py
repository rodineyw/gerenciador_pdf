import sys
from cx_Freeze import setup, Executable

# Pacotes adicionais para incluir
build_exe_options = {
    "packages": ["os", "sys", "fitz", "PyQt6", "pandas", "numpy", "PyPDF2", "requests"], 
    "includes": [
        "app.utils.pdf_utils",
        "app.utils.gerenciador_pdf",
        "app.utils.autoatualizador",
        "requests"
    ],
    "include_files": [
        "app/resources/icons/icone_gerenciador.ico",
        "gs/"
    ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Gerenciador PDF",
    version="1.1.4",
    description="Gerenciador de Arquivos PDF",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "app/main.py",
            base=base,
            target_name="Gerenciador PDF.exe",
            icon="app/resources/icons/icone_gerenciador.ico"
        )
    ]
)