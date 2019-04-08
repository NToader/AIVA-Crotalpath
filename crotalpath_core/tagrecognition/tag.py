"""Conjunto de clases que definen los componentes de un crotal, siguiendo la interfaz Tag"""
import json
import cv2
import numpy as np


class NotAFileError(Exception):
    """Excepción que indica que no la ruta no es un fichero"""


class Tag:
    """Interfaz común a seguir por los descriptores de crotales"""

    def set_detection(self, text: str, bounding_rectangles: np.array)-> None:
        """Añade los datos del reconocimiento del crotal y sus rectángulos delimitadores"""

        raise NotImplementedError()

    def get_detection(self) -> dict:
        """Exporta la descripción del crotal"""

        raise NotImplementedError()

    def export_json(self) -> str:
        """Exporta una secuencia de caracteres con la descripción del crotal en formato JSON"""

        raise NotImplementedError()

    def show_result_window(self) -> None:
        """Muestra el resultado del reconocimiento en una ventana"""

        raise NotImplementedError()


class CowTag(Tag):
    """Alberga la imagen de un tag y su predicción"""

    def __init__(self, image: np.array):
        """
        Crea un descriptor de crotales de vaca inicializado con la imagen recibida

        :param image: imagen en color (3 canales) en forma de numpy array
        """
        self.identifier = None
        self.image = image
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.digits = None
        self.bounding_rectangles = None

    def set_detection(self, text: str, bounding_rectangles: np.array):
        """
        Añade los datos del reconocimiento del crotal y sus rectángulos delimitadores

        :param text: dígitos que contiene la imagen del crotal
        :param bounding_rectangles: rectángulos delimitadores de los dígitos de la imagen del crotal
        """
        self.digits = text
        self.bounding_rectangles = bounding_rectangles[bounding_rectangles[:, 0].argsort()].tolist()

    def get_detection(self) -> dict:
        """
        Devuelve la descripción del crotal

        :returns: la descripción del crotal en formado diccionario con los digitos (digits), los rectángulos
        ('bounding_rects') y el identificador ('identifier')
        """
        output = {'digits': self.digits,
                  'bounding_rects': self.bounding_rectangles,
                  'identifier': str(self.identifier)}
        return output

    def export_json(self) -> str:
        """
        Exporta la detección a una cadena de caracteres en format JSON. Los dígitos estarán en la clave 'digits' y los
        rectángulos, que engloban a estos, en la clave 'bounding_rects' y el identificador en la clave 'identifier'

        :returns: la cadena de caracteres con información del crotal en formato JSON
        """
        return json.dumps(self.get_detection())

    def show_result_window(self):
        """Muestra el resultado del reconocimiento en una ventana de OpenCV con el resultado como titulo de ventana"""

        if self.digits is not None and self.image is not None and self.bounding_rectangles is not None:
            shown_image = self.image.copy()
            for rect in self.bounding_rectangles:
                cv2.rectangle(shown_image, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3)
            cv2.imshow(self.digits, shown_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
