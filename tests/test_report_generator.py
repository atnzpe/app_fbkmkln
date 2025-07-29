# tests/test_report_generator.py

import pytest
import os
import numpy as np
from unittest.mock import patch, MagicMock

from src.report_generator import ReportGenerator


@pytest.fixture
def mock_analysis_data():
    """
    Cria um conjunto de dados de análise falsos para os testes.
    """
    scores = [85.5, 92.1, 78.3, 95.8]
    feedbacks = [
        {"feedback": "Bom"},
        {"feedback": "Ótimo"},
        {"feedback": "Ajuste o quadril"},
        {"feedback": "Excelente movimento!"},
    ]
    mock_image = np.zeros((10, 10, 3), dtype=np.uint8)
    return {
        "scores": scores,
        "feedbacks": feedbacks,
        "frame_aluno_melhor": mock_image,
        "frame_mestre_melhor": mock_image,
        "frame_aluno_pior": mock_image,
        "frame_mestre_pior": mock_image,
    }


@patch("src.report_generator.FPDF")
@patch("src.report_generator.cv2.imwrite")
@patch("src.report_generator.os.remove")
def test_generate_report_success(
    mock_os_remove, mock_imwrite, mock_fpdf_class, mock_analysis_data
):
    """
    Testa o fluxo de sucesso da geração de um relatório PDF.
    """
    mock_pdf_instance = MagicMock()
    mock_fpdf_class.return_value = mock_pdf_instance

    generator = ReportGenerator(**mock_analysis_data)

    output_path = "test_report.pdf"

    success, error = generator.generate(output_path)

    assert success is True
    assert error is None

    assert mock_pdf_instance.add_page.call_count == 2
    assert mock_pdf_instance.cell.call_count > 0
    mock_pdf_instance.output.assert_called_once_with(output_path)

    assert mock_imwrite.call_count == 4
    assert mock_os_remove.call_count == 4
