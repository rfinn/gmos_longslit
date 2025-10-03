#!/usr/bin/env python

from recipe_system import cal_service

caldb = cal_service.set_local_database()

try:
    caldb.init()
except LocalManagerError:
    print("cal database already exists")

# You can manually add processed calibrations with caldb.add_cal(<filename>),
# list the database content with caldb.list_files(), and caldb.remove_cal(<filename>) to remove a file from the database (it will not remove the file on disk.)

# con=mmands from https://dragons.readthedocs.io/projects/gmosls-drtutorial/en/v4.0.0/ex1_gmosls_dithered_api.html

import glob

import astrodata
import gemini_instruments
from recipe_system.reduction.coreReduce import Reduce
from gempy.adlibrary import dataselect

from gempy.utils import logutils
logutils.config(file_name='gmosls_tutorial.log')


# create file lists

all_files = glob.glob('../playdata/example1/*.fits')
all_files.sort()

# create lists of bias frames

# to check which biases are in the directory
detector_roi_setting.

all_biases = dataselect.select_data(all_files, ['BIAS'])
for bias in all_biases:
    ad = astrodata.open(bias)
    print(bias, '  ', ad.detector_roi_setting())


    
