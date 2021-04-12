import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
import numpy as np  # noqa

# this script generates the aperture file for a hexagonal surface given
# the radius. One nice aperture plot is also generated.

show = False
center = [0, 0]
angle = 0
r_hex = 106.8098
zmx_txt = "POL 0 0 %3.3f 6 30" % r_hex

fig, ax = plt.subplots(figsize=[8, 8.5])
ax.axis('equal')


patches = []
p = RegularPolygon(xy=center,
                   radius=r_hex,
                   numVertices=6,
                   orientation=angle,
                   fill=False,
                   edgecolor='black',
                   lw=3)
ax.add_artist(p)

c = Circle(center, r_hex,
           fill=False,
           edgecolor='black',
           lw=2,
           ls='--')
ax.add_artist(c)


c2 = Circle(center,
            r_hex * np.sqrt(3)/2,
            fill=False,
            edgecolor='black',
            lw=1,
            ls='--')
ax.add_artist(c2)

ax.annotate('',
            xy=r_hex*np.array([np.cos(30/180*np.pi),
                               np.sin(30/180*np.pi)]),
            xytext=(0, 0),
            arrowprops=dict(facecolor='black', shrink=0.05)
            )
ax.text(r_hex/2.0*np.cos(30/180*np.pi),
        r_hex/2.0*np.sin(30/180*np.pi),
        '$r_{circ}$=%3.1f mm' % r_hex,
        ha='right',
        va='bottom')

ax.annotate('',
            xy=r_hex*np.array([1, 0])*np.sqrt(3)/2,
            xytext=(0, 0),
            arrowprops=dict(facecolor='black', shrink=0.05))
ax.text(r_hex*np.sqrt(3)/2/2,
        -5,
        '$r_{ins}$=%3.1f mm' % (r_hex*np.sqrt(3)/2),
        ha='center',
        va='top')
plt.figtext(0.8, 0.115, zmx_txt, fontsize=5)

ax.set_title('Window Aperture')
ax.set_xlim(1.2*-r_hex, 1.2*r_hex)
ax.set_ylim(1.2*-r_hex, 1.2*r_hex)
if show:
    plt.show()
else:
    plt.savefig('plots/window.png', dpi=150)
    plt.savefig('plots/window.pdf')

with open(r'C:\Users\pgall\Documents\Zemax\Objects\Apertures\S4cam_hex_window_aperture.UDA', 'w') as f:  # noqa
    f.write(zmx_txt)
