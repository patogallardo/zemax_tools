# Time reverse system

The time reverse optimization seems to be working better now. The stop size
needs to be fixed before the optimization starts, and the merit function seems
to be able to find a system with good strehls that respects a clearance at the primary and lenses.

For instance, here I show the result of optimizing for a 40mm Lyot stop
diameter and an illumination of 2450mm at the primary. This system gives a
15.5 deg half angle.

![](layout_40mm_stopdia.png)

![](MF3_footprints.png)

![](img_qual.png)

# Effect of stop size in half angle

I tested three stop (35, 40, 45mm) sizes to explore the effect in the overall design.

Smaller stop sizes give shorter cameras, with higher lens curvatures.

Half angle tends to increase with wider stop sizes, 15.3 deg at 35 mm stop size, 15.47 at 40 mm and 15.57 deg at 45 mm.

![](../varying_stop_size_study/3DLayout_stop_35mm.png)
![](../varying_stop_size_study/3DLayout_stop_40mm.png)
![](../varying_stop_size_study/3DLayout.png)

# f/# metric

Up to now, we have been reporting f/#=1/(2tan(h)), with h the half angle at
the focal plane.

The optics literature however uses f/#=1/(2sin(h)), these two are similar for high f/# but at f/1.8 they start to deviate. What metric do we need to for the sensitivity calculations?

I reviewed some textbooks, here's what I found: 1) Hecht, defines f/#=f/D then switches to 1/2NA, 2) The handbook of optics by M. Bass has a section called "the f-numbers and its problems", where they basically say stay away from the tan(h) formalism.

More info here:
https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.183.4748&rep=rep1&type=pdf

https://wp.optics.arizona.edu/jpalmer/wp-content/uploads/sites/65/2018/11/f_word.pdf


## Next steps
Implement 85 cameras and group them

![](85camstatus.png)
