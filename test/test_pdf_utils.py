import os
import subprocess
import platform
import pytest

from PyPDF2 import PdfWriter, PdfReader
from app.utils.pdf_utils import (
    dividir_pdf,
    mesclar_pdfs,
    renomear_com_texto,
    comprimir_pdf_ghostscript
)


def create_pdf(path, num_pages):
    """ Gera um PDF om num_pages páginas em brancoo."""
    writer = PdfWriter()
    for _ in range(num_pages):
        # Cria uma página em brando de tamanho padrão
        writer.add_blank_page(width=72, height=72)
    with open(path, "wb") as f:
        writer.write(f)
        
def test_dividir_pdf(tmp_path):
    # 1) cria um PDF de 5 páginas
    original = tmp_path / "original.pdf"
    create_pdf(str(original), 5)
    
    # 2) chama dividir_pdf com 2 páginas por parte
    out_dr = tmp_path / "parts"
    out_dir.mkdir()
    dividir_pdf(str(original), str(out_dir), paginas_por_arquivo=2)
    
    # 3) espera 3 arquivos: 2+2+1 páginas
    partes = sorted(out_dir.glob("original_parte_*.pdf"))
    assert len(partes) == 3
    
    # 4) verifica contagem de páginas em cada parte
    expected = [2, 2, 1]
    for pdf_file, exp in zip(partes, expected):
        reader = PdfReader(str(pdf_file))
        assert len(reader.pages) == exp
        
        
def test_mesclar_pdfs(tmp_path):
    # 1) cria dois PDFs (2 e 3 Páginas)
    pdf1 = tmp_path / "a.pdf"; create_pdf(str(pdf1), 2)
    pdf2 = tmp_path / "b.pdf"; create_pdf(str(pdf2), 3)
    
    # 2) chama mesclar_pdfs
    out_dir = tmp_path / "merged"
    out_dir.mkdir()
    ignorados = mesclar_pdfs([str(pdf1), str(pdf2)], str(out_dir))
    
    # 3) não deve ignorar nenhum
    assert ignorados == []
    
    # 4) arquivo Documento_mesclado.pdf existe e tem 5 páginas
    merged = out_dr / "Documento_mesclado.pdf"
    assert merged.exists()
    reader = PdfReader(str(merged))
    assert len(reader.pages) == 5
    
    
def test_renomear_com_texto(tmp_path):
    # 1) cria dois arquivos de texto "orig1.txt" e "orig2.txt"
    file1 = tmp_path / "orig1.txt"; file1.write_text("conteúdo1")
    file2 = tmp_path / "orig2.txt"; file2.write_text("conteúdo2")
    
    # 2) cria arquivo de nomes com duas linhas
    names = tmp_path / "nomes.txt"
    names.write_text("novo1\nnovo2")
    
    # 3) simula lista de "itens" com atributo .data()
    class DummyItem:
        def __init__(self, path): self._path = path
        def data(self, role): return (self._path,)
        
    items = [DummyItem(str(file1)), DummyItem(str(file2))]
    
    # 4) chama a função
    renomear_com_texto(items, str(names))
    
    # 5) verifica que os arquivos foram renomeados no FS
    renamed1 = tmp_path / "novo1.txt"
    renamed2 = tmp_path / "novo2.txt"
    assert renamed1.exists() and not file1.exists()
    assert renamed2.exists() and not file2.exists()
    
    # 6) verifica que a lista items foi atualizada para caminhos string
    assert items[0] == str(renamed1)
    assert items[1] == str(renamed2)
    
    
def test_comprimir_pdf_ghostscript_invalid(tmp_path, monkeypatch):
    # 1) arquivo inexiste -> retorna (None, None)
    missing = str(tmp_path / "no.pdf")
    orig, final = comprimir_pdf_ghostscript(missing, str(tmp_path / "out.pdf"))
    assert (orig, final) == (None, None)
    
    # 2) arquivo vazio -> retorna (None, None)
    empty = tmp_path / "empty.pdf"; empty.write_bytes(b"")
    orig2, final2 = comprimir_pdf_ghostscript(str(empty), str(tmp_path / "out2.pdf"))
    assert (orig2, final2) == (None, None)
    
    # 3) simula GS não instalado: força plataforma windows sem gs no PATH
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setenv("PATH", "")
    fake = tmp_path / "fake.pdf"; create_pdf(str(fake), 1)
    orig3, final3 = comprimir_pdf_ghostscript(str(fake), str(tmp_path / "out3.pdf"))
    # original deve ser tamanho do arquivo, final=None
    assert isinstance(orig3, int) and final3 is None