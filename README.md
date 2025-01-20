# MMS_Box 

###  1) Partitioning your big LAS file into small chunks of rectangle tiles of size 500 meter.
   Using PDAL eg. pdal tile ../Data/Lasfile/201-00260289.las   "tile#.las" --length 500  

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

### 2) manipulate the folder of tiles using first 3 steps by MMS_Box application.
   Option "-copc" is applied together with -m or --merge option and for
   producing resource-efficient and performance-optimized COPC format.
   Otherwise, standard LAS format will be produced during merging step.   
   The 4th step is organizing of image files falling within each boxes.  

```
usage: MMS_Box.py [-h] [-c] [-m] [--copc] [-i] [--version] TOML

positional arguments:
  TOML          TOML file, read trajectory and BOX parameters [STEP-1]

options:
  -h, --help    show this help message and exit
  -c, --clip    clip point-cloud data in multiple parts [STEP-2]
  -m, --merge   merge clipped parts, write BOXs of Las [STEP-3]
  --copc        use COPC format instead of LAS, during "merge" stage
  -i, --images  copy images to BOX folders [STEP-4]
  --version     show program's version number and exit

```  

### 3) The result of an MMS mission will be visualized in KML.
![Alt text](https://github.com/phisan-chula/MMS_Box/blob/main/MMS_Box_Concept.png)
  
### 4) Result will be put in folder './CACHE or other name specified in TOML

```
CACHE/MMS_BoxViz.kml

CACHE/RESULT/km_012000_013000.copc.laz
CACHE/RESULT/km_011000_012000.copc.laz
CACHE/RESULT/km_013000_013184.copc.laz
CACHE/RESULT/km_010300_011000.copc.laz

CACHE/RESULT/km_013000_013184/076KNA46062003201.jpg
CACHE/RESULT/km_013000_013184/076KNA46062003221.jpg
CACHE/RESULT/km_013000_013184/076KNA46062000774.jpg
...
CACHE/RESULT/km_011000_012000/076KNA46062002872.jpg
CACHE/RESULT/km_011000_012000/076KNA46062002963.jpg
CACHE/RESULT/km_011000_012000/076KNA46062001128.jpg
CACHE/RESULT/km_011000_012000/076KNA46062001009.jpg
CACHE/RESULT/km_011000_012000/076KNA46062001038.jpg
```

---

### 5) The merged MMS_Box in LAS or COPC format can be opened and rendered very quickly in a COPC viewer.

...
-rw-r--r-- 1 phisan phisan 1.1G Jan 20 14:50 km_010300_011000.copc.laz
-rw-r--r-- 1 phisan phisan 9.4G Jan 20 15:19 km_010300_011000.las
-rw-r--r-- 1 phisan phisan 672M Jan 20 14:57 km_011000_012000.copc.laz
-rw-r--r-- 1 phisan phisan 4.7G Jan 20 15:20 km_011000_012000.las
-rw-r--r-- 1 phisan phisan 581M Jan 20 15:01 km_012000_013000.copc.laz
-rw-r--r-- 1 phisan phisan 4.4G Jan 20 15:21 km_012000_013000.las
-rw-r--r-- 1 phisan phisan 351M Jan 20 15:04 km_013000_013184.copc.laz
-rw-r--r-- 1 phisan phisan 3.4G Jan 20 15:22 km_013000_013184.las
...
![Alt text](https://github.com/phisan-chula/MMS_Box/blob/main/MMS_Box_COPCViewer.png)

### 6) Misaglignment of installation and heading precision of INS compared to geodetic azimuth  from final trajectory solution.
![Alt text](https://github.com/phisan-chula/MMS_Box/blob/main/CHC_AU20_Misalignment.png)

