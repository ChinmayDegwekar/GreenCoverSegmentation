# -*- coding: utf-8 -*-
"""satellite.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1934bVMagMda5s1DGWrFXuO4ifjkqz2qt
"""

# Commented out IPython magic to ensure Python compatibility.
# cd to the folder in drive where this file is present
# %cd drive/My\ Drive/MinorProject/Mask_RCNN/samples/satellite/

import os
import sys
import json
import datetime
import numpy as np
import skimage.draw

ROOT_DIR = os.getcwd()
print(ROOT_DIR)
if ROOT_DIR.endswith("samples/satellite"):
  # Go up two levels to the repo root
  ROOT_DIR = os.path.dirname(os.path.dirname(ROOT_DIR))

print(ROOT_DIR)

# Import Mask RCNN (mrcnn folder)
sys.path.append(ROOT_DIR+"/mrcnn/")
from config import Config
import utils
import model as modellib

# Path to trained weights file
COCO_WEIGHTS_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
print(COCO_WEIGHTS_PATH)

# Directory to save logs and model checkpoints, if not provided
# through the command line argument --logs
DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")
print(DEFAULT_LOGS_DIR)

############################################################
#  Configurations
############################################################


class SatelliteConfig(Config):
  """Configuration for training on the toy  dataset.
  Derives from the base Config class and overrides some values.
  """
  # Give the configuration a recognizable name
  NAME = "satellite"

  # We use a GPU with 12GB memory, which can fit two images.
  # Adjust down if you use a smaller GPU.
  IMAGES_PER_GPU = 2

  # Number of classes (including background)
  NUM_CLASSES = 1 + 3  # Background + {water,built_up,green_cover}

  # Number of training steps per epoch
  STEPS_PER_EPOCH = 100

  # Skip detections with < 90% confidence
  DETECTION_MIN_CONFIDENCE = 0.9

############################################################
#  Dataset
############################################################

class SatelliteDataset(utils.Dataset):

  """  init variables of Dataset
    self._image_ids = []
    self.image_info = []    
    # Background is always the first class
    self.class_info = [{"source": "", "id": 0, "name": "BG"}]
    self.source_class_ids = {}

  """



  def load_satellite(self,dataset_dir,subset):
    """Load a subset of the satellite dataset.
    dataset_dir: Root directory of the dataset.
    type: type to load: train or validation
    """
    # Add classes. We have only three class to add.
    self.add_class("satellite", 1, "water")  #  def add_class(self, source, class_id, class_name):
    self.add_class("satellite", 2, "built_up")
    self.add_class("satellite", 3, "green_cover")

    dataset_dir = os.path.join(dataset_dir, subset)
    # annotations = json.load(open('Anmol/BATCH_1_100_150.json'))
    annotations = json.load(open(os.path.join(dataset_dir, "BATCH_1_100_150.json")))
    images_data = annotations['_via_img_metadata']

    for image_id, image_data in images_data.items():
      regions = image_data['regions']        # regions per image
      image_path = os.path.join(dataset_dir, image_data['filename'])
      width = 500
      height = 500
      # filename : image_data['filename']

      polygons = [r['shape_attributes'] for r in regions]
      # 
      # print(image_data['filename'])
      # Class ids corresponding to each each polygon
      class_ids = [r['region_attributes'][""] for r in regions]
      int_class_ids =[]
      for ci in class_ids:
  #         print(ci)
        if ci == 'greencover':
          int_class_ids.append(3)
        elif ci == 'buildup':
          int_class_ids.append(2)
        else:
          int_class_ids.append(1) # water body




        # add_image(self, source, image_id, path, **kwargs):
      print(image_data['filename'],":added")
      self.add_image( "satellite",
                      image_id = image_data['filename'],
                      path = image_path,
                      width=width, height=height,
                      polygons=polygons,
                      class_ids = int_class_ids)

  def load_mask(self,image_id):
    """Generate instance masks for an image.
    Returns:
    masks: A bool array of shape [height, width, instance count] with
        one mask per instance.
    class_ids: a 1D array of class IDs of the instance masks.
    """
    image_info = self.image_info[image_id]

    # Convert polygons to a bitmap mask of shape
    # [height, width, instance_count]
    info = self.image_info[image_id]

    #length of polygons = number of regions
    mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                    dtype=np.uint8)
    for i, p in enumerate(info["polygons"]):
      # Get indexes of pixels inside the polygon and set them to 1
      rr, cc = skimage.draw.polygon(p['all_points_y'], p['all_points_x'])
      mask[rr, cc, i] = 1

    # Return mask, and array of class IDs of each instance. Since we have
    # one class ID only, we return an array of 1s          #earlier

    # Return mask, and array of class IDs of each instance.
    return mask, info['class_ids']         #np.ones([mask.shape[-1]], dtype=np.int32)

  def image_reference(self, image_id):
    """Return the path of the image."""
    info = self.image_info[image_id]
    if info["source"] == "satellite":
      return info["path"]
    else:
      super(self.__class__, self).image_reference(image_id)

