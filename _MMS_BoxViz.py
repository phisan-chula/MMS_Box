#
#
#
import simplekml
from shapely.geometry import LineString
from pathlib import Path

class MMS_BoxViz:
    def WriteVizKML( self ):
        kml = simplekml.Kml()
        FoldBox = kml.newfolder(name="Boxes")
        self.KML_Box( FoldBox )
        FoldDiv = kml.newfolder(name="Division")
        self.KML_Div( FoldDiv )
        FoldTrj = kml.newfolder(name="Trajectory")
        FoldTrj.visibility = 0
        self.KML_Trj( FoldTrj )
        FoldImg = kml.newfolder(name="Imageries")
        FoldImg.visibility = 0
        self.KML_Img( FoldImg )
        # Save the KML file
        KML = Path( self.TOML.OUT_FOLDER ) / "MMS_BoxViz.kml"
        print( f'Writing ...{KML} ...')
        #import pdb; pdb.set_trace()
        KML.parent.mkdir( parents=True, exist_ok=True )
        kml.save( KML )

    def KML_Box( self, Folder ):
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
            pol.style.polystyle.color = '990000ff'  # Transparent red
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
            pnt.style.iconstyle.scale = 3  # Icon big
            pnt.style.iconstyle.icon.href =\
            'http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png'
            pnt.style.iconstyle.color = '7f0000ff'

    def KML_Trj( self, Folder ):
        trj = self.dfTRJ[['Longitude(deg)','Latitude(deg)']]
        Folder.newlinestring(name="Trajectory", description="Filerted Trajectory",
                        coords=trj.values.tolist() )
        for index, row in self.dfTRJ.iterrows():
            pnt = Folder.newpoint(name= str(index),
                    coords=[(row['Longitude(deg)'], row['Latitude(deg)'])])
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

