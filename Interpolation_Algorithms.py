import Plotter as pl
import numpy as np
from Array_Utilities import Separate_NonFluid_Connections, Remove_Internal_Solid, array3D_to_dataframe
from pykrige.uk3d import UniversalKriging3D
from sklearn.neighbors import NearestNeighbors
import os

def interpolate_solid(volume, fluid_default_value=1, file_name=""):
    print("-Full Volume (with Surface), sample cells: ", np.sum((volume != 0) & (volume != 1)))
    print("-Full Volume (with Surface), fluid cells: ", np.sum((volume == 1)))
    print("-Full Volume (with Surface), solid cells: ", np.sum((volume == 0)))
    volume_shape = volume.shape

    # Coleta o sub domínio em analise
    x_lim = 0, volume_shape[0]
    y_lim = 0, volume_shape[1]
    z_lim = 0, volume_shape[2]
    
    
    # Convert array to dataframe in order to apply interpolation methods
    df_volume = array3D_to_dataframe(volume, volume_shape, remove_where_value=fluid_default_value)

    # Remove rock(value=0) and fluid(value=1) voxels that do not influence interpolation
    df_reads_volume = df_volume[(df_volume['angle'] != 1) & (df_volume['angle'] != 0)]
    if df_reads_volume.empty: raise ValueError("Empty dataframe. Make sure to provide samples for interpolation")
    
    # Create a complete block with interpolated values
    krig_domain = Apply_Kriging(df_reads_volume, n_points=5, tested_methods=["linear"], x_lim=x_lim, y_lim=y_lim, z_lim=z_lim)
    nn_domain = Apply_NearestNeighbor(df_reads_volume)
    
    # Remove fluid cells from the complete 3D interpolated block, only solid cells must be interpolated
    krig_final_domain = limit_interpolation_to_solid(volume, krig_domain, fluid_default_value)
    nn_final_domain = limit_interpolation_to_solid(volume, nn_domain, fluid_default_value)
    
    # Ensure unsigned char cells
    krig_final_domain = krig_final_domain.astype(np.uint8)
    nn_final_domain = nn_final_domain.astype(np.uint8)

    if file_name != "":
        # Verificar se a pasta existe, caso contrário, criar
        folder = os.path.dirname(file_name)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        
        krig_final_domain.tofile(file_name+"_krig.raw")
        nn_final_domain.tofile(file_name+"_nn.raw")

    return krig_final_domain, nn_final_domain


def interpolate_solid_connections(volume, fluid_default=1, file_name="", make_plot=True):
    # Separate full solid into sub-solid with connected cells
    sub_arrays, connected_labels, labels = Separate_NonFluid_Connections(volume, fluid_default)

    # Apply kriging to each sub array
    volume_krig = volume.copy()
    volume_nn = volume.copy()
    
    print("---Array diveded into ",len(sub_arrays), " sub arrays. ")
        
    for conn_label, sub_domain in zip(labels, sub_arrays):
        pl.Plot_Domain(sub_domain, "EXCLUIR")
        print("---Group ", conn_label, " with shape ",sub_domain.shape, ", Sample cells: ",np.sum((sub_domain != 0) & (sub_domain != 1)))
        
        # If no samples are present on the solid group: keep original 
        if np.sum((sub_domain != 0) & (sub_domain != 1)) == 0: 
            krig_sub_domain = sub_domain
            nn_sub_domain = sub_domain
        else:
            krig_sub_domain, nn_sub_domain = interpolate_solid(sub_domain, fluid_default_value=fluid_default)

        # Mask identify cells that belong to the interpolated group
        mask = (connected_labels == conn_label)
        # Substitute interpolated cells to the right spots
        volume_krig[mask] = krig_sub_domain[mask]
        volume_nn[mask] = nn_sub_domain[mask]
        
    if file_name != "":
        # Verificar se a pasta existe, caso contrário, criar
        folder = os.path.dirname(file_name)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        volume_krig.tofile(file_name+"_SolConn_krig.raw")
        volume_nn.tofile(file_name+"_SolConn_nn.raw")

    return volume_krig, volume_nn


def interpolate_solid_connection_surfaces(volume, fluid_default=1, file_name=""):
    print("-Full Volume (with Surface), sample cells: ", np.sum((volume != 0) & (volume != 1)))
    volume_surface = Remove_Internal_Solid(volume)
    
    print("-Full Volume (no Surface), sample cells: ", np.sum((volume_surface != 0) & (volume_surface != 1)))
    volume_krig, volume_nn = interpolate_solid_connections(volume_surface, fluid_default=fluid_default) 
    
    
    if file_name != "":
        # Verificar se a pasta existe, caso contrário, criar
        folder = os.path.dirname(file_name)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        volume_krig.tofile(file_name+"_Surface_SolConn_krig.raw")
        volume_nn.tofile(file_name+"_Surface_SolConn_nn.raw")
    
    return volume_krig, volume_nn


def limit_interpolation_to_solid(volume, interpolated_domain, fluid_default_value):

    final_domain = volume.copy()
    for index in np.ndindex(volume.shape):
        # If is solid: final = interpolated
        if volume[index] != fluid_default_value:
            final_domain[index] = interpolated_domain[index]

    return final_domain


def Apply_Kriging(df, n_points=5, tested_methods=["linear", "power", "gaussian", "spherical", "exponential", "hole-effect"],
                  x_lim=(0, 250), y_lim=(0, 250), z_lim=(0, 250)):
    print("-Applying Kriging: ")
    
    # Coleta o sub domínio em analise
    x_min, x_max = x_lim
    y_min, y_max = y_lim
    z_min, z_max = z_lim

    # Coletar as coordenadas e o ângulo
    x = df['x'].values
    y = df['y'].values
    z = df['z'].values
    angle = df['angle'].values

    # Definindo a grade de pontos para a interpolação (menos pontos para otimizar memória)
    gridx = np.arange(x_min, x_max, 1)
    gridy = np.arange(y_min, y_max, 1)
    gridz = np.arange(z_min, z_max, 1)
    gridx = gridx.astype(float)
    gridy = gridy.astype(float)
    gridz = gridz.astype(float)

    # Obter as dimensões do grid
    x_dim = len(gridx)
    y_dim = len(gridy)
    z_dim = len(gridz)

    # Se todas as medicoes sao iguais, a estimativa para todo o dominio sera esse valor
    # Esse caso eh importante para subdominios pequenos (com poucas medidas).
    if np.all(angle == angle[0]):
        print(f"--All samples provided have the exact same value ({angle[0]}), kriging was not necessary. The single value was propagated.")
        # Criar o array 3D preenchido com angle[0]
        return np.full((x_dim, y_dim, z_dim), angle[0])
    elif angle.size <= 2:
        print("--Only 2 samples were provided, kriging is not applicable. Mean values was propagated.")
        # Criar o array 3D preenchido com angle[0]
        return np.full((x_dim, y_dim, z_dim), (angle[0]+angle[1])/2) 
    else:
        
        # Criar o modelo de krigagem com variogram model (Ex: exponencial)
        # Definindo o modelo de variograma, neste caso exponencial (exponential)

        best_residual = float('inf')
        best_prediction = None

        for method in tested_methods:
            print("--Universal Kriging, method: ", method)
            ok3d = UniversalKriging3D(x, y, z, angle, variogram_model=method, enable_plotting=True)

            # A matriz de kriging de cada ponto do grid tem N = (n_samples+1)**2 elementos,
            # O método vetorizado utiliza a inversao da matriz, demandando 32*N**2 bytes.
            # O metodo loop evita a inversao de matriz, executando cada ponto do grid em loop

            predictions_3D, residual_variances = ok3d.execute(
                style="grid",
                backend='loop',
                xpoints=gridx,
                ypoints=gridy,
                zpoints=gridz)

            predictions_3D = predictions_3D.transpose( 2, 1, 0)  # Ajuste de [z, y, x] para [x, y, z]
            
            statistical_maximum_residual = np.mean(residual_variances)+2*np.std(residual_variances)
            if  statistical_maximum_residual < best_residual:
                print("New best solution found: statistical maximum residual: ", round(statistical_maximum_residual,2))
                best_prediction = predictions_3D
            
        return best_prediction


def Filtra_KNN(df_medidas, K=5):
    # Parâmetro K (número de vizinhos mais próximos)
    coords = df_medidas[['x', 'y', 'z']].values
    # Aplicando o modelo de K-vizinhos mais próximos
    knn = NearestNeighbors(n_neighbors=K)
    knn.fit(coords)
    distances, indices = knn.kneighbors(coords)

    # Calculando a média ou mediana dos ângulos dos K vizinhos mais próximos
    angulo_filtrado_knn = []
    for i in range(len(df_medidas)):
        centroid_grupo = indices[i]
        # Usando média, pode ser mediana
        angulo_filtrado_knn.append(
            df_medidas.iloc[centroid_grupo]['angle'].mean())

    df_filtered = df_medidas.copy()
    df_filtered['angle'] = angulo_filtrado_knn

    return df_filtered


def Apply_NearestNeighbor(sub_df, n_neighbors=1, x_lim=(0, 250), y_lim=(0, 250), z_lim=(0, 250)):
    print("-Applying Nearest Neighbor:")
    # Nearest Neighbor model
    x = sub_df['x'].values
    y = sub_df['y'].values
    z = sub_df['z'].values
    angle = sub_df['angle'].values
    coords = np.vstack([x, y, z]).T  # Combine sampled coordinates
    nn = NearestNeighbors(n_neighbors=n_neighbors)  # Configure the model
    nn.fit(coords)  # Fit the model to the sampled coordinates

    # Coleta o sub domínio em analise
    x_min, x_max = x_lim
    y_min, y_max = y_lim
    z_min, z_max = z_lim

    gridx = np.arange(x_min, x_max, 1)
    gridy = np.arange(y_min, y_max, 1)
    gridz = np.arange(z_min, z_max, 1)

    # Create the interpolation grid
    x_grid, y_grid, z_grid = np.meshgrid(gridx, gridy, gridz, indexing='ij')
    # Flatten grid to [x, y, z] points
    grid_points = np.vstack([x_grid.ravel(), y_grid.ravel(), z_grid.ravel()]).T
    # Find the nearest neighbors and their indices
    distances, indices = nn.kneighbors(grid_points)
    # Assign the corresponding values to the grid points
    # Use the nearest neighbor's value
    interpolated_values = angle[indices[:, 0]]
    # Reshape the interpolated values to match the 3D grid shape
    interpolated_grid = interpolated_values.reshape(x_grid.shape)

    
    return interpolated_grid