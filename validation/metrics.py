import csv

import numpy as np

from pathlib import Path
from pandas_ods_reader import read_ods

from crotalpath_core.__main__ import TagBatchRecognizer


def write_csv(path, content):
    with open(path, 'a', newline='') as file:
        file.write(content+'\n')
    file.close()


def parse_ground_truth(ground_truth_path: Path, test_length: int = 500):
    """
    Genera el dicionario de resultados de crotales a partir del fichero "GroundTruth.ods"

    :param ground_truth_path:
    :param test_length:
    :return:
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


if __name__ == '__main__':
    tag_recognizer = TagBatchRecognizer(recognizer_type=1, display_result=False)
    images_path = Path('../crotalpath_core/tests/dataset/TestSamples')
    ground_truth = parse_ground_truth(Path('../crotalpath_core/tests/dataset/GroundTruth.ods'), 500)
    output_metrics_path = './metrics.csv'
    metrics = {'true_positive': 0, 'true_negative': 0, 'false_positive': 0, 'false_negative': 0}
    precision = []
    recall = []
    write_csv(output_metrics_path, 'precision,recall,TP,FP,TN,FN')
    for key in ground_truth.keys():
        tag = tag_recognizer.recognize_image(str(images_path / key))
        if len(tag.digits) == len(ground_truth[key]):
            print('{} {}'.format(tag.digits, ground_truth[key]))
            if tag.digits == ground_truth[key]:
                metrics['true_positive'] += 1
            else:
                metrics['false_positive'] += 1
        else:
            metrics['false_negative'] += 1
        precision = round(metrics['true_positive'] / (metrics['true_positive'] + metrics['false_positive']), 3)
        recall = round((metrics['true_positive'] + metrics['false_positive']) / len(ground_truth), 3)
        write_csv(output_metrics_path, '{},{},{},{},{},{}'.format(precision, recall, metrics['true_positive'],
                                                                  metrics['false_positive'], metrics['true_negative'],
                                                                  metrics['false_negative']))
        print('precision: {} recall:{} metrics: {}'.format(precision, recall, metrics))
