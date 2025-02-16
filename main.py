# main.py
from config import Config
from ocr_engine import OCREngine
import argparse
from pathlib import Path
import sys
import logging

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ocr.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description='Sistema Inteligente de OCR')
    parser.add_argument('input', help='Caminho da imagem ou diretório de entrada')
    parser.add_argument('--output', '-o', help='Diretório de saída')
    parser.add_argument('--lang', '-l', help='Idiomas para OCR (separados por +)')
    parser.add_argument('--no-preprocessing', action='store_true',
                        help='Desativa o pré-processamento')
    parser.add_argument('--format', '-f', choices=['txt', 'json', 'both'],
                        default='both', help='Formato de saída')
    
    args = parser.parse_args()
    
    try:
        # Inicializa configurações e engine
        config = Config()
        engine = OCREngine(config)
        
        # Prepara caminhos
        input_path = Path(args.input)
        output_dir = Path(args.output) if args.output else config.OUTPUT_DIR
        
        # Define formatos de saída
        formats = ['txt', 'json'] if args.format == 'both' else [args.format]
        
        if input_path.is_file():
            # Processa um único arquivo
            logger.info(f"Processando arquivo: {input_path.name}")
            
            results = engine.process_image(
                input_path,
                lang=args.lang,
                preprocessing=not args.no_preprocessing
            )
            
            saved_files = engine.save_results(
                results,
                output_dir / input_path.stem,
                formats
            )
            
            logger.info("Processamento concluído!")
            for file in saved_files:
                logger.info(f"Arquivo salvo em: {file}")
            
        elif input_path.is_dir():
            # Processa um diretório
            logger.info(f"Processando diretório: {input_path}")
            
            image_files = list(input_path.glob("*.[pj][npj][gg]"))
            for img_path in image_files:
                logger.info(f"Processando: {img_path.name}")
                
                results = engine.process_image(
                    img_path,
                    lang=args.lang,
                    preprocessing=not args.no_preprocessing
                )
                
                saved_files = engine.save_results(
                    results,
                    output_dir / img_path.stem,
                    formats
                )
            
            logger.info("Processamento do diretório concluído!")
            
        else:
            raise ValueError(f"Caminho inválido: {input_path}")
        
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    