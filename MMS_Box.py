#
# MMS_Box : first, crop large LAS files by creating simple rectangular tiles.
#           Then, create boxes of 1-kilometer length parallel to the road alignment.
#           Each box will cropped out its corresponding point cloud data in multiple parts.
#           Finally, merge the cropped parts to form the complete point cloud data i
#           within the full box boundary.
#
# history : Phisan Santitamnont ( phisan.chula@gmail.com , phisan.s@cdg.co.th )
# VERSION = "0.1 (Dec15,2024)
#VERSION = "0.71 (Jan28,2025) --copc & --ncore N "
#VERSION = "0.8 (Jan29,2025) # remove --merge use --las/laz/cope ; --copc & --ncore N "
VERSION = "0.9 (Feb14,2025) # one-line summary" 
#
import datetime 
import tomllib
import json
import glob
import pdal
import laspy
import shutil
import pandas as pd
import geopandas as gpd
import numpy as np
import simplekml
import argparse
from shapely.geometry import Point,LineString,box
from shapely.ops import substring
from pathlib import Path

import _MMS_BoxViz
class MMS_Box(_MMS_BoxViz.MMS_BoxViz):
    def __init__(self, ARGS ):
        self.ARGS = ARGS
        with open( ARGS.TOML , "rb") as f:
            # Parse the TOML file content
            TOML = tomllib.load(f)
        #import pdb ;pdb.set_trace()
        self.InitialOptional(TOML)
        self.dfIMG = pd.read_csv(self.TOML.TRJ_IMG, sep='\\s+',engine='c' )
        # bug AU20 CHC-AU20
        self.dfIMG = self.dfIMG.rename( columns={'GPSTime(sec)': 'UTCTime' } )
        self.dfIMG = gpd.GeoDataFrame( self.dfIMG, crs=self.TOML.EPSG, 
           geometry=gpd.points_from_xy( self.dfIMG['Easting(m)'], self.dfIMG['Northing(m)'] ) )
        print( f'Reading {len(self.dfIMG)} images...')
        if 'IMG_FRTO' in self.TOML.keys():
            self.dfCL = self.Filter( self.dfIMG, self.TOML.IMG_FRTO )
            print( f'Filter from-to : {self.TOML.IMG_FRTO} ...' )
            print( f'Filtered {len(self.dfCL)} images...')
        else:
            print( '***WARNING*** TOML.IMG_FRTO not defined...')
            self.dfCL = self.dfIMG
        if self.TOML.REVERSE_TRJ:
            self.dfCL = self.dfCL.iloc[::-1]
        self.dfCL.reset_index(drop=True,inplace=True)
        self.dfDIV,self.dfLS = self.LineStringDIV()
        self.dfBOX = self.GenerateBox()
        print( self.dfBOX[['km_fr', 'km_to', 'div_len', 'npnt' , 'geometry']] )

    def InitialOptional( self , TOML):
        DEFAULT = { 'OUT_FOLDER':'./CACHE', 'EPSG':32647, 'REVERSE_TRJ':False,
                    'OFFSET_TRJ':False, 'DIV':1000, 'STA_BEG':0, 'WIDTH':30 }
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
        LS = LineString( self.dfCL[['Easting(m)', 'Northing(m)']].to_numpy() )
        if self.TOML.OFFSET_TRJ:
            LS = LS.offset_curve( self.TOML.OFFSET_TRJ,join_style=2,mitre_limit=10 )
        next_div = DIV*(divmod(STA_BEG,DIV)[0]+1)
        rest_div = next_div-STA_BEG
        pnt = np.arange( next_div, next_div+LS.length-rest_div, DIV )
        pnt = np.insert( pnt,  0, STA_BEG ) 
        pnt = np.append( pnt,  STA_BEG+LS.length ) 
        pnt0 = pnt-pnt[0]
        df = pd.DataFrame( {'dist_km': pnt ,'dist_0':pnt0 } ) 
        def MkPnt( row, LS ):
            km,meter = divmod(row.dist_km,1000)
            sta = '{:03d}+{:03d}'.format(int(km),int(meter))
            pnt = LS.interpolate( row.dist_0 , normalized=False )
            return sta,pnt
        df[['STA','geometry']] = df.apply( MkPnt, axis=1, result_type='expand', args=(LS,) )
        dfDIV = gpd.GeoDataFrame( df, crs=self.TOML.EPSG, geometry=df.geometry )
        dfLS =  gpd.GeoDataFrame( crs=self.TOML.EPSG, geometry=[LS,] )
        return dfDIV,dfLS

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
            stt = self.dfDIV.iloc[i  ].dist_0 ; end = self.dfDIV.iloc[i+1].dist_0
            ss = substring( self.dfLS.iloc[0].geometry, 
                            start_dist=stt, end_dist=end, normalized=False)
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

    def MakeTileIndex( self, dfTile ):
        def GetLasBound(row):
            with laspy.open( row.FileLAS ) as las:
                header = las.header
                # Get boundary coordinates
                min_x, min_y, min_z = header.mins
                max_x, max_y, max_z = header.maxs
                bnd_rect = box(min_x, min_y, max_x, max_y)
            return max_x-min_x, max_y-min_y, max_z-min_z, bnd_rect
        #import pdb; pdb.set_trace()
        dfTile[['width','length','height','geometry']] = \
             dfTile.apply( GetLasBound, axis=1, result_type='expand' )
        dfTile = gpd.GeoDataFrame( dfTile, crs=self.TOML.EPSG, geometry=dfTile.geometry )
        return dfTile

    def GenerateBoxClipTile( self ):
        ''' generate list of operations only, no actual crop'''
        dfTile = pd.DataFrame(  glob.glob(self.TOML.PNT_CLD), columns=['FileLAS'] )
        assert len(dfTile)>0,\
          f'Expecting many tiles from "pdal tile --length 500 BIG_PC.las tile#.las"'
        dfTile['tiles'] = dfTile.index.map(lambda x: f'TILE{x:04d}')  
        self.dfTile = self.MakeTileIndex( dfTile )
        self.dfBOX['boxes'] = self.dfBOX.index.map(lambda x: f'BOX{x:04d}')  
        dfInter = gpd.overlay( self.dfBOX, self.dfTile, how='intersection' )
        ####################################
        box_tile = list()
        for i_box,row_box in dfInter.groupby("boxes"):
            box_folder = Path( self.TOML.OUT_FOLDER ) / 'BOX_TILE' / i_box
            for i_tile, row_tile in row_box.iterrows(): 
                OUTFILE = str( box_folder / f'{row_tile.tiles:}.las' )
                box_tile.append( [i_box, row_tile.geometry, row_tile.FileLAS, OUTFILE])
        dfCROP = pd.DataFrame( box_tile , columns=['BOX', 'WKT_GEOM','TILES', 'BOXTILE'] )
        self.dfCROP = gpd.GeoDataFrame( dfCROP,crs=self.TOML.EPSG,geometry=dfCROP.WKT_GEOM )
        #import pdb; pdb.set_trace()

    def GenerateBoxClipImage( self ):
        ''' generate list of operations only, no actual crop'''
        joined = gpd.sjoin(self.dfIMG, self.dfBOX[['geometry', 'boxes']], 
                           how='left', predicate='intersects')
        self.dfIMG_BOX = joined.dropna()[['Name','boxes', 'geometry']]
        
    def ClipPoly( self, WKT, INFILE, OUTFILE ):
        polygon = WKT  # Replace with your actual polygon "string" WKT
        pipeline = {
            "pipeline": [
                { "type": "readers.las", "filename": INFILE },
                { "type": "filters.crop", "polygon": polygon },
                { "type": "writers.las", "filename": str(OUTFILE) }
            ]
        }
        pipe_json = json.dumps(pipeline)
        if self.ARGS.debug: print( f'ClipPoly(),{pipe_json}' )
        try:
            pipeline = pdal.Pipeline( pipe_json )
            pipeline.execute()
        except Exception as e:
            print(f"Error ClipPoly() LAS files: {e}")

    def MergePart( self, LASFiles, WRITER, LASOut):
        assert type(LASFiles)==list
        pipeline_list = LASFiles 
        pipeline_list.append( { "type":"filters.merge" } )
        if self.ARGS.ncore>1 and self.ARGS.copc:
            print( f'*** invoke --ncores {self.ARGS.ncore:} and --COPC ... ' )
            pipeline_list.append( { "type":WRITER, "filename": LASOut, 
                                    "threads":self.ARGS.ncore  } )
        else:
            pipeline_list.append( { "type":WRITER, "filename": LASOut } )
        # Convert dictionary to JSON string
        pipe_json = json.dumps(pipeline_list)
        #import pdb; pdb.set_trace()
        if self.ARGS.debug: print( f'ClipPoly(),{pipe_json}' )
        try:
            pipeline = pdal.Pipeline(json=pipe_json)
            pipeline.execute()
            print(f"Merging successful. Output file: {LASOut}")
        except Exception as e:
            print(f"Error during MergePart(): {e}")

    def OneLineSummary(self, IMU_SAMPLING=1_000):
        '''  IMU_SAMPLING Extract imu-data from every nth line. '''
        def _skip(nLINE):
            BEG_LINE = 13  # Novate WayPoint/IE  format
            return nLINE < BEG_LINE or (nLINE - BEG_LINE) % IMU_SAMPLING != 0
        TRJ_IMU = self.TOML.TRJ_IMU
        _HDR = pd.read_csv(TRJ_IMU,skiprows=lambda x: x != 11, header=None)
        _HDR = _HDR.iloc[0][0].split()
        ########################################
        dfIMU = pd.read_csv(TRJ_IMU,skiprows=_skip,sep='\\s+', #nrows=5000, 
                                names=_HDR, header=None, engine='c') 
        dfIMU['spd_kmh'] = (36/10)*dfIMU[["VelBdyX", "VelBdyY", "VelBdyZ"]].apply(
                                lambda row: np.linalg.norm(row), axis=1)
        def spd_from_TRJ():
            trj_beg = self.dfCL.iloc[ 0];  trj_end = self.dfCL.iloc[-1] 
            idx_beg = ((dfIMU["UTCTime"] - trj_beg['UTCTime']  ).abs()).idxmin()
            idx_end = ((dfIMU["UTCTime"] - trj_end['UTCTime']  ).abs()).idxmin()
            if idx_beg>idx_end:
                idx_beg,idx_end = idx_end,idx_beg
            spd = dfIMU.iloc[idx_beg:idx_end].spd_kmh.describe()
            return (int(spd['mean']),int(spd['max']) )
        SPD = spd_from_TRJ()
        DTbeg = datetime.datetime.fromtimestamp(self.dfCL.iloc[0].UTCTime)
        DTend = datetime.datetime.fromtimestamp(self.dfCL.iloc[-1].UTCTime)
        def HHMM( DTbeg,DTend):
            if DTbeg > DTend: dura = DTbeg-DTend
            else: dura = DTend-DTbeg
            # prevent 'minute' truncation ; adjust insignificant 30 second
            minu,secs = divmod( dura.total_seconds()+30, 60 )
            hour,minu = divmod( minu, 60 )
            return f"{int(hour):02d}:{int(minu):02d}"
        ######################################
        STEM = Path(self.ARGS.TOML).stem
        DURA = HHMM( DTbeg,DTend )
        KM_fr = self.dfBOX.iloc[0].km_fr 
        KM_to = self.dfBOX.iloc[-1].km_to 
        nImage = '{:04d}'.format( len(self.dfCL) )
        ACQ = DTbeg.strftime("%Y-%m-%dT%H:%M"),DTend.strftime("%Y-%m-%dT%H:%M"),DURA
        PROC = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        CL_LEN = '{:.0f}'.format( self.dfLS.iloc[0].geometry.length )
        print( 'NAME,KM_fr,KM_to,nIMAGE,DT_beg,DT_end,HHMM,KMH_mean,KMH_max,CL_LEN,DT_proc' )
        print( f'{STEM},{KM_fr},{KM_to},{nImage},{",".join(ACQ)},{SPD[0]},{SPD[1]},{CL_LEN},{PROC}' )
        #import pdb; pdb.set_trace()

##################################################################
##################################################################
##################################################################
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("TOML", 
            help="TOML file, read trajectory and BOX parameters [STEP-1]")

    parser.add_argument('-c',"--crop", action='store_true',
            help="crop point-cloud data in multiple parts [STEP-2]")

    parser.add_argument('-n',"--ncore", type=int, default=0,
            help='parallel processing with multicore , only with --copc')
    parser.add_argument("--las", action='store_true',
            help="merge cropped parts and write BOXes of LAS [STEP-3a]")
    parser.add_argument("--laz", action='store_true',
            help="merge cropped parts and write BOXes of LAZ [STEP-3b]")
    parser.add_argument("--copc", action='store_true',
            help="merge cropped parts and write BOXes of COPC [STEP-3c]")

    parser.add_argument('-i', "--images", action='store_true',
            help="copy images to BOX folders [STEP-4]")

    parser.add_argument('-d', "--debug", action='store_true',
            help="debug mode ; echo PDAL pipelines for crop and merge")
    parser.add_argument("--version", action="version", 
            version=f"%(prog)s : version {VERSION}" )
    ARGS = parser.parse_args()
    print(ARGS)

    ####################################################
    mms = MMS_Box( ARGS )
    mms.GenerateBoxClipTile()
    mms.WriteVizGPCK()
    mms.WriteVizKML()
    mms.OneLineSummary()

    if ARGS.crop:
        for i,row in mms.dfCROP.iterrows():
            #import pdb; pdb.set_trace()
            print( f'Clipping las files to {row.BOXTILE} ...' )
            Path(row.BOXTILE).parent.mkdir( parents=True, exist_ok=True ) 
            mms.ClipPoly( str(row.WKT_GEOM), row.TILES, row.BOXTILE ) 

    SECT_FMT = 'km_{:06d}_{:06d}'
    if ARGS.las or ARGS.laz or ARGS.copc:
        if ARGS.las:
            WRITER='writers.las';  LAS_FMT = SECT_FMT + '.las'
        elif ARGS.laz:
            WRITER="writers.las";  LAS_FMT = SECT_FMT + '.laz'
        elif ARGS.copc:
            WRITER="writers.copc"; LAS_FMT = SECT_FMT + '.copc.laz'
        for grp,row in mms.dfCROP.groupby('BOX'):
            this_box = mms.dfBOX[mms.dfBOX.boxes==grp ].iloc[0]
            OUTFILE = LAS_FMT.format( this_box.km_fr, this_box.km_to )
            print( f'Merging las files to {OUTFILE} ...' )
            OUTPATH = Path(mms.TOML.OUT_FOLDER) / 'RESULT' / OUTFILE
            OUTPATH.parent.mkdir( parents=True, exist_ok=True ) 
            mms.MergePart( list(row.BOXTILE), WRITER, str(OUTPATH) )

    if ARGS.images:
        mms.GenerateBoxClipImage()
        dfImages = pd.DataFrame(  glob.glob(mms.TOML.IMAGES), columns=['Images'] )
        dfImages["Stem"] = dfImages["Images"].apply(lambda x: Path(x).stem) 
        for i,row in mms.dfIMG_BOX.iterrows():
            this_box = mms.dfBOX[ mms.dfBOX.boxes==row.boxes].iloc[0]
            fr = Path( dfImages[dfImages.Stem==row.Name ].iloc[0].Images )
            to = Path( mms.TOML.OUT_FOLDER ) / 'RESULT' /\
                       SECT_FMT.format( this_box.km_fr,this_box.km_to )
            OUTPATH = to / fr.name
            print( f'Copying to {OUTPATH} ...' )
            OUTPATH.parent.mkdir( parents=True, exist_ok=True ) 
            shutil.copy( fr , OUTPATH  )
            #import pdb; pdb.set_trace()
