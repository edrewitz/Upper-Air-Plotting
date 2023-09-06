# Imports needed packages
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib import transforms as transform
import pandas as pd
from datetime import datetime
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT, colortables
from metpy.units import units
import math
from siphon.simplewebservice.wyoming import WyomingUpperAir
from metpy.units import units, pandas_dataframe_to_unit_arrays
import numpy as np
import metpy.calc as mpcalc
import pytz

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
strNow = str(datetimeNow)
strUTC = str(UTC_Now)


# Makes the date and time readable
if hr1 >= 2 and hr1 < 15:
    hour = 0
if hr1 < 2 or hr1 >= 15:
    hour = 12

date = datetime(yr1, mon1, dy1, hour)


   
# Makes a string version of the date and time
strdate = str(date)

# pings the server to request data
try:
    df = WyomingUpperAir.request_data(date, 'OAK')

except:
    df = pd.DataFrame()


#### Vandenburg #########
if df.empty == False:
    # Drops duplicate pressure levels that will cause issues with LCL, LFC, EL and Parcel Path
    df.drop_duplicates(inplace=True,subset='pressure',ignore_index=True)
    df.dropna(axis=0, inplace=True)
    # Parses through the dataframe
    p = df['pressure'].values * units.hPa
    T = df['temperature'].values * units.degC
    Td = df['dewpoint'].values * units.degC
    wind_speed = df['speed'].values * units.knots
    wind_speedSI = df['speed'].values * units('m/s')
    wind_dir = df['direction'].values * units.degrees
    height = df['height'].values * units.meters
    u, v = mpcalc.wind_components(wind_speed, wind_dir)
    uSI, vSI = mpcalc.wind_components(wind_speedSI, wind_dir)
    d = pandas_dataframe_to_unit_arrays(df)
    p1 = df['pressure']
    wind_speed1 = df['speed']
    wind_dir1 = df['direction']
    OAK_logic = True
else:
    OAK_logic = False

if OAK_logic == True:
    # Create a new figure. The dimensions here give a good aspect ratio
    fig = plt.figure(figsize=(20, 7))
    fig.suptitle("OAK Vertical Profiles |  Date: " + strdate, fontsize=14, fontweight='bold')
    fig.patch.set_facecolor('bisque')
    fig.text(0.35, 0, "Image Created: " + strNow + " Local | " + strUTC + " UTC", color='k', fontsize=12, fontweight='bold')
    fig.text(0.1, 0,'Developed By: Eric Drewitz\nPowered by MetPy', fontsize=12, fontweight='bold', color='blue')
    # Grid for plots
    gs = gridspec.GridSpec(15, 19)
    skew = SkewT(fig, rotation=45, subplot=gs[0:15, 0:10])
    
    # Creates mask to limit certain functions to exclude levels above 100mb
    mask = p >= 100 * units.hPa
    mask1 = p >= 200 * units.hPa
    # Calculation for wind barb spacing on the plot
    interval = np.logspace(2, 3) * units.hPa
    idx = mpcalc.resample_nn_1d(p, interval)
    
    interval1 = np.logspace(1, 2) * units.hPa
    idx1 = mpcalc.resample_nn_1d(p, interval1)
    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot
    skew.plot(p[mask], T[mask], 'red', linewidth=3)
    skew.plot(p[mask], Td[mask], 'green', linewidth=3)
    skew.plot_barbs(p[idx], u[idx], v[idx], color='b')
    
    # Wetbulb Temperature
    wetbulb = mpcalc.wet_bulb_temperature(p[0], T, Td).to('degC')
    skew.plot(p, wetbulb, 'cyan', alpha=0.75, linewidth=2)
    
    skew.ax.set_ylim(1000, 100)
    
    # Calculate LCL height and plot as black dot. Because `p`'s first value is
    # ~1000 mb and its last value is ~250 mb, the `0` index is selected for
    # `p`, `T`, and `Td` to lift the parcel from the surface. If `p` was inverted,
    # i.e. start from low value, 250 mb, to a high value, 1000 mb, the `-1` index
    # should be selected.
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    lfc_pressure, lfc_temperature = mpcalc.lfc(p, T, Td)
    el_pressure, el_temperature = mpcalc.el(p, T, Td)
    
    
    
    # Calculate full parcel profile and add to plot as black line
    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    skew.plot(p, prof, 'k', linestyle='--', linewidth=2)
    
    # Shade areas of CAPE and CIN
    skew.shade_cin(p, T, prof, Td)
    skew.shade_cape(p, T, prof)
    
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='bisque', alpha=0.5)
    indices = dict(boxstyle='round', facecolor='white', alpha=1)
    
    # Data table LCL
    rounded_LCL_Pres = round(lcl_pressure.m, 1)
    rounded_LCL_Temp = round(lcl_temperature.m, 1)
    strLCL_Pres = str(rounded_LCL_Pres)
    strLCL_Temp = str(rounded_LCL_Temp)
    
    # Data table LFC
    rounded_LFC_Pres = round(lfc_pressure.m, 1)
    rounded_LFC_Temp = round(lfc_temperature.m, 1)
    strLFC_Pres = str(rounded_LFC_Pres)
    strLFC_Temp = str(rounded_LFC_Temp)
    
    # Data table EL
    rounded_EL_Pres = round(el_pressure.m, 1)
    rounded_EL_Temp = round(el_temperature.m, 1)
    strEL_Pres = str(rounded_EL_Pres)
    strEL_Temp = str(rounded_EL_Temp)
    
    # Checks if there is an LFC or not
    LFC_NAN = np.isnan(lfc_pressure)
    
    # Table if no LFC or EL
    if LFC_NAN == True:
        skew.ax.text(0.6, 0.99,'LCL Pressure: ' + strLCL_Pres + 'hPa\nLCL Temperature: ' + strLCL_Temp + '℃', transform=skew.ax.transAxes,
                     fontsize=10, fontweight='bold', verticalalignment='top', bbox=props)
    
    # Table if LFC and EL  
    if LFC_NAN == False:
        skew.ax.text(0.6, 0.99,'LCL Pressure: ' + strLCL_Pres + 'hPa\nLCL Temperature: ' + strLCL_Temp + '℃\n\nLFC Pressure: ' + strLFC_Pres + 'hPa\nLFC Temperature: ' + strLFC_Temp + '℃\n\nEL Pressure: ' + strEL_Pres + 'hPa\nEL Temperature: ' + strEL_Temp + '℃', transform=skew.ax.transAxes,
                     fontsize=8, fontweight='bold', verticalalignment='top', bbox=props)  
    
    
       
    # x-limits of the skewT        
    skew.ax.set_xlim(-25, 30)
    
    # Plots LCL LFC and EL
    if lcl_pressure:
        skew.ax.plot(lcl_temperature, lcl_pressure, marker="_", label='LCL', color='tab:purple', markersize=30, markeredgewidth=3)
    if lfc_pressure:
        skew.ax.plot(lfc_temperature, lfc_pressure, marker="_", label='LFC', color='tab:purple', markersize=30, markeredgewidth=3)
    if el_pressure:
        skew.ax.plot(el_temperature, el_pressure, marker="_", label='EL', color='tab:purple', markersize=30, markeredgewidth=3)
    
    # Colors of the freezing level isotherm (cyan) and the boundaries of the dendridic growth zone (yellow)
    skew.ax.axvline(0, color='c', linestyle='--', linewidth=3)
    skew.ax.axvspan(-20, -10, alpha=0.5, color='y')
    
    
    # Titles the SkewT
    #skew.ax.set_title(stationUpper + " Sounding " + strdate)
    # Titles both x and y axes
    skew.ax.set_xlabel(u'Temperature (℃)')
    skew.ax.set_ylabel(u'Pressure (hPa)')
    
    # Add the relevant special lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()
    
    
    
    # Creates a slice to get every 10 data points in the array
    decimate = 12
    # Loops through to plot all of the height values in meters
    for p, t, h in zip(d['pressure'][::decimate], d['temperature'][::decimate], d['height'][::decimate]):
        # Bounding the height output to the top of the skewT
        km = h.m / 1000
        if p >= 100 * units.hPa and p <= 1000 * units.hPa:      
            skew.ax.text(0.01, p, str(round(km,0)) + 'km', transform=skew.ax.get_yaxis_transform(which='tick2'), fontweight ='bold')
           
    # Good bounds for aspect ratio
    skew.ax.set_xlim(-60, 45)
    
    #--------------------------------------------------------------------------------------
    # This section partions or "trims" data into various heights
    #--------------------------------------------------------------------------------------
    
    # Finds maximum height in the dataframe
    height = d['height']
    mHeight = height.max().m / 1000
    maxHeight = mHeight * units.km
    #print(maxHeight)
    # These if-statements will correct height issues if the balloon reaches less than 10km
    
    # Max Height is at least 10km for a full 0-10km wind profile
    if maxHeight >= 10 * units.km:
        (_, u_trimmed, v_trimmed,
            speed_trimmed, height_trimmed) = mpcalc.get_layer(d['pressure'],
                                                            d['u_wind'],
                                                            d['v_wind'],
                                                            d['speed'],
                                                            d['height'],
                                                            depth=10 * units.km)
    
    # Gets 0-6km if 0-10km cannot be done
    if maxHeight < 10 * units.km:
        (_, u_trimmed, v_trimmed,
            speed_trimmed, height_trimmed) = mpcalc.get_layer(d['pressure'],
                                                            d['u_wind'],
                                                            d['v_wind'],
                                                            d['speed'],
                                                            d['height'],
                                                            depth=6 * units.km)    
    
    # 0-6km
    (pres_trimmed, u_trimmed1, v_trimmed1,
        speed_trimmed1, height_trimmed1) = mpcalc.get_layer(d['pressure'],
                                                        d['u_wind'],
                                                        d['v_wind'],
                                                        d['speed'],
                                                        d['height'],
                                                        depth=6 * units.km)
    
    
    #-------------------------------------------------------------------
    # This next section we will calculate all the indices for our sounding
    #-------------------------------------------------------------------
    
    #--------------------Calculations----------------------------------
    # ***0-6km Bulk Shear***
    # Gets u and v shear components from 0-6km
    u_shear, v_shear = mpcalc.bulk_shear(pres_trimmed, u_trimmed1, v_trimmed1, depth = 6 * units.km)
    
    # Drops the units of u and v and just takes the magnitude of u and v shear
    a = u_shear.m
    b = v_shear.m
    
    # Finds resultant shear vector via pythagorean theorum
    bulk_shear = math.sqrt((a**2) + (b**2))
    
    # Rounds the resultant shear vector magnitude to the nearest whole number
    rounded_bulk_shear = round(bulk_shear, 1)
    
    # Converts value to a string variable
    strShear = str(rounded_bulk_shear)
    
    """
    #***Bunkers Storm Motion***
    # Gets u and v components for each type of bunkers storm motion
    # Wind mean is the U and v component of sfc-6km mean flow
    #right, left, wind_mean = mpcalc.bunkers_storm_motion(p, u, v, height)
    
    # Extracts u and v components for each category
    uright = right[0]
    vright = right[1]
    uleft = left[0]
    vleft = left[1]
    uwind_mean = wind_mean[0]
    vwind_mean = wind_mean[1]
    
    #***Most Unstable CAPE/CIN***
    #MUCAPE, MUCIN = mpcalc.most_unstable_cape_cin(p[0], T, Td)
    #m_MUCAPE = MUCAPE.m
    #m_MUCIN = MUCIN.m
    #r_MUCAPE = round(m_MUCAPE, 0)
    #r_MUCIN = round(m_MUCIN, 0)
    """
    
    
    #-------------------------------Output----------------------------------------
    
    #fig.text(0, 0.9,'0-6km Bulk Shear: ' + strShear + 'kts', fontsize=10, fontweight='bold')
    #fig.text(0, 0.85,'MUCAPE: ' + str(r_MUCAPE) + 'J/kg', fontsize=10, fontweight='bold')
    
    #-----------------------------------------------------------------------------
    # HODOGRAPH
    #-----------------------------------------------------------------------------
    
    # Create a hodograph
    # Make a figure and axis
    # Create a hodograph
    ax = fig.add_subplot(gs[7:15, 12:19])
    h = Hodograph(ax, component_range=100)
    
    # Add "range rings" to the plot
    h.add_grid(increment=20)
    
    # Add vectors
    norm, cmap = colortables.get_with_range('ir_rgbv', np.nanmin(speed_trimmed.m),
                                                np.nanmax(speed_trimmed.m))
    
    h.plot_colormapped(u_trimmed, v_trimmed, speed_trimmed,
                        cmap=cmap, norm=norm, linewidth=3)
    
    h.wind_vectors(u_trimmed[::8], v_trimmed[::8], alpha = 0.25)
    #h.wind_vectors(uright, vright, label='RM', color='orange', width=1.5)
    #h.wind_vectors(uleft, vleft, label='LM', color='purple', width=1.5)
    #h.wind_vectors(uwind_mean, vwind_mean, label='Mean', color='green', width=1.5)
    
    # Titles both x and y axes
    h.ax.set_xlabel("U-Wind (kts)")
    h.ax.set_ylabel("V-Wind (kts)")
    h.ax.legend(loc=(1,0.3))
    
    #---------------------------------------------------------------------
    # Total Wind vs. Pressure Graph
    #----------------------------------------------------------------------
    # Wind vs. Pressure
    ax0 = fig.add_subplot(gs[0:6, 14:15])
    ax0.set_xlabel("Wind Speed (kts)",fontsize=9)
    ax0.set_ylabel("Pressure (hPa)",fontsize=9)
    ax0.set_ylim(1000, 100)
    
    
    # Finds the max wind in the data frame    
    maxWind = df['speed'][df['speed'].idxmax()]
    
    # Sets the x limits to the max wind and zero
    ax0.set_xlim(0,maxWind)
    
    # Title
    #ax0.set_title("Total Wind Speed", fontsize=10)
    
    # Wind vs. Pressure line plotted
    
    ax0.plot(wind_speed1[idx], p1[idx], linewidth=3, color='r')
    
    #------------------------------------------------------------------------
    # u and v wind components vs. pressure
    #------------------------------------------------------------------------
    # U and V Wind vs. Pressure
    ax1 = fig.add_subplot(gs[0:15, 11:13])
    ax1.set_xlabel("U and V Wind (m/s)", fontsize=10)
    ax1.set_ylabel("Pressure (hPa)", fontsize=10)
    ax1.set_ylim(1000, 100)
    #ax1.set_title("U and V Wind Components", fontsize=10)
    ax1.plot(uSI[idx], p1[idx], label='U-Wind', linewidth=3, alpha=0.75, color='orange')
    ax1.plot(vSI[idx], p1[idx], label='V-Wind', linewidth=3, alpha=0.75, color='purple')
    ax1.legend(loc=(0.22, 0.95))
    
    #----------------------------------------------------------
    # Brunt–Väisälä Frequency Profile
    #-----------------------------------------------------------
    # Calculates Potential Temperature
    theta = mpcalc.potential_temperature(p, T)
    
    # Calculates the Brunt–Väisälä Frequency Squared
    bv_squared = mpcalc.brunt_vaisala_frequency_squared(height, theta)
    
    # Adds a subplot for the Brunt–Väisälä Frequency Squared graph
    ax2 = fig.add_subplot(gs[0:6, 16:19])
    
    # Adds a y=0 line to show when N < 0 = unstable and N > 0 = stable
    ax2.axvline(x=0, color='k', alpha=0.5, linestyle='--')
    
    ax2.set_xlabel("BVF-Squared (1/s^2)", fontsize=9)
    ax2.set_ylabel("Height (m)", fontsize=9)
    ax2.set_title("Brunt–Väisälä Frequency Squared", fontsize=10)
    
    # Plots the Brunt–Väisälä Frequency Squared
    ax2.plot(bv_squared, height, color='blue')

    fig.savefig("OAK Sounding")

if OAK_logic == False:
    fig = plt.figure(figsize=(20, 7))
    fig.suptitle("OAK Vertical Profiles |  Date: " + strdate, fontsize=14, fontweight='bold')
    fig.patch.set_facecolor('bisque')
    fig.text(0.35, 0, "Image Created: " + strNow + " Local | " + strUTC + " UTC", color='k', fontsize=12, fontweight='bold')
    fig.text(0.1, 0,'Developed By: Eric Drewitz\nPowered by MetPy', fontsize=12, fontweight='bold', color='blue')
    fig.text(0.15, 0.5, 'NO DATA FOR: ' + date.strftime('%m/%d/%Y %HZ'), fontsize=60, fontweight='bold')
    
    fig.savefig("OAK Sounding")
