import zmx_api
import zmx  # noqa
import numpy as np
import sys
import zmx_plot
import pandas as pd
import os

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

MFE = TheSystem.MFE
MCE = TheSystem.MCE

print("usage: this_script.py MCE_row")
MCE_row = sys.argv[1]

number_of_configurations = MCE.NumberOfConfigurations

MCE_row_values = np.zeros(number_of_configurations)
for conf in range(1, number_of_configurations+1):
    MCEOperand = MCE.GetOperandAt(1)
    val = MCEOperand.GetOperandCell(conf).DoubleValue
    MCE_row_values[conf-1] = val

df = pd.read_csv('./groups_info/85cam_groups.csv')
df.sort_values(by=['config'], inplace=True)
x = df.x.values
y = df.y.values

if not os.path.exists('stop_values'):
    os.mkdir('stop_values')
zmx_plot.mk_hex(x, y, MCE_row_values, show=False,
                plot_fname="./stop_values/stop_val_dist")
