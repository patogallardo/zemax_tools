# TMP 85 cam Strehl coverage

For each camera in the design, it is possible to evaluate the Strehl ratio in the sky and use the chief ray to evaluate the position of each field in the focal plane. This yields a map in x-y coordinates in the focal plane with a Strehl value for each frequency of interest. In this instance we evaluate Strehls at 1/2/3mm. In an effort to distill the image quality information in a single number, we can evaluate the area of Strehls better than s for s in [0.7, 0.8, 0.9] and compare this to the area within a circle of the approximate size of the array, in this case a circle of diameter 130mm. A visualization of such calculation for configuration 15 looks like:
![](../strehls_1mm/15.png)

The design being evaluated in this instance has the following layout,
![](../camera_groups.png)
Where the color indicates camera groups, which follow the camera with the lowest number in the group.

The area covered with a given Strehl cut can then be evaluated in the whole 85 camera system:

![](../strehls_1mm/area_above_0p8.png)

Here I am showing the percentage of coverage above S=0.8 at 1mm. Similar plots can be found in "strehls_Xmm/area_above_0pY.png", where X and Y are the wavelength in mm and the strehl cut in question.

At 2mm the same plot looks like:

![](../strehls_2mm/area_above_0p8.png)

Next steps:

* Force x-y symmetry, seems that the left hand side of the array of cameras is better optimized if one chooses camera 35 as the group leader rather than camera 68.
* Evaluate f/#s and distill this metric into a table that can be easily read.
