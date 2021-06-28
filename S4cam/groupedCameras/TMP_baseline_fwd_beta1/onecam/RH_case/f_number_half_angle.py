import numpy as np
import matplotlib.pyplot as plt

half_angle = np.linspace(15, 18, 100)
half_angle_rad = np.deg2rad(half_angle)

one_over_2_sin = 1/(2 * np.sin(half_angle_rad))
one_over_2_tg = 1/(2 * np.tan(half_angle_rad))


plt.plot(one_over_2_sin, one_over_2_tg)
plt.plot(one_over_2_sin,
         one_over_2_sin, color='black', label='no error line')
angle_center_pix_rad = np.arctan(29622.9001/1e5)
plt.scatter([1/(2*np.sin(angle_center_pix_rad))],
            [1/(2*np.tan(angle_center_pix_rad))],
            label='center_pix')
plt.xlabel('$\\frac{1}{2 \\sin(\\theta)}$')
plt.ylabel('$\\frac{1}{2 \\tan(\\theta)}$')
plt.legend()
plt.grid()
plt.savefig('f_num.pdf')
