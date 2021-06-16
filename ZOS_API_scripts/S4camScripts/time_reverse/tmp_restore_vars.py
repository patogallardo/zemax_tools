# restores variables in initial values files

import zmx_api
import pandas as pd

c = zmx_api.connect_zmx_interactive()
TheSystem, ZOSAPI, ZOSAPI_NetHelper = c
MCE = TheSystem.MCE

df = pd.read_csv('groups_info/initial_values_it1.csv')

for j in range(len(df)):
    row = df.mcerow.values[j]
    value = df.initial_value.values[j]
    op = MCE.GetOperandAt(row)
    c = op.GetCellAt(1)
    c.DoubleValue = value
