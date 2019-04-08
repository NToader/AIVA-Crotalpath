"""Conjunto de detectores de texto en imágenes de crotales que siguen la interfaz definida por TextLocator"""
import cv2
import numpy as np


class TextLocator:
    """Interfaz común a seguir por los detectores de texto"""

    def locate_text(self, image: np.array) -> tuple:
        """Detecta el texto de una imagen y devuelve su localización junto con la imagen postprocesada"""

        raise NotImplementedError()


class LargestTextLocator(TextLocator):
    """Detector de texto especializado en la detección de los caracteres de mayor tamaño de una imagen"""

    def __init__(self, thresholding_threshold, noise_size, digit_difference_threshold):
        """
        Crea un reconocedor de los caracteres de mayor tamaño de una imagen

        :param thresholding_threshold: valor de intensidad límite para la umbralización
        :param noise_size: tamaño del ruido esperando en la imagen
        :param digit_difference_threshold: ratio de diferencia entre los digitos a localizar
        """
        self.thresholding_threshold = thresholding_threshold
        self.noise_size = noise_size
        self.digit_difference_threshold = digit_difference_threshold
        self.structuring_element = np.ones((self.noise_size, self.noise_size), np.uint8)

    def locate_text(self, image: np.array) -> tuple:
        """
        Detecta el texto de una imagen y devuelve su localización

        :param image: imagen donde realizar la detección
        :returns: una tupla formada por los rectángulos que delimitan los caracteres y la imagen postprocesada donde se
        ha realizado esta localización
        """
        tag_foreground_mask = self.__get_tag_mask(image)
        digits_only_image = self.__remove_background(image=image, tag_mask=tag_foreground_mask)
        enclosing_rectangles = self.__locate_largest_text(digits_only_image)

        return enclosing_rectangles, digits_only_image

    def __get_tag_mask(self, image: np.array) -> np.array:
        """
        Umbraliza la imagen y aplica operaciones morfológicas de cierre y apertura para eliminar imperfecciones

        :param image: imagen en escala de grises (1 solo canal)
        :returns: una máscara con la zona del crotal a True y el fondo a False
        """
        _, binary_image = cv2.threshold(image, self.thresholding_threshold, 1, cv2.THRESH_BINARY)

        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, self.structuring_element)
        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, self.structuring_element)

        return binary_image.astype(np.bool)

    def __remove_background(self, image: np.array, tag_mask: np.array) -> np.array:
        """
        Elimina todos los elementos de la imagen a excepción de los caracteres que sean de mayor tamaño al elemento
        estructurante

        :param image: imagen en escala de grises (1 solo canal)
        :param tag_mask: una máscara con la zona del crotal a True y el fondo a False
        :returns: una imagen en blanco (255) y negro (0) con los caracteres presentes en la imagen original
        """
        image = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(19, 19)).apply(image)

        _, binary_image = cv2.threshold(image, self.thresholding_threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        binary_image[~tag_mask] = 255
        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, self.structuring_element)

        return binary_image

    def __locate_largest_text(self, image: np.array) -> np.array:
        """
        Localiza los caracteres de mayor tamaño presentes en una imagen

        :param image: imagen en blanco y negro siendo los caracteres los elementos de mayor tamaño
        tamaño respecto al de menor tamaño, en un rango de 0 a 1
        :returns: un numpy arrau con los rectángulos que engloban a los caracteres candidatos
        """
        image_objects_contour, _ = cv2.findContours(~image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        binary_image = ~image / 255

        object_enclosing_rect = [cv2.boundingRect(contour) for contour in image_objects_contour]
        object_areas = [np.sum(binary_image[y:y + h, x:x + w]) for x, y, w, h in object_enclosing_rect]

        max_object_area = np.max(object_areas)
        max_object_area_index = np.argmax(object_areas)

        biggest_object_enclosing_rect = object_enclosing_rect[max_object_area_index]

        normalized_object_areas = (object_areas - np.min(object_areas)) / (max_object_area - np.min(object_areas))
        digit_candidate_index = normalized_object_areas > self.digit_difference_threshold

        digit_enclosing_rects = []
        for digit_enclosing_rect in np.array(object_enclosing_rect)[digit_candidate_index]:
            if abs(digit_enclosing_rect[1] - biggest_object_enclosing_rect[1]) < biggest_object_enclosing_rect[3] / 3:
                digit_enclosing_rects.append(digit_enclosing_rect)

        return np.array(digit_enclosing_rects)
