This model uses the Itzi flood model and incoming precipitation data to evaluate water depths in a given region.

### Expected Input

This model expects comma-delimited 2-dimensional files corresponding to precipitation in mm/m^2 for each cell.

Cell sizes are adaptively mapped, which may induce warping if regions are not correctly aligned.

### Expected Output

This model creates a new folder for each simulation run, tagged with a unique identifier for each simulation.

Within this folder, a context.json file is written identifying a variety of relevant information about the simulation:

* timestamp: The time at which the simulation was executed by the user.
* simulation_id: A UUID for this simulation
* result_type: A descriptor for the output; i.e. water depth
* output_format: The on-disk format for the output data; i.e. CSV
* output_count: The number of output files generated, one per time step (if any results for that step)
* time
    * begin: The earliest time within the simulation, in YYYY-MM-DD HH:MM
    * end: The latest time within the simulation, in YYYY-MM-DD HH:MM
    * step_size: The time step resolution within the simulation, in HH:MM:SS
* map_statistics
    * rows: number of rows in the dataset
    * cols: number of columns in the dataset
    * north: the northern edge of the extent, in absolute resolution
    * south: the southern edge of the extent, in absolute resolution
    * east: the eastern edge of the extent, in absolute resolution
    * west: the western edge of the extent, in absolute resolution
    * nsres: absolute resolution per row
    * ewres: absolute resolution per column

The model also updates a file in the parent directory, "most_recent.txt", with the UUID of the most-recently executed simulation.