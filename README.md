# MMS_Box

# MMS_Box : first, clip large LAS files by creating simple rectangular tiles.
#           Then, create boxes of 1-kilometer length parallel to the road alignment.
#           Each box will clip out its corresponding point cloud data in multiple parts.
#           Finally, merge the clipped parts to form the complete point cloud data i
#           within the full box boundary.**


'''
usage: MMS_Box.py [-h] [-c] [-m] [--copc] TOML

positional arguments:
  TOML         TOML file ; read images trajectory and defined parameters

options:
  -h, --help   show this help message and exit
  -c, --clip   clip point-cloud data in multiple parts
  -m, --merge  merge clipped parts within box polygon
  --copc       use COPC format instead of LAS, used in "merge" stage
'''
