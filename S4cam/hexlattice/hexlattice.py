import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
import itertools
import pandas as pd


def hexToxy(hexx, hexy, scale=1):
    '''Receives the hex coordinate and converts it to
    a physical coordinate in the hexagonal lattice.'''
    A = np.array([[np.sqrt(3), np.sqrt(3)/2],[0, 3/2]])
    b = np.array([hexx, hexy])
    r = np.dot(A, b.T) * scale
    return r[0], r[1]


def genLattice(order, scale=1):
    xrange, yrange = range(-order, order+1), range(-order, order+1)
    hexcoords = list(itertools.product(xrange, yrange))
    hex_x = [hexcoords[j][0] for j in range(len(hexcoords))]
    hex_y = [hexcoords[j][1] for j in range(len(hexcoords))]
    coords = [hexToxy(hexcoords[j][0], hexcoords[j][1], scale=scale)
              for j in range(len(hexcoords))]
    x = [coords[j][0] for j in range(len(hexcoords)) ]
    y = [coords[j][1] for j in range(len(hexcoords)) ]
    return hex_x, hex_y, x, y


def gen_hex_layout(order, scale=1, clip_edges=True):
    hex_x, hex_y, x, y = genLattice(order, scale=scale)
    df = pd.DataFrame({'x': x , 'y': y,
                       'hex_x': hex_x, 'hex_y': hex_y})
    if clip_edges:
        df = df.query('hex_x + hex_y <= %i and hex_x+ hex_y>=%i' 
                      %(order, -order))
        df.reset_index(drop=True, inplace=True)
    return df

def plot_df(df, scale, order):
    fig, ax = plt.subplots(figsize=[8, 8])
    patches = []
    for x_coord,y_coord in zip(df.x.values,df.y.values):
        p = RegularPolygon([x_coord, y_coord], 6, scale*0.8, 0)
        patches.append(p)
    collection = PatchCollection(patches)
    ax.add_collection(collection)
    
    ax.set_aspect('equal')
    plt.title('order: %i' %order)
    plt.scatter(df.x, df.y, color='white')
