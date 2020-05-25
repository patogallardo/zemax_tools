# TMA design analysis

|Name           |Layout                               |Img quality                                                   |   Telecentricity                                    |F/#        |
|---            |---                                  |---                                                           |---                                                  |---        |
|SP TMA         |[png](TmaV1_SP/layout/3DLayout.png)  |[focal plane](TmaV1_SP/strehls/TmaV1x_focal_plane_strehls.png)|[plot](TmaV1_SP/chief_ray/chief_ray_angles_map.png)  |           |
|PAG f/3.0      |[png](PAG_F3p0/layout/3DLayout.png)  |[focal plane](PAG_F3p0/strehls/F3p0_focal_plane_strehls.png)  |[plot](PAG_F3p0/chief_ray/chief_ray_angles_map.png)  |           |
|MDN            |[png](MDN_F3p3/layout/3DLayout.png)  |[focal plane](MDN_F3p3/strehls/TmaV1x_focal_plane_strehls.png)|[plot](MDN_F3p3/chief_ray/chief_ray_angles_map.png)  |           |
|PAG F/3.4      |[png](PAG_F3p4/layout/3DLayout.png)  |[focal plane](PAG_F3p4/strehls/F3p4_focal_plane_strehls.png)  |[plot](PAG_F3p4/chief_ray/chief_ray_angles_map.png)  |           |


* Image quality is obtained by a rms-field map in Zemax. Focal plane map is obtained by mapping Strehl ratios across a rectangular grid in field space and mapping angles to focal plane coordinates via chief-ray positions and a linear bidimensional interpolation.
* Telecentricity angle is obtained by tracing the chief-ray and using the z-axis cosine at the image plane surface.
* F/# is obtained by tracing the chief-ray and marginal rays in the x, and y directions. F/# is computed with the dot product of the direction vector of the marginal ray and the chief ray for each case. f/# is then averaged in the x-y direcitons as 0.25(f_x- + f_x+ + f_y- + f_y+) where f_x+ denotes the f number in the positive x direction and so forth.
