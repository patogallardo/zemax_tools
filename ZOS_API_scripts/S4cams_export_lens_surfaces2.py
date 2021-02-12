import pandas as pd
import os
folder = 'surfaceDefinitions'
df = pd.read_csv(os.path.join(folder, 'lens_data.csv'))


def mk_standalone_tex(fname_out, tex_path, ln):
    s = []
    s.append('\\documentclass[convert]{standalone}')
    s.append('\\usepackage{booktabs}')
    s.append('\\begin{document}')
    s.append('\\input{./%s}' % fname_out)
    s.append('\\end{document}')
    string_out = "\n".join(s)
    with open(os.path.join(tex_path, 'standalone_L%i.tex' % ln), 'w') as f:
        f.write(string_out)


assert df.SurfType[0] == 'Biconic Zernike'

# column numbers for biconic zernike
columns_for_table = ['SurfType', 'Radius', 'Thickness', 'Semi-Diameter',
                     'Conic', 'X Radius', 'X Conic', 'Norm Radius', 'X^1',
                     'X^2', 'X^3', 'X^4', 'X^5', 'X^6', 'X^7', 'X^8',
                     'X^9', 'X^10', 'X^11', 'X^12', 'X^13', 'X^14',
                     'X^15', 'X^16', 'Y^1', 'Y^2', 'Y^3', 'Y^4', 'Y^5',
                     'Y^6', 'Y^7', 'Y^8', 'Y^9', 'Y^10', 'Y^11',
                     'Y^12', 'Y^13', 'Y^14', 'Y^15', 'Y^16']
columnNumbersToExportMultiline = [0, 8, 24, len(columns_for_table)]


print(df[columns_for_table])
df = df[columns_for_table]
df.to_latex(os.path.join(folder, 'lens_definitions_table.tex'),
            float_format="%1.4e")


Nlenses = df.shape[0]
assert Nlenses == 3

for j in range(Nlenses):
    tex_path = os.path.join(folder, 'lensDef_L%i' % (j+1))
    if not os.path.exists(tex_path):
        os.mkdir(tex_path)

# now write tex files
for j in range(Nlenses):
    tex_path = os.path.join(folder, 'lensDef_L%i' % (j+1))
    fname_out = 'lens_definitions_table_L%i.tex' % (j+1)
    tex_fname = os.path.join(tex_path, fname_out)

    df_Ln = df.loc[j].to_frame().T
    df_Ln[columns_for_table[1:]] = df_Ln[columns_for_table[1:]].astype(float)
    df_Ln.to_latex(tex_fname,
                   float_format="%1.4e", index=False)
    mk_standalone_tex(fname_out, tex_path, j+1)

# break into rows
for j in range(Nlenses):
    tex_path = os.path.join(folder, 'lensDef_L%i' % (j+1))
    df_Ln = df.loc[j].to_frame().T
    df_Ln[columns_for_table[1:]] = df_Ln[columns_for_table[1:]].astype(float)

    for row in range(3):  # three lines
        fname_out = 'lens_definitions_L%i_row%i.tex' % (j+1, row+1)
        tex_fname = os.path.join(tex_path, fname_out)

        beg = columnNumbersToExportMultiline[row]
        end = columnNumbersToExportMultiline[row+1]
        df_Ln_row = df_Ln[columns_for_table[beg:end]] # noqa
        df_Ln_row.to_latex(tex_fname,
                           float_format='%1.4e', index=False)
