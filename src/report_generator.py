# src/report_generator.py

import logging
import os
from datetime import datetime
import numpy as np
from fpdf import FPDF
import cv2
from src.utils import get_logger

logger = get_logger(__name__)

class PDF(FPDF):
    # ... (código inalterado) ...
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Relatório de Análise de Movimento - Krav Maga', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

class ReportGenerator:
    """
    Gera um relatório de análise em PDF com destaques visuais e detalhes de ângulo.
    """
    
    def __init__(self, scores, feedbacks, frame_aluno_melhor, frame_mestre_melhor, 
                 frame_aluno_pior, frame_mestre_pior, best_angle_diffs, worst_angle_diffs, key_angles_map):
        self.scores = [s for s in scores if s is not None]
        self.feedbacks = feedbacks
        self.frame_aluno_melhor = frame_aluno_melhor
        self.frame_mestre_melhor = frame_mestre_melhor
        self.frame_aluno_pior = frame_aluno_pior
        self.frame_mestre_pior = frame_mestre_pior
        # NOVOS DADOS: Diferenças de ângulo e mapa de nomes para a tabela
        self.best_angle_diffs = best_angle_diffs
        self.worst_angle_diffs = worst_angle_diffs
        self.key_angles_map = key_angles_map

        self.pdf = PDF()
        logger.info("ReportGenerator inicializado com dados detalhados de ângulo.")

    # ... (_add_section_title e _add_summary inalterados) ...
    def _add_section_title(self, title):
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, title, 0, 1, 'L')
        self.pdf.line(self.pdf.get_x(), self.pdf.get_y(), self.pdf.get_x() + 190, self.pdf.get_y())
        self.pdf.ln(5)

    def _add_summary(self):
        self._add_section_title('Resumo de Performance')
        avg_score, max_score, min_score = (np.mean(self.scores), np.max(self.scores), np.min(self.scores)) if self.scores else (0, 0, 0)
        self.pdf.set_font('Arial', '', 11)
        self.pdf.cell(0, 8, f'Pontuação Média de Similaridade: {avg_score:.2f}%', 0, 1, 'L')
        self.pdf.cell(0, 8, f'Melhor Pontuação (Destaque): {max_score:.2f}%', 0, 1, 'L')
        self.pdf.cell(0, 8, f'Pior Pontuação (Ponto de Melhoria): {min_score:.2f}%', 0, 1, 'L')
        self.pdf.ln(10)

    def _add_moment_analysis(self, title, score, feedback, frame_aluno, frame_mestre, angle_diffs, temp_suffix):
        """Função genérica para adicionar uma seção de análise de momento (melhor ou pior)."""
        self._add_section_title(title)
        self.pdf.set_font('Arial', '', 11)
        self.pdf.multi_cell(0, 8, f'Com uma pontuação de {score:.2f}%, o feedback geral foi: "{feedback}".', 0, 'L')
        self.pdf.ln(5)

        self._add_comparison_images(frame_aluno, frame_mestre, temp_suffix)
        self._add_angle_details_table(angle_diffs)
        self.pdf.ln(10)
    
    def _add_comparison_images(self, frame_aluno, frame_mestre, temp_suffix):
        # ... (código inalterado) ...
        temp_aluno_path = f'temp_aluno_{temp_suffix}.png'
        temp_mestre_path = f'temp_mestre_{temp_suffix}.png'
        try:
            cv2.imwrite(temp_aluno_path, frame_aluno)
            cv2.imwrite(temp_mestre_path, frame_mestre)
            
            if self.pdf.get_y() > 150:
                self.pdf.add_page()

            image_y_pos = self.pdf.get_y()
            self.pdf.image(temp_aluno_path, x=25, y=image_y_pos, w=75)
            self.pdf.image(temp_mestre_path, x=110, y=image_y_pos, w=75)
            
            img_height = 75 * frame_aluno.shape[0] / frame_aluno.shape[1]
            self.pdf.ln(img_height + 5)
            
            self.pdf.set_font('Arial', 'I', 9)
            self.pdf.set_x(25)
            self.pdf.cell(75, 10, 'Sua Execução (Aluno)', 0, 0, 'C')
            self.pdf.set_x(110)
            self.pdf.cell(75, 10, 'Execução de Referência (Mestre)', 0, 1, 'C')
            self.pdf.ln(5)
        finally:
            if os.path.exists(temp_aluno_path): os.remove(temp_aluno_path)
            if os.path.exists(temp_mestre_path): os.remove(temp_mestre_path)

    def _add_angle_details_table(self, angle_diffs, threshold=15.0):
        """Adiciona uma tabela ao PDF com o status de cada ângulo (Correto/A Melhorar)."""
        if not angle_diffs: return
        
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, "Detalhes por Articulação:", 0, 1, 'L')
        
        # Cabeçalho da tabela
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(60, 8, 'Articulação', 1, 0, 'C')
        self.pdf.cell(40, 8, 'Diferença', 1, 0, 'C')
        self.pdf.cell(40, 8, 'Status', 1, 1, 'C')

        # Linhas da tabela
        self.pdf.set_font('Arial', '', 10)
        for angle_name, diff in sorted(angle_diffs.items()): # Ordena para consistência
            readable_name = self.key_angles_map.get(angle_name, angle_name)
            status = "Correto" if diff <= threshold else "A Melhorar"
            
            self.pdf.cell(60, 8, readable_name, 1, 0, 'L')
            self.pdf.cell(40, 8, f'{diff:.2f}°', 1, 0, 'C')
            
            # Define a cor do texto para o status
            if status == "Correto":
                self.pdf.set_text_color(0, 150, 0) # Verde escuro
            else:
                self.pdf.set_text_color(220, 50, 50) # Vermelho
                
            self.pdf.cell(40, 8, status, 1, 1, 'C')
            self.pdf.set_text_color(0, 0, 0) # Reseta para preto

    def generate(self, output_path):
        """Gera e salva o arquivo PDF completo."""
        try:
            logger.info(f"Gerando PDF para: {output_path}")
            self.pdf.add_page()
            self._add_summary()

            if self.scores:
                best_score_index = np.argmax(self.scores)
                worst_score_index = np.argmin(self.scores)
                
                self._add_moment_analysis(
                    'Destaque da Sessão (Melhor Execução)',
                    self.scores[best_score_index],
                    self.feedbacks[best_score_index]['feedback'],
                    self.frame_aluno_melhor,
                    self.frame_mestre_melhor,
                    self.best_angle_diffs,
                    'melhor'
                )
                
                self.pdf.add_page()

                self._add_moment_analysis(
                    'Ponto de Melhoria (Pior Execução)',
                    self.scores[worst_score_index],
                    self.feedbacks[worst_score_index]['feedback'],
                    self.frame_aluno_pior,
                    self.frame_mestre_pior,
                    self.worst_angle_diffs,
                    'pior'
                )
            
            self.pdf.output(output_path)
            logger.info(f"Relatório PDF gerado com sucesso em: {output_path}")
            return True, None
        except Exception as e:
            logger.error(f"Falha ao gerar o relatório PDF: {e}", exc_info=True)
            return False, str(e)