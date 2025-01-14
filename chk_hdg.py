#
# chk_hdg : check misalignment between true (geodetic) trajectory compared
#           with heading produced directly from INS
#
import pandas as pd
import geopandas as gpd
import numpy as np
import pyogrio
from pyproj import Geod
import matplotlib.pyplot as plt

#######################################################
def azi_diff(azimuth1, azimuth2):
    diff = azimuth2 - azimuth1
    while diff > 180:
        diff -= 360
    while diff <= -180:
        diff += 360
    return diff

######################################################
def custom_skip(n):
    ''' read Novatel IE processed trajectory '''
    BEG_LINE = 13
    GET_NTH = 10  #Extract data from every nth line.
    return n < BEG_LINE or (n - BEG_LINE) % GET_NTH != 0

#####################################################################
#####################################################################
#####################################################################
SPEED = 5   # km/h

geod = Geod(ellps="WGS84")  # Use WGS84 ellipsoid
TRJ = './Data/Trajectory/Trajectory.PosT'
# header columns according to NovatelIE  line=11  !!!
HDR = pd.read_csv(TRJ, skiprows=lambda x: x != 11, header=None)
HDR = HDR.iloc[0][0].split()
dfTRJ = pd.read_csv(TRJ,skiprows=custom_skip,sep='\\s+',names=HDR,
                        # nrows=5000, 
                        header=None, engine='python') 
dfTRJ.UTCTime=pd.to_datetime(dfTRJ.UTCTime,unit='s')  # seconds since 1970
dfTRJ['spd_kmh'] = (36/10)*dfTRJ[["VelBdyX", "VelBdyY", "VelBdyZ"]].apply(
                                lambda row: np.linalg.norm(row), axis=1)
 
#########################################
az = list()
for i in range(len(dfTRJ)-1):
    fr = dfTRJ.iloc[i] 
    to = dfTRJ.iloc[i+1]
    fwd_azi, bwd_azi, dist = geod.inv(
            fr.Longitude, fr.Latitude, to.Longitude, to.Latitude)
    spd_kmh = (fr.spd_kmh + to.spd_kmh )/2
    diff_sec = (to.UTCTime-fr.UTCTime).total_seconds()
    diff_fr = azi_diff( fwd_azi, fr.Heading )
    diff_to = azi_diff( (180+bwd_azi), to.Heading )
    az.append( [fr.UTCTime, to.UTCTime, diff_sec, spd_kmh, diff_fr, diff_to ] )
dfAz = pd.DataFrame( az, columns=['fr_UTCTime','to_UTCTime', 'diff_sec', 
                                  'spd_kmh', 'diff_fr', 'diff_to' ] )
count_Hz  = dfAz.diff_sec.value_counts() 
print( count_Hz )
dt = count_Hz.index[0] ; Hz = 1/dt
print( f'dt = {dt:} sec   Hz= {Hz:.1f}  ' )
#########################################

print( f'Filtered speed above {SPEED} km/h...')
dfAz = dfAz[dfAz.spd_kmh>SPEED]    

print( dfAz.spd_kmh.describe() )
print( dfAz.diff_fr.describe() )
print( dfAz.diff_to.describe() )
#import pdb; pdb.set_trace()
if 1:
    fig, ax = plt.subplots(2)
    binrange=[-5,+5]
    dfAz.diff_fr.hist(ax=ax[0], bins=100, color='red', alpha=0.7, range=binrange ) 
    ax[0].set_xlabel( "Azimuth diff at begin epoch (deg)" )
    dfAz.diff_to.hist(ax=ax[1], bins=100, color='green',alpha=0.7, range=binrange ) 
    ax[1].set_xlabel( "Azimuth diff at end epoch (deg)" )
    # Customize the plot (optional)
    plt.suptitle(f'CHCNAV MMS AU20 (NP#2), Speed={SPEED} kmh')
    plt.tight_layout()
    plt.show()

