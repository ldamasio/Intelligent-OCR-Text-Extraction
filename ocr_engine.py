# ocr_engine.py
from config import Config
from image_processor import ImageProcessor
from typing import Union, Dict, List, Optional
import cv2
import pytesseract
from datetime import datetime
import json
from pathlib import Path

class OCREngine:
    """Classe principal para extração de texto usando OCR"""
    
    def __init__(self, config: Config):
        self.config = config
        self.image_processor = ImageProcessor()
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
        
    def process_image(
        self,
        image_path: Union[str, Path],
        lang: Optional[str] = None,
        preprocessing: bool = True
    ) -> Dict:
        """Processa uma imagem e extrai texto com metadados"""
        try:
            # Carrega a imagem
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
            
            # Pré-processamento
            if preprocessing:
                # Detecta e corrige orientação
                angle = self.image_processor.detect_orientation(image)
                image = self.image_processor.correct_skew(image, angle)
                
                # Aplica técnicas de melhoramento
                processed_image = self.image_processor.preprocess_image(image)
            else:
                processed_image = image
            
            # Configuração do OCR
            custom_config = f"""--oem 3 --psm 3 
                              -l {lang or '+'.join(self.config.LANGUAGES)}"""
            
            # Executa OCR com dados detalhados
            ocr_data = pytesseract.image_to_data(
                processed_image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Filtra resultados por confiança
            confident_text = []
            for i in range(len(ocr_data['text'])):
                confidence = float(ocr_data['conf'][i])
                if confidence >= self.config.MIN_CONFIDENCE:
                    confident_text.append({
                        'text': ocr_data['text'][i],
                        'confidence': confidence,
                        'bbox': {
                            'x': ocr_data['left'][i],
                            'y': ocr_data['top'][i],
                            'w': ocr_data['width'][i],
                            'h': ocr_data['height'][i]
                        },
                        'line_num': ocr_data['line_num'][i],
                        'word_num': ocr_data['word_num'][i]
                    })
            
            # Prepara resultado
            result = {
                'metadata': {
                    'filename': Path(image_path).name,
                    'timestamp': datetime.now().isoformat(),
                    'preprocessing': preprocessing,
                    'orientation_angle': angle if preprocessing else 0,
                    'language': lang or '+'.join(self.config.LANGUAGES)
                },
                'text_blocks': confident_text,
                'full_text': ' '.join([block['text'] for block in confident_text])
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no processamento OCR: {str(e)}")
            raise
    
    def save_results(
        self,
        results: Dict,
        output_path: Union[str, Path],
        formats: List[str] = ['txt', 'json']
    ) -> List[Path]:
        """Salva os resultados do OCR em diferentes formatos"""
        output_path = Path(output_path)
        saved_files = []
        
        try:
            for fmt in formats:
                if fmt == 'txt':
                    # Salva apenas o texto extraído
                    txt_path = output_path.with_suffix('.txt')
                    txt_path.write_text(results['full_text'], encoding='utf-8')
                    saved_files.append(txt_path)
                    
                elif fmt == 'json':
                    # Salva todos os dados incluindo metadados
                    json_path = output_path.with_suffix('.json')
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    saved_files.append(json_path)
            
            return saved_files
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultados: {str(e)}")
            raise
