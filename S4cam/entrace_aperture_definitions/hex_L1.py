# this script generates the aperture file for a hexagonal surface given
# the radius. One nice aperture plot is also generated.

center = [0, 0]
r_hex = 100
zmx_txt = "POL 0 0 %3.3f 6 30" % r_hex

with open(r'C:\Users\pgall\Documents\Zemax\Objects\Apertures\S4cam_hex_L1_aperture.UDA', 'w') as f:  # noqa
    f.write(zmx_txt)
