import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
import numpy as np  # noqa

# this script generates the aperture file for a hexagonal surface given
# the radius. One nice aperture plot is also generated.

show = False
orientation = 0
center = [0, 0]
r_mech = 65.0
r_det_center = 61.4

zmx_txt = "POL 0 0 %3.3f 6 30" % r_mech

fig, ax = plt.subplots(figsize=[8, 8.5])
ax.axis('equal')

# plot detector centers
edg_angle = np.deg2rad(np.arange(30, 360, 60))
x, y = r_det_center * np.cos(edg_angle), r_det_center * np.sin(edg_angle)
plt.scatter(x, y,
            color='black',
            marker='.',
            label='edge det centers')
plt.legend()
# end plot det centers

# plot mechanical hexagon
patches = []
p = RegularPolygon(xy=center,
                   radius=r_mech,
                   numVertices=6,
                   orientation=orientation,
                   fill=False,
                   edgecolor='black',
                   lw=3)
ax.add_artist(p)

c = Circle(center, r_mech,
           fill=False,
           edgecolor='black',
           lw=2,
           ls='--')
ax.add_artist(c)

c2 = Circle(center,
            r_mech * np.sqrt(3)/2,
            fill=False,
            edgecolor='black',
            lw=1,
            ls='--')
ax.add_artist(c2)
# end plot mechanical hexagon

# plot dimensions and radii
ax.annotate('',
            xy=r_mech*np.array([np.cos(30/180*np.pi),
                               np.sin(30/180*np.pi)]),
            xytext=(0, 0),
            arrowprops=dict(facecolor='black', shrink=0.01)
            )
ax.text(r_mech/2.0*np.cos(30/180*np.pi),
        r_mech/2.0*np.sin(30/180*np.pi),
        '$r_{mech}$=%3.1f mm' % r_mech,
        ha='right',
        va='bottom')

ax.annotate('',
            xy=r_mech*np.array([1, 0])*np.sqrt(3)/2,
            xytext=(0, 0),
            arrowprops=dict(facecolor='black', shrink=0.01))
ax.text(r_mech*np.sqrt(3)/2/2,
        -5,
        '$r_{ins}$=%3.1f mm' % (r_mech*np.sqrt(3)/2),
        ha='center',
        va='top')

ax.annotate('',
            xy=np.array([0, -1]) * r_det_center,
            xytext=(0, 0),
            arrowprops=dict(facecolor='black', shrink=0.01))
ax.text(5, -r_det_center/2.0,
        '$r_{det~cnt}$=%3.1f mm' % r_det_center,
        ha='left',
        va='center')

plt.figtext(0.8, 0.115, zmx_txt, fontsize=5)

ax.set_title('Focal Plane')
ax.set_xlim(1.2*-r_mech, 1.2*r_mech)
ax.set_ylim(1.2*-r_mech, 1.2*r_mech)
if show:
    plt.show()
else:
    plt.savefig('plots/focal_plane.png', dpi=150)
    plt.savefig('plots/focal_plane.pdf')

with open(r'C:\Users\pgall\Documents\Zemax\Objects\Apertures\S4cam_hex_focal_plane.UDA', 'w') as f:  # noqa
    f.write(zmx_txt)
