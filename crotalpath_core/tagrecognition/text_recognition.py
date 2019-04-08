"""Conjunto reconocedores de textos de crotales que siguen la interfaz definida por TextRecognizer"""
import cv2
import pytesseract
import numpy as np


class TextRecognizer:
    """Interfaz común a seguir por los reconocedores de textos"""

    def recognize_text(self, image: np.array, enclosing_rectangles: np.array) -> str:
        """Reconoce el texto presente en la imagen recibida dentro de cada rectángulo delimitador"""

        raise NotImplementedError()


class ClassicOCR(TextRecognizer):
    """Algoritmo OCR clásico usado para reconocimiento de caracteres"""

    def __init__(self, image_width: int, image_height: int,
                 config: str = '--psm 8 --oem 0 -c tessedit_char_whitelist=0123456789', padding: int = 50):
        """
        Genera una instancia del algoritmo OCR (Tesseract) inicializado con la configuración recibida, por defecto
        la configuración acepta bloques de una sola palabra siendo esta solo dígitos

        :param config: ancho de la imagen donde realizar la proyección
        :param config: alto de la imagen donde realizar la proyección
        :param config: cadena de caracteres de configuración para Tesseract
        :param padding: espacio entre caracteres y caracteres y borde de la imagen donde realizar el reconocimiento
        """
        self.padding = padding
        self.config = config
        self.image_width = image_width
        self.image_height = image_height

    def recognize_text(self, image: np.array, enclosing_rectangles: np.array) -> str:
        """
        Reconoce el texto presente en la imagen recibida dentro de cada rectángulo delimitador

        :param image: imagen donde realizar el reconocimiento
        :param enclosing_rectangles: conjunto de rectangulos que delimitan los caracteres
        :return: una cadena de caracteres con el resultado del reconocimiento, sin espacios
        """

        projected_char_image = self.__align_characters(image, enclosing_rectangles)
        spaced_digits_image = self.__separate_characters(projected_char_image)

        return pytesseract.image_to_string(spaced_digits_image, config=self.config).replace(" ", "")

    def __align_characters(self, image: np.array, char_enclosing_rects: np.array) -> np.array:
        """
        Ajusta la perspectiva de la imagen en base a los rectángulos que engloban los caracteres

        :param image: imagen en escala de grises (1 solo canal)
        :param char_enclosing_rects: array numpy 4xN con las 4 componentes (x, y, ancho, alto) de los rectángulos
        que delimitan cada digito de la imagen de entrada
        :returns: imagen proyectada para ajustarse a los caracteres de la imagen original
        """
        min_char_pos_x = np.min(char_enclosing_rects[:, 0])
        max_char_pos_x_arg = np.argmax(char_enclosing_rects[:, 0])
        max_char_pos_x = char_enclosing_rects[max_char_pos_x_arg, 0] + char_enclosing_rects[max_char_pos_x_arg, 2]

        min_char_pos_y = np.min(char_enclosing_rects[:, 1])
        max_char_pos_y_arg = np.argmax(char_enclosing_rects[:, 1])
        max_char_pos_y = char_enclosing_rects[max_char_pos_y_arg, 1] + char_enclosing_rects[max_char_pos_y_arg, 3]

        cropped_image = image[min_char_pos_y:max_char_pos_y, min_char_pos_x:max_char_pos_x]

        char_enclosing_rects = np.array(
            [np.array([x - min_char_pos_x, y - min_char_pos_y, w, h]) for x, y, w, h in char_enclosing_rects])

        min_arg_x = np.argmin(char_enclosing_rects[:, 0])
        max_char_pos_x_arg = np.argmax(char_enclosing_rects[:, 0])

        corner1_x = int(char_enclosing_rects[min_arg_x, 0])
        corner1_y = int(char_enclosing_rects[min_arg_x, 1])

        corner2_x = int(char_enclosing_rects[max_char_pos_x_arg, 0] +
                        char_enclosing_rects[max_char_pos_x_arg, 2])
        corner2_y = int(char_enclosing_rects[max_char_pos_x_arg, 1])

        corner3_x = corner2_x
        corner3_y = int(char_enclosing_rects[max_char_pos_x_arg, 1] +
                        char_enclosing_rects[max_char_pos_x_arg, 3])

        corner4_x = corner1_x
        corner4_y = int(char_enclosing_rects[min_arg_x, 1] + char_enclosing_rects[min_arg_x, 3])

        source_projection_points = np.float32([[corner1_x, corner1_y], [corner2_x, corner2_y],
                                               [corner3_x, corner3_y], [corner4_x, corner4_y]])

        destination_projection_points = np.float32([[0, 0], [self.image_width, 0],
                                                    [self.image_width, self.image_height], [0, self.image_height]])

        projection_matrix = cv2.getPerspectiveTransform(source_projection_points, destination_projection_points)
        projected_image = cv2.warpPerspective(cropped_image, projection_matrix, (self.image_width, self.image_height))

        return projected_image

    def __separate_characters(self, image: np.array):
        """
        Separa los caracteres presentes en una imagen

        :param image: imagen en blanco y negro (1 canal) donde los caracteres sean de color negro y el fondo blanco
        :returns: imagen con los caracteres espaciados
        """
        structuring_element = np.ones((5, 5), np.uint8)
        deionised_images = cv2.morphologyEx(image, cv2.MORPH_CLOSE, structuring_element)

        structuring_element = np.ones((9, 9), np.uint8)
        image = cv2.morphologyEx(deionised_images, cv2.MORPH_OPEN, structuring_element)

        padded_image = cv2.copyMakeBorder(image, self.padding, self.padding, self.padding, self.padding,
                                          cv2.BORDER_CONSTANT,
                                          None, 255)

        digits_contours, _ = cv2.findContours(~padded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(padded_image, digits_contours, -1, 0, 3)

        digit_enclosing_rects = np.array([cv2.boundingRect(cnt) for cnt in digits_contours])
        sort = np.argsort(digit_enclosing_rects[:, 0])
        digit_enclosing_rects = digit_enclosing_rects[sort]
        result_image = np.ones(
            (
                np.max(digit_enclosing_rects[:, 3]) + (self.padding * 2),
                np.sum(digit_enclosing_rects[:, 2]) + ((len(digit_enclosing_rects) + 1) * self.padding)
            ), np.uint8) * 255

        last_x = 0
        for (x_pos, y_pos, width, height) in digit_enclosing_rects:
            result_image[self.padding:self.padding + height, last_x + self.padding:last_x + self.padding + width] = \
                padded_image[y_pos:y_pos + height, x_pos:x_pos + width]
            last_x = last_x + self.padding + width

        return result_image
