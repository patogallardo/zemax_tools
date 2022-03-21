'''This takes a npz file with best fits and fills up
the MC editor rows with appropriate numbers.

P. Gallardo 2021-10-22
'''
import zmx_api
import numpy as np

pri_fit_fname = './5th_order_fits/Primary_model_parameters_deg_5.npz'
ter_fit_fname = '5th_order_fits/Tertiary_model_parameters_deg_5.npz'

pri_fit_data = np.load(pri_fit_fname)
ter_fit_data = np.load(ter_fit_fname)

A_pri = pri_fit_data['A']
A_ter = ter_fit_data['A']
degree = int(pri_fit_data['degree'])
A_sec = A_pri * 0.64
A_zeros = np.zeros(len(A_pri))

print("Pri: coefficients are:", A_pri)
print("Ter: coefficients are:", A_ter)
print("Sec: coefficients are:", A_sec)

TheSystem, ZOSAPI, ZOSAPI_NetHelper = zmx_api.connect_zmx_interactive()
MCE = TheSystem.MCE


def write_params(starting_operand_row,
                 how_many_operand_rows,
                 copy_from_conf,
                 target_conf,
                 A,
                 replace=False,
                 MCE=MCE):
    for mce_row in range(starting_operand_row,
                         starting_operand_row + how_many_operand_rows):
        op = MCE.GetOperandAt(mce_row)  # read origin
        original_value = op.GetOperandCell(copy_from_conf).DoubleValue
        targetCell = op.GetOperandCell(target_conf)  # target
        delta_coeff = A[mce_row - starting_operand_row + 1]
        if replace:
            targetCell.DoubleValue = delta_coeff
        else:
            targetCell.DoubleValue = original_value + delta_coeff


# add deformations
starting_operand_row = 9  # primary
how_many_operand_rows = 17
copy_from_conf = 1
target_conf = 2  # gravitational

# configuration 2, combined
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_pri, MCE=MCE,
             replace=False)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_sec, MCE=MCE,
             replace=False)

starting_operand_row = 45  # tert
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_ter, MCE=MCE,
             replace=False)


# configuration 3, gravity alone
target_conf = 3  # gravity
starting_operand_row = 9
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_pri, MCE=MCE,
             replace=False)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_sec, MCE=MCE,
             replace=False)

starting_operand_row = 45  # tert
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_ter, MCE=MCE,
             replace=False)
# configuration 4, thermal alone, do nothing
# configuration 5, gravity primary

target_conf = 5 
starting_operand_row = 9
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_pri, MCE=MCE,
             replace=False)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_zeros, MCE=MCE,
             replace=False)

starting_operand_row = 45
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_zeros, MCE=MCE,
             replace=False)

# configuration 6, gravity secondary

target_conf = 6  # test
starting_operand_row = 9
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_zeros, MCE=MCE,
             replace=False)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_sec, MCE=MCE,
             replace=False)

starting_operand_row = 45
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_zeros, MCE=MCE,
             replace=False)

# configuration 7, gravity ter

target_conf = 7  # test
starting_operand_row = 9
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_zeros, MCE=MCE,
             replace=False)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_zeros, MCE=MCE,
             replace=False)

starting_operand_row = 45
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_ter, MCE=MCE,
             replace=False)

# configuration 12 Test grav
target_conf = 12  # gravitational

write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_pri, MCE=MCE,
             replace=True)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_sec, MCE=MCE,
             replace=True)

starting_operand_row = 45  # tert
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A_ter, MCE=MCE,
             replace=True)
