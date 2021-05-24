import zmx_api
import numpy as np
import progressbar

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()

FIELDRADIUSMAX = 0.5
FIELDRADIUSMIN = 0.1

WINDOW_CIRCLE_RADIUS = np.sqrt(3)/2 * 106.8
L1_CIRCLE_RADIUS = 100.0

WINDOWSURF = 43
L1SURF = 58
FIELD_SCALE_ROW = 45

ANGULAR_RES_FIELDS = 120.0
ANGULAR_RES_PUPIL = 90.0
NCONF = 85  # set this to 85 in production

MFE = TheSystem.MFE
OPERANDS = ZOSAPI.Editors.MFE.MeritOperandType

MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)

MFE.AddOperand()
MFE.AddOperand()

# define fields and pupil points
t_Hxy = np.deg2rad(np.arange(60, 360 + 60, ANGULAR_RES_FIELDS))
t_Pxy = np.deg2rad(np.arange(0, 360, ANGULAR_RES_PUPIL))

r_inscribed_fractional = np.sqrt(3)/2
Hxs = np.cos(t_Hxy) * r_inscribed_fractional
Hys = np.sin(t_Hxy) * r_inscribed_fractional

Hxs_L1 = np.cos(t_Hxy)
Hys_L1 = np.sin(t_Hxy)

Pxs = np.cos(t_Pxy)
Pys = np.sin(t_Pxy)

# end define fields and pupil points

# maximize solid angle
op = MFE.AddOperand()
op.GetCellAt(1).Value = "Total solid angle"

for currentconf in range(1, NCONF + 1):
    op = MFE.AddOperand()
    if currentconf == 1:
        startRow = op.OperandNumber
    if currentconf == NCONF:
        endRow = op.OperandNumber
    op.ChangeType(OPERANDS.MCOV)
    op.GetCellAt(2).IntegerValue = FIELD_SCALE_ROW
    op.GetCellAt(3).IntegerValue = currentconf
    op.Weight = 0.0
op = MFE.AddOperand()
op.ChangeType(OPERANDS.QSUM)
op.GetCellAt(2).IntegerValue = startRow
op.GetCellAt(3).IntegerValue = endRow

op = MFE.AddOperand()  # square
op.ChangeType(OPERANDS.PROD)
op.GetCellAt(2).IntegerValue = op.OperandNumber - 1
op.GetCellAt(3).IntegerValue = op.OperandNumber - 1

op = MFE.AddOperand()  # hex area
op.ChangeType(OPERANDS.CONS)
op.Target = 3 * np.sqrt(3)

op = MFE.AddOperand()
op.ChangeType(OPERANDS.PROD)
op.GetCellAt(2).IntegerValue = op.OperandNumber - 2
op.GetCellAt(3).IntegerValue = op.OperandNumber - 1
op.Weight = 1.0
op.Target = 42.5

# end maximize solid angle

for currentconf in progressbar.progressbar(range(1, NCONF + 1)):
    MFE.AddOperand()
    MFE.AddOperand()
    op = MFE.AddOperand()
    op.GetCellAt(1).Value = "For this conf. evaluate field sweep"

    # per configuration operands
    op = MFE.AddOperand()
    op.ChangeType(OPERANDS.CONF)
    op.GetCellAt(2).IntegerValue = currentconf

    op = MFE.AddOperand()
    op.ChangeType(OPERANDS.RAID)
    op.Target = FIELDRADIUSMAX
    op.Weight = 0.0
    row_number = op.OperandNumber
    op.GetCellAt(5).DoubleValue = 1.0

    op = MFE.AddOperand()
    op.ChangeType(OPERANDS.OPGT)
    op.Target = FIELDRADIUSMIN
    op.Weight = 1000
    op.GetCellAt(2).IntegerValue = row_number

    op = MFE.AddOperand()
    op.ChangeType(OPERANDS.MCOG)
    op.Weight = 1000
    op.GetCellAt(2).IntegerValue = FIELD_SCALE_ROW
    op.GetCellAt(3).IntegerValue = currentconf

    # end maximize field size

    # Window offset evaluation
    op = MFE.AddOperand()
    op.GetCellAt(1).Value = "Window center"
    op = MFE.AddOperand()
    op.ChangeType(OPERANDS.REAX)
    op.Weight = 1.0
    op.GetCellAt(2).IntegerValue = WINDOWSURF

    op = MFE.AddOperand()
    op.ChangeType(OPERANDS.REAY)
    op.Weight = 1.0
    op.GetCellAt(2).IntegerValue = WINDOWSURF
    # End  Window offset evaluation

    # hexagonal window

    op = MFE.AddOperand()
    op.GetCellAt(1).Value = "Hex Window constraint"

    for i in range(len(Hxs)):  # Hex window
        Hx, Hy = Hxs[i], Hys[i]
        for j in range(len(Pxs)):
            Px, Py = Pxs[j], Pys[j]
            op = MFE.AddOperand()
            if i == 0 and j == 0:
                firstRow = op.OperandNumber

            op.ChangeType(OPERANDS.REAX)
            op.GetCellAt(2).IntegerValue = WINDOWSURF
            op.GetCellAt(4).DoubleValue = Hx
            op.GetCellAt(5).DoubleValue = Hy
            op.GetCellAt(6).DoubleValue = Px
            op.GetCellAt(7).DoubleValue = Py
            rowx = op.OperandNumber

            op = MFE.AddOperand()
            op.ChangeType(OPERANDS.REAY)
            op.GetCellAt(2).IntegerValue = WINDOWSURF
            op.GetCellAt(4).DoubleValue = Hx
            op.GetCellAt(5).DoubleValue = Hy
            op.GetCellAt(6).DoubleValue = Px
            op.GetCellAt(7).DoubleValue = Py
            rowy = op.OperandNumber

            op = MFE.AddOperand()
            op.ChangeType(OPERANDS.QSUM)
            op.GetCellAt(2).IntegerValue = rowx
            op.GetCellAt(3).IntegerValue = rowy
            if i == len(t_Hxy) - 1 and j == len(t_Pxy) - 1:
                lastRow = op.OperandNumber
        MFE.AddOperand()

    op = MFE.AddOperand()  # get max radius
    op.ChangeType(OPERANDS.MAXX)
    op.GetCellAt(2).IntegerValue = firstRow
    op.GetCellAt(3).IntegerValue = lastRow
    op.Weight = 0

    op = MFE.AddOperand()  # ensure it fits
    op.ChangeType(OPERANDS.OPLT)
    op.GetCellAt(2).IntegerValue = op.OperandNumber - 1
    op.Target = WINDOW_CIRCLE_RADIUS
    op.Weight = 10.0

    MFE.AddOperand()
    op = MFE.AddOperand()
    # end hex window

    op.GetCellAt(1).Value = "L1 constraint"

    for i in range(len(Hxs)):  # L1 rim
        Hx, Hy = Hxs_L1[i], Hys_L1[i]
        for j in range(len(Pxs)):
            Px, Py = Pxs[j], Pys[j]
            op = MFE.AddOperand()
            if i == 0 and j == 0:
                firstRow = op.OperandNumber

            op.ChangeType(OPERANDS.REAX)
            op.GetCellAt(2).IntegerValue = L1SURF
            op.GetCellAt(4).DoubleValue = Hx
            op.GetCellAt(5).DoubleValue = Hy
            op.GetCellAt(6).DoubleValue = Px
            op.GetCellAt(7).DoubleValue = Py
            rowx = op.OperandNumber

            op = MFE.AddOperand()
            op.ChangeType(OPERANDS.REAY)
            op.GetCellAt(2).IntegerValue = L1SURF
            op.GetCellAt(4).DoubleValue = Hx
            op.GetCellAt(5).DoubleValue = Hy
            op.GetCellAt(6).DoubleValue = Px
            op.GetCellAt(7).DoubleValue = Py
            rowy = op.OperandNumber

            op = MFE.AddOperand()
            op.ChangeType(OPERANDS.QSUM)
            op.GetCellAt(2).IntegerValue = rowx
            op.GetCellAt(3).IntegerValue = rowy
            if i == len(t_Hxy) - 1 and j == len(t_Pxy) - 1:
                lastRow = op.OperandNumber
        MFE.AddOperand()

    op = MFE.AddOperand()  # get max radius
    op.ChangeType(OPERANDS.MAXX)
    op.GetCellAt(2).IntegerValue = firstRow
    op.GetCellAt(3).IntegerValue = lastRow
    op.Weight = 0

    op = MFE.AddOperand()  # ensure it fits
    op.ChangeType(OPERANDS.OPLT)
    op.GetCellAt(2).IntegerValue = op.OperandNumber - 1
    op.Target = L1_CIRCLE_RADIUS
    op.Weight = 10.0

    MFE.AddOperand()
    MFE.AddOperand()
    # end hex window
