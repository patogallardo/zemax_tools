import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
SHOW = False

queries = ['goodat1mm == 1',
           'goodat2mm == 1 and goodat1mm == 0',
           'goodat3mm == 1 and goodat2mm == 0']

df_layout = pd.read_csv('85cam_groups.csv')
df_imgqual = pd.read_excel('./cam_band_allocation.xlsx', engine='openpyxl')

cols = df_imgqual.columns[1:]

dfs = [df_imgqual.query(query) for query in queries]


fig, ax = plt.subplots(figsize=[8, 8])
r = 100
patches = []
colors = []

for camtype, df in enumerate(dfs):
    indx = df.cam.values - 1
    df_toplot = df_layout.loc[indx]
    x_coords, y_coords = df_toplot.x.values, df_toplot.y.values
    
    for j in range(len(df_toplot)):
        color = "C%i" % (camtype + 1)
        p = RegularPolygon([x_coords[j], y_coords[j]], 6, r, 0)
        colors.append(color)
        patches.append(p)
    plt.scatter(df_toplot.x, df_toplot.y)
collection = PatchCollection(patches, color=colors)
ax.add_collection(collection)

ax.set_aspect('equal')
if SHOW:
    plt.show()
else:
    plt.savefig('cam_allocation.png', dpi=120)
    plt.close()
