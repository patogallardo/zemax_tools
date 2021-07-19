# Two groups for TMA cam

Last week I showed that we can populate a center group with identical cameras and get several cameras with Strehls better than 0.8, if we just evaluate camera 8 in the optimization. The exception is of course the two strips at the left and right.

![](../../TMP_baseline_rev_multicam_test1_allcamsfollow1/strehls_1mm/area_above_0p8.png)

Using this knowledge we can patch the two left/right strips with a new group like this:

![](../groups_info/camera_groups.png)

And if we optimize only camera 39 and make the orange group with identical lenses we get.

![](../strehls_1mm/area_above_0p8.png)

This looks primising. We might need an additional group in side groups to bump up up the Strehls a bit. Also, we can improve the Strehls at the center by creating another group if we want to exceed the Strehl 0.8 requirement.
