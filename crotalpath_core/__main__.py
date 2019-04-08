"""Alberga el punto de entrada al paquete Crotalpath"""
from pathlib import Path
from typing import List

import cv2

from crotalpath_core.tagrecognition.tag import Tag, NotAFileError
from crotalpath_core.tagrecognition.tag_recognition import CowTagRecognizer

RECOGNIZER_TYPES = {1: {'recognizer': CowTagRecognizer, 'description': 'Cow recognizer'}}


class TagBatchRecognizer:
    """Reconocedor de crotales destinado a procesar conjuntos de estos"""

    def __init__(self, recognizer_type: int, display_result: bool = False):
        """
        Crea una instancia del reconocedor de conjuntos de crotales que utilizara un reconocedor concreto

        :param recognizer_type: identificador del tipo de reconocedor de crotales a usar
        :param display_result: indicador que determina si mostrar o no el resultado del reconocimiento
        """
        if recognizer_type not in RECOGNIZER_TYPES:
            recognizer_types = [
                '{} - {}'.format(recognizer_type_key, RECOGNIZER_TYPES[recognizer_type_key]['description']) for
                recognizer_type_key in RECOGNIZER_TYPES.keys()]
            raise ValueError('Recognizer type not available, try one of: {}'.format(recognizer_types))

        self.display_result = display_result
        self.recognizer = RECOGNIZER_TYPES[recognizer_type]['recognizer']()

    def process_path(self, folder_path: str = None, images_path: List[str] = None) -> str:
        """
        Realiza el reconocimiento de todas las imágenes presentes en una carpeta o de todas las rutas a imágenes
        recibida

        :param folder_path: ruta relativa de la carpeta con imágenes a reconocer
        :param images_path: ruta relativa a cada imagen a reconocer
        :returns: cadena de caracteres en formado JSON con el resultado del reconocimiento
        :raises TypeError: si la ruta indicada no existe
        """
        if folder_path is not None:
            recognized_tags = self.recognize_folder(folder_path)
        elif images_path is not None:
            recognized_tags = self.recognize_images(images_path)
        else:
            raise TypeError('No args have been passed')

        result_json = [tag.export_json() for tag in recognized_tags]
        return '[' + ','.join(result_json) + ']'

    def recognize_folder(self, folder_path: str) -> List[Tag]:
        """
        Realiza el reconocimiento de todas las imágenes presentes en una carpeta

        :param folder_path: ruta relativa de la carpeta con imágenes a reconocer
        :returns: lista de objetos Tag con el resultado de cada reconocimiento
        :raises NotADirectoryError: si la ruta indicada no es un directorio
        :raises FileNotFoundError: si la ruta indicada no existe
        """
        input_dataset_path = Path(folder_path)

        if input_dataset_path.exists() and input_dataset_path.is_dir():
            dataset_images_path = [str(img_path) for img_path in input_dataset_path.glob('*.*')]
        elif not input_dataset_path.exists():
            raise FileNotFoundError('Specified data path does not exist: ' + str(input_dataset_path))
        else:
            raise NotADirectoryError('Specified data path is not a directory:  ' + str(input_dataset_path))

        return self.recognize_images(dataset_images_path)

    def recognize_images(self, images_path: List[str]) -> List[Tag]:
        """
        Realiza el reconocimiento de todas las rutas de las imágenes recibidas

        :param images_path: lista con las rutas de las imágenes a reconocer
        :returns: lista de objetos Tag con el resultado de cada reconocimiento
        :raises NotAFileError: si alguna de las rutas indicadas no es un fichero
        :raises FileNotFoundError: si alguna de las rutas indicadas no existe
        :raise TypeError: si el argumento recibido no es una lista
        """
        if isinstance(images_path, list):
            input_paths = [Path(path) for path in images_path]
        else:
            raise TypeError('Image(s) path must be a list.')

        tags = []
        for path in input_paths:
            recognized_tag = self.recognize_image(path)
            recognized_tag.identifier = path
            if self.display_result:
                recognized_tag.show_result_window()
            tags.append(recognized_tag)

        return tags

    def recognize_image(self, image_path: str) -> Tag:
        """
        Realiza el reconocimiento de la ruta de las imágene recibida

        :param image_path: ruta de la imagen a reconocer
        :returns: objeto Tag con el resultado del reconocimiento
        :raises NotAFileError: si la ruta indicada no es un fichero
        :raises FileNotFoundError: si la ruta indicada no existe
        """
        image_path = Path(image_path)
        recognized_tag = None

        if image_path.is_file():
            image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            recognized_tag = self.recognizer.recognize_image(image)
        elif not image_path.exists():
            raise FileNotFoundError('Specified image path does not exist: ' + str(image_path))
        elif not image_path.is_file():
            raise NotAFileError('Specified image path is not a file: ' + str(image_path))

        return recognized_tag


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_path", type=str, help='Relative path to the output file.')
    parser.add_argument("-t", "--type", type=int, required=True, help='Tag type. 1 - Cow')
    parser.add_argument("-d", "--display_result", dest='display_result', action='store_true',
                        help='If stated the result of each recognized tag will be shown.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--images", nargs='+', help='One or more images relative path to recognize.')
    group.add_argument("-f", "--folder", type=str, help='Relative folder path with images to recognize.')
    kwargs = parser.parse_args()

    tag_batch_recognizer = TagBatchRecognizer(recognizer_type=kwargs.type, display_result=kwargs.display_result)
    result = tag_batch_recognizer.process_path(kwargs.folder, kwargs.images)

    output_file = open(kwargs.output_path, "w")
    output_file.write(result)
    output_file.close()
