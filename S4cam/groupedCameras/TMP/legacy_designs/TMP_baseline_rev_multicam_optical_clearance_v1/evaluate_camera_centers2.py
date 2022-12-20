import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_hdf('cameracoords/coords.hdf')
df['camnum'] = np.arange(1, 86)
df.to_csv("cameracoords/coords.csv")

ax = plt.subplot()
plt.scatter(df.xpos, df.ypos)
ax.set_aspect('equal')
for j in range(1, 86):
    x = df.xpos.values[j-1]
    y = df.ypos.values[j-1]
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
    x = df.xpos.values[j-1]
    y = df.ypos.values[j-1]
    string = "(%i, %1.2f, %1.2f) &" % (j, x, y)
    string_out += string
    if j%4 == 0:
        string_out += "\\\\\n"
print(string_out)
with open("cameracoords/table.tex", 'w') as f:
    f.write(string_out)
