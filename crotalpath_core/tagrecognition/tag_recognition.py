"""Conjunto reconocedores de crotales que siguen la interfaz definida por TagRecognizer"""
import numpy as np

from crotalpath_core.tagrecognition.tag import Tag, CowTag
from crotalpath_core.tagrecognition.text_location import LargestTextLocator
from crotalpath_core.tagrecognition.text_recognition import ClassicOCR


class TagRecognizer:
    """Interfaz común a seguir por los reconocedores de crotales"""

    def recognize_image(self, image: np.array) -> Tag:
        """Reconoce los caracteres presentes en la imagen del crotal recibida"""
        raise NotImplementedError()


class CowTagRecognizer(TagRecognizer):
    """Reconocedor de los dígitos de los crotales de vacas"""

    def __init__(self):
        """Crea un reconocedor de crotales de vaca"""

        self.ocr = ClassicOCR(image_width=600, image_height=300)
        self.text_locator = LargestTextLocator(thresholding_threshold=30, noise_size=5, digit_difference_threshold=0.3)

    def recognize_image(self, image: np.array) -> Tag:
        """
        Reconoce los dígitos  del crotal recibido

        :param image: una instancia de la clase Tag con la descripción  del crotal a reconocer
        :returns: una instancia de la clase Tag con los resultados del reconocimiento
        """
        tag = CowTag(image)
        image = tag.gray_image
        enclosing_rectangles, digits_only_image = self.text_locator.locate_text(image)
        recognized_digits = self.ocr.recognize_text(digits_only_image, enclosing_rectangles)
        tag.set_detection(text=recognized_digits, bounding_rectangles=enclosing_rectangles)
        return tag
