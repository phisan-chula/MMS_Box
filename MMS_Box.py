#
# MMS_Box : first, clip large LAS files by creating simple rectangular tiles.
#           Then, create boxes of 1-kilometer length parallel to the road alignment.
#           Each box will clip out its corresponding point cloud data in multiple parts.
#           Finally, merge the clipped parts to form the complete point cloud data i
#           within the full box boundary.**
#
import tomllib
import json
import glob
import pdal
import pandas as pd
import geopandas as gpd
import numpy as np
import simplekml
import argparse
from shapely.geometry import LineString
from shapely.ops import substring
from pathlib import Path

import _MMS_BoxViz

class MMS_Box(_MMS_BoxViz.MMS_BoxViz):
    def __init__( self, TOML, ARGS ):
        self.FillOptional(TOML)
        self.ARGS = ARGS
        self.dfIMG = pd.read_csv(self.TOML.TRJ_IMG, sep='\\s+',engine='python' )
        print( f'Reading {len(self.dfIMG)} images...')
        if 'IMG_FRTO' in self.TOML.keys():
            self.dfTRJ = self.Filter( self.dfIMG, self.TOML.IMG_FRTO )
            print( f'Filter from-to : {self.TOML.IMG_FRTO} ...' )
            print( f'Filtered {len(self.dfTRJ)} images...')
        else:
            print( '***WARNING*** TOML.IMG_FRTO not defined...')
            self.dfTRJ = self.dfIMG
        if self.TOML.REVERSE_TRJ:
            self.dfTRJ = self.dfTRJ.iloc[::-1]
        self.dfTRJ.reset_index(drop=True,inplace=True)

        self.dfDIV,self.LS = self.LineStringDIV()
        self.dfBOX = self.GenerateBox()
        print( self.dfBOX[['km_fr', 'km_to', 'div_len', 'npnt' , 'geometry']] )
        self.WriteVizKML()
        #import pdb ; pdb.set_trace()

    def FillOptional( self , TOML):
        DEFAULT = { 'OUT_FOLDER' : './CACHE', 'OUT_MERGE' : 'MERGED',
                    'EPSG':32647, 'REVERSE_TRJ' : False,
                    'DIV':1000,'STA_BEG':0,'WIDTH':30 }
        for k,v in DEFAULT.items():
            if k not in TOML.keys():
                TOML[k]=v
        self.TOML = pd.Series(TOML)

    def Filter( self, df, FR_TO ):
        beg = df[df['Name']==FR_TO[0]].index[0]
        end = df[df['Name']==FR_TO[1]].index[0]
        return df.loc[beg:end]

    def LineStringDIV( self ): 
        DIV = self.TOML.DIV
        STA_BEG = self.TOML.STA_BEG
        ls = LineString( self.dfTRJ[['Easting(m)', 'Northing(m)']].to_numpy() )
        next_div = DIV*(divmod(STA_BEG,DIV)[0]+1)
        rest_div = next_div-STA_BEG
        pnt = np.arange( next_div, next_div+ls.length-rest_div, DIV )
        pnt = np.insert( pnt,  0, STA_BEG ) 
        pnt = np.append( pnt,  STA_BEG+ls.length ) 
        pnt0 = pnt-pnt[0]
        df = pd.DataFrame( {'dist_km': pnt ,'dist_0':pnt0 } ) 
        def MkPnt( row, LS ):
            #import pdb ;pdb.set_trace()
            km,meter = divmod(row.dist_km,1000)
            sta = '{:03d}+{:03d}'.format(int(km),int(meter))
            pnt = LS.interpolate( row.dist_0 , normalized=False )
            return sta,pnt
        df[['STA','geometry']] = df.apply( MkPnt, axis=1, result_type='expand', args=(ls,) )
        gdf = gpd.GeoDataFrame( df, crs=self.TOML.EPSG, geometry=df.geometry )
        return gdf,ls

    def POLY2WKT( self, poly ):
        coord = list()
        for x,y in list(poly.exterior.coords):
            coord.append((round(x,2), round(y,2)))
        wkt_string = "POLYGON (("
        for i, (x, y) in enumerate(coord):
            wkt_string += f"{x} {y}"
            if i < len(coord) - 1:
                wkt_string += ", "
        wkt_string += "))"
        return wkt_string

    def GenerateBox( self ):
        boxes = list()
        for i in range(len(self.dfDIV)-1):
            stt = self.dfDIV.iloc[i  ].dist_0
            end = self.dfDIV.iloc[i+1].dist_0
            ss = substring( self.LS, start_dist=stt, end_dist=end, normalized=False)
            buf = ss.buffer(self.TOML.WIDTH, cap_style='flat' )
            npnt = len(buf.exterior.coords)-1
            boxes.append( [self.dfDIV.iloc[i].dist_km, self.dfDIV.iloc[i+1].dist_km, 
                          end-stt, npnt, self.POLY2WKT( buf ), buf] )
        dfBox = pd.DataFrame( boxes, columns=['km_fr','km_to','div_len', 
                                              'npnt', 'wkt_geom', 'geometry' ] )
        print( f'Sum division lengths : {dfBox.div_len.sum():,.2f} meter')
        #import pdb ; pdb.set_trace()
        for col in dfBox.columns[0:3]:
            dfBox[col] = dfBox[col].astype('int64')
        gdfBox = gpd.GeoDataFrame( dfBox, crs=self.TOML.EPSG, geometry=dfBox.geometry )
        return gdfBox

    def GenerateBoxClipTile( self ):
        ''' generate list of operations only, no actual clipping'''
        dfTile = pd.DataFrame(  glob.glob(self.TOML.PNT_CLD), columns=['FileLAS'] )
        dfTile['tiles'] = dfTile.index.map(lambda x: f'TILE{x:03d}')  
        self.dfBOX['boxes'] = self.dfBOX.index.map(lambda x: f'BOX{x:03d}')  
        box_tile = list()
        for i_box,row_box in self.dfBOX.iterrows():
            box_folder = Path( self.TOML.OUT_FOLDER ) / 'BOX_TILE' / row_box.boxes 
            for i_tile, row_tile in dfTile.iterrows(): 
                OUTFILE = str( box_folder / f'{row_tile.tiles:}.las' )
                box_tile.append( [row_box.boxes, row_box.wkt_geom, row_tile.FileLAS, OUTFILE])
        self.dfCLIP = pd.DataFrame( box_tile , columns=['BOX', 'WKT_GEOM','TILES', 'BOXTILE'] )

    def ClipPoly( self, WKT, INFILE, OUTFILE ):
        polygon = WKT  # Replace with your actual polygon WKT
        pipeline = {
            "pipeline": [
                { "type": "readers.las", "filename": INFILE },
                { "type": "filters.crop", "polygon": polygon },
                { "type": "writers.las", "filename": str(OUTFILE) }
            ]
        }
        try:
            pipeline = pdal.Pipeline(json.dumps(pipeline))
            pipeline.execute()
        except Exception as e:
            print(f"Error ClipPoly() LAS files: {e}")

    def MergePart( self, LASFiles, WRITER, LASOut):
        pipeline_dict = {
            "pipeline": [
                *[{"type": "readers.las", "filename": las_file} for las_file in LASFiles],
               # {   "type": WRITER,  "a_srs":  f"EPSG:{self.TOML.EPSG}" , "filename": str(LASOut) }
                {   "type": WRITER,  "filename": str(LASOut) }
            ]
        }
        try:
            pipeline_json = json.dumps(pipeline_dict)
            pipeline = pdal.Pipeline(pipeline_json)
            pipeline.execute()  # Execute the pipeline
        except Exception as e:
            print(f"Error MergePart() LAS files: {e}")

##################################################################
##################################################################
##################################################################
parser = argparse.ArgumentParser()
parser.add_argument("TOML", 
        help="TOML file ; read images trajectory and defined parameters")
parser.add_argument('-c',"--clip", action='store_true',
        help="clip point-cloud data in multiple parts")
parser.add_argument('-m', "--merge", action='store_true',
        help="merge clipped parts within box polygon")
parser.add_argument("--copc", action='store_true',
        help='use COPC format instead of LAS, used in "merge" stage')
ARGS = parser.parse_args()
print(ARGS)
with open("Rachada.toml", "rb") as f:
    # Parse the TOML file content
    TOML = tomllib.load(f)
#########################################################
mms = MMS_Box( TOML, ARGS )
#import pdb; pdb.set_trace()
if ARGS.clip or ARGS.merge:
    mms.GenerateBoxClipTile()

if ARGS.clip:
    for i,row in mms.dfCLIP.iterrows():
        #import pdb; pdb.set_trace()
        print( f'Clipping las files to {row.BOXTILE} ...' )
        Path(row.BOXTILE).parent.mkdir( parents=True, exist_ok=True ) 
        mms.ClipPoly( row.WKT_GEOM, row.TILES, row.BOXTILE ) 

if ARGS.merge:
    TEMPLATE = 'km_{:06d}_{:06d}'
    if ARGS.copc:
        WRITER="writers.copc"
        TEMPLATE = f'{TEMPLATE}.copc.laz'
    else:
        WRITER='writers.las'
        TEMPLATE = f'{TEMPLATE}.las'
    for grp,row in mms.dfCLIP.groupby('BOX'):
        this_box = mms.dfBOX[mms.dfBOX.boxes==grp ].iloc[0]
        #import pdb; pdb.set_trace()
        OUTFILE = TEMPLATE.format( this_box.km_fr, this_box.km_to )
        print( f'Merging las files to {OUTFILE} ...' )
        OUTPATH = Path(mms.TOML.OUT_FOLDER) / 'RESULT' / OUTFILE
        OUTPATH.parent.mkdir( parents=True, exist_ok=True ) 
        mms.MergePart( list(row.BOXTILE), WRITER, OUTPATH )

