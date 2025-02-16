# image_processor.py
import cv2
import numpy as np
import logging

class ImageProcessor:
    """Classe para processamento avançado de imagens antes do OCR"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Aplica várias técnicas de pré-processamento na imagem"""
        try:
            # Converte para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Remove ruído com filtro bilateral
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Binarização adaptativa
            binary = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Dilatação para melhorar a conectividade dos caracteres
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            processed = cv2.dilate(binary, kernel, iterations=1)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Erro no pré-processamento: {str(e)}")
            raise
    
    def detect_orientation(self, image: np.ndarray) -> float:
        """Detecta a orientação da imagem"""
        try:
            # Detecta bordas
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            
            # Detecta linhas usando transformada de Hough
            lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
            
            if lines is not None:
                angles = []
                for rho, theta in lines[:, 0]:
                    angle = np.degrees(theta)
                    angles.append(angle)
                
                # Calcula o ângulo médio
                mean_angle = np.mean(angles) % 180
                if mean_angle > 90:
                    mean_angle -= 180
                
                return mean_angle
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de orientação: {str(e)}")
            return 0
    
    def correct_skew(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Corrige a inclinação da imagem"""
        try:
            if abs(angle) > 0.5:  # Corrige apenas se a inclinação for significativa
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, M, (w, h),
                                       flags=cv2.INTER_CUBIC,
                                       borderMode=cv2.BORDER_REPLICATE)
                return rotated
            return image
            
        except Exception as e:
            self.logger.error(f"Erro na correção de inclinação: {str(e)}")
            return image
