import zmx_api
import zmx  # noqa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from progressbar import progressbar
import os

XRADIUS = 2500
YRADIUS = 2747
TARGET_KEEPOUT_RADIUS_MM = 150.0
PRECISE_VIGNETTING = False


def eval_distance_to_rim(max_rs, MFE, surfnum):
    qsum_rownums = []
    radius_rownums = []

    MFE.AddOperand()
    for j_field in range(len(max_rs)):
        op_x = MFE.AddOperand()

        rownum_x = op_x.OperandNumber
        op_x.ChangeType(REAX)
        op_x.GetOperandCell(2).IntegerValue = surfnum
        op_x.GetOperandCell(4).DoubleValue = max_rs.hx.values[j_field]  # Hx
        op_x.GetOperandCell(5).DoubleValue = max_rs.hy.values[j_field]  # Hy
        op_x.GetOperandCell(6).DoubleValue = max_rs.px.values[j_field]  # Px
        op_x.GetOperandCell(7).DoubleValue = max_rs.py.values[j_field]  # Py
        op_x.Weight = 0.0

        op_y = MFE.AddOperand()
        rownum_y = op_y.OperandNumber
        op_y.ChangeType(REAY)
        op_y.GetOperandCell(2).IntegerValue = surfnum
        op_y.GetOperandCell(4).DoubleValue = max_rs.hx.values[j_field]  # Hx
        op_y.GetOperandCell(5).DoubleValue = max_rs.hy.values[j_field]  # Hy
        op_y.GetOperandCell(6).DoubleValue = max_rs.px.values[j_field]  # Px
        op_y.GetOperandCell(7).DoubleValue = max_rs.py.values[j_field]  # Py
        op_y.Weight = 0.0

        op_qsum = MFE.AddOperand()
        op_qsum.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.QSUM)
        op_qsum.GetOperandCell(2).IntegerValue = rownum_x
        op_qsum.GetOperandCell(3).IntegerValue = rownum_y
        op_qsum.Weight = 0.0

        MFE.CalculateMeritFunction()

        y = op_y.Value
        x = op_x.Value
        angle = np.arctan2(y, x)
        r = np.sqrt((XRADIUS*np.cos(angle))**2
                    + (YRADIUS*np.sin(angle))**2)
        op_rim = MFE.AddOperand()
        op_rim.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CONS)
        op_rim.Target = r

        radius_rownums.append(op_rim.OperandNumber)
        qsum_rownums.append(op_qsum.OperandNumber)

    for j in range(len(qsum_rownums)):
        op_diff = MFE.AddOperand()
        if j == 0:
            first_diff_rownum = op_diff.OperandNumber
        if j == len(qsum_rownums) - 1:
            last_diff_rownum = op_diff.OperandNumber
        op_diff.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.DIFF)
        op_diff.GetOperandCell(2).IntegerValue = radius_rownums[j]
        op_diff.GetOperandCell(3).IntegerValue = qsum_rownums[j]
        op_diff.Weight = 0.0

    op_equa = MFE.AddOperand()
    op_equa.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.EQUA)
    op_equa.GetOperandCell(2).IntegerValue = first_diff_rownum
    op_equa.GetOperandCell(3).IntegerValue = last_diff_rownum
    op_equa.Weight = 1.0e-2

    op_min = MFE.AddOperand()
    op_min.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.MINN)
    op_min.GetOperandCell(2).IntegerValue = first_diff_rownum
    op_min.GetOperandCell(3).IntegerValue = last_diff_rownum
    op_min.Weight = 1.0
    op_min.Target = TARGET_KEEPOUT_RADIUS_MM

    op_max = MFE.AddOperand()
    op_max.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.MAXX)
    op_max.GetOperandCell(2).IntegerValue = first_diff_rownum
    op_max.GetOperandCell(3).IntegerValue = last_diff_rownum
    op_max.Weight = 1.0e-2
    op_max.Target = TARGET_KEEPOUT_RADIUS_MM + 40

    op_opgt = MFE.AddOperand()
    op_opgt.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.OPGT)
    op_opgt.Target = 149
    op_opgt.Weight = 1e15
    op_opgt.GetOperandCell(2).IntegerValue = op_min.OperandNumber

    op_oplt = MFE.AddOperand()
    op_oplt.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.OPLT)
    op_oplt.Target = 200
    op_oplt.Weight = 1e10
    op_oplt.GetOperandCell(2).IntegerValue = op_min.OperandNumber

    op_opgt = MFE.AddOperand()
    op_opgt.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.OPGT)
    op_opgt.Target = 140
    op_opgt.Weight = 1e12
    op_opgt.GetOperandCell(2).IntegerValue = op_min.OperandNumber

    op_oplt = MFE.AddOperand()
    op_oplt.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.OPLT)
    op_oplt.Target = 1200.
    op_oplt.Weight = 1e12
    op_oplt.GetOperandCell(2).IntegerValue = op_min.OperandNumber


def find_max_radius_fields(df, x_mean, y_mean):
    max_rs = []
    gs = df.groupby(['px', 'py'])
    for g in gs:
        r = np.sqrt((x_mean - g[1].x)**2 + (y_mean-g[1].y)**2)
        ind = r.idxmax()
        max_rs.append(g[1].loc[ind])
    max_rs = pd.DataFrame(max_rs)
    return max_rs


def plot_rim(active_conf, df, max_rs):
    fname_plotout = os.path.join(MF_DIROUT,
        "footprint_rim_conf%02i.png" % active_conf)  # noqa
    plt.gca().set_aspect('equal')
    plt.scatter(df.x, df.y, marker='.')

    plt.scatter(max_rs.x, max_rs.y, marker='.')
    plt.title("configuration number: %i" % active_conf)
    plt.xlim([-3000, 3000])
    plt.savefig(fname_plotout)
    plt.close()


def eval_rim_centroid(max_rs, MFE, surfnum, REAXORY):
    for j_field in range(len(max_rs)):
        op = MFE.AddOperand()
        if j_field == 0:
            row_start = op.OperandNumber
        if j_field == len(max_rs) - 1:
            row_end = op.OperandNumber
        op.ChangeType(REAXORY)
        op.GetOperandCell(2).IntegerValue = surfnum
        op.GetOperandCell(4).DoubleValue = max_rs.hx.values[j_field]  # Hx
        op.GetOperandCell(5).DoubleValue = max_rs.hy.values[j_field]  # Hy
        op.GetOperandCell(6).DoubleValue = max_rs.px.values[j_field]  # Px
        op.GetOperandCell(7).DoubleValue = max_rs.py.values[j_field]  # Py
        op.Weight = 0.0
    op = MFE.AddOperand()
    op.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.OSUM)
    op.GetOperandCell(2).IntegerValue = row_start
    op.GetOperandCell(3).IntegerValue = row_end
    op.Weight = 10.0


MKPLOT = True
RUNOPTIMIZER = False
MK_MERITFUNCTIONS = True

mce_rows_to_optimize = [19, 20]

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE

REAX = ZOSAPI.Editors.MFE.MeritOperandType.REAX
REAY = ZOSAPI.Editors.MFE.MeritOperandType.REAY
surfnum = 44
wavenum = 1

t = np.linspace(0, 2*np.pi, 17)[:-1]
rs = np.linspace(0, 1, 4)
Pxs = np.cos(t)
Pys = np.sin(t)

Hxs = np.concatenate([np.cos(t) * r for r in rs])
Hys = np.concatenate([np.sin(t) * r for r in rs])

MF_DIROUT = './center_pri_footprint/'
if not os.path.exists(MF_DIROUT):
    os.mkdir(MF_DIROUT)

if MK_MERITFUNCTIONS:
    for active_conf in progressbar(range(1, 86)):
        #  MFE.GetOperandAt(1).GetOperandCell(2).IntegerValue = 1
        MCE.SetCurrentConfiguration(active_conf)
        px_out, py_out, hx_out, hy_out, x, y = [], [], [], [], [], []
        for (Hx, Hy) in zip(Hxs, Hys):
            for (Px, Py) in zip(Pxs, Pys):
                valx = MFE.GetOperandValue(REAX, surfnum, wavenum,
                                           Hx, Hy, Px, Py, 0, 0)
                valy = MFE.GetOperandValue(REAY, surfnum, wavenum,
                                           Hx, Hy, Px, Py, 0, 0)
                px_out.append(Px)
                py_out.append(Py)
                hx_out.append(Hx)
                hy_out.append(Hy)
                x.append(valx)
                y.append(valy)
        stopval = MFE.GetOperandValue(REAX, 6, 1,
                                      0, 0, 1, 0, 0, 0)
        df = pd.DataFrame({'hx': hx_out,
                           'hy': hy_out,
                           'px': px_out,
                           'py': py_out,
                           'x': x,
                           'y': y})

        x_mean, y_mean = df.x.mean(), df.y.mean()
        max_rs = find_max_radius_fields(df, x_mean, y_mean)
        x_mean, y_mean = max_rs.x.mean(), max_rs.y.mean()
        max_rs = find_max_radius_fields(df, x_mean, y_mean)

        if MKPLOT:
            plot_rim(active_conf, df, max_rs)

        # now clear merit function and write up a new one
        MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)
        MFE.AddOperand()
        MFE.GetOperandAt(1).GetOperandCell(2).IntegerValue = active_conf
        MFE.AddOperand()

        op_cvig = MFE.AddOperand()
        op_svig = MFE.AddOperand()
        op_cvig.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CVIG)
        op_svig.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.SVIG)
        if PRECISE_VIGNETTING:
            op_svig.GetOperandCell(2).IntegerValue = 1
        else:
            op_svig.GetOperandCell(2).IntegerValue = 2

        eval_rim_centroid(max_rs, MFE, surfnum, REAX)
        eval_rim_centroid(max_rs, MFE, surfnum, REAY)

        eval_distance_to_rim(max_rs, MFE, surfnum)

        mf_fnameout = os.path.abspath(os.path.join(MF_DIROUT,
                     "MF_conf%02i.MF" % active_conf))  # noqa
        MFE.SaveMeritFunction(mf_fnameout)


if RUNOPTIMIZER:
    for active_conf in progressbar(range(1, 86)):
        mf_fnameout = os.path.abspath(os.path.join(MF_DIROUT,
                                      "MF_conf%02i.MF" % active_conf))
        MFE.LoadMeritFunction(mf_fnameout)
        TheSystem.Tools.RemoveAllVariables()
        zmx.set_variables_or_const(mce_rows_to_optimize,
                                   active_conf,
                                   MCE, ZOSAPI, vars=True)
        zmx.zemax_optimize(TheSystem, ZOSAPI)
