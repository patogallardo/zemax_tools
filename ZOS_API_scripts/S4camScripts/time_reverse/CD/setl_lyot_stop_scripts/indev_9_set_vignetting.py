import zmx_api
import zmx  # noqa
from progressbar import progressbar
import os  # noqa


TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

print("Working on current file. You should save when done.")

MFE = TheSystem.MFE
MCE = TheSystem.MCE
Fields = TheSystem.SystemData.Fields

Nconf = 85

# Truncate semiaxes
for active_conf in progressbar(range(1, Nconf + 1)):
    MCE.SetActiveConfiguration(active_conf)
    Fields.ClearVignetting()
    Fields.SetVignetting()
