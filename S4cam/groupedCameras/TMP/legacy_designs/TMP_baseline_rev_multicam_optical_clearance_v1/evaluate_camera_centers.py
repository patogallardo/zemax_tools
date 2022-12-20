import zmx_api
import zmx
import numpy as np
import math as mt
import os

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()
LDE = TheSystem.LDE
MCE = TheSystem.MCE

FlatFP_surf = 31 # this is the telescope focal plane surface
DetectorFP_surf = 2

x_coord = np.zeros(85)
y_coord = np.zeros(85)

for conf in range(1, 86):
    MCE.SetCurrentConfiguration(conf)
    
    #set global
    surf = LDE.GetSurfaceAt(FlatFP_surf)
    typeData = surf.TypeData
    typeData.IsGlobalCoordinateReference = True
    
    surf = LDE.GetSurfaceAt(DetectorFP_surf)
    
    a = 0.0
    ret = LDE.GetGlobalMatrix(DetectorFP_surf, a, a, a,
                              a, a, a,
                              a, a, a,
                              a, a, a)
    x, y, z = ret[-3], ret[-2], ret[-1]
    x_coord[conf-1] = x
    y_coord[conf-1] = y

dic = {"xpos": x_coord, "ypos": y_coord}
import pandas as pd
df = pd.DataFrame(dic)
if not os.path.exists("./cameracoords"):
    os.mkdir('cameracoords')
df.to_hdf('cameracoords/coords.hdf', 'df')
