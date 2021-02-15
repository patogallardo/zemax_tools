import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import hexlattice
import os

Ngroups = 5
scale = 219/np.sqrt(3)
df = hexlattice.gen85CamPosition(scale=scale)

fig, ax = plt.subplots(figsize=[8, 8])
coll = ax.scatter(df.x.values, df.y.values,
                  color=["C0"]*len(df),
                  picker=5,
                  s=[50]*len(df))
plt.grid(True)
ax.set_aspect('equal')
plt.axis()


def on_pick(event):
    print(df.loc[event.ind], "clicked")
    coll._facecolors[event.ind, :] = matplotlib.colors.to_rgba("C1")
    coll._edgecolors[event.ind, :] = matplotlib.colors.to_rgba("C1")
    fig.canvas.draw()


class camSelect:
    def __init__(self, coll, df):
        self.group_indices = [[] for j in range(Ngroups)]  # stores indices
        self.current_group_indx = 0  # currently selecting this group
        self.coll = coll
        self.df = df
        df['group'] = np.zeros(len(df), dtype='int') + 1000
        self.cid = coll.figure.canvas.mpl_connect("key_press_event",
                                                  self.press)
        self.cid2 = coll.figure.canvas.mpl_connect("pick_event",
                                                   self.on_click)
        plt.show()
        for j in range(Ngroups):
            df.loc[df.index[self.group_indices[j]], 'group'] = j

    def press(self, event):
        print("press")
        self.current_group_indx += 1
        if self.current_group_indx == Ngroups:
            print("selected all groups!")
            self.current_group_indx = 1000
            plt.close()

    def on_click(self, event):
        print("click:", self.df.loc[event.ind])
        j = self.current_group_indx
        self.group_indices[j].append(event.ind[0])  # store index
        self.coll._facecolors[event.ind, :] = matplotlib.colors.to_rgba("C%i" %(j+1))  # noqa
        self.coll._edgecolors[event.ind, :] = matplotlib.colors.to_rgba("C%i" %(j+1))  # noqa
        fig.canvas.draw()


c = camSelect(coll, df)
df.sort_values(['group', 'ring', 'angle'], ignore_index=True, inplace=True)

df.to_csv('85cam_groups.csv')
hexlattice.plot_df(df, 100*0.8, show=True)

os.system('python plot_grouped_cams.py')
