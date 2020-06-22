import pandas as pd
import glob
directory = ['layout', 
             'strehls',
             'fNumbers',
             'chief_ray',
             'plate_scale',
             'distortion',
             'ellipticity',
             'footprints',
             'sag']

name = ['Layout', 
        'Strehl Ratios',
        'f/#',
        'Chief Ray Angles',
        'Plate Scale',
        'Distortion',
        'Ellipticity',
        'Footprints',
        'Mirror Sag']

def list_images_in_dir(dir):
    fnames = glob.glob(dir)
    for j in range(len(fnames)):
        fnames[j] = fnames[j].replace('\\','/')
    return fnames

df_system = pd.read_hdf('ray_db.hdf',key='system_variables')
project_name = df_system.project_name

assert len(directory) == len(name)

text = ['# %s\n' %project_name]

for j in range(len(name)):
    text.append('## %s\n' %name[j])
    fnames = list_images_in_dir(directory[j] + '/*.png')
    fnames += list_images_in_dir(directory[j] + '/*.JPG')
    for fname in fnames:
        text.append('![](%s)\n' %fname)

f = open('readme.md', 'w')
for line in text:
#    print(line)
    f.write(line)
f.close()
