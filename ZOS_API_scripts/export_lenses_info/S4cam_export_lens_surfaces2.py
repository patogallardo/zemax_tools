import pandas as pd
import os
import subprocess

folder = 'CAD/surface_definitions'
df = pd.read_csv(os.path.join(folder, 'lens_surface_data.csv'))


def mk_standalone_tex_from_df(df, fname_out):
    os.makedirs(os.path.split(fname_out)[0], exist_ok=True)
    s = []
    s.append('\\documentclass[convert={convertexe={magick.exe}}]{standalone}')
    s.append('\\usepackage{booktabs}')
    s.append('\\usepackage{cmbright}')
    s.append('\\begin{document}')
    s.append(df.to_latex(float_format="%1.4e",
                         index=False,
                         column_format='l'*len(df.columns)))
    s.append('\\end{document}')
    string_out = "\n".join(s)
    with open(fname_out, 'w') as f:
        f.write(string_out)
    subprocess.run("pdflatex --shell-escape %s" % (os.path.split(fname_out)[-1]),  # noqa
                   cwd=os.path.split(fname_out)[0])  # noqa


surf_type = df.SurfType[0]
assert surf_type == 'Biconic Zernike' or surf_type == 'Even Asphere' or surf_type == 'Standard'  # noqa

# column numbers for biconic zernike
if df.SurfType[0] == 'Biconic Zernike':
    columns_for_table = ['SurfType', 'Radius', 'Thickness', 'Semi-Diameter',
                     'Conic', 'X Radius', 'X Conic', 'Norm Radius', 'X^1',  # noqa
                     'X^2', 'X^3', 'X^4', 'X^5', 'X^6', 'X^7', 'X^8',  # noqa
                     'X^9', 'X^10', 'X^11', 'X^12', 'X^13', 'X^14',  # noqa
                     'X^15', 'X^16', 'Y^1', 'Y^2', 'Y^3', 'Y^4', 'Y^5',  # noqa
                     'Y^6', 'Y^7', 'Y^8', 'Y^9', 'Y^10', 'Y^11',  # noqa
                     'Y^12', 'Y^13', 'Y^14', 'Y^15', 'Y^16']  # noqa
    columnNumbersToExportMultiline = [0, 8, 24, len(columns_for_table)]  # noqa
elif df.SurfType[0] == 'Even Asphere':
    columns_for_table = ['SurfType', 'Radius', 'Thickness',
                         'Clear Semi-Dia', 'Conic', '2nd Order Term',
                         '4th Order Term', '6th Order Term',
                         '8th Order Term', '10th Order Term',
                         '12th Order Term', '14th Order Term',
                         '16th Order Term']
    columnNumbersToExportMultiline = []
elif surf_type == 'Standard':
    columns_for_table = ['SurfType', 'Radius', 'Thickness', 'Clear Semi-Dia', 'Conic']  # noqa
    columnNumbersToExportMultiline = []

print(df[columns_for_table])
df = df[columns_for_table]
mk_standalone_tex_from_df(df,
                          os.path.join(folder, "lens_definitions_table",
                                       "all_lens_definitions_table.tex"))

Nlenses = df.shape[0]
assert Nlenses == 3


# now write tex files
for j in range(Nlenses):
    tex_path = os.path.join(folder, 'lensDef_L%i' % (j+1))
    fname_out = 'lens_definitions_table_L%i.tex' % (j+1)
    tex_fname = os.path.join(tex_path, fname_out)

    df_Ln = df.loc[j].to_frame().T
    df_Ln[columns_for_table[1:]] = df_Ln[columns_for_table[1:]].astype(float)
    mk_standalone_tex_from_df(df_Ln, os.path.join(tex_path, fname_out))


# break into rows
if columnNumbersToExportMultiline != []:
    for j in range(Nlenses):
        tex_path = os.path.join(folder, 'lensDef_L%i' % (j+1))
        df_Ln = df.loc[j].to_frame().T
        df_Ln[columns_for_table[1:]] = df_Ln[columns_for_table[1:]].astype(float)  # noqa

        text = []
        fname_out = 'lens_definitions_3rows_L%i.tex' % (j+1)
        fname_out = os.path.join(tex_path, fname_out)

        for row in range(3):  # three lines
            beg = columnNumbersToExportMultiline[row]
            end = columnNumbersToExportMultiline[row+1]
            df_Ln_row = df_Ln[columns_for_table[beg:end]] # noqa

            text.append(df_Ln_row.to_latex(float_format='%1.4e', index=False))

        text = "\n".join(text)  # write one tex file per lens

        os.makedirs(os.path.split(fname_out)[0], exist_ok=True)
        s = []
        s.append('\\documentclass[varwidth=\\maxdimen, convert={convertexe={magick.exe}}]{standalone}')  # noqa
        s.append('\\usepackage{cmbright}')
        s.append('\\usepackage{booktabs}')
        s.append('\\begin{document}')
        s.append(text)
        s.append('\\end{document}')
        string_out = "\n".join(s)
        with open(fname_out, 'w') as f:
            f.write(string_out)
        subprocess.run("pdflatex --shell-escape %s" % (os.path.split(fname_out)[-1]),  # noqa
                       cwd=os.path.split(fname_out)[0])  # noqa
