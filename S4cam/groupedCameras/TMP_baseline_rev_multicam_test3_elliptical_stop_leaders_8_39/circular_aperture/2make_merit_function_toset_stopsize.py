import zmx_api
import zmx  # noqa
import numpy as np
from progressbar import progressbar
import os

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE

MF_fnameout = os.path.abspath("./adjust_circular_stop_MF_envelope.MF")

x_radius, y_radius = 2500., 2747.
TARGET_KEEPOUT_RADIUS_MM = 150
SURF, Hx, Hy, Px, Py = [2, 4, 5, 6, 7]


def add_eval_field(MFE, px, py, hx, hy, surf_num):
    op_rx = MFE.AddOperand()
    op_rx.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAX)
    reax_row = op_rx.OperandNumber
    op_rx.GetOperandCell(SURF).IntegerValue = surf_num
    op_rx.GetOperandCell(Hx).DoubleValue = hx
    op_rx.GetOperandCell(Hy).DoubleValue = hy
    op_rx.GetOperandCell(Px).DoubleValue = px
    op_rx.GetOperandCell(Py).DoubleValue = py

    op_ry = MFE.AddOperand()
    op_ry.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.REAY)
    reay_row = op_ry.OperandNumber
    op_ry.GetOperandCell(SURF).IntegerValue = surf_num
    op_ry.GetOperandCell(Hx).DoubleValue = hx
    op_ry.GetOperandCell(Hy).DoubleValue = hy
    op_ry.GetOperandCell(Px).DoubleValue = px
    op_ry.GetOperandCell(Py).DoubleValue = py

    op_qs = MFE.AddOperand()
    op_qs.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.QSUM)
    qsum_rownum = op_qs.OperandNumber
    op_qs.GetOperandCell(2).IntegerValue = reax_row
    op_qs.GetOperandCell(3).IntegerValue = reay_row

    MFE.CalculateMeritFunction()

    y = op_ry.Value
    x = op_rx.Value
    angle = np.arctan2(y, x)
    r = np.sqrt((x_radius*np.cos(angle))**2
                + (y_radius*np.sin(angle))**2)

    op_rim = MFE.AddOperand()
    op_rim.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.CONS)
    cons_rownum = op_rim.OperandNumber
    op_rim.Target = r
    return [qsum_rownum, cons_rownum]


def compute_keepout(rows_to_diff):
    for j, row_pair in enumerate(rows_to_diff):
        op = MFE.AddOperand()
        if j == 0:
            start_row = op.OperandNumber
        if j == len(rows_to_diff) - 1:
            end_row = op.OperandNumber
        op.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.DIFF)
        op.GetOperandCell(2).IntegerValue = row_pair[1]
        op.GetOperandCell(3).IntegerValue = row_pair[0]
        op.Weigth = 0.0
    op = MFE.AddOperand()
    op.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.MINN)
    op.Target = TARGET_KEEPOUT_RADIUS_MM
    op.GetOperandCell(2).IntegerValue = start_row
    op.GetOperandCell(3).IntegerValue = end_row
    op.Weight = 1.0

    op = MFE.AddOperand()
    op.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.EQUA)
    op.Target = 0.0
    op.GetOperandCell(2).IntegerValue = start_row
    op.GetOperandCell(3).IntegerValue = end_row
    op.Weight = 0  # 1e-5


t_p = np.deg2rad(np.arange(0, 360, 30))
t_h = np.deg2rad(np.arange(0, 360, 60) + 30)
pxs, pys = np.cos(t_p), np.sin(t_p)
hxs = np.append([0], np.cos(t_h))
hys = np.append([0], np.sin(t_h))

surf_num = 44


MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)

rows_to_diff = []
for i in progressbar(range(len(hxs))):
    MFE.AddOperand()
    for j in range(len(pxs)):
        px, py = pxs[j], pys[j]
        hx, hy = hxs[i], hys[i]
        todiff = add_eval_field(MFE, px, py, hx, hy, surf_num)
        rows_to_diff.append(todiff)

compute_keepout(rows_to_diff)
MFE.SaveMeritFunction(MF_fnameout)
