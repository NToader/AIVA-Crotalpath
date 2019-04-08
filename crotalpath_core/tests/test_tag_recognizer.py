"""Conjuntos de prueba para los reconocedores de crotales"""
import json
from pathlib import Path

import unittest
import numpy as np

from pandas_ods_reader import read_ods

from crotalpath_core.__main__ import TagBatchRecognizer
from crotalpath_core.tagrecognition.tag import NotAFileError


class TagRecognizerTest(unittest.TestCase):
    """Realiza las pruebas a la clase TagRecognizer"""

    @staticmethod
    def parse_ground_truth(ground_truth_path: Path, test_length: int = 500):
        """
        Genera el diccionario de resultados de crotales a partir del fichero 'GroundTruth.ods'

        :param ground_truth_path: la ruta relativa al fichero 'GroundTruth.ods'
        :param test_length: número máximo de elementos a usar en el test, por defecto se usan 500 o el máximo disponible
        :return: diccionario donde cada entrada es el nombre de una imagen y su valor la predicción
        """
        ground_truth = read_ods(ground_truth_path, 1)
        parsed_ground_truth = {}

        for index, row in ground_truth.iterrows():
            image_name = '{:04d}'.format(index + 1) + '.TIF'
            digits = row['Real']
            parsed_ground_truth[image_name] = digits
            if index == (test_length - 1):
                break

        # Invalid images
        parsed_ground_truth.pop('0237.TIF', None)
        parsed_ground_truth.pop('0238.TIF', None)

        return parsed_ground_truth

    @staticmethod
    def intersection_over_union(rect_1, rect_2):
        """
        Calcula la medida IoU entre los dos rectángulos recibidos

        :param rect_1: coordenadas del primer rectángulo en formato OpenCV -> x, y, ancho, alto
        :param rect_2: coordenadas del segundo rectángulo en formato OpenCV -> x, y, ancho, alto
        :return: la media IoU entre los dos rectángulos
        """
        rect_1 = rect_1.copy()
        rect_2 = rect_2.copy()
        rect_1[2] = rect_1[0] + rect_1[2]
        rect_1[3] = rect_1[1] + rect_1[3]
        rect_2[2] = rect_2[0] + rect_2[2]
        rect_2[3] = rect_2[1] + rect_2[3]

        corner1_x = max(rect_1[0], rect_2[0])
        corner1_y = max(rect_1[1], rect_2[1])
        corner2_x = min(rect_1[2], rect_2[2])
        corner2_y = min(rect_1[3], rect_2[3])

        intersection = float(max(0, corner2_x - corner1_x) * max(0, corner2_y - corner1_y))
        area_rect_1 = (rect_1[2] - rect_1[0]) * (rect_1[3] - rect_1[1])
        area_rect_2 = (rect_2[2] - rect_2[0]) * (rect_2[3] - rect_2[1])
        inter_over_union = intersection / (area_rect_1 + area_rect_2 - intersection)

        return inter_over_union

    @classmethod
    def setUpClass(cls):
        """
        Genera y comprueba la existencia de las rutas de las imágenes y directorios a utilizar en los tests. También
        inicializa la instancia de TagRecognizer para su prueba.
        """
        test_dataset_path = Path(Path(__file__).parent / 'dataset')
        ground_truth_path = Path(test_dataset_path) / 'GroundTruth.ods'
        non_valid_base_path = Path(test_dataset_path) / 'WrongNotTestSamples'
        valid_base_path = Path(test_dataset_path) / 'TestSamples'

        test_image_1 = valid_base_path / '0001.TIF'
        test_image_2 = valid_base_path / '0002.TIF'
        test_image_3 = valid_base_path / '0003.TIF'
        test_image_4 = valid_base_path / '0004.TIF'
        test_image_5 = valid_base_path / '0005.TIF'

        folder_paths = [test_dataset_path, valid_base_path]
        file_paths = [test_image_1, test_image_2, test_image_3, test_image_4, test_image_5]

        for folder_path in folder_paths:
            if not folder_path.exists() or not folder_path.is_dir():
                assert False

        for file_path in file_paths:
            if not file_path.exists() or not file_path.is_file():
                assert False

        if non_valid_base_path.exists():
            assert False

        cls.valid_folder_path = str(valid_base_path)
        cls.valid_folder_path_10_images = str(test_dataset_path / 'TestSamples5')
        cls.valid_folder_path_20_images = str(test_dataset_path / 'TestSamples10')

        cls.valid_image_path = str(test_image_1)
        cls.valid_image_path_list = [str(test_image_1)]
        cls.valid_multi_image_path_list = [str(test_image_1), str(test_image_2), str(test_image_3)]

        cls.non_valid_folder_path = str(non_valid_base_path)
        cls.non_valid_image_path = [str(non_valid_base_path / '0001.TIF')]
        cls.some_non_valid_image_path_list = [str(valid_base_path),
                                              str(non_valid_base_path / '0002.TIF'),
                                              str(non_valid_base_path / '0003.TIF')]
        cls.some_non_valid_image_path_list_2 = [str(valid_base_path / '0001.TIF'),
                                                str(non_valid_base_path / '0002.TIF'),
                                                str(non_valid_base_path / '0003.TIF')]
        cls.all_non_valid_image_path_list = [str(non_valid_base_path / '0001.TIF'),
                                             str(non_valid_base_path / '0002.TIF'),
                                             str(non_valid_base_path / '0003.TIF')]

        cls.ground_truth = cls.parse_ground_truth(ground_truth_path, 500)
        cls.valid_images = [{'path': test_image_1,
                             'digits': '0288',
                             'bounding_rects': [[95, 326, 74, 123],
                                                [190, 333, 74, 124],
                                                [291, 338, 72, 124],
                                                [389, 344, 73, 122]]
                             },
                            {'path': test_image_2,
                             'digits': '9926',
                             'bounding_rects': [[126, 270, 73, 125],
                                                [222, 273, 73, 123],
                                                [322, 273, 74, 123],
                                                [421, 273, 72, 125]]
                             },
                            {'path': test_image_3,
                             'digits': '7383',
                             'bounding_rects': [[67, 238, 76, 138],
                                                [150, 242, 69, 139],
                                                [233, 249, 73, 163],
                                                [324, 252, 68, 139]]
                             },
                            {'path': test_image_4,
                             'digits': '0054',
                             'bounding_rects': [[122, 310, 77, 139],
                                                [217, 313, 76, 139],
                                                [313, 316, 73, 140],
                                                [403, 318, 77, 140]]
                             },
                            {'path': test_image_5,
                             'digits': '0055',
                             'bounding_rects': [[89, 293, 77, 137],
                                                [182, 293, 77, 138],
                                                [281, 293, 72, 138],
                                                [375, 292, 72, 138]]
                             }
                            ]

        cls.tag_recognizer = TagBatchRecognizer(recognizer_type=1, display_result=False)

    def test_incorrect_folder_path(self):
        """Prueba con ruta que no es un directorio y con ruta inexistente"""
        self.assertRaises(NotADirectoryError, self.tag_recognizer.recognize_folder, folder_path=self.valid_image_path)
        self.assertRaises(FileNotFoundError, self.tag_recognizer.recognize_folder,
                          folder_path=self.non_valid_folder_path)

    def test_incorrect_method_call(self):
        """Prueba de llamada sin argumentos"""
        self.assertRaises(TypeError, self.tag_recognizer.process_path)

    def test_incorrect_intialization_call(self):
        """Prueba de inicialización del reconocedor con un tipo incorrecto"""
        self.assertRaises(ValueError, TagBatchRecognizer, recognizer_type=9999)

    def test_correct_folder_path(self):
        """Prueba con dos carpetas que contienen 5 y 10 ficheros cada una"""
        tags_result_5 = self.tag_recognizer.process_path(folder_path=self.valid_folder_path_10_images)
        tags_result_5 = json.loads(tags_result_5)
        self.assertEqual(len(tags_result_5), 5)
        for tag in tags_result_5:
            self.assertEqual(len(tag['digits']), 4)
            self.assertEqual(len(tag['bounding_rects']), 4)

        tags_result_10 = self.tag_recognizer.recognize_folder(self.valid_folder_path_20_images)
        self.assertEqual(len(tags_result_10), 10)
        for tag in tags_result_10:
            self.assertEqual(len(tag.digits), 4)
            self.assertEqual(len(tag.bounding_rectangles), 4)

    def test_incorrect_image_path(self):
        """Prueba con rutas de imágenes incorrectas y llamada incorrecta al método"""
        self.assertRaises(TypeError, self.tag_recognizer.recognize_images,
                          images_path=self.valid_image_path)
        self.assertRaises(FileNotFoundError, self.tag_recognizer.recognize_images,
                          images_path=self.some_non_valid_image_path_list_2)
        self.assertRaises(FileNotFoundError, self.tag_recognizer.recognize_images,
                          images_path=self.all_non_valid_image_path_list)
        self.assertRaises(NotAFileError, self.tag_recognizer.recognize_images,
                          images_path=self.some_non_valid_image_path_list)

    def test_correct_image_path(self):
        """
        Prueba de una serie de rutas a imágenes correctas, se comprueba el resultado frente al definido en la prueba
        calculándose la medida IoU y comprobando que esta sea mayor de 0.7. Esta prueba se realiza también en formato
        JSON.
        """
        for test_dict in self.valid_images:
            tag = self.tag_recognizer.recognize_image(test_dict['path'])
            self.assertEqual(tag.digits, test_dict['digits'])
            self.assertEqual(len(tag.bounding_rectangles), len(test_dict['bounding_rects']))
            inter_over_union_results = [self.intersection_over_union(rect, gd_rect) for rect, gd_rect in
                                        zip(tag.bounding_rectangles, test_dict['bounding_rects'])]
            self.assertGreater(np.mean(inter_over_union_results), 0.70)

        for test_dict in self.valid_images:
            json_result = self.tag_recognizer.process_path(images_path=[test_dict['path']])
            tag = json.loads(json_result)[0]
            self.assertEqual(tag['digits'], test_dict['digits'])
            self.assertEqual(len(tag['bounding_rects']), len(test_dict['bounding_rects']))
            inter_over_union_results = [self.intersection_over_union(rect, gd_rect) for rect, gd_rect in
                                        zip(tag['bounding_rects'], test_dict['bounding_rects'])]
            self.assertGreater(np.mean(inter_over_union_results), 0.70)

    def test_correct_image_path_get_detection(self):
        """
        Prueba de una serie de rutas a imágenes correctas, se comprueba que el resultado devuelto por el método
        get_detection sea correcto
        """
        for test_dict in self.valid_images:
            tag = self.tag_recognizer.recognize_image(test_dict['path'])
            tag_result = tag.get_detection()
            self.assertEqual(tag_result['digits'], test_dict['digits'])
            self.assertEqual(len(tag_result['bounding_rects']), len(test_dict['bounding_rects']))

    def test_correct_image_path_export_json(self):
        """
        Prueba de una serie de rutas a imágenes correctas, se comprueba que el resultado devuelto por el método
        export_json sea correcto
        """
        for test_dict in self.valid_images:
            tag = self.tag_recognizer.recognize_image(test_dict['path'])
            tag_result = json.loads(tag.export_json())
            self.assertEqual(tag_result['digits'], test_dict['digits'])
            self.assertEqual(len(tag_result['bounding_rects']), len(test_dict['bounding_rects']))

    def test_ground_truth_accuracy(self):
        """
        Se comprueban las imágenes presentes en el dataset de prueba. Se computa la tasa de acierto y se comprueba que
        esta sea mayor al 0.8 (limite que se definió al proponer el sistema)
        """
        recognized_digits = np.array([])
        ground_truths = np.array([])
        accuracy = 0
        output_msg = 'Tasa de acierto: {} con {} imágenes, ultimo crotal {} reconocido como {}'

        print('Comprobando tasa de acierto:')

        for key in self.ground_truth.keys():
            tag = self.tag_recognizer.recognize_image(str(Path(self.valid_folder_path) / key))

            recognized_digits = np.append(recognized_digits, tag.digits)
            ground_truths = np.append(ground_truths, self.ground_truth[key])

            accuracy = np.sum(recognized_digits == ground_truths) / recognized_digits.shape[0]

            print(output_msg.format(np.round(accuracy, 3),
                                    recognized_digits.shape[0],
                                    self.ground_truth[key],
                                    tag.digits))

        self.assertGreater(accuracy, 0.8)


if __name__ == '__main__':
    unittest.main()
