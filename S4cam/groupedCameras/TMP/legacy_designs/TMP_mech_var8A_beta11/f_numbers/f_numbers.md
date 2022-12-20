# TMP Var8A cam beta 11 F/#

This design was optimized to allow a maximum f/# variation of 12% and a maximum telecentric angle at the focal plane of 2.5 degrees.

![](./raytrace_cam1.png)
![](chiefray_raytrace.png)

This can be checked by looking at the footprints at L3
![](L3_back.png)
Or by looking at a screen at 100 meters from the focal plane in the direction of L3.
![](footrprints_at_infty.png)

On this surface we can then fit ellipses to each field position and evaluate the semi-axes (a, b) for these. This fitting is better than we have done in the past as it allows the ellipse to be rotated in an arbitrary angle.

The solid angle for this ellipse is![](formulas/solidangle.png) while for a rotationally symmetric cone we get  ![](formulas/angle.png). If we want to convert the elliptical solid angle into a single angle cone with the same solid angle then ![](formulas/theta.png) and the equivalent f/# is

![](formulas/f_numb.png).


With this in mind we can visualize the following:

## Semi axis angles
![](a/a_conf_01.png)
![](b/b_conf_01.png)
## Solid angle
![](solidangle/solidangle_conf_01.png)
## Ellipticity (a/b)
![](ellipticity/ellipticity_map_conf_01.png)
## Equivalent f/#
![](equivalent_f_number/eq_f_n_01.png)
![](equivalent_f_number/eq_fn_01_hist.png)
For the center camera we will have an average f/#=1.9 with a minimum of 1.84 and a max of 2.01.
## All camera f/# metrics
Are in file f_numbers.csv

# Caveats

**Vignetting** is the biggest effect, in the last meeting we showed that if we are able to displace the window positions, we can have the three inner rings unobstructed (0.37 deg semi fov), for these cameras the calculation here will hold.

For the outer two rings, vignetting will reduce the fov, for which the f/# will have to increase.
