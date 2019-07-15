import random

def main():
    hurricaneHeaderLine1 = " HURRICANE  2018 FEBRUARY 5: FLORIDA;  (ABC BEST TRACK)\n"        # NOT used by SLOSH model
    hurricaneHeaderLine2 = " DELTA-P = 58MB: CAT= 3; RMW=15 ST.MI; DATUMS= -1.0 FT  NGVD\n"   # NOT used by SLOSH model
    lat = [0 for x in range(100)]        # degrees
    lon = [0 for x in range(100)]        # degrees
    windSpeed = [0 for x in range(100)]  # mph
    stormSpeed = [0 for x in range(100)] # knots
    deltaP = [0 for x in range(100)]     # mb
    rmw = [0 for x in range(100)]        # miles
    hurricaneFooter1 = " 54 78 70                IBGNT ITEND JHR\n"
    hurricaneFooter2 = "HR1400 27 OCT 1921       NEAREST APPROACH, OR LANDFALL, TIME\n"
    hurricaneFooter3 = "  -1.  -1.               SEA AND LAKE DATUM"

    # construct data that emulates the tpa1921.trk file
    # note that 100 data points should be extracted using grib_extractor.py, 
    # then placed into the various arrays (lat, lon, etc.) in place of this step
    for i in range(0,100):

        # 1. Hurricane Center Coordinates
        if i == 0:
            lat[i] = 16.6   # .128 increment
            lon[i] = 86.4   # -.093 increment
        else: 
            lat[i] = lat[i-1] + .128
            lon[i] = lon[i-1] + (-.093)

        # 2. Max Wind Speed (mph)
        if 0 <= i and i <= 47:
            windSpeed[i] = 11.5
        elif 48 <= i and i <= 90:
            windSpeed[i] = random.randint(1,3)*12
        else:
            windSpeed[i] = 5.5

        # 3. Storm Speed (knots)
        if 0 <= i and i <= 43:
            stormSpeed[i] = 5.6
        elif i == 44:
            stormSpeed[i] = 12
        elif 45 <= i and i <= 90:
            stormSpeed[i] = stormSpeed[i - 1] + 1.59
        else:
            stormSpeed[i] = stormSpeed[i - 1] - 2

        # 4. Delta Pressure (mb)
        if 0 <= i and i <= 65:
            deltaP[i] = 55
        elif 66 <= i and i <= 70:
            deltaP[i] = 58
        elif 71 <= i and i <= 80:
            deltaP[i] = 45
        else:
            deltaP[i] = 35

        # 5. Radius of Maximum Wind (miles)
        rmw[i] = 15

    # write to file
    f = open("sample.trk","w+")
    f.write(hurricaneHeaderLine1)
    f.write(hurricaneHeaderLine2)
    for i in range(0,100):
        if (i + 1) != 70:
            f.write("                   ")
        else:
            f.write("       NAP-----    ")	# 70th point should be Nearest Approach Point

        f.write(str(i + 1) + "\t")
        f.write(format(lat[i], '7.4f') + "\t")
        f.write(format(lon[i], '7.3f') + "\t")
        f.write(format(windSpeed[i], '7.2f') + "\t")
        f.write(format(stormSpeed[i], '7.2f') + "\t")
        f.write(format(deltaP[i], '7.2f') + "\t")
        f.write(format(rmw[i], '7.2f') + "\t")

        if (i + 1) != 70:
            f.write(str(i + 1) + "\n")
        else:
            f.write(str(i + 1) + " ---NAP\n") # 70th point should be Nearest Approach Point

    f.write(hurricaneFooter1)
    f.write(hurricaneFooter2)
    f.write(hurricaneFooter3)
    f.close()
    print("Done making sample.trk.")
    
if __name__ == '__main__':
    main()