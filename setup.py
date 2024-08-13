import sys
from cx_Freeze import setup, Executable

# Adicionar pacotes e incluir arquivos adicionais
build_exe_options = {
    "packages": ["os", "sys", "fitz", "PyQt6", "pandas", "numpy", "PyPDF2"],
    "includes": [
        "app.utils.pdf_utils",
        "app.utils.gerenciador_pdf",
    ],
    "include_files": ["app/resources/icons/icone_gerenciador.ico"]
}

base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(
    name="Gerenciador PDF",
    version="0.2",
    description="Gerenciador de Arquivos PDF",
    options={"build_exe": build_exe_options},
    executables=[Executable("app/main.py", base=base,
                            icon="app/resources/icons/icone_gerenciador.ico")]
)
