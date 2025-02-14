**MMS_Box.py : version 0.8 (Jan29,2025) # remove --merge use --las/laz/cope ; --copc & --ncore N**  
**MMS_Box.py : version 0.9 (Feb14,2025) # one-line summary**  

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
usage: MMS_Box.py [-h] [-c] [-n NCORE] [--las] [--laz] [--copc] [-i] [-d] [--version] TOML

positional arguments:
  TOML                  TOML file, read trajectory and BOX parameters [STEP-1]

options:
  -h, --help            show this help message and exit
  -c, --crop            crop point-cloud data in multiple parts [STEP-2]
  -n NCORE, --ncore NCORE
                        parallel processing with multicore , only with --copc
  --las                 merge cropped parts and write BOXes of LAS [STEP-3a]
  --laz                 merge cropped parts and write BOXes of LAZ [STEP-3b]
  --copc                merge cropped parts and write BOXes of COPC [STEP-3c]
  -i, --images          copy images to BOX folders [STEP-4]
  -d, --debug           debug mode ; echo PDAL pipelines for crop and merge
  --version             show program's version number and exit
```

```
Namespace(TOML='Rachada.toml', crop=False, ncore=0, las=False, laz=False, copc=False, images=False, debug=False)
Reading 1193 images...
Filter from-to : ['076KNA46062000757', '076KNA46062001353'] ...
Filtered 597 images...
Sum division lengths : 2,882.64 meter
   km_fr  km_to  div_len  npnt                                           geometry
0  10300  11000      700   417  POLYGON ((669109.703 1521225.664, 669109.803 1...
1  11000  12000     1000   598  POLYGON ((669300.378 1521915.196, 669300.599 1...
2  12000  13000     1000   617  POLYGON ((669900.802 1522724.309, 669903.707 1...
3  13000  13182      182   113  POLYGON ((670042.586 1523658.434, 670042.775 1...
Writing ...CACHE/MMS_BoxViz.gpkg ...
Writing ...CACHE/MMS_BoxVizTILE.gpkg ...
Writing ...CACHE/MMS_BoxVizIMG.gpkg ...
Writing ...CACHE/MMS_BoxViz.kml ...
NAME,KM_fr,KM_to,nIMAGE,DT_beg,DT_end,HHMM,KMH_mean,KMH_max,CL_LEN,DT_proc
Rachada,10300,13184,0597,2024-11-24T09:25,2024-11-24T09:16,00:09,19,38,2885,2025-02-14T15:47
คำอธิบาย :
NAME:ชื่อถนน, KM_fr:กิโลเมตรเริ่มต้น, KM_to:กิโลเมตรสิ้นสุด, nIMAGE:จำนวนภาพที่ผลิต,
DT_beg: วันเวลาเริ่มต้น, DT_end:วันเวลาสิ้นสุด, HHMM:ระยะเวลาวิ่ง ชั่วโมง:นาที, 
KMH_mean: ความเร็วเฉลี่ย กิโลเมตรต่อชั่วโมง, KMH_max: ความเร็วสูงสุด กิโลเมตรต่อชั่วโมง, 
CL_LEN: ความยาวช่วงถนน เมตร, DT_proc:วันเวลาประมวลผล  
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

