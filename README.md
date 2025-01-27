**MMS_Box.py : version 0.7 (Jan26,2025)**

# MMS_Box 

###  1) Partition your large LAS file into smaller rectangular tiles, each tile size is 500 meters.
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

### 2) Manipulate the tile folder using the first three steps of the MMS_Box application.
   Option "-copc" is applied together with -m or --merge option and for
   producing resource-efficient and performance-optimized COPC format or
   simply industry-standared lossless compress LAZ format.
   Otherwise, standard LAS format will be produced during merging step.   
   The 4th step is organizing of image files falling within each boxes.  

```
usage: MMS_Box.py [-h] [-c] [-m] [--copc | --laz] [-i] [-d] [--version] TOML

positional arguments:
  TOML          TOML file, read trajectory and BOX parameters [STEP-1]

options:
  -h, --help    show this help message and exit
  -c, --crop    crop point-cloud data in multiple parts [STEP-2]
  -m, --merge   merge cropped parts, write BOXs of Las [STEP-3]
  --copc        use COPC format instead of LAS, during "merge" stage
  --laz         use LAZ format instead of LAS, during "merge" stage
  -i, --images  copy images to BOX folders [STEP-4]
  -d, --debug   debug mode ; echo pipelines for crop and merge
  --version     show program's version number and exit

```  

### 3) The result of an MMS mission will be visualized in KML or GPCK.
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

### 5) The merged MMS_Box in LAZ or COPC format can be opened and rendered very quickly in a point cloud viewer (e.g., CloudCompare, Potree, ArcGIS)..

Table 1: File Size Comparison of LAS, LAZ, and COPC Formats  
| Section           | las (MB) | laz (MB) | copc (MB) |
|-------------------|---------|--------|---------|
| km_010300_011000 | 10,082  | 1,092  | 1,124   |
| km_011000_012000 | 5,038   | 581    | 704     |
| km_012000_013000 | 4,711   | 517    | 608     |
| km_013000_013184 | 3,598   | 370    | 367     |


![Alt text](https://github.com/phisan-chula/MMS_Box/blob/main/LASType_SizeMB.png)
![Alt text](https://github.com/phisan-chula/MMS_Box/blob/main/MMS_Box_COPCViewer.png)

### 6) Misaglignment of installation and heading precision of INS compared to geodetic azimuth  from final trajectory solution.
![Alt text](https://github.com/phisan-chula/MMS_Box/blob/main/CHC_AU20_Misalignment.png)

