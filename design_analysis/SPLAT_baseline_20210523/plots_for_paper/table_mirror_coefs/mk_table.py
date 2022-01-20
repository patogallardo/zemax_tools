import zmx_api
import shutil

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()
filepath = r"C:\Users\pgall\OneDrive - The University of Chicago\Github\zemax_tools\design_analysis\SPLAT_baseline_20210523\SPLAT_Base_Fwd.zmx"  # noqa
TheSystem.LoadFile(filepath, False)


LDE = TheSystem.LDE


surface_numbers = [8, 12, 16]
names = ['M1', 'M2', 'M3']

sc = ZOSAPI.Editors.LDE.SurfaceColumn
col_numbers = [sc.Par16, sc.Par17, sc.Par19, sc.Par21,
               sc.Par23, sc.Par24, sc.Par26, sc.Par28,
               sc.Par30, sc.Par32, sc.Par34]
# extract names
M2 = LDE.GetSurfaceAt(surface_numbers[2])
col_names = ["$A_{%s}$" % M2.GetSurfaceCell(col_num).Header.replace("X", '').replace("Y", ',')  # noqa
             for col_num in col_numbers]
s = '\\begin{tabular}{rrrrrrrrrrrr}\n\\toprule\n'
s += ' & '
s += ' & '.join(col_names) + '\\\\\n'
s += '\\midrule\n'

for j, surface_number in enumerate(surface_numbers):
    s += "%s & " % names[j]
    for col_num in col_numbers:
        LDE_row = LDE.GetSurfaceAt(surface_number)
        cell = LDE_row.GetSurfaceCell(col_num)
        val = cell.Value
        if val == '':
            val = 0.0
        else:
            val = float(cell.Value)
        s += "%1.3f & " % val
    s = s[:-3]
    s += '\\\\\n'
s += "\\bottomrule"
s += "\\end{tabular}"
print(s)

fname_out = 'mirrorcoef_table.tex'
with open(fname_out, 'w') as f:
    f.write(s)

dir_out = r"C:\Users\pgall\OneDrive - The University of Chicago\Github\SPLAT_paper\tables"  # noqa
shutil.copy(fname_out, dir_out)
