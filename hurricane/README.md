This model used the PyGrib Package to read and parse the grib2 files.

### GribParser.py

The `GribParser.py` package is built on-top of the `PyGrib` library for serialized reading and writing of data from grib files with the extension `grib2`.

The method `filter` defined the `GribParser` acts as an agent that reads the specified grib file and extracts the information for a specific spatial region.

### Function Definition: `filter`

@param

 * fileName : Takes the grib file name string (including extension)
 * lng_min : Lower bound along the longitude
 * lat_min : Lower bound along the latitude
 * lng_max : Upper bound along the longitude
 * lat_max : Upper bound along the latitude
 * verbose : Default, True, To print in the console the progress of the parser.
 
 @return
 
 * There is not output from the function, however,successful execution results in six files being saved to the disk. 5 CSVs and 1 TXT.
 
 @files
 
 The parser creates 5 data files in `.csv` extension on the disk. The name of the files is defined using the following convention *GRIB_FILE_NAME.DATATYPE.csv*
 
 * gribfilename.rain.csv : 2D matrix containing rain in mm
 * gribfilename.lat.csv : 2D matrix containing latitude of each grid cell
 * gribfilename.lng.csv : 2D matrix containing longitude of each grid cell
 * gribfilename.U.csv : 2D matrix containing U, horizontal wind component, in meters per sec
 * gribfilename.V.csv : 2D matrix containing V, vertical wind component, in meters per sec
