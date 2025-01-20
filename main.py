from Plotter import Plot_Domain, Plot_Sliced_Planes
import numpy as np
from Interpolation_Algorithms import interpolate_solid, interpolate_solid_connections, interpolate_solid_connection_surfaces  
from Array_Utilities import Remove_Internal_Solid 
from Path_Planning_Algorithms import FindPaths, PlotPath_fromSources


def Interpolation_Progress(input_file_name, output_file_name_base, volume_shape, fluid_default_value):
    
    
    # Open Solid 
    volume_array = np.fromfile(input_file_name, dtype=np.uint8).reshape(volume_shape)
    
    """
    # Full-solid interpolation
    print(" Full-solid interpolation")
    krig_final_domain, nn_final_domain = interpolate_solid(volume_array,fluid_default_value=fluid_default_value, file_name=output_file_name_base)
    Plot_Domain(krig_final_domain, output_file_name_base+"_krig", remove_value=[fluid_default_value])
    Plot_Domain(nn_final_domain, output_file_name_base+"_nn", remove_value=[fluid_default_value])
    Plot_Sliced_Planes(krig_final_domain, file_name=output_file_name_base+"_krig_slicedPlanes")
    Plot_Sliced_Planes(nn_final_domain, file_name=output_file_name_base+"_nn_slicedPlanes")
    """    
    """   
    # Solid Connected only
    print(" Solid Connected only interpolation")
    krig_final_domain, nn_final_domain = interpolate_solid_connections(volume_array, fluid_default=fluid_default_value, file_name=output_file_name_base) 
    Plot_Domain(krig_final_domain, output_file_name_base+"_krig_SolConn", remove_value=[fluid_default_value])  
    Plot_Domain(nn_final_domain, output_file_name_base+"_nn_SolConn", remove_value=[fluid_default_value])
    Plot_Sliced_Planes(krig_final_domain, file_name=output_file_name_base+"_krig_SolConn_slicedPlanes")
    Plot_Sliced_Planes(nn_final_domain, file_name=output_file_name_base+"_n_SolConnn_slicedPlanes")
    """
   
    # Surface Solid Connections only interpolation
    print(" Solid Surface Connected only interpolation")
    krig_final_domain, nn_final_domain = interpolate_solid_connection_surfaces(volume_array, fluid_default=fluid_default_value, file_name=output_file_name_base) 
    Plot_Domain(krig_final_domain, output_file_name_base+"_krig_Surface_SolConn", remove_value=[fluid_default_value])
    Plot_Domain(nn_final_domain, output_file_name_base+"_nn_Surface_SolConn", remove_value=[fluid_default_value])
    Plot_Sliced_Planes(krig_final_domain, file_name=output_file_name_base+"_krig_Surface_SolConn_slicedPlanes")
    Plot_Sliced_Planes(nn_final_domain, file_name=output_file_name_base+"_nn_Surface_SolConn_slicedPlanes")

    # Surface Path Interpolation 
    
    
    
"""
volume_shape = (250,250,250)
fluid_default_value= 1
input_file_name = "Rock Volumes/Example_4.raw"
output_file_name_base = "Interpolated Volumes/Example_4"
Interpolation_Progress(input_file_name,output_file_name_base,volume_shape,fluid_default_value)
"""

"""
print("Running Example 5 interpolations")
volume_shape = (250,250,250)
fluid_default_value= 1
input_file_name = "Rock Volumes/Example_5.raw"
output_file_name_base = "Interpolated Volumes/Example_5"
Interpolation_Progress(input_file_name,output_file_name_base,volume_shape,fluid_default_value)
"""

"""
print("Running Example 6 interpolations")
volume_shape = (250,250,250)
fluid_default_value= 1
input_file_name = "Rock Volumes/Example_6.raw"
output_file_name_base = "Interpolated Volumes/Example_6"
Interpolation_Progress(input_file_name,output_file_name_base,volume_shape,fluid_default_value)
"""

"""
volume_shape = (250,250,250)
fluid_default_value= 1
input_file_name = "Rock Volumes/Example_7.raw"
output_file_name_base = "Interpolated Volumes/Example_7"
Interpolation_Progress(input_file_name,output_file_name_base,volume_shape,fluid_default_value)
"""



# TEST DE PATH PLANNING
field = np.ones((50, 50, 50), dtype=np.uint8) # Initial block of void space cells
field[0:10, :, :] = 0 # Solid Surface cells
field[45:50, :, :] = 0  # Solid Surface cells
field[0, 0, 0] = 10 # One cell of contact angle
field[0, 15, 49] = 5 # Another cell of contact angle
field = Remove_Internal_Solid(field) # Only keep surface, removing internal solid for available path
all_paths = FindPaths(field) 
random_target_point = (9,25,25)
PlotPath_fromSources(field, all_paths, target=random_target_point, fill_value=10)
