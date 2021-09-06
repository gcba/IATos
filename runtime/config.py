from pathlib import Path
import yaml
from algos.cleansing import CleansingParams
from algos.segmentation import SegmentationParams
from algos.prediction import MelSpecParams, ColorSpecParams

def load_config(yaml_path: str = "config.yml"):
    with open(Path(yaml_path), "r") as file:
        doc = yaml.load(file, Loader=yaml.FullLoader)
        cleansing = CleansingParams(**doc['cleansing'])
        segmentation = SegmentationParams(**doc['segmentation'])
        mel_spec = MelSpecParams(**doc['mel_spec'])
        color_spec = ColorSpecParams(**doc['color_spec'])
        return cleansing, segmentation, mel_spec, color_spec
