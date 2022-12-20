# F/#s in TMP8A (with no window offsets)


To explore the hit in f/# in the TMP8A model if we cannot allow for
window entrance displacements I have set up the TMP8A model with individual fov
for each camera, which was set to allow the full beam through the window entrance.

The center camera allows for 0.37 degrees semi-fov, while camera 20 needs this
to be reduced to 0.33 due to vignetting.

![](footprint_cam20.png)

This gets worse at the cameras located at the edges, the worse being camera 78
where the semi-fov goes down to **0.26** deg.

![](footprint_cam78.png)

All cams look like this:

![](3DLayout_varying_fov.png)

For these FoVs I optimized cameras individually and computed f/#s with the
 prescription shown last week.

 ![](../f_numbers/summary_fn.png)

 Here notice that the bottom part of the diagram shows the highest f/#s with
 the largest hit in performance. The highest f/# is 2.66.
