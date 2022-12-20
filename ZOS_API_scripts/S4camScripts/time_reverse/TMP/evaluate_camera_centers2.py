import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_hdf('cameracoords/coords.hdf')
df['camnum'] = np.arange(1, 86)
df.to_csv("cameracoords/coords.csv")

ax = plt.subplot()
plt.scatter(df.x_cam_center, df.y_cam_center)
ax.set_aspect('equal')
for j in range(1, 86):
    x = df.x_cam_center.values[j-1]
    y = df.y_cam_center.values[j-1]
    string = "%i\nx=%1.2f\ny=%1.2f" % (j, x, y)
    plt.text(x,
             y+20,
             string,
             ha='center',
             va='bottom',
             fontsize=6)
ax.tick_params(left=False, bottom=False)
ax.set(yticklabels=[])
ax.set(xticklabels=[])
ax.axis('off')
plt.tight_layout()
plt.savefig('cameracoords/camcoords.pdf')
plt.close()

string_out = ""
for j in range(1, 86):
    x = df.x_cam_center.values[j-1]
    y = df.y_cam_center.values[j-1]
    string = "(%i, %1.2f, %1.2f) &" % (j, x, y)
    string_out += string
    if j%4 == 0:
        string_out += "\\\\\n"
print(string_out)
with open("cameracoords/cam_centers.tex", 'w') as f:
    f.write(string_out)


ax = plt.subplot()
plt.scatter(df.x_window_center, df.y_window_center)
ax.set_aspect('equal')
for j in range(1, 86):
    x = df.x_window_center.values[j-1]
    y = df.y_window_center.values[j-1]
    string = "%i\nx=%1.2f\ny=%1.2f" % (j, x, y)
    plt.text(x,
             y+20,
             string,
             ha='center',
             va='bottom',
             fontsize=6)
ax.tick_params(left=False, bottom=False)
ax.set(yticklabels=[])
ax.set(xticklabels=[])
ax.axis('off')
plt.tight_layout()
plt.savefig('cameracoords/window_coords.pdf')
plt.close()

ax = plt.subplot()
plt.scatter(df.x_window_center - df.x_cam_center,
            df.y_window_center - df.y_cam_center)
ax.set_aspect('equal')
for j in range(1, 86):
    x = df.x_window_center.values[j-1] - df.x_cam_center.values[j-1]
    y = df.y_window_center.values[j-1] - df.y_cam_center.values[j-1]
    string = "%i\nx=%1.2f\ny=%1.2f" % (j, x, y)
    plt.text(x,
             y+0.5,
             string,
             ha='center',
             va='bottom',
             fontsize=5)
ax.tick_params(left=False, bottom=False)
ax.set(yticklabels=[])
ax.set(xticklabels=[])
ax.axis('off')
plt.tight_layout()
plt.savefig('cameracoords/window_offsets.pdf')
plt.close()



string_out = ""
for j in range(1, 86):
    x = df.x_window_center.values[j-1]
    y = df.y_window_center.values[j-1]
    string = "(%i, %1.2f, %1.2f) &" % (j, x, y)
    string_out += string
    if j%4 == 0:
        string_out += "\\\\\n"
print(string_out)
with open("cameracoords/window_centers.tex", 'w') as f:
    f.write(string_out)
