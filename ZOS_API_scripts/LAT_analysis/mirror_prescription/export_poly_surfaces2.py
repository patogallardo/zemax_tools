'''Takes pickle file and generates a html file with the numbers
defining the polynomial surfaces with offsets.
'''

import pickle as pk
import pandas as pd
import numpy as np
import glob
import re
import matplotlib.pyplot as plt
import os
import subprocess

fnames = glob.glob('./CAD/surfaceDefinitions/polysurfaces.pck')
assert len(fnames) == 1  # check number of files.

fname = fnames[0]
with open(fname, 'rb') as f:
    [lens_surfaces] = pk.load(f)


def mk_tex(tex_table, label, targetdir):
    '''Write the tex file with the table and compile it'''
    tex_out_fname = os.path.join(targetdir,
                                 "%s_shape_table.tex" % label)

    out_str = ("\\documentclass[convert={convertexe={magick.exe}, density={150}}]{standalone}"  # noqa
               "\n\\usepackage{booktabs}"
               "\n\\usepackage{cmbright}"
               "\n\\begin{document}")
    out_str += tex_table + "\n\\end{document}"
    with open(tex_out_fname, "w") as f:
        f.write(out_str)
    print(out_str)
    subprocess.run('pdflatex --shell-escape %s_shape_table.tex' % label,
                   cwd=targetdir)


def getCoefficients(lens_surfaces, start_at=23):
    coefficients = []
    lengths = []
    mirror_names = []
    for j in range(len(lens_surfaces)):
        nterms = lens_surfaces[j][start_at]
        lens_surface = lens_surfaces[j][start_at:start_at+nterms+2]
        coefficients.append(lens_surface)
        lengths.append(len(coefficients))
        mirror_names.append(lens_surfaces[j]['Comment'])
    maxl_indx = np.where(lengths == np.max(lengths))[0][0]
    print(maxl_indx)
    row_names = coefficients[maxl_indx].index
    return coefficients, row_names, mirror_names


def combineDataFrames(df1, df2):
    '''df1: dataframe with the polynomial definition
       df2: dataframe with the aperture information
    returns a dataframe with this information combined into one.
    '''
    df2.index = df1.index
    df = pd.concat([df1, df2], axis=1)
    return df


def ispolyval(str):
    if "X" in str and "Y" in str:
        return True
    else:
        return False


def polyMatrix(row):
    matrix = np.zeros([6, 6])
    maxterm = row['Maximum Term #']
    count = 1
    for j in range(len(row)):
        colname = row.index[j]
        if ispolyval(colname):
            if count > maxterm:
                break
            m = re.match("X([0-9])Y([0-9])", colname)
            Xind, Yind = int(m.group(1)), int(m.group(2))
            matrix[Xind, Yind] = row[j]
            count += 1
    return matrix


def matrix_to_df(matrix):
    shape = matrix.shape
    rowlen, collen = shape[0], shape[1]
    namerows = ["i=%i" % i for i in range(0, rowlen, 1)]
    namecols = ["j=%i" % j for j in range(0, collen, 1)]
    df = pd.DataFrame(matrix, index=namerows, columns=namecols)
    return df


class mirror():
    def __init__(self, row, sampling=1000):
        self.row = row
        self.name = row.name
        norm = row['Norm Radius']
        matrix = polyMatrix(row)
        self.matrix = matrix
        self.matrix_df = matrix_to_df(matrix)
        self.x = np.linspace(-1.2, 1.2, sampling)
        self.y = np.linspace(-1.2, 1.2, sampling)
        self.xx, self.yy = np.meshgrid(self.x, self.y)
        z = np.polynomial.polynomial.polyval2d(self.xx, self.yy, matrix)
        self.x = self.x * norm
        self.y = self.y * norm
        self.xx = self.xx * norm
        self.yy = self.yy * norm
        self.z = z

    def mkParam_tex_table(self):
        params = self.row
        nozero = params.values != 0.0
        isnumber = np.isfinite(params.values.astype(float))
        sel = nozero
        sel[0] = False  # exclude max term #
        sel[-1], sel[-2] = False, False  # exclude decx decy
        sel[-3], sel[-4] = False, False
        sel = np.logical_and(isnumber, sel)
        labels = params.index[sel]
        values = params.values[sel]
        df_ = pd.DataFrame([values], columns=labels,
                           index=['Value'])
        tex_table = df_.to_latex()
        if not os.path.exists("CAD/tex_tables"):
            os.mkdir("CAD/tex_tables")
        mk_tex(tex_table, m.name, 'CAD/tex_tables')

    def plotSurface(self, save=False):
        fig, ax = plt.subplots()
        sel_flatten = np.isfinite(self.z.flatten())
        peaktopeak = (self.z.flatten()[sel_flatten].max() -
                      self.z.flatten()[sel_flatten].min())
        plt.hexbin(self.xx.flatten(),
                   self.yy.flatten(),
                   self.z.flatten(),
                   gridsize=500)
        plt.title(self.row.name)
        plt.colorbar(label='z [mm]')
        ax.set_aspect('equal')
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')

        plt.ylim([-3000, 3000])
        plt.figtext(0.65, 0.02, "Max depth = %1.2f mm" % peaktopeak)
        # plt.ylim([self.row.yhalfwidth*1.05, -self.row.yhalfwidth*1.05])

        if save:
            plt.savefig('CAD/surfaceDefinitions/%s.png' % self.row.name,
                        dpi=150)
            plt.close()
        else:
            plt.show()
            plt.close()


coeffs, row_names, mirror_names = getCoefficients(lens_surfaces)
df = pd.concat(coeffs, axis=1)
df.columns = mirror_names
df = df.transpose()

df.to_latex('CAD/surfaceDefinitions/mirror_defs.tex')
df.to_html('CAD/surfaceDefinitions/mirror_defs.html')

# test code...

mirrors = []
for j in range(3):
    row = df.loc[df.index[j]]
    m = mirror(row)
    mirrors.append(m)
    m.plotSurface(save=True)
    m.matrix_df.to_latex('CAD/surfaceDefinitions/%s.tex' % m.name)
    m.matrix_df.to_html('CAD/surfaceDefinitions/%s.html' % m.name)
    m.mkParam_tex_table()
