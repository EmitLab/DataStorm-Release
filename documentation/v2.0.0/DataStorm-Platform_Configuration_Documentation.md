# Datastorm-Platform Configurations
In this document, we describe how to configure individual simulation model 
with DataStorm Actor, integrate models and further execute them in 
Kepler scientific workflow engine.

## Configurations for entire simulation
Users should follow DataStorm Mongo DB schema **ds_config** to specify their configurations for DataStorm Actor
in DataStorm platform.


### Temporal & Spatial Configuration
To configure temporal/spatial information for whole simulation, 
users should assign these information in the database for DataStorm platform 
ahead of time. In current release, it will be:
<pre>
ds_config
    ->simulation_context
        ->spatial // longtitudes and latitudes
            ->top
            ->left
            ->bottom
            ->right
        ->temporal  // timestamp
            ->begin
            ->end
</pre>

### Alignment Manager Configuration
To configure alignment manager in DataStorm actor, 
users can indicate their configuration 
(E.g. alignment strategy) 
in the following field:
<pre>
ds_config
    -> alignment_setting
</pre>

### Sampling Manager Configuration 
To configure sampling manager in DataStorm actor, 
users can indicate their configuration 
(E.g. sampling/weighting strategy, number of samples, etc.)
in the following field:
<pre>
ds_config
    -> sample_setting
</pre>

### Post-Synchronization Manager Configuration
To configure post-synchronization manager in DataStorm actor, 
users can indicate their configuration 
(E.g. aggregation strategy)
in the following field:
<pre>
ds_config
    -> post_synchronization_setting
</pre>


### Model Configuration
To configure simulation models in DataStorm platform, 
users can indicate their models descriptions in the following fields:
<pre>
ds_config
    ->model
</pre> 
This field could be a list of individual model descriptions.
The configuration for individual model can be found in the following section.

## Configurations for individual model
Users should transform their model property to fit 
DataStorm Mongo DB **ds_config** schema in the following:

* upstream_model: the upstream model name for given model
* downstream_model: the downstream model name for given model
* input_window: the size for input time window
* output_window: the size for output time window
* shift_size: shift size for time window
* variable_size: the number of parameters for given model
* variables: key-value pair for model parameters
* x_resolution: the spacial resolution for x-axis
* y_resolution: the spacial resolution for y-axis
* run_command: the command to execute given model
* aggregation_strategy: the aggregation strategy for multiple DSIRs from model output.


## Integration in Kepler workflow engine
1. User create "model.txt" to indicate what model they will use in their workflow. 
The content of this file will be the name of model E.g. hurricane, flood, etc..
2. Execute Kepler workflow engine and create a new workflow. (See: DataStorm - Kepler Platform Documentation)
3. Drag DS-Actor.kar file (E.g. DS_flood.kar) to the workflow, each DS-Actor represent one model.
4. Connect these DS-Actors in the way that users intend to design their workflows.
5. Execute workflow.


  