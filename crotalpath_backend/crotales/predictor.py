from pathlib import Path
import sys
from random import randint
import numpy as np
import json


class NotAFileError(Exception):
    pass


class Predictor:
    def __init__(self, images_path=None, folder_path=None):
        if images_path is not None and folder_path is not None:
            raise ValueError('Both file(s) path and folder path specified, only one of them is accepted.')

        elif images_path is not None:
            if isinstance(images_path, list):
                self.input_paths = [Path(path) for path in images_path]
            else:
                raise TypeError('Image(s) path must be a list.')

        elif folder_path is not None:
            input_dataset_path = Path(folder_path)

            if input_dataset_path.exists() and input_dataset_path.is_dir():
                self.input_paths = [img_path for img_path in input_dataset_path.glob('*.*')]

            elif not input_dataset_path.exists():
                raise FileNotFoundError('Specified data path does not exist.')

            else:
                raise NotADirectoryError('Specified data path is not a directory.')

        else:
            raise ValueError('Neither file(s) path nor folder path were specified.')

        for path in self.input_paths:
            if not path.exists():
                raise FileNotFoundError('Specified image path does not exist.')

            elif not path.is_file():
                raise NotAFileError('Specified image path is not a file.')

    def predict(self):
        output = {}
        for path in self.input_paths:
            output[path.name] = {}
            output[path.name]['code'] = '{}{}{}{}'.format(randint(0, 9), randint(0, 9), randint(0, 9), randint(0, 9))
            output[path.name]['bounding_rects'] = [rect.tolist() for rect in
                                                   np.split(np.random.randint(400, size=16), 4)]
        return json.dumps(output)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--image", nargs='+')
    group.add_argument("-f", "--folder", type=str)
    kwargs = parser.parse_args()

    predictor = Predictor(kwargs.image, kwargs.folder)
    result = predictor.predict()

    sys.stdout.write(result)
    sys.stdout.flush()
    sys.exit(0)
