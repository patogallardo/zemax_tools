'''This runs all the analysis in the list programs_to_run.
'''

import os
import glob
import subprocess

fnames = glob.glob('./*/')
fnames.sort()

opticstudio = r'C:\Program Files\Zemax OpticStudio\OpticStudio.exe'

programs_to_run = [r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\extract_raytrace_chief_and_extreme_rays.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\extract_strehl_ratios.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\focal_plane_strehl_ratios.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\f_numbers.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\plate_scale.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\distortion.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\extract_marginal_pupil_rays.py',
r'C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\fit_ellipses.py',
'-zpl=C:\\Users\\pgall\\Documents\\Zemax\\Macros\\export_sag.ZPL',
'-zpl=C:\\Users\\pgall\\Documents\\Zemax\\Macros\\export_footprints.ZPL',
'-zpl=C:\\Users\\pgall\\Documents\\Zemax\\Macros\\extract_angle_between_boresight_and_focal_plane_chief_ray.ZPL'
]

#programs_to_run = programs_to_run[-2:] # tests last 2 zemax scripts

print('Processing all files within subfolders...')
for fname in fnames: # change this later
    abs_path = os.path.abspath(fname)
    print('Processing: %s\n\n\n' %abs_path)
    for script in programs_to_run:
        if ".py" in script:
            command = "python %s" %script
        else:
            zmxfile = glob.glob(os.path.join(abs_path, '*.zmx'))[0]
            command = [opticstudio, script, '-vFileName=%s' % zmxfile]
        working_directory = abs_path
        print(command)
        print(working_directory)
        p = subprocess.Popen(command, cwd=working_directory)
        p.wait()

    p = subprocess.Popen(r'python C:\Users\pgall\Documents\wilson\code\zemax_tools\ZOS_API_scripts\make_reports.py', cwd=working_directory)
    p.wait()

print('Done! :)')
