# Camera generation algorithm

Generation of multiple configurations in Zemax can be tedious, and for a large number of configurations this becomes impractical with the GUI. The Zemax API (ZOSPI) allows the automation of such tasks. Here I document the creation of the 85 camera design for the S4 LAT.

The automated part begins with the creation of a single configuration. The user is expected to take the LAT design and make the necessary changes to control the variables of interest with one single column in the multi configuration editor.

## Necessary changes

The changes to the LAT that are needed to enable the multiconfiguration setting are:

1. Tilt angles at the primary, these need to be controlled by a coordinate break before the primary and the primary has to be set as the global coordinate reference
2. Camera surfaces and wedge (three lenses and a silica wedge)
3. Camera center (defined as a coordinate break with x/y offsets before the beginning of the camera definition)

## Multi configuration creation:

The first step to create the multi configuration file consists in copying the first configuration N times. In our case N=85. This step has to be followed by adding a displacement of each configuration which has to be defined. We implement this with a pandas dataframe that needs to exist in  folder groups_info. This file also defines the camera groups but at this stage we don't need this info and we will only use the x/y coordinates of the cameras.

The following script has automated this step:
`ZOS_API_scripts/S4camScripts/S4cam_TMP_design0_generate_85groupedCams_from_csv.py`

## Sky fields

After we have defined the 85 configurations with the focal plane offsets we
need to find the sky angles for each camera. This is done with the script

`ZOS_API_scripts/S4camScripts/S4cam_TMP_design0_set_sky_field_per_camera.py`

Which finds numerically the tilt that makes the chief ray fall at the center of
the wedge surface.

## Wedge tilt and rotation

The next step is to find the wedge tilt and rotation that keeps all the cameras
parallel. We do this by asking the chief ray of the center field to fall at
the center of the lyot stop surface.

The wedge tilt is controlled by a single number tan(alpha), it is implemented
 as a tilt in the X direction. The X direction rotated to yield any orientation.
To make interpretation easy and remove some degeneracy in theese parameters,
 the sign of tan(alpha) is restricted to be positive and the rotation angles are
 restricted to fall in the 0-360 degree range.

 The script that generates this part of the design is

`ZOS_API_scripts/S4camScripts/S4cam_TMP_design0_set_wedge_tilt_and_rotation_per_camera.py`

## Camera groups

With the 85 configurations generated and the fields in the sky set, we need
to set the groups of cameras that share the same optical prescription. This
is done with the script:

`ZOS_API_scripts/S4camScripts/S4cam_TMP_design1_set_camera_groups.py`

Which requires the files:
`85cam_groups.csv
group_leaders.csv`

These files set which cameras should pick up parameters from where.

## Optimization

The optimization is done in three steps:

For each group:
1. Set initial ansatz values to get us close to the answer, this is controlled in file initial_values.csv
2. Set aspheric terms to zero and optimize the rest of the variables. This is controlled in file variables.csv
3. Set all aspheric terms to variable and optimize again.

This algorithm is implemented in

`S4cam_TMP_design2_optimize_groups.py`
