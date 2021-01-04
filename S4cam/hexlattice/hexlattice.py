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

def plot_df(df, scale, show=True):
    fig, ax = plt.subplots(figsize=[8, 8])
    patches = []
    are_there_groups = "group" in df
    colors = []
    
    for j in range(len(df)):
        x_coord,y_coord = df.x.values[j], df.y.values[j]
        if are_there_groups:
            color = "C%i" %df.group.values[j]
        else:
            color = None
        p = RegularPolygon([x_coord, y_coord], 6, scale*0.8, 0)
        colors.append(color)
        patches.append(p)
    collection = PatchCollection(patches, color=colors)
    ax.add_collection(collection)
    
    for j in range(len(df)):
        s_hex = "[%01i, %01i]" % (df.hex_x.values[j], df.hex_y.values[j])
        s_conf = "%i" % (df.index.values[j] + 1) # configs start at 1
        x, y = df.x.values[j], df.y.values[j]
        plt.text(x, y+20, s_conf, fontsize=8, color='white', ha='center', 
                 va='bottom')
    
    ax.set_aspect('equal')
    plt.scatter(df.x, df.y, color='white')
    plt.title('Camera Layout')
    plt.xlabel('x [mm]')
    plt.ylabel('y [mm]')    

    if show:
        plt.show()
    else:
        plt.savefig('camera_groups.png', dpi=150)
        plt.close()
    
def isin(df1, df2):
    '''checks if df1 is in df2'''
    hx1 = df1.hex_x.values
    hx2 = df2.hex_x.values
    
    hy1 = df1.hex_y.values
    hy2 = df2.hex_y.values
    
    isit = np.zeros(len(df1), dtype=bool)
    for row in range(len(isit)):
        isitin = np.logical_and((hx1[row] == hx2), (hy1[row] == hy2))
        if np.any(isitin):
            isit[row] = True
    
    return isit


def makering(order, scale=1):
    df = gen_hex_layout(order, scale=scale)
    if not order == 0:
        df_previous = gen_hex_layout(order - 1, scale)
        sel = isin(df, df_previous)
        df.drop(df.loc[sel].index, inplace=True)
    df['ring'] = order
    if order == 0:
        df['angle'] = 0
    else:
        angle = np.rad2deg(np.arctan2(df.y, df.x))
        sel = angle < 0
        angle[sel] = angle + 360
        df['angle'] = angle
    df.sort_values('angle', inplace=True, ignore_index=True)
    return df

def getConcentricRings(Nrings, scale):
    '''Generate a set of concentric rings with a given scale.'''
    Nrings = np.arange(0, Nrings, 1)
    dfs = [makering(N, scale) for N in Nrings]
    df = pd.concat(dfs, ignore_index=True)
    return df

def gen85CamPosition(scale):
    df = getConcentricRings(6, scale)
    topop = ["hex_x==0 and hex_y==5", 
             "hex_x==0 and hex_y==-5",
             "hex_x==5 and hex_y==-5",
             "hex_x==-5 and hex_y==5",
             "hex_x==-5 and hex_y==0",
             "hex_x==5 and hex_y==0"]
    for j in range(len(topop)):
        #print(topop[j])
        indxtopop = df.query(topop[j]).index[0]
        df.drop(index=indxtopop, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df
    
