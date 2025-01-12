# MMS_Box

1) tile your big LAS file into small chunks of rectangle tile of size 500 meter.  
pdal tile ../Data/Lasfile/201-00260289.las   "tile#.las" --length 500  

```
tiles/
tiles/tile0_-1.las
tiles/tile-1_-4.las
tiles/tile0_-2.las
tiles/tile-1_-3.las
tiles/tile-1_0.las
tiles/tile-1_-1.las
tiles/tile-2_-5.las
tiles/tile0_0.las
tiles/tile-3_-5.las
tiles/tile-1_-2.las
tiles/tile-2_-4.las
tiles/tile-3_-6.las
tiles/tile-2_-6.las
tiles/tile-2_-3.las
tiles/tile0_-3.las
```

MMS_Box : first, clip large LAS files by creating simple rectangular tiles.
          Then, create boxes of 1-kilometer length parallel to the road alignment.
          Each box will clip out its corresponding point cloud data in multiple parts.
          Finally, merge the clipped parts to form the complete point cloud data i
          within the full box boundary.


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
