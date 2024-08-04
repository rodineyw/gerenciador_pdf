import sys
import pytest
from PyQt6.QtWidgets import QApplication
from app.utils.gerenciador_pdf import GerenciadorPdf


@pytest.fixture
def app(qtbot):
    """Fixture para criar e retornar a aplicação com qtbot."""
    test_app = QApplication(sys.argv)
    window = GerenciadorPdf()
    qtbot.addWidget(window)
    yield window
    # Assegura que o QApplication seja finalizado corretamente após o teste
    test_app.exit()


def test_initial_state(app, qtbot):
    """Teste para verificar o estado inicial da janela."""
    assert app.isVisible() == True  # Verifica se a janela está visível
    # Verifica se a lista de colunas está inicialmente invisível
    assert not app.lista_colunas.isVisible()


def test_button_clicks(app, qtbot):
    """Testa interações com botões."""
    qtbot.mouseClick(app.botao_selecionar, Qt.MouseButton.LeftButton)
    # Verifique mudanças de estado após o clique
