# TMP cam circular Stop

The TMA LAT shows some variation in the beam ellipticity at the tertiary (flashback from TMA design)

![](../../../../design_analysis/SPLAT_baseline_20210523/footprints/footprints_tert.JPG)

This translates to a varying illumination at the primary if we impose a circular stop inside the camera.

If we pick a circular stop the footprints at the primary tend to be more elliptical in the lower cameras as seen below.

![](../Footprints/PRI/footprint_cam_80.JPG)

I tried adjusting the (circular) stop size to leave a 250mm gap in the x and y direction.

This seems to be working ok in terms of illumination, but still could use some improvement for the cases where the ellipticity is somewhat tilted.
![](Footprints/PRI/footprint_cam_84.JPG)

## Camera F-numbers

![](f_numbers/summary_fn.png)
![](f_numbers/cam_fnumbers_hist.png)

# TMA f-numbers

During the TMA design we found the same kind of pattern in the f-number variation.

![](../../../../design_analysis/SPLAT_baseline_20210523/fNumbers/fnumber_av.png)
