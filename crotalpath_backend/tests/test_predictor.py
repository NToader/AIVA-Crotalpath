import unittest
from crotalpath_backend.crotales.predictor import Predictor, NotAFileError
from pathlib import Path
import json

TEST_DATA_PATH = str(Path(__file__).parents[3] / 'CrotalesTest')


class PredictorTest(unittest.TestCase):
    def setUp(self):
        test_dataset_path = Path(TEST_DATA_PATH)
        non_valid_base_path = Path(TEST_DATA_PATH) / 'WrongNotTestSamples'
        valid_base_path = Path(TEST_DATA_PATH) / 'TestSamples'
        test_image_1 = valid_base_path / '0001.TIF'
        test_image_2 = valid_base_path / '0002.TIF'
        test_image_3 = valid_base_path / '0003.TIF'

        folder_paths = [test_dataset_path, valid_base_path]
        file_paths = [test_image_1, test_image_2, test_image_3]

        for folder_path in folder_paths:
            if not folder_path.exists() or not folder_path.is_dir():
                assert False

        for file_path in file_paths:
            if not file_path.exists() or not file_path.is_file():
                assert False

        if non_valid_base_path.exists():
            assert False

        self.valid_folder_path = str(valid_base_path)
        self.valid_image_path = str(test_image_1)
        self.valid_image_path_list = [str(test_image_1)]
        self.valid_multi_image_path_list = [str(test_image_1), str(test_image_2), str(test_image_3)]

        self.non_valid_folder_path = str(non_valid_base_path)
        self.non_valid_image_path = [str(non_valid_base_path / '0001.TIF')]
        self.some_non_valid_image_path_list = [str(valid_base_path),
                                               str(non_valid_base_path / '0002.TIF'),
                                               str(non_valid_base_path / '0003.TIF')]
        self.some_non_valid_image_path_list_2 = [str(valid_base_path / '0001.TIF'),
                                                 str(non_valid_base_path / '0002.TIF'),
                                                 str(non_valid_base_path / '0003.TIF')]
        self.all_non_valid_image_path_list = [str(non_valid_base_path / '0001.TIF'),
                                              str(non_valid_base_path / '0002.TIF'),
                                              str(non_valid_base_path / '0003.TIF')]

    def test_no_args(self):
        self.assertRaises(ValueError, Predictor)

    def test_incorrect_arg_number(self):
        self.assertRaises(ValueError, Predictor, folder_path=self.valid_folder_path, images_path=self.valid_image_path)

    def test_incorrect_folder_path(self):
        self.assertRaises(NotADirectoryError, Predictor, folder_path=self.valid_image_path)
        self.assertRaises(FileNotFoundError, Predictor, folder_path=self.non_valid_folder_path)

    def test_correct_folder_path(self):
        predictor = Predictor(folder_path=self.valid_folder_path)
        results = json.loads(predictor.predict())
        self.assertGreater(len(results.keys()), 0)
        self.check_results(results, code_length=4, num_rects=4)

    def test_incorrect_image_path(self):
        self.assertRaises(TypeError, Predictor, images_path=self.valid_image_path)
        self.assertRaises(FileNotFoundError, Predictor, images_path=self.some_non_valid_image_path_list_2)
        self.assertRaises(FileNotFoundError, Predictor, images_path=self.all_non_valid_image_path_list)
        self.assertRaises(NotAFileError, Predictor, images_path=self.some_non_valid_image_path_list)

    def test_correct_image_path(self):
        predictor = Predictor(images_path=self.valid_image_path_list)
        results = json.loads(predictor.predict())
        self.assertEqual(len(results.keys()), len(self.valid_image_path_list))
        self.check_results(results, code_length=4, num_rects=4)

        predictor = Predictor(images_path=self.valid_multi_image_path_list)
        results = json.loads(predictor.predict())
        self.assertEqual(len(results.keys()), len(self.valid_multi_image_path_list))
        self.check_results(results, 4, 4)

    def check_results(self, results, code_length, num_rects):
        for key in results.keys():
            self.assertEqual(len(results[key]['code']), code_length)
            bounding_rects = results[key]['bounding_rects']
            self.assertEqual(len(bounding_rects), num_rects)
            for rect in bounding_rects:
                self.assertEqual(len(rect), 4)


if __name__ == '__main__':
    unittest.main()
