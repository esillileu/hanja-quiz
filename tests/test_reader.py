import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.reader import read_file, read_text_file, read_pdf_file

def test_read_text_file():
    mock_content = "Hello Hanja"
    with patch("builtins.open", mock_open(read_data=mock_content)):
        result = read_text_file("dummy.txt")
        assert result == mock_content

def test_read_pdf_file():
    # Mock PdfReader and its pages
    with patch("src.reader.PdfReader") as MockPdfReader:
        mock_reader_instance = MockPdfReader.return_value
        
        page1 = MagicMock()
        page1.extract_text.return_value = "Page 1 Content"
        
        page2 = MagicMock()
        page2.extract_text.return_value = "Page 2 Content"
        
        mock_reader_instance.pages = [page1, page2]
        
        result = read_pdf_file("dummy.pdf")
        assert "Page 1 Content" in result
        assert "Page 2 Content" in result

def test_read_file_dispatch():
    with patch("src.reader.read_text_file") as mock_txt, \
         patch("src.reader.read_pdf_file") as mock_pdf:
        
        mock_txt.return_value = "txt"
        mock_pdf.return_value = "pdf"
        
        assert read_file("test.txt") == "txt"
        assert read_file("test.pdf") == "pdf"
        
        with pytest.raises(ValueError):
            read_file("test.doc")

