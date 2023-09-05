# Imports needed packages
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib import transforms as transform
import pandas as pd
from datetime import datetime, timedelta
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT, colortables
from metpy.units import units
import math
from siphon.simplewebservice.wyoming import WyomingUpperAir
from siphon.simplewebservice.iastate import IAStateUpperAir
from metpy.units import units, pandas_dataframe_to_unit_arrays
import numpy as np
import metpy.calc as mpcalc
import pytz
import sys

# Defines the column names
col_names = ['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed']
# Gets current time
now = datetime.now()
UTC = now.astimezone(pytz.utc)

sec = now.second
mn = now.minute
hr = now.hour
dy = now.day
mon = now.month
yr = now.year

sec1 = UTC.second
mn1 = UTC.minute
hr1 = UTC.hour
dy1 = UTC.day
mon1 = UTC.month
yr1 = UTC.year

datetimeNow = datetime(yr, mon, dy, hr, mn, sec)
UTC_Now = datetime(yr1, mon1, dy1, hr1, mn1, sec1)

#UTC = datetimeNow.astimezone(pytz.utc)
strUTC = str(UTC_Now)
strNow = str(datetimeNow)

if hr1 >= 2 and hr1 < 15:
    hour = 0
if hr1 < 2 or hr1 >= 15:
    hour = 12

# Makes the date and time readable
date = datetime(yr, mon, dy, hour)
date1 = date - timedelta(hours=24)

# Makes a string version of the date and time
strdate = str(date)

# Stations of interest
station = 'vbg'
station1 = 'oak'
station2 = 'nkx'

# pings the university of wyoming server to request data arrays
try:
    df_vbg = WyomingUpperAir.request_data(date, station)
except: 
    df_vbg = pd.DataFrame()
try:
    df_vbg_24 = WyomingUpperAir.request_data(date1, station)
except:
    df_vbg_24 = pd.DataFrame()
try:
    df_oak = WyomingUpperAir.request_data(date, station1)
except:
    df_oak = pd.DataFrame()
try:
    df_oak_24 = WyomingUpperAir.request_data(date1, station1)
except:
    df_oak_24 = pd.DataFrame()
try:
    df_nkx = WyomingUpperAir.request_data(date, station2)
except:
    df_nkx = pd.DataFrame()
try:
    df_nkx_24 = WyomingUpperAir.request_data(date1, station2)
except:
    df_nkx_24 = pd.DataFrame()  

#------------------------------------------------------------------------------------
# This section does the following:
# 1) Drops all the duplicate and/or NaN values from each dataframe
# 2) Parses through each data frame for the variables of interest
# 3) Finds the RH profile from the T and Td profiles using MetPy
# 4) Assigns a logical operator for dealing with cases of missing and/or incomplete data
#---------------------------------------------------------------------------------------

# Current Vandenburg Profile
if df_vbg.empty == False:
    df_vbg.drop_duplicates(inplace=True,subset='pressure',ignore_index=True)
    df_vbg.dropna(axis=0, inplace=True)
    p_vbg = df_vbg['pressure'].values * units.hPa
    T_vbg = df_vbg['temperature'].values * units.degC
    Td_vbg = df_vbg['dewpoint'].values * units.degC
    RH_vbg = mpcalc.relative_humidity_from_dewpoint(T_vbg, Td_vbg)
    RH_Percent_vbg = RH_vbg * 100
    vbg_logic = True
else:
    vbg_logic = False

# Vandenburg profile from 24 hours ago
if df_vbg_24.empty == False:
    df_vbg_24.drop_duplicates(inplace=True,subset='pressure',ignore_index=True)
    df_vbg_24.dropna(axis=0, inplace=True)
    p_vbg_24 = df_vbg_24['pressure'].values * units.hPa
    T_vbg_24 = df_vbg_24['temperature'].values * units.degC
    Td_vbg_24 = df_vbg_24['dewpoint'].values * units.degC
    RH_vbg_24 = mpcalc.relative_humidity_from_dewpoint(T_vbg_24, Td_vbg_24)
    RH_Percent_vbg_24 = RH_vbg_24 * 100
    vbg_24_logic = True
else:
    vbg_24_logic = False

# Current Oakland profile
if df_oak.empty == False:
    df_oak.drop_duplicates(inplace=True,subset='pressure',ignore_index=True)
    df_oak.dropna(axis=0, inplace=True)
    p_oak = df_oak['pressure'].values * units.hPa
    T_oak = df_oak['temperature'].values * units.degC
    Td_oak = df_oak['dewpoint'].values * units.degC
    RH_oak = mpcalc.relative_humidity_from_dewpoint(T_oak, Td_oak)
    RH_Percent_oak = RH_oak * 100
    oak_logic = True
else:
    oak_logic = False

# Oakland profile from 24 hours ago
if df_oak_24.empty == False:
    df_oak_24.drop_duplicates(inplace=True,subset='pressure',ignore_index=True)
    df_oak_24.dropna(axis=0, inplace=True)
    p_oak_24 = df_oak_24['pressure'].values * units.hPa
    T_oak_24 = df_oak_24['temperature'].values * units.degC
    Td_oak_24 = df_oak_24['dewpoint'].values * units.degC
    RH_oak_24 = mpcalc.relative_humidity_from_dewpoint(T_oak_24, Td_oak_24)
    RH_Percent_oak_24 = RH_oak_24 * 100
    oak_24_logic = True
else:
    oak_24_logic = False

# Current San Diego profile
if df_nkx.empty == False:
    df_nkx.drop_duplicates(inplace=True,subset='pressure',ignore_index=True)
    df_nkx.dropna(axis=0, inplace=True)
    p_nkx = df_nkx['pressure'].values * units.hPa
    T_nkx = df_nkx['temperature'].values * units.degC
    Td_nkx = df_nkx['dewpoint'].values * units.degC
    RH_nkx = mpcalc.relative_humidity_from_dewpoint(T_nkx, Td_nkx)
    RH_Percent_nkx = RH_nkx * 100
    nkx_logic = True
else:
    nkx_logic = False

# San Diego profile from 24 hours ago
if df_nkx_24.empty == False:
    df_nkx_24.drop_duplicates(inplace=True,subset='pressure',ignore_index=True)
    df_nkx_24.dropna(axis=0, inplace=True)
    p_nkx_24 = df_nkx_24['pressure'].values * units.hPa
    T_nkx_24 = df_nkx_24['temperature'].values * units.degC
    Td_nkx_24 = df_nkx_24['dewpoint'].values * units.degC
    RH_nkx_24 = mpcalc.relative_humidity_from_dewpoint(T_nkx_24, Td_nkx_24)
    RH_Percent_nkx_24 = RH_nkx_24 * 100
    nkx_24_logic = True
else:
    nkx_24_logic = False

# Create a new figure. The dimensions here give a good aspect ratio
fig = plt.figure(figsize=(20, 7))
stationUpper_VBG = station.upper()
stationUpper_OAK = station1.upper()
stationUpper_NKX = station2.upper()
fig.suptitle("Vertical Relative Humidity Change |  Date: " + strdate, fontsize=14, fontweight='bold')
fig.patch.set_facecolor('bisque')
fig.text(0.35, 0.001, "Image Created: " + strNow + " Local | " + strUTC + " UTC", color='k', fontsize=12, fontweight='bold')
fig.text(0.1, 0.001,'Developed By: Eric Drewitz\nPowered by MetPy', fontsize=12, fontweight='bold', color='blue')
# Grid for plots
gs = gridspec.GridSpec(10, 10)

#---------------------------------------------------------------------------------------------------------
# RH plots
#---------------------------------------------------------------------------------------------------------

# Vandenburg
ax1 = fig.add_subplot(gs[0:4, 0:4])

if vbg_logic == False:
    ax1.text(0.20, 0.50, "There is no data at Vandenburg for " + strdate, fontweight='bold')
    
if vbg_logic != False:
    ax1.set_xlabel("Relative Humidity(%)",fontsize=9, fontweight='bold')
    ax1.set_ylabel("Pressure (hPa)",fontsize=9, fontweight='bold')
    ax1.set_title("24 Hour RH Change: Vandenburg", fontweight='bold')
    ax1.set_ylim(1000, 700)
    ax1.set_xlim(0, 100)
    ax1.plot(RH_Percent_vbg, p_vbg, label=date.strftime('%m-%d %HZ'), linewidth=3, color='green', alpha=0.5)
    if vbg_24_logic != False:     
        ax1.plot(RH_Percent_vbg_24, p_vbg_24, label=date1.strftime('%m-%d %HZ'), linewidth=3, color='blue', alpha=0.5)
    ax1.legend(loc=(1.0001, 0.50))
    
# Oakland
ax2 = fig.add_subplot(gs[6:10, 0:4])

if oak_logic == False:
    ax2.text(0.20, 0.50, "There is no data at Oakland for " + strdate, fontweight='bold')
    
if oak_logic != False:
    ax2.set_xlabel("Relative Humidity(%)",fontsize=9, fontweight='bold')
    ax2.set_ylabel("Pressure (hPa)",fontsize=9, fontweight='bold')
    ax2.set_title("24 Hour RH Change: Oakland", fontweight='bold')
    ax2.set_ylim(1000, 700)
    ax2.set_xlim(0, 100)
    ax2.plot(RH_Percent_oak, p_oak, label=date.strftime('%m-%d %HZ'), linewidth=3, color='green', alpha=0.5)
    if oak_24_logic != False:
        ax2.plot(RH_Percent_oak_24, p_oak_24, label=date1.strftime('%m-%d %HZ'), linewidth=3, color='blue', alpha=0.5)
    ax2.legend(loc=(1.0001, 0.50))
   
    
# San Diego
ax3 = fig.add_subplot(gs[0:4, 6:10])

if nkx_logic == False: 
    ax3.text(0.20, 0.50, "There is no data at San Diego for " + strdate, fontweight='bold')
    
if nkx_logic != False:
    ax3.set_xlabel("Relative Humidity(%)",fontsize=9, fontweight='bold')
    ax3.set_ylabel("Pressure (hPa)",fontsize=9, fontweight='bold')
    ax3.set_title("24 Hour RH Change: San Diego", fontweight='bold')
    ax3.set_ylim(1000, 700)
    ax3.set_xlim(0, 100)
    ax3.plot(RH_Percent_nkx, p_nkx, label=date.strftime('%m-%d %HZ'), linewidth=3, color='green', alpha=0.5)
    if nkx_24_logic != False:
        ax3.plot(RH_Percent_nkx_24, p_nkx_24, label=date1.strftime('%m-%d %HZ'), linewidth=3, color='blue', alpha=0.5)
    ax3.legend(loc=(1.0001, 0.50))


# Combo comparison
ax4 = fig.add_subplot(gs[6:10, 6:10])
ax4.set_xlabel("Relative Humidity(%)",fontsize=9, fontweight='bold')
ax4.set_ylabel("Pressure (hPa)",fontsize=9, fontweight='bold')
ax4.set_title("Current Vertical RH Profile Comparison", fontweight='bold')
ax4.set_ylim(1000, 700)
ax4.set_xlim(0, 100)

if vbg_logic != False:
    ax4.plot(RH_Percent_vbg, p_vbg, label='Vandenburg', linewidth=3, color='blue', alpha=0.5)
else: 
    pass
if oak_logic != False:
    ax4.plot(RH_Percent_oak, p_oak, label='Oakland', linewidth=3, color='green', alpha=0.5)
else:
    pass
if nkx_logic != False:
    ax4.plot(RH_Percent_nkx, p_nkx, label='San Diego', linewidth=3, color='purple', alpha=0.5)
else: 
    pass
    
ax4.legend(loc=(1.0001, 0.50))

# Saves figure to directory
plt.savefig("Vertical_RH_Profiles.png")
