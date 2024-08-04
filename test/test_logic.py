from unittest.mock import patch, MagicMock, mock_open
from app.utils import pdf_utils


def test_process_pdf():
    with patch('PyPDF2.PdfReader') as mock_reader:
        mock_reader.return_value.pages = [MagicMock()] * 5
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            pdf_utils.process_pdf('fake_path.pdf', 'fake_output')
            assert mock_file.call_count == 6


def test_merge_pdfs():
    with patch('PyPDF2.PdfWriter') as mock_writer:
        writer_instance = mock_writer.return_value
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_reader.return_value.pages = [MagicMock()]
            with patch('builtins.open', new_callable=mock_open) as mock_file:
                pdf_utils.merge_pdfs(['fake1.pdf', 'fake2.pdf'], 'fake_output')
                assert writer_instance.write.called
                assert mock_file.call_count == 3
