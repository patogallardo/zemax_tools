# TMA design analysis

|Name           |Layout                                           |Img quality                                                   |   Telecentricity                                    |F/#        |
|---            |---                                              |---                                                           |---                                                  |---        |
|[SP TMA](TmaV1_SP)         |[png](TmaV1_SP/layout/3DLayout.png)  |[focal plane](TmaV1_SP/strehls/focal_plane_strehls.png)| [<2.8 deg](TmaV1_SP/chief_ray/chief_ray_angles_map.png)  |3.70 [map](TmaV1_SP/fNumbers/fnumber_av.png) [hist](TmaV1_SP/fNumbers/fnumber_hists.png)          |
|[PAG f/3.0](PAG_F3p0)      |[png](PAG_F3p0/layout/3DLayout.png)  |[focal plane](PAG_F3p0/strehls/focal_plane_strehls.png)  |  [<12 deg](PAG_F3p0/chief_ray/chief_ray_angles_map.png)  |3.03 [map](PAG_F3p0/fNumbers/fnumber_av.png) [hist](PAG_F3p0/fNumbers/fnumber_hists.png)          |
|[MDN f/3.3](MDN_F3p3)      |[png](MDN_F3p3/layout/3DLayout.png)  |[focal plane](MDN_F3p3/strehls/focal_plane_strehls.png)|   [<7 deg](MDN_F3p3/chief_ray/chief_ray_angles_map.png)  |3.39 [map](MDN_F3p3/fNumbers/fnumber_av.png) [hist](MDN_F3p3/fNumbers/fnumber_hists.png)          |
|[PAG f/3.4](PAG_F3p4)      |[png](PAG_F3p4/layout/3DLayout.png)  |[focal plane](PAG_F3p4/strehls/focal_plane_strehls.png)  | [<3.8 deg](PAG_F3p4/chief_ray/chief_ray_angles_map.png)  |3.47 [map](PAG_F3p4/fNumbers/fnumber_av.png) [hist](PAG_F3p4/fNumbers/fnumber_hists.png)          |
|[RH f/3.0](RH_F3p0)        |[png](RH_F3p0/layout/3DLayout.png)   |[focal plane](RH_F3p0/strehls/focal_plane_strehls.png)  | [<6.5 deg](RH_F3p0/chief_ray/chief_ray_angles_map.png)  |3.03 [map](RH_F3p0/fNumbers/fnumber_av.png) [hist](RH_F3p0/fNumbers/fnumber_hists.png)          |
|[RH f/3.5 10x10](RH_TMP_f3p5_10x10) |[png](RH_TMP_f3p5_10x10/layout/3DLayout.png) | [focal plane](RH_TMP_f3p5_10x10/strehls/focal_plane_strehls.png) | [<5.3 deg](RH_TMP_f3p5_10x10/chief_ray/chief_ray_angles_map.png) | 3.47 [map](RH_TMP_f3p5_10x10/fNumbers/fnumber_av.png) [hist](RH_TMP_f3p5_10x10/fNumbers/fnumber_hists.png) |



* Image quality is obtained by a rms-field map in Zemax. Focal plane map is obtained by mapping Strehl ratios across a rectangular grid in field space and mapping angles to focal plane coordinates via chief-ray positions and a linear bidimensional interpolation.
* Telecentricity angle is obtained by tracing the chief-ray and using the z-axis cosine at the image plane surface.
* F/# is obtained by tracing the chief-ray and marginal rays in the x, and y directions. F/# is computed with the dot product of the direction vector of the marginal ray and the chief ray for each case. f/# is then averaged in the x-y direcitons as 0.25(f_x- + f_x+ + f_y- + f_y+) where f_x+ denotes the f number in the positive x direction and so forth.

## Vignetting

This analysis was done setting a tertiary diameter based in SPV1TMA as an upper bound. Outer white areas in maps are vignetted areas for the marginal rays.
