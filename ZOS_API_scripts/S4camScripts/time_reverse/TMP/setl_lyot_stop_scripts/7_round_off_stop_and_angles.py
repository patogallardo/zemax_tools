import zmx_api
import zmx  # noqa
from progressbar import progressbar
import os  # noqa
import math as mt

mce_rows_to_roundoff = [1, 2, 3]
mce_wedge_slope_row = 20
mce_wedge_angle_row = 19

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

print("Working on current file. You should save when done.")

MFE = TheSystem.MFE
MCE = TheSystem.MCE

NDECIMALS = 2
FACTOR = 10**NDECIMALS

Nconf = 85

# Truncate semiaxes
for active_conf in progressbar(range(1, Nconf + 1)):
    for row in mce_rows_to_roundoff:
        op_row = MCE.GetOperandAt(row)
        op_col = op_row.GetOperandCell(active_conf)
        current_value = op_col.DoubleValue
        if row == mce_rows_to_roundoff[0] or row == mce_rows_to_roundoff[1]:
            # semiaxes
            new_value = mt.trunc(current_value * FACTOR)/FACTOR
        elif row == mce_rows_to_roundoff[2]:  # angle
            new_value = round(current_value, NDECIMALS)
        print("\n %1.3f, %1.3f" % (current_value, new_value))
        op_col.DoubleValue = new_value


# Set wedges
for active_conf in progressbar(range(1, Nconf + 1)):
    row = mce_wedge_slope_row
    op_row = MCE.GetOperandAt(row)
    op_col = op_row.GetOperandCell(active_conf)
    current_value = op_col.DoubleValue
    if current_value < 0.0:
        new_value = -1.0 * current_value
        print("\n %1.3f, %1.3f" % (current_value, new_value))
        op_col.DoubleValue = new_value

        row = mce_wedge_angle_row
        op_row = MCE.GetOperandAt(row)
        op_col = op_row.GetOperandCell(active_conf)
        current_value = op_col.DoubleValue
        new_value = current_value + 180.0
        print("\n %1.3f, %1.3f" % (current_value, new_value))
        op_col.DoubleValue = new_value
