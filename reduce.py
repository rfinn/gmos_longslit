#!/usr/bin/env python

from recipe_system import cal_service

caldb = cal_service.set_local_database()

try:
    caldb.init()
except LocalManagerError:
    print("cal database already exists")

# You can manually add processed calibrations with caldb.add_cal(<filename>),
# list the database content with caldb.list_files(), and caldb.remove_cal(<filename>) to remove a file from the database (it will not remove the file on disk.)

