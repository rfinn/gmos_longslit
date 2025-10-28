#!/usr/bin/env python

import glob
import os

from recipe_system import cal_service
import astrodata
import gemini_instruments
from recipe_system.reduction.coreReduce import Reduce
from gempy.adlibrary import dataselect
from gempy.utils import logutils


def display_result(filename):
    display = Reduce()
    display.files = [filename]
    display.recipename = 'display'
    display.runr()


makebias = False
makeflat = False
makearc = False
reduce_standard = False
reduce_science = False

    
caldb = cal_service.set_local_database()
try:
    caldb.init()
except cal_service.localmanager.LocalManagerError: 
    print("cal database already exists")

# You can manually add processed calibrations with caldb.add_cal(<filename>),
# list the database content with caldb.list_files(), and caldb.remove_cal(<filename>) to remove a file from the database (it will not remove the file on disk.)

# commands from https://dragons.readthedocs.io/projects/gmosls-drtutorial/en/v4.0.0/ex1_gmosls_dithered_api.html

logutils.config(file_name='gmosls_tutorial.log')
#logutils.config(file_name='gmosls_VFID5842_NGC5356.log')


# create file lists

all_files = glob.glob('../playdata/example1/*.fits')
#all_files = glob.glob('../raw/*.fits')
all_files.sort()

#########################################################
# CREATE LISTS OF DIFFERENT FILE TYPES
#########################################################

flats = dataselect.select_data(all_files, ['FLAT'])
arcs = dataselect.select_data(all_files, ['ARC'])
stdstar = dataselect.select_data(all_files, ['STANDARD'])
all_science = dataselect.select_data(
    all_files,
    [],
    ['CAL'],
    )

scitarget = dataselect.select_data(
    all_files,
    [],
    ['CAL'],
    dataselect.expr_parser('object=="J2145+0031"')
)

print("#############################")
print("SCIENCE FILES:")
for sci in all_science:
    ad = astrodata.open(sci)
    print(sci, '  ', ad.object())


######################################################
# ADD BAD PIXEL MASKS TO DATABASE
#
# Q: what if you run this multiple times?
######################################################
for bpm in dataselect.select_data(all_files, ['BPM']):
    caldb.add_cal(bpm)
    

if makebias:
    all_biases = dataselect.select_data(all_files, ['BIAS'])    
    for bias in all_biases:
        ad = astrodata.open(bias)
        print(bias, '  ', ad.detector_roi_setting())


    biasstd = dataselect.select_data(
        all_files,
        ['BIAS'],
        [],
        dataselect.expr_parser('detector_roi_setting=="Central Spectrum"')
        )

    biassci = dataselect.select_data(
        all_files,
        ['BIAS'],
        [],
        dataselect.expr_parser('detector_roi_setting=="Full Frame"')
        )
    
    reduce_biasstd = Reduce()
    reduce_biassci = Reduce()
    reduce_biasstd.files.extend(biasstd)
    reduce_biassci.files.extend(biassci)
    reduce_biasstd.runr()
    reduce_biassci.runr()


if makeflat:

    reduce_flats = Reduce()
    reduce_flats.files.extend(flats)
    reduce_flats.uparms = dict([('interactive', True)])
    reduce_flats.runr()

if makearc:
    
    reduce_arcs = Reduce()
    reduce_arcs.files.extend(arcs)
    reduce_arcs.uparms = dict([('interactive', True)])
    reduce_arcs.runr()

if reduce_standard:
    reduce_std = Reduce()
    reduce_std.files.extend(stdstar)
    reduce_std.uparms = dict([('interactive', True)])
    reduce_std.runr()

if reduce_science:
    
    display_1d = True
    
    reduce_science = Reduce()
    reduce_science.files.extend(scitarget)
    reduce_science.runr()

    # construct name of output file
    output_rootname = os.path.basename(scitarget[0])
    print("guess for the name of the 2D spectrum is: ", output_rootname.replace('.fits','_2D.fits'))
    spectrum_2d = output_rootname.replace('.fits','_2D.fits')
    spectrum_1d = output_rootname.replace('.fits','_1D.fits')    
    try:
        display_result(spectrum_2d)
    except:
        print("Problem displaying result")



    if display_1d:
        from gempy.adlibrary import plotting
        import matplotlib.pyplot as plt

        ad = astrodata.open(reduce_science.output_filenames[0])
        plt.ioff()
        plotting.dgsplot_matplotlib(ad, 1)
        plt.ion()


        writeascii = Reduce()
        writeascii.files = [spectrum_1d]
        writeascii.recipename = 'write1DSpectra'
        writeascii.runr()
