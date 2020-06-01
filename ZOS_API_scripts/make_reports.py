import pandas as pd
import glob
directory = ['layout', 
             'chief_ray', 
             'fNumbers', 
             'strehls']
name = ['Layout', 
        'Chief Ray Angles', 
        'f/#', 
        'Strehl Ratios']

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
    fnames = list_images_in_dir(directory[j]+'/*.png')
    for fname in fnames:
        text.append('![](%s)\n' %fname)

f = open('readme.md', 'w')
for line in text:
#    print(line)
    f.write(line)
f.close()
