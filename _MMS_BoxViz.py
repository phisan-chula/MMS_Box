#
#
#
import simplekml
import numpy as np
import glob
import laspy
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString,box
from pathlib import Path
from itertools import cycle

class MMS_BoxViz:
    def WriteVizGPCK(self):
        # Save the KML file
        GPKG = Path( self.TOML.OUT_FOLDER ) / "MMS_BoxViz.gpkg"
        print( f'Writing ...{GPKG} ...')
        GPKG.parent.mkdir( parents=True, exist_ok=True )
        self.dfBOX.to_file( GPKG, layer="Box", driver="GPKG")
        self.dfTile.to_file(GPKG, layer="Tile", driver="GPKG")
        #self.dfCLIP.to_file(GPKG, layer="Clip_Inter", driver="GPKG")
        for i in range(len(self.dfCLIP)):
            df = self.dfCLIP.iloc[i:i+1]
            #import pdb; pdb.set_trace()
            df.to_file(GPKG, layer=f"{df.BOXTILE.iloc[0]}", driver="GPKG")


    def WriteVizKML( self ):
        kml = simplekml.Kml()
        FoldBox = kml.newfolder(name="Boxes")
        self.KML_Box( FoldBox )
        FoldDiv = kml.newfolder(name="Division")
        self.KML_Div( FoldDiv )
        FoldTrj = kml.newfolder(name="Trajectory" )
        self.KML_Trj( FoldTrj )
        FoldImg = kml.newfolder(name="Imageries" )
        self.KML_Img( FoldImg )
        FoldTile = kml.newfolder(name="Tiles")
        self.KML_Tindex( FoldTile )
        
        # Save the KML file
        KML = Path( self.TOML.OUT_FOLDER ) / "MMS_BoxViz.kml"
        print( f'Writing ...{KML} ...')
        KML.parent.mkdir( parents=True, exist_ok=True )
        kml.save( KML )

    def KML_Box( self, Folder ):
        colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99',
                    '#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a']        
        color_cycle = cycle( colors )
        dfBOX = self.dfBOX.to_crs(4326)
        for index, row in dfBOX.iterrows():
            #import pdb; pdb.set_trace()
            coord = list(row.geometry.exterior.coords)
            pol = Folder.newpolygon(name= f'STA_{row.km_fr}_{row.km_to}',
                    outerboundaryis=coord )
            pol.description = f"""
                div_len : {row.div_len}
                num_pnt : {row.npnt}
            """
            pol.style.polystyle.color = next(color_cycle).replace('#','7f')
            pol.style.linestyle.color = next(color_cycle).replace('#','ff')
            pol.style.polystyle.outline = 1

    def KML_Div( self, Folder ):
        dfDIV = self.dfDIV.to_crs(4326)
        for index, row in dfDIV.iterrows():
            #import pdb; pdb.set_trace()
            pnt = Folder.newpoint(name= row.STA,
                    coords=[ (row.geometry.x,row.geometry.y) ])
            pnt.description = f"""
                dist_km : {row.dist_km}
                dist_0  : {row.dist_0 }
            """
            pnt.style.labelstyle.color = '7f0000ff'
            pnt.style.iconstyle.scale = 1.5  # Icon big
            pnt.style.iconstyle.icon.href =\
                  'http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png'
            pnt.style.iconstyle.color = '7f0000ff'

    def KML_Trj( self, Folder, ALTITUDE=10 ):
        ls = Folder.newlinestring(name="Trajectory",description="Trajectory")
        trj = self.dfTRJ[['Longitude(deg)','Latitude(deg)']]
        ls.coords = np.insert(trj.values, 2, ALTITUDE, axis=1).tolist()
        #import pdb; pdb.set_trace()
        ls.altitudemode = simplekml.AltitudeMode.relativetoground
        ls.extrude = 1  # Extend the LineString to the ground
        for index, row in self.dfTRJ.iterrows():
            pnt = Folder.newpoint(name= str(index),
                    coords=[(row['Longitude(deg)'], row['Latitude(deg)'])])
            pnt.visibility = 0
            pnt.description = f"""
                Image : {row['Name']}
                Height(m): {row['Height(m)']}
                H_Ell(m): {row['H_Ell(m)']}
            """
            pnt.style.labelstyle.color = '7f0000ff'
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
            pnt.style.iconstyle.color = '7f0000ff'

    def KML_Img( self, Folder ):
        for index, row in self.dfIMG.iterrows():
            pnt = Folder.newpoint(name=row['Name'],
                    coords=[(row['Longitude(deg)'], row['Latitude(deg)'])])
            pnt.visibility = 0
            pnt.description = f"""
                GPSTime(sec): {row['GPSTime(sec)']}
                Easting(m): {row['Easting(m)']}
                Northing(m): {row['Northing(m)']}
                Height(m): {row['Height(m)']}
                H_Ell(m): {row['H_Ell(m)']}
                Roll(deg): {row['Roll(deg)']}
                Pitch(deg): {row['Pitch(deg)']}
                Heading(deg): {row['Heading(deg)']}
                Phi(deg): {row['Phi(deg)']}
                Omega(deg): {row['Omega(deg)']}
                Kappa(deg): {row['Kappa(deg)']}
            """

    def KML_Tindex( self, Folder ):
        dfTile = self.dfTile.to_crs( crs='EPSG:4326')
        #import pdb; pdb.set_trace()


        for index, row in dfTile.iterrows():
            coord = list(row.geometry.exterior.coords)
            pol = Folder.newpolygon(name= f'{row.FileLAS}',
                    outerboundaryis=coord )
            pol.visibility = 0
            pol.description = f"""
                width  : {row.width:.2f} m.
                length : {row.length:.2f} m.
                height : {row.height:.2f} m.
            """
            pol.style.polystyle.color = "7F808080" 
            pol.style.linestyle.color = "7F808080"
            pol.style.polystyle.outline = 2
