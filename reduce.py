#!/usr/bin/env python

import glob
import os
import sys

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



def reduceall(args):

    caldb = cal_service.set_local_database()
    try:
        caldb.init()
    except cal_service.localmanager.LocalManagerError: 
        print("cal database already exists")

    # You can manually add processed calibrations with caldb.add_cal(<filename>),
    # list the database content with caldb.list_files(), and caldb.remove_cal(<filename>) to remove a file from the database (it will not remove the file on disk.)

    # commands from https://dragons.readthedocs.io/projects/gmosls-drtutorial/en/v4.0.0/ex1_gmosls_dithered_api.html

    #logutils.config(file_name='gmosls_tutorial.log')
    logutils.config(file_name='gmosls_VFID5842_NGC5356.log')


    # create file lists

    #all_files = glob.glob('../playdata/example1/*.fits')
    all_files = glob.glob('../raw/*.fits')
    all_files.sort()
    if args.verbose:
        print(f"Found {len(all_files)} files to work with.\n")

    #########################################################
    # CREATE LISTS OF DIFFERENT FILE TYPES
    #########################################################





    ######################################################
    # ADD BAD PIXEL MASKS TO DATABASE
    #
    # Q: what if you run this multiple times?
    ######################################################
    for bpm in dataselect.select_data(all_files, ['BPM']):
        caldb.add_cal(bpm)


    if args.makebias:
        print("Combining bias frames... \n")
        all_biases = dataselect.select_data(all_files, ['BIAS'])    
        for bias in all_biases:
            ad = astrodata.open(bias)
            print('BIAS:', bias, '  ', ad.detector_roi_setting())


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

        if len(biasstd) >  0:
            reduce_biasstd = Reduce()
            reduce_biasstd.files.extend(biasstd)
            reduce_biasstd.runr()
        
        reduce_biassci = Reduce()
        reduce_biassci.files.extend(biassci)
        reduce_biassci.runr()


    if args.makeflat:
        print("Combining flat frames... \n")
        flats = dataselect.select_data(all_files, ['FLAT'])
        if args.verbose:
            print(f"found {len(flats)} flat files.  First one is: {flats[0]}")

        reduce_flats = Reduce()
        reduce_flats.files.extend(flats)
        reduce_flats.uparms = dict([('interactive', True)])
        reduce_flats.runr()

    if args.makearc:
        print("Combining arc frames... \n")
        arcs = dataselect.select_data(all_files, ['ARC'])
        if args.verbose:
            print(f"found {len(arcs)} arc files.  First one is: {arcs[0]}")
        
        reduce_arcs = Reduce()
        reduce_arcs.files.extend(arcs)
        reduce_arcs.uparms = dict([('interactive', True)])
        reduce_arcs.runr()

    if args.standards:
        stdstar = dataselect.select_data(all_files, ['STANDARD'])
        if args.verbose:
            print(f"found {len(stdstar)} standard star files.  First one is: {stdstar[0]}")
        
        reduce_std = Reduce()
        reduce_std.files.extend(stdstar)
        reduce_std.uparms = dict([('interactive', True)])
        reduce_std.runr()

    if args.science:

        #all_science = dataselect.select_data(
        #    all_files,
        #    [],
        #    ['CAL'],
        #    )

        scitarget = dataselect.select_data(
            all_files,
            [],
            ['CAL'],
            dataselect.expr_parser(f'object=="{args.target}"')
        )
        if len(scitarget) == 0:
            print(f"WARNING: no science target found that match name: {args.target}")
            sys.exit()
            
        print(f"found {len(scitarget)} science target files. First one is: {scitarget[0]}")

        
        if args.verbose: 
            print("#############################")
            print("ALL SCIENCE FILES:")
            for sci in scitarget:
                ad = astrodata.open(sci)
                print(sci, '  ', ad.object())

        

        display_1d = True

        reduce_science = Reduce()
        reduce_science.files.extend(scitarget)
        reduce_science.runr()

        # construct name of output file
        output_rootname = os.path.basename(scitarget[0])
        #print("guess for the name of the 2D spectrum is: ", output_rootname.replace('.fits','_2D.fits'))
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Script to reduce GMOS longslit data for NGC 5356.\n\n USAGE:\n\n python ~/github/gmos_longslit/reduce.py 'NGC 5356 - extended source' --verbose --makebias ",
    formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('target', type=str, help="Specify the science target name reduce. Use single quotes if the target name contains multiple words/has spaces. For example: 'NGC 5356 - extended source'")
    parser.add_argument('--makebias', action='store_true', default=False, help='Build the master bias frame.')
    parser.add_argument('--makeflat', action='store_true', default=False, help='Build the master flat.')
    parser.add_argument('--makearc', action='store_true', default=False, help='Build the master arc.')
    parser.add_argument('--standards', action='store_true', default=False, help='Reduce the standard star images.')
    parser.add_argument('--science', action='store_true', default=False, help='Reduce the science images.')            
    parser.add_argument('--verbose', action='store_true', default=False, help='Be verbose.')
    args = parser.parse_args()

    if args.verbose:
        print("starting script to reduce ", args.target)
        print()
        print("hold on tight!")
        print()

    reduceall(args)
