from zmx_api import connect_zmx_interactive
from zmx import zemax_optimize
import glob
import os

fnames = glob.glob('*.zmx')
assert len(fnames) == 1
fname_parent = fnames[0]
fname_parent = os.path.abspath(fname_parent)

c = connect_zmx_interactive()
TheSystem, ZOSAPI, ZOSAPI_NetHelper = c
MFE = TheSystem.MFE
if not os.path.exists('./replicated_cam'):
    os.mkdir('./replicated_cam')


for j in range(1, 86):
    TheSystem.LoadFile(fname_parent, False)
    MFE.GetOperandAt(1).GetCellAt(2).IntegerValue = j

    zemax_optimize(TheSystem, ZOSAPI, CyclesAuto=True)

    if not os.path.exists('replicated_cam/cam%02i' % j):
        os.mkdir("replicated_cam/cam%02i" % j)
    fname_out = os.path.join(os.path.abspath('./'), "replicated_cam",
                             'cam%02i' % j, 'cam%02i.zmx' % j)
    print("writing: %s" % fname_out)
    TheSystem.SaveAs(fname_out)
