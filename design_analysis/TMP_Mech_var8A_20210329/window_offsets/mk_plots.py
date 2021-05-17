import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # noqa

show = False

fname = 'window_offsets.csv'
df = pd.read_csv(fname)
x_mm = df.x_mm.values
y_mm = df.y_mm.values

V8A_dx = df['8A_dx'].values
V8A_dy = df['8A_dy'].values

V10C_dx = df['10C_dx'].values
V10C_dy = df['10C_dy'].values


# plot 8A differences
plt.figure(figsize=[8, 8])
plt.scatter(V8A_dx, V8A_dy, label='8A')
# end 8A differences

# plot 10C differences
plt.scatter(V10C_dx, V10C_dy, label='10C')

plt.legend()
for j in range(len(V10C_dx)):
    plt.text(V10C_dx[j], V10C_dy[j],
             '%i' % (j+1),
             ha='left', va='bottom')
# end 10C differences

plt.title('Window displacements')
plt.xlabel('dx [mm]')
plt.ylabel('dy [mm]')

plt.axis('equal')

if show:
    plt.show()
else:
    plt.savefig('window_displacements.png')
    plt.savefig('window_displacements.pdf')
