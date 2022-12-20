import zmx_api
import zmx
import numpy as np
import math as mt


TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()
MFE = TheSystem.MFE
op_types = ZOSAPI.Editors.MFE.MeritOperandType

# constants
L321_surf_num, _, _ = zmx.get_lens_surfaces(TheSystem)
#L321_diameter_mm = [158, 152, 177] # 8mm clearance
#L321_diameter_mm = [158, 148, 173] # 8mm clearance

L321_diameter_mm = [158, 138, 163] # 15mm clearance
# end constants


# delete merit function and add a few operands
def initialize_merit_function(MFE):
    MFE.RemoveOperandsAt(1, MFE.NumberOfOperands)
    MFE.AddOperand()
    MFE.AddOperand()
    zmx.set_MFE_row(op_types.CVIG, 2, MFE, ZOSAPI)


def write_L321_diameter_constraints(MFE, start_at_row,
                                    L321_surf_num, L321_diameter_mm,
                                    weight_l1illum=1e10,
                                    hardweight=1e13):

    MFE.AddOperand()

    current_row = start_at_row
    lens_index = 0

    weights_for_exact_diameter = [weight_l1illum,
                                  0.0,
                                  weight_l1illum]
    for lens_index in range(len(L321_surf_num)):
        zmx.set_MFE_row(op_types.BLNK, current_row, MFE, ZOSAPI,
                        param1val="Lens Diameter")
        MFE.AddOperand()
        current_row += 1
        zmx.set_MFE_row(op_types.DMLT, current_row, MFE, ZOSAPI,
                        param1val=L321_surf_num[lens_index],
                        weight=hardweight,
                        target=L321_diameter_mm[lens_index])
        current_row += 1
        MFE.AddOperand()
        zmx.set_MFE_row(op_types.DMLT, current_row, MFE, ZOSAPI,
                        param1val=L321_surf_num[lens_index] + 1,
                        weight=hardweight,
                        target=L321_diameter_mm[lens_index])

        current_row += 1
        MFE.AddOperand()
        zmx.set_MFE_row(op_types.DMVA,
                        current_row, MFE, ZOSAPI,
                        param1val=L321_surf_num[lens_index],
                        weight=0.0)

        current_row += 1
        MFE.AddOperand()
        zmx.set_MFE_row(op_types.DMVA,
                        current_row, MFE, ZOSAPI,
                        param1val=L321_surf_num[lens_index]+1,
                        weight=0.0)
        current_row += 1
        MFE.AddOperand()

        zmx.set_MFE_row(op_types.MAXX, current_row, MFE, ZOSAPI,
                    param1val=current_row - 2,
                    param2val=current_row -1,
                    target=L321_diameter_mm[lens_index] - 0.1,
                    weight=weights_for_exact_diameter[lens_index])
        current_row += 1
        MFE.AddOperand()
    return current_row

def write_thickness_constraints(MFE, start_at_row,
                                surfaces_to_control_thickness=[2, 4, 6, 9],
                                max_thickness=400.,
                                weight=1e5):
    MFE.AddOperand()
    current_row = start_at_row
    
    zmx.set_MFE_row(op_types.BLNK, current_row, MFE, ZOSAPI,
                        param1val= "Thickness constraints")

    MFE.AddOperand()
    current_row += 1

    zmx.set_MFE_row(op_types.TTHI, current_row, MFE, ZOSAPI,
                    param1val=2, param2val=11)
    MFE.AddOperand()
    current_row += 1
    MFE.AddOperand()

    zmx.set_MFE_row(op_types.OPLT, current_row, MFE, ZOSAPI, target=800,
                    weight=weight, param1val=current_row-1)
    MFE.AddOperand()
    current_row += 1
    MFE.AddOperand()

    for j, surf_num in enumerate(surfaces_to_control_thickness):
        zmx.set_MFE_row(op_types.CTLT, current_row, MFE, ZOSAPI,
                        param1val=surf_num, target=max_thickness,
                        weight=weight)
        MFE.AddOperand()
        current_row += 1
        MFE.AddOperand()

    for j, surf_num in enumerate(surfaces_to_control_thickness):
        zmx.set_MFE_row(op_types.CTGT, current_row, MFE, ZOSAPI,
                        param1val=surf_num, target=0.0,
                        weight=weight)
        MFE.AddOperand()
        current_row += 1
        MFE.AddOperand()
    return current_row


def write_fnumber(MFE, start_at_row,
                  Hx, Hy, direction):
    current_row = start_at_row
    Hx = float(Hx)
    Hy = float(Hy)

    zmx.set_MFE_row(op_types.BLNK, current_row, MFE, ZOSAPI,
            param1val= "fnum Hx,Hy: %1.2f %1.2f" % (Hx, Hy))


    MFE.AddOperand()
    current_row+=1
    if direction == 'x':
        zmx.set_MFE_row(op_types.REAX, current_row, MFE, ZOSAPI,
                        param1val=1, param2val=1, param3val=Hx, param4val=Hy,
                        param5val=1.0, param6val=0.0,
                        weight=0)
        MFE.AddOperand()
        current_row += 1
        zmx.set_MFE_row(op_types.REAX, current_row, MFE, ZOSAPI,
                        param1val=1, param2val=1, 
                        param3val=Hx, param4val=Hy, param5val=-1., param6val=0.,
                        weight=0)
        MFE.AddOperand()
    elif direction == 'y':
        zmx.set_MFE_row(op_types.REAY, current_row, MFE, ZOSAPI,
                        param1val=1, param2val=1, param3val=Hx, param4val=Hy,
                        param5val=0.0, param6val=1.0,
                        weight=0)
        MFE.AddOperand()
        current_row += 1
        zmx.set_MFE_row(op_types.REAY, current_row, MFE, ZOSAPI,
                        param1val=1, param2val=1, 
                        param3val=Hx, param4val=Hy, param5val=0., param6val=-1.,
                        weight=-0.0)
        MFE.AddOperand()
       
    current_row += 1
    zmx.set_MFE_row(op_types.DIFF, current_row, MFE, ZOSAPI,
                    param1val=current_row-2, param2val=current_row-1)
    MFE.AddOperand()
    current_row += 1
    zmx.set_MFE_row(op_types.CONS, current_row, MFE, ZOSAPI,
                    target=1e5)
    MFE.AddOperand()
    current_row +=1
    zmx.set_MFE_row(op_types.DIVI, current_row, MFE, ZOSAPI,
                    param1val=current_row-1, param2val=current_row-2)
    MFE.AddOperand()
    fnum_cell_num = current_row
    return fnum_cell_num


def write_fnum_constraint(MFE, start_at_row,
                          center_fnum_cell_num, side_fnum_cell_num,
                          max_ratio=1.12, weight=1e13):
    MFE.AddOperand()
    current_row = start_at_row
    zmx.set_MFE_row(op_types.BLNK, current_row, MFE, ZOSAPI,
                    param1val= "fnum")
    MFE.AddOperand()
    current_row += 1


    zmx.set_MFE_row(op_types.DIVI, current_row, MFE, ZOSAPI,
                    param1val=center_fnum_cell_num, param2val=side_fnum_cell_num)
    current_row += 1
    MFE.AddOperand()
    zmx.set_MFE_row(op_types.OPLT, current_row, MFE, ZOSAPI,
                    param1val=current_row-1, weight=weight, target=max_ratio)
    MFE.AddOperand()
    current_row += 1
    return current_row


def write_primary_footprint(MFE, start_at_row,
                            Hx, Hy, 
                            weight=5e6, Npoints=4):
    MFE.AddOperand()
    current_row = start_at_row
    zmx.set_MFE_row(op_types.BLNK, current_row, MFE, ZOSAPI,
                    param1val= "Primary footprint Hx, Hy: %1.2f, %1.2f" % (Hx, Hy))

    MFE.AddOperand()
    current_row += 1

    ts = np.linspace(0, 2*np.pi, Npoints+1)[:-1]

    start_row = start_at_row
    for t in ts:
        px = mt.cos(t)
        py = mt.sin(t)
        zmx.set_MFE_row(op_types.REAX,
                        current_row, MFE, ZOSAPI,
                        param1val=44,
                        param2val=1,
                        param3val=Hx,
                        param4val=Hy,
                        param5val=float(px),
                        param6val=py,
                        weight=0.)
        MFE.AddOperand()
        current_row+=1
    end_row = current_row-1
    zmx.set_MFE_row(op_types.OSUM,
                    current_row, MFE, ZOSAPI,
                    param1val=start_row,
                    param2val=end_row,
                    weight=weight,
                    target=0.0)

    MFE.AddOperand()
    current_row+=1
    start_row = current_row
    for t in ts:
        px = mt.cos(t)
        py = mt.sin(t)
        zmx.set_MFE_row(op_types.REAY,
                        current_row, MFE, ZOSAPI,
                        param1val=44,
                        param2val=1,
                        param3val=Hx,
                        param4val=Hy,
                        param5val=px,
                        param6val=py,
                        weight=0.)
        MFE.AddOperand()
        current_row+=1
    end_row = current_row-1
    zmx.set_MFE_row(op_types.OSUM,
                    current_row, MFE, ZOSAPI,
                    param1val=start_row,
                    param2val=end_row,
                    weight=weight,
                    target=0.0)
    MFE.AddOperand()
    current_row+=1
    return current_row


def write_telecentric_angle_cons(MFE, start_at_row,
                                 weight=1e4):
    Hxs = [0.0, 1.0, -1.0, 0.0,  0.0]
    Hys = [0.0, 0.0,  0.0, 1.0, -1.0]
    MFE.AddOperand()
    current_row = start_at_row
    zmx.set_MFE_row(op_types.BLNK, current_row, MFE, ZOSAPI,
                        param1val= "Telecentric angle")
    MFE.AddOperand()
    current_row+=1



    for j in range(len(Hxs)):
        Hx, Hy = Hxs[j], Hys[j]
        zmx.set_MFE_row(op_types.RAID,
                        current_row, MFE, ZOSAPI,
                        param1val=1,
                        param2val=1,
                        param3val=Hx,
                        param4val=Hy,
                        param5val=0.0,
                        param6val=0.0,
                        weight=0.0)
        MFE.AddOperand()
        current_row+=1
    zmx.set_MFE_row(op_types.MAXX,
                    current_row, MFE, ZOSAPI,
                    param1val=start_at_row,
                    param2val=current_row-1)
    current_row+=1
    zmx.set_MFE_row(op_types.OPLT,
                    current_row, MFE, ZOSAPI,
                    param1val=current_row-1,
                    target=2.5,
                    weight=1e10)
    current_row += 1
    return current_row

    
def write_primary_aperture_diameter(MFE, start_at_row, 
                                    weight=1e10,
                                    radius_mm=2450):
    def ap_diameter(px, py, Hxs, Hys, row_start,
                    direction):
        current_row = row_start
        for hxhy in zip(Hxs, Hys):
            Hx, Hy = hxhy
            zmx.set_MFE_row(op_types.REAX,
                            current_row, MFE, ZOSAPI,
                            param1val=44,
                            param2val=1,
                            param3val=float(Hx),
                            param4val=float(Hy),
                            param5val=px,
                            param6val=py)
            MFE.AddOperand()
            current_row+=1
        MFE.AddOperand()
        if direction == 'xp':
            op_type = op_types.MINN
        elif direction == 'xm':
            op_type = op_types.MAXX
        zmx.set_MFE_row(op_type,
                        current_row, MFE, ZOSAPI,
                        param1val=row_start,
                        param2val=current_row-1)
        current_row+=1
        return current_row


    zmx.set_MFE_row(op_types.BLNK, start_at_row, MFE, ZOSAPI,
                        param1val= "Radius")
    MFE.AddOperand()
    start_at_row+=1

   

    Hxs = list(np.arange(-1.0, 1.1, 0.1))
    Hys = [0.0] * len(Hxs)
    px, py = -1.0, 0.0
    row1 = ap_diameter(px, py, Hxs, Hys, start_at_row,
                      'xm')

    px, py = 1.0, 0.0
    row2 = ap_diameter(px, py, Hxs, Hys, row1,'xp')
    
    current_row = row2
    zmx.set_MFE_row(op_types.CONS,
                    current_row, MFE, ZOSAPI,
                    target=-1)

    MFE.AddOperand()
    current_row+=1
    zmx.set_MFE_row(op_types.PROD,
                    current_row, MFE, ZOSAPI,
                    param1val=current_row-1,
                    param2val=current_row-2)

    MFE.AddOperand()
    current_row+=1
    zmx.set_MFE_row(op_types.OPVA,
                    current_row, MFE,ZOSAPI,
                    param1val=row1-1)

    MFE.AddOperand()
    current_row+=1
    zmx.set_MFE_row(op_types.MAXX,
                    current_row, MFE, ZOSAPI,
                    param1val=current_row-2,
                    param2val=current_row-1,
                    target=radius_mm,
                    weight=weight)

    MFE.AddOperand()
    current_row+=1
    zmx.set_MFE_row(op_types.BLNK, current_row, MFE, ZOSAPI,
                        param1val= "Collimate")
 

    MFE.AddOperand()
    current_row+=1
    zmx.set_MFE_row(op_types.EQUA,
                    current_row, MFE, ZOSAPI,
                    param1val=start_at_row,
                    param2val=row1-2,
                    weight=1e5)

    MFE.AddOperand()
    current_row+=1
    zmx.set_MFE_row(op_types.EQUA,
                    current_row, MFE, ZOSAPI,
                    param1val=row1,
                    param2val=row1 + (row1-start_at_row)-2,
                    weight=1e5)


    return current_row

def write_img_qual_MF(MFE, row_start, weight):
    w = MFE.SEQOptimizationWizard
    w.Data=1
    w.OverallWeight=weight
    w.Ring = 5;
    w.Arms=1
    
    w.IsGlassUsed = False;
    w.IsAirUsed = False
    w.IsAssumeAxialSymmetryUsed = False
    w.Configuration = 1

    w.StartAt = row_start+3
    w.Apply();
    MFE.RemoveOperandAt(row_start+5)


initialize_merit_function(MFE)

current_row = write_L321_diameter_constraints(MFE, 3, L321_surf_num, L321_diameter_mm)

current_row = write_thickness_constraints(MFE, current_row+1)

f_cen_row = write_fnumber(MFE, current_row+1, 0, 0, 'x')
f_side1_row = write_fnumber(MFE, f_cen_row+1, 0, 1, 'x')
f_side2_row = write_fnumber(MFE, f_side1_row+1, 0, 1, 'y')

current_row = write_fnum_constraint(MFE, f_side2_row+1,
                      f_side2_row, f_cen_row)

weight_pri_footprint = 1e6
current_row = write_primary_footprint(MFE, current_row, 
                                      0.0, 0.0,
                                      Npoints=16,
                                      weight=weight_pri_footprint)

current_row = write_primary_footprint(MFE, current_row, 
                                      1.0, 0.0,
                                      Npoints=16,
                                      weight=weight_pri_footprint)

current_row = write_primary_footprint(MFE, current_row, 
                                      -1.0, 0.0,
                                      Npoints=16,
                                      weight=weight_pri_footprint)

current_row = write_primary_footprint(MFE, current_row, 
                                      0.0, 1.0,
                                      Npoints=16,
                                      weight=weight_pri_footprint)

current_row = write_primary_footprint(MFE, current_row, 
                                      0.0, -1.0,
                                      Npoints=16,
                                      weight=weight_pri_footprint)

current_row = write_telecentric_angle_cons(MFE, 
                                           current_row+1)

current_row = write_primary_aperture_diameter(MFE, current_row+1,
                                              radius_mm=2450.0)

write_img_qual_MF(MFE, current_row, weight=0.5)

TheSystem.UpdateStatus()

import os
fname_out = os.path.join(os.path.abspath('./'),
                         'groups_info/merit_function.MF')
MFE.SaveMeritFunction(fname_out)
