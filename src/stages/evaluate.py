import argparse
import joblib
import json
import pandas as pd
from pathlib import Path
from sklearn.datasets import load_iris
from sklearn.metrics import confusion_matrix, f1_score
from typing import Text, Dict
import yaml

from src.report.visualization import plot_confusion_matrix


def evaluate_model(config_path: Text) -> None:
    
    with open("params.yaml") as config_file:
        config = yaml.safe_load(config_file)
        
    #load model
    print('Load model...')
    model_path = config['model']['model_path']
    model = joblib.load(model_path)
    
    # Get X and Y
    print('Load test dataset...')
    test_dataset = pd.read_csv(config['test']['testset_path'])
    target_column = config['features']['target_column']
    y_test = test_dataset.loc[:, target_column].values.astype('int32')
    X_test = test_dataset.drop(target_column, axis=1).values.astype('float32')
    
    prediction = model.predict(X_test)
    cm = confusion_matrix(prediction, y_test)
    f1 = f1_score(y_true = y_test, y_pred = prediction, average='macro')
    
    print('Build report...')
    report = {
        'f1': f1,
        'cm': cm,
        'actual': y_test,
        'predicted': prediction
    }
    
    print('Save metrics')
    # save f1 metrics file
    reports_folder = Path(config['evaluate']['reports_dir'])
    metrics_path = reports_folder / config['evaluate']['metrics_file']

    json.dump(
        obj={'f1_score': report['f1']},
        fp=open(metrics_path, 'w')
    )

    print(f'F1 metrics file saved to : {metrics_path}')

    print('Save confusion matrix')
    # save confusion_matrix.png
    plt = plot_confusion_matrix(cm=report['cm'],
                                target_names=load_iris(as_frame=True).target_names.tolist(),
                                normalize=False)
    confusion_matrix_png_path = reports_folder / config['evaluate']['confusion_matrix_image']
    plt.savefig(confusion_matrix_png_path)
    print(f'Confusion matrix saved to : {confusion_matrix_png_path}')


if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--config', dest='config', required=True)
    args = args_parser.parse_args()

    evaluate_model(config_path=args.config)