from hexlattice import *

order = 5
patches = []
rotation = np.pi/2*0

df = gen_hex_layout(order, clip_edges=True)
hex_x, hex_y, x, y = df.hex_x.values, df.hex_y.values, df.x.values, df.y.values

for x_coord,y_coord in zip(x,y):
    p = RegularPolygon([x_coord, y_coord], 6, 0.8, rotation)
    patches.append(p)


collection = PatchCollection(patches)

fig, ax = plt.subplots(figsize=[8,8])
ax.add_collection(collection)
plt.scatter(x, y, color='black', marker='.')

for j in range(len(x)):
    plt.text(x[j], y[j]+0.05, '(%i, %i)' %(hex_x[j], hex_y[j]),
             ha='center', va='bottom' )

plt.title('Order: %i' % order)

ax.set_aspect('equal')
plt.xlim([np.min(x) - 1.5, np.max(x) + 1.5])
plt.ylim([np.min(y) - 1.5, np.max(y) + 1.5])

plt.savefig('hexgrid.png', dpi=150)
plt.show()
