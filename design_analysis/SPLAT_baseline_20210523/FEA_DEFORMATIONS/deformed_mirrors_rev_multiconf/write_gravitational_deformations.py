'''This takes a npz file with best fits and fills up
the MC editor rows with appropriate numbers.

P. Gallardo 2021-10-22
'''
import zmx_api
import numpy as np

fit_fname = '../deformation_fits/model_parameters_deg_5.npz'
fit_data = np.load(fit_fname)
A = fit_data['A']
degree = int(fit_data['degree'])
print("coefficients are:", A)
A_sec = A * 0.64

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
starting_operand_row = 9
how_many_operand_rows = 17
copy_from_conf = 1
target_conf = 2  # gravitational

write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A, MCE=MCE,
             replace=False)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_sec, MCE=MCE,
             replace=False)

starting_operand_row = 45  # tert
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A, MCE=MCE,
             replace=False)


target_conf = 4  # combined
starting_operand_row = 9
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A, MCE=MCE,
             replace=False)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_sec, MCE=MCE,
             replace=False)

starting_operand_row = 45  # tert
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A, MCE=MCE,
             replace=False)


target_conf = 6  # test
starting_operand_row = 9
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A, MCE=MCE,
             replace=True)

starting_operand_row = 27  # sec
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, A_sec, MCE=MCE,
             replace=True)

starting_operand_row = 45
write_params(starting_operand_row, how_many_operand_rows,
             copy_from_conf, target_conf, -1*A, MCE=MCE,
             replace=True)
