# TMP Var 8 cam beta 1

The TMPVar8 LAT was optimized to eliminate the tilt at the cryostat entrance
and to minimize the wedge tilt angle needed to keep all cameras parallel.

As it can be seen in the following figure, the minimum wedge tilt is located
higher than in previous iterations of the TMP telescope, this helps distributing
the wedge tilts more evenly between the top and bottom part of the focal plane.

![](layout/wedges_front.png)

![](layout/wedges_side.png)

This gives a maximum sag of ~11.4mm peak to peak in the alumina wedge.

![](sags/wedge/sag_cam_69.JPG)

The design shown was produced optimizing all cameras one by one.

![](layout/3DLayout2.png)

![](layout/layout_side.png)

![](layout/3dLayout1.png)

This design was made placing the first lens 2 inches from the focal point at the center field, the wedge is placed 1 inch from the focus. This yields a L1 semi-fov of ~0.38 deg, which gives 38.5 sq deg solid angle, ~55% of the total TMP solid angle.

![](Footprints/L1/footprint_cam_01.JPG)

## Next steps:

* Incorporate changes to the merit function proposed by RH.
* Iterate on lens 1 placement to improve camera fov
* Produce a grouped design
* Evaluate camera Strehls in the grouped configuration.
