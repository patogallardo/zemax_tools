'''This runs all the analysis in the list programs_to_run.
'''

import os
import glob
import subprocess

fnames = glob.glob('./*/')
fnames.sort()
programs_to_run = [r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\extract_raytrace_chief_and_extreme_rays.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\extract_strehl_ratios.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\focal_plane_strehl_ratios.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\f_numbers.py']

print('Processing all files within subfolders...')
for fname in fnames: # change this later
    abs_path = os.path.abspath(fname)
    print('Processing: %s\n\n\n' %abs_path)
    for script in programs_to_run:
        command = "python %s" %script
        working_directory = abs_path
        print(command)
        print(working_directory)
        p = subprocess.Popen(command, cwd=working_directory)
        p.wait()

        p = subprocess.Popen(r'python C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\make_reports.py', cwd=working_directory)
p.wait()

print('Done! :)')
