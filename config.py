# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    # Diretórios do projeto
    BASE_DIR = Path(__file__).parent
    INPUT_DIR = BASE_DIR / "input"
    OUTPUT_DIR = BASE_DIR / "output"
    TEMP_DIR = BASE_DIR / "temp"
    
    # Configurações de OCR
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", "tesseract")
    LANGUAGES = ["por", "eng"]  # Idiomas suportados
    
    # Configurações de pré-processamento
    DEFAULT_DPI = 300
    MIN_CONFIDENCE = 60  # Porcentagem mínima de confiança
    
    def __init__(self):
        # Cria diretórios necessários
        self.INPUT_DIR.mkdir(exist_ok=True)
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.TEMP_DIR.mkdir(exist_ok=True)
