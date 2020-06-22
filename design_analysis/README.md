# TMA design analysis

|Name         | f/# | fov [deg^2] | focal plane [m^2] | M1, M2, M3 (2rx,2ry)[mm] | M1, M2, M3 sag[mm]| cr-boresight angle [deg] |
| ---| --- |--- |--- | --- | --- | --- |
[TMPf2p5_c2p2A](20200611_RH_TMPf2p5_c2p2A) |2.47 |82.6 |4.1| (5002, 5865), (3216, 4738), (5194, 5500)|243, 444,445| 15.5|
[TMPf2p8_c2p2A](20200611_RH_TMPf2p8_c2p2A) |2.75 |65.4 |4.0| (5001, 5818), (3280, 4446), (5238, 5499)|226, 335,348| 13.6|  
[TMPf3p0C2p8](20200617_RH_TMPf3p0C2p8)   |3.00 |92.0 |6.7| (5001, 5535), (3217, 4301), (5244, 5499)|189, 330, 386| 17.5|  
[TMPf3p1_c2p9A](20200611_RH_TMPf3p1_c2p9A) |3.11 |88.8 |6.9| (5001, 5556), (3188, 4294), (5216, 5500)|195, 336, 367| 16.5|
[TMPf3p15C2p8](20200617_RH_TMPf3p15C2p8)  |3.16 |83.7 |6.7| (5001, 5503), (3260, 4237), (5222, 5500)|177, 283, 341| 12.9|
[TMPf3p25_c2p9A](20200611_RH_TMPf3p25_c2p9A)|3.27 |80.0 |6.8| (5000, 5503), (3185, 4126), (5203, 5499)|189, 289, 328| 14.1|
[TMPf3p3_c3p2A](20200611_RH_TMPf3p3_c3p2A) |3.32 |93.4 |8.3| (5001, 5603), (3032, 2103), (5196, 5500)|219, 278, 383| 20.4| 
[TMPf3p6_c3p2A](20200611_RH_TMPf3p6_c3p2A) |3.61 |79.7 |8.2| (5500, 5480), (3130, 3985), (5218, 5499)|183, 275, 312| 15.5|
[TmaV1_SP](TmaV1_SP)      |3.70 |62.3 |6.6| [(5100, 5628), (3700, 3779), (5500, 4742)](https://github.com/patogallardo/zemax_tools/blob/master/design_analysis/TmaV1_SP/cad/TmaV1x.PDF)|[155,133,249](https://github.com/patogallardo/zemax_tools/blob/master/design_analysis/TmaV1_SP/cad/TmaV1x.PDF)| 9.95|
[TMP_big_f3p0](20200621_RH_TMP_Big_f3p00) |3.01 |86.9 |6.3| (5002, 5527), (3588, 5074), (5348, 5499)|158, 318, 339| 10.8|
[TMP_small_f3p66](20200621_RH_TMP_Small_f2p66)|2.64| 69.5| 3.9| (5001, 5772.8), (3544,4836), (5320, 5499)| 173, 293, 354| 8,3|


* Image quality is obtained by a rms-field map in Zemax. Focal plane map is obtained by mapping Strehl ratios across a rectangular grid in field space and mapping angles to focal plane coordinates via chief-ray positions and a linear bidimensional interpolation.
* Telecentricity angle is obtained by tracing the chief-ray and using the z-axis cosine at the image plane surface.
* F/# is obtained by tracing the chief-ray and marginal rays in the x, and y directions. F/# is computed with the dot product of the direction vector of the marginal ray and the chief ray for each case. f/# is then averaged in the x-y direcitons as 0.25(f_x- + f_x+ + f_y- + f_y+) where f_x+ denotes the f number in the positive x direction and so forth.
* Grid distortion was computed by tracing a uniform grid equally spaced (1 deg) rays in x-y and mapping the chief ray to the focal plane.
* Plate scale was computed by tracing rays in the x and y direction and mapping the chief ray to the focal plane. A first order polynomial was then fit.
* Footprints are obtained by doing a footprint analysis in Zemax, the stop is kept before the primary.
* Mirror diameter is obtained from the x-y max ray for a footprint as described in the previous line. This works for TMP models. TMAV1_SP requires a special treatment as the tilt in the mirror makes the x-y footprint less meaninginful. For this reason the diamters for this model are taken from the solid model.
* Sag is exported directly from Zemax. This works for TMP models, and its interpretation is not straightfoward for TMAV1_SP. In this case, the three reflectors were exported to solidworks, where sag was evaluated by defining a plane across the rim of the mirror and measuring the distance from the plane to the center point of the reflector.


## Vignetting

* White areas in maps (f/# and strehls) corresponds to one of the marginal rays vignetting.
