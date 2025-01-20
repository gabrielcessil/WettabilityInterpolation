import numpy as np
import pandas as pd
from scipy.ndimage import label, generate_binary_structure


def Separate_NonFluid_Connections(volume, fluid_default=1):
    # Collect sub-arrays
    original_array = volume.copy()

    # Collect every cell with 'A' as 1, otherwise 0
    solid_volume = (original_array != fluid_default).astype(np.uint8)
    s = generate_binary_structure(rank=3, connectivity=2)
    connected_labels, num_features = label(solid_volume, structure=s)
    connected_labels = connected_labels.astype(np.uint8)

    sub_arrays = []
    labels = range(1, num_features + 1)
    for label_value in labels:
        
        # Which cells belong to this group
        mask = (connected_labels == label_value)
        
        # Replace non-matching regions with 'fluid_default
        sub_array = np.where(mask, original_array, fluid_default)
        sub_array = sub_array.astype(np.uint8)
        
        # Save result
        sub_arrays.append(sub_array)

    return sub_arrays, connected_labels, labels

def Get_Neighbors(array, i, j, k):
    dim = array.shape
    i_max, j_max, k_max = dim[0]-1, dim[1]-1, dim[2]-1
    # Connectivity level 1

    top = array[i][j][k+1] if k < k_max else None
    bottom = array[i][j][k-1] if k > 0 else None
    left = array[i][j+1][k] if j < j_max else None
    right = array[i][j-1][k] if j > 0 else None
    front = array[i+1][j][k] if i < i_max else None
    back = array[i-1][j][k] if i > 0 else None
    return [top, bottom, left, right, front, back]

def Remove_Internal_Solid(array, fluid_default_value=1):
    # Create array to work on
    new_array = array.copy()
    
    # Iterate over dimensions
    dim = array.shape
    for i in range(dim[0]):
        for j in range(dim[1]):
            for k in range(dim[2]):

                # If the current cell is a solid (not fluid):
                if array[i][j][k] != fluid_default_value:

                    neighbors = Get_Neighbors(array, i, j, k)

                    # If any neighbor is fluid or None (boundary), the cell is not internal solid
                    # If not, it is an internal solid and must be set to fluid
                    if any((n == fluid_default_value) or (n is None) for n in neighbors):
                        continue  # Keep the current solid cell
                    else:
                        # Set internal solid to fluid
                        new_array[i][j][k] = fluid_default_value
    
    # Return all samples to original cells: samples should not be removed with internal solid
    mask_sample_cells = ~np.isin(array, [1, 0])
    new_array[mask_sample_cells] = array[mask_sample_cells]

    return new_array



def df_to_3d_array(df, x_col='x', y_col='y', z_col='z', angle_col='angle'):

    # Determinar os tamanhos do array 3D
    x_size = int(df['x'].max())
    y_size = int(df['y'].max())
    z_size = int(df['z'].max())

    # Inicializar o array 3D com NaNs
    array_3d = np.full((x_size, y_size, z_size), np.nan)

    # Preencher o array com os valores de angle
    for _, row in df.iterrows():
        x = int(row['x'])
        y = int(row['y'])
        z = int(row['z'])
        array_3d[x, y, z] = row[angle_col]

    return array_3d





def array3D_to_dataframe(volume, volume_shape, remove_where_value=1.):

    # Gere grades de coordenadas 3D (x, y, z)
    x_coords = np.arange(volume_shape[0])  # Coordenadas x
    y_coords = np.arange(volume_shape[1])  # Coordenadas y
    z_coords = np.arange(volume_shape[2])  # Coordenadas z

    # Crie matrizes 3D de coordenadas para cada eixo
    x_grid, y_grid, z_grid = np.meshgrid(
        x_coords, y_coords, z_coords, indexing="ij")

    # Achate (flatten) os arrays 3D para 1D para formar as colunas
    x_flat = x_grid.ravel()  # Coordenadas x achatadas
    y_flat = y_grid.ravel()  # Coordenadas y achatadas
    z_flat = z_grid.ravel()  # Coordenadas z achatadas
    values_flat = volume.ravel()  # Valores do volume achatados

    # Crie o DataFrame com as colunas x, y, z e value
    df = pd.DataFrame({
        'x': x_flat,
        'y': y_flat,
        'z': z_flat,
        'angle': values_flat
    })

    df = df[df["angle"] != remove_where_value]
    return df

def RandomCube(mean1, mean2, x_bins, y_bins, z_bins, cube_size):
    """
    Creates a 3D numpy array divided into sub-cubes based on predefined bins and fills each sub-cube
    with a random value (mean1 or mean2).

    Parameters:
        mean1 (float): First value to assign randomly to sub-cubes.
        mean2 (float): Second value to assign randomly to sub-cubes.
        x_bins (np.ndarray): Bin edges for the x dimension.
        y_bins (np.ndarray): Bin edges for the y dimension.
        z_bins (np.ndarray): Bin edges for the z dimension.
        cube_size (int): Size of each sub-cube along x, y, z axes.

    Returns:
        np.ndarray: A 3D numpy array filled with mean1 or mean2.
    """
    # Determinar o número de bins em cada eixo
    x_size = len(x_bins) - 1
    y_size = len(y_bins) - 1
    z_size = len(z_bins) - 1

    # Criar um array 3D para os subcubos preenchido aleatoriamente com mean1 ou mean2
    subcubo_array = np.random.choice(
        [mean1, mean2], size=(x_size, y_size, z_size))

    # Expandir os subcubos para preencher o domínio
    array_3d = np.repeat(np.repeat(np.repeat(
        subcubo_array, cube_size, axis=0), cube_size, axis=1), cube_size, axis=2)

    # Ajustar o tamanho final do array ao domínio exato
    x_final_size = int(x_bins[-1] - x_bins[0])
    y_final_size = int(y_bins[-1] - y_bins[0])
    z_final_size = int(z_bins[-1] - z_bins[0])

    array_3d = array_3d[:x_final_size, :y_final_size, :z_final_size]

    return array_3d

def separate_into_cubes(df, x_bins, y_bins, z_bins, cube_size):

    # Criar colunas categóricas para x, y e z
    df['x_bin'] = pd.cut(df['x'], bins=x_bins,
                         right=False, include_lowest=True)
    df['y_bin'] = pd.cut(df['y'], bins=y_bins,
                         right=False, include_lowest=True)
    df['z_bin'] = pd.cut(df['z'], bins=z_bins,
                         right=False, include_lowest=True)

    # Inicializar dicionário para armazenar os sub-cubos
    sub_dataframes = []

    # Iterar sobre os bins únicos de cada eixo
    for x_bin in df['x_bin'].cat.categories:
        for y_bin in df['y_bin'].cat.categories:
            for z_bin in df['z_bin'].cat.categories:
                # Filtrar o DataFrame para obter os dados do sub-cubo atual
                sub_df = df[(df['x_bin'] == x_bin) & (
                    df['y_bin'] == y_bin) & (df['z_bin'] == z_bin)]

                if not sub_df.empty:
                    # Adicionar colunas para os limites de cada bin
                    sub_df = sub_df[['x', 'y', 'z', 'angle']].copy()
                    sub_df['x_min'] = x_bin.left
                    sub_df['x_max'] = x_bin.right
                    sub_df['y_min'] = y_bin.left
                    sub_df['y_max'] = y_bin.right
                    sub_df['z_min'] = z_bin.left
                    sub_df['z_max'] = z_bin.right

                    # Armazenar o sub-DataFrame na lista
                    sub_dataframes.append(sub_df)

    return sub_dataframes.copy()
