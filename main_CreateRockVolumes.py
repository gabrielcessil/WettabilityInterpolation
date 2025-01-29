import numpy as np
import Plotter as pl
import math
import os


# === MODULE FUNCTIONS ===

def create_centered_cube(domain_shape, cube_shape, points, file_path):
    # Verificar se a pasta existe, caso contrário, criar
    folder = os.path.dirname(file_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    """
    Cria um volume 3D com um cubo centralizado de dimensões específicas e valores nos cantos.

    Parameters:
        domain_shape (tuple): Dimensões do domínio 3D (x, y, z).
        cube_shape (tuple): Dimensões do cubo (xc, yc, zc).
        corner_values (list): Valores atribuídos aos 8 cantos do cubo.
        file_path (str): Caminho para salvar o arquivo .raw.

    Returns:
        numpy.ndarray: O volume 3D com o cubo centralizado.
    """
    domain = np.ones(domain_shape, dtype=np.uint8)
    
    # Calcular os limites do cubo
    x_start = int((domain_shape[0] - cube_shape[0]) // 2)
    y_start = int((domain_shape[1] - cube_shape[1]) // 2)
    z_start = int((domain_shape[2] - cube_shape[2]) // 2)
    
    
    x_end, y_end, z_end = x_start + cube_shape[0], y_start + cube_shape[1], z_start + cube_shape[2]
    domain[x_start:x_end, y_start:y_end, z_start:z_end] = 0
    
    for x, y, z, value in points:
        print(f"Cell ({x} {y} {z}) replaced {domain[x,y,z]} with {value}")
        domain[int(x), int(y), int(z)] = value
    

    domain.tofile(file_path + ".raw")
    print(f"Volume salvo como {file_path}.raw")
    return domain


def create_array_with_parallel_planes(points, shape, plane_axis, thickness, file_path):
    """
    Cria um volume 3D com dois planos paralelos de zeros, localizados nas duas faces opostas do domínio,
    com uma espessura específica, e insere pontos anotados.

    Parameters:
        points (list of tuples): Lista de pontos para anotar no array, no formato (x, y, z, valor).
        shape (tuple): Dimensões do array 3D.
        plane_axis (int): Eixo ao longo do qual os planos são criados (0 para x, 1 para y, 2 para z).
        thickness (int): Espessura dos planos.
        file_path (str): Caminho para salvar o arquivo .raw.

    Returns:
        numpy.ndarray: O array 3D com os planos paralelos e os pontos anotados.
    """

    array = np.ones(shape, dtype=np.uint8)

    # Definir a posição dos planos nas duas faces opostas
    plane1_center = thickness // 2
    plane2_center = shape[plane_axis] - thickness // 2

    plane1_bounds = (plane1_center - thickness // 2, plane1_center + (thickness + 1) // 2)
    plane2_bounds = (plane2_center - thickness // 2, plane2_center + (thickness + 1) // 2)

    # Criar os planos
    slices = [slice(None)] * 3
    slices[plane_axis] = slice(*plane1_bounds)
    array[tuple(slices)] = 0
    slices[plane_axis] = slice(*plane2_bounds)
    array[tuple(slices)] = 0

    # Adicionar pontos
    for x, y, z, value in points:
        print(f"Cell ({x} {y} {z}) replaced {array[x,y,z]} with {value}")
        array[int(x), int(y), int(z)] = value

    # Verificar se a pasta existe, caso contrário, criar
    folder = os.path.dirname(file_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    
    # Salvar o array em um arquivo .raw
    array.tofile(file_path + ".raw")
    print(f"Volume salvo como {file_path}.raw")
    return array

def create_array_with_single_plane(points, shape, plane_axis, thickness, file_path=None):
    """
    Cria um volume 3D com um único plano de zeros na face extrema do domínio (índice máximo),
    com uma espessura específica, e insere pontos anotados.

    Parameters:
        points (list of tuples): Lista de pontos para anotar no array, no formato (x, y, z, valor).
        shape (tuple): Dimensões do array 3D.
        plane_axis (int): Eixo ao longo do qual o plano é criado (0 para x, 1 para y, 2 para z).
        thickness (int): Espessura do plano.
        file_path (str): Caminho para salvar o arquivo .raw.

    Returns:
        numpy.ndarray: O array 3D com o plano e os pontos anotados.
    """

    # Criação do array preenchido com 1's
    array = np.ones(shape, dtype=np.uint8)

    # Definir a posição do plano na face extrema do domínio
    plane_start = shape[plane_axis] - thickness
    plane_end = shape[plane_axis]

    # Criar o plano
    slices = [slice(None)] * 3
    slices[plane_axis] = slice(plane_start, plane_end)
    array[tuple(slices)] = 0

    # Adicionar pontos
    for x, y, z, value in points:
        print(f"Cell ({x} {y} {z}) replaced {array[x,y,z]} with {value}")
        array[int(x), int(y), int(z)] = value


    if file_path is not None: 
        # Verificar se a pasta existe, caso contrário, criar
        folder = os.path.dirname(file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        
        
        # Salvar o array em um arquivo .raw
        array.tofile(file_path + ".raw")
        print(f"Volume salvo como {file_path}.raw")
    return array
    

def create_plane_with_circles(shape, plane, spacing, radius1, radius2, value1, value2, num_points1, num_points2, file_path=""):
    
    """
    Cria um plano no domínio 3D com dois círculos de pontos igualmente espaçados no perímetro.

    Parameters:
        shape (tuple): Dimensões do domínio 3D (x, y, z).
        plane (str): O plano a ser criado, pode ser "XY", "XZ" ou "YZ".
        spacing (int): Distância entre os centros dos dois círculos.
        radius1 (int): Raio do primeiro círculo.
        radius2 (int): Raio do segundo círculo.
        value1 (int): Valor atribuído aos pontos do primeiro círculo.
        value2 (int): Valor atribuído aos pontos do segundo círculo.
        num_points1 (int): Número de pontos no perímetro do primeiro círculo.
        num_points2 (int): Número de pontos no perímetro do segundo círculo.
        file_path (str): Caminho para salvar o volume gerado como arquivo .raw.

    Returns:
        numpy.ndarray: O volume 3D gerado.
    """
    # Verificar se a pasta existe, caso contrário, criar
    folder = os.path.dirname(file_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
        
    # Inicializar o volume com valores 1
    array = np.ones(shape, dtype=np.uint8)
    
    # Determinar o eixo fixo do plano
    if plane.upper() == "XY":
        plane_axis = 2  # Z é fixo
        plane_slice = shape[plane_axis] // 2
        plane_dim = shape[:2]
    elif plane.upper() == "XZ":
        plane_axis = 1  # Y é fixo
        plane_slice = shape[plane_axis] // 2
        plane_dim = (shape[0], shape[2])
    elif plane.upper() == "YZ":
        plane_axis = 0  # X é fixo
        plane_slice = shape[plane_axis] // 2
        plane_dim = shape[1:]
    else:
        raise ValueError("O plano deve ser 'XY', 'XZ' ou 'YZ'")
    
    # Verificar se os raios e o espaçamento cabem no plano
    total_width = radius1 + radius2 + spacing
    plane_width, plane_height = plane_dim
    if total_width > plane_width:
        raise ValueError(f"A soma dos raios e o espaçamento ({total_width}) excedem a largura do plano ({plane_width}).")
    
    if max(radius1, radius2) * 2 > plane_height:
        raise ValueError(f"O maior círculo excede a altura do plano ({plane_height}).")
    
    # Calcular os centros dos círculos o mais próximo possível do início do plano
    center_y = plane_height // 2  # Os círculos serão alinhados verticalmente no centro do plano
    center1_x = radius1  # Primeiro círculo próximo ao início do plano
    center2_x = center1_x + radius1 + spacing + radius2  # Segundo círculo logo após o primeiro

    center1 = (center1_x, center_y)
    center2 = (center2_x, center_y)

    # Criar o plano no array (espessura = 1) e preenchê-lo com 0
    slices = [slice(None)] * 3
    slices[plane_axis] = plane_slice
    plane_array = array[tuple(slices)]
    plane_array.fill(0)  # Plano base preenchido com 0

    # Função auxiliar para calcular pontos no perímetro de um círculo
    def calculate_perimeter_points(center, radius, num_points, other_center):
        cx, cy = center
        ox, oy = other_center
        # Ângulo inicial: em direção ao outro círculo
        angle_to_other = math.atan2(oy - cy, ox - cx)
        points = []
        for i in range(num_points):
            angle = angle_to_other + 2 * math.pi * i / num_points
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            points.append((x, y))
        return points

    # Calcular os pontos no perímetro dos dois círculos
    points1 = calculate_perimeter_points(center1, radius1, num_points1, center2)
    points2 = calculate_perimeter_points(center2, radius2, num_points2, center1)

    # Desenhar os pontos dos círculos no plano
    for x, y in points1:
        if 0 <= x < plane_array.shape[0] and 0 <= y < plane_array.shape[1]:
            plane_array[x, y] = value1

    for x, y in points2:
        if 0 <= x < plane_array.shape[0] and 0 <= y < plane_array.shape[1]:
            plane_array[x, y] = value2

    # Atualizar o array com o plano gerado
    array[tuple(slices)] = plane_array

    # Salvar o volume gerado como arquivo .raw, se o caminho for fornecido
    if file_path:
        array.tofile(file_path + ".raw")
        print(f"Volume salvo como {file_path}.raw")

    return array


def create_array_with_c_plane(points, shape, plane_axis, thickness, file_path, c_cut_size, fill_value=1):
    """
    Creates a 3D volume with a 'C'-shaped plane on the extreme face of the domain (maximum index),
    with a specific thickness, and inserts annotated points.

    Parameters:
        points (list of tuples): List of points to annotate in the array, in the format (x, y, z, value).
        shape (tuple): Dimensions of the 3D array.
        plane_axis (int): Axis along which the plane is created (0 for x, 1 for y, 2 for z).
        thickness (int): Thickness of the plane.
        file_path (str): Path to save the .raw file.
        fill_value (int): Value to fill the "C" area. Default is 1.
        c_cut_size (int, optional): Size of the cut-out rectangle in the "C". Defaults to shape[other_axis]//4.

    Returns:
        numpy.ndarray: The 3D array with the "C"-shaped plane and annotated points.
    """
    # Create the initial array with a plane
    array = create_array_with_single_plane(points, shape, plane_axis, thickness, file_path=None)


    # Define the plane slice for modification
    plane_start = shape[plane_axis] - thickness
    plane_end = shape[plane_axis]

    # Identify other axes for the "C" shape
    other_axes = [i for i in range(3) if i != plane_axis]
    axis1, axis2 = other_axes

    # Calculate the cut-out rectangle for the "C" shape
    cut_start1 = shape[axis1] // 2 - c_cut_size // 2  # Centered along axis1 (y-axis)
    cut_end1 = shape[axis1] // 2 + c_cut_size // 2

    cut_start2 = shape[axis2] // 2  # Starting from the middle of axis2 (z-axis)
    cut_end2 = shape[axis2]  # Going down to the bottom (z-axis)

    # Apply the cut-out rectangle (create the "C")
    slices = [slice(None)] * 3
    slices[plane_axis] = slice(plane_start, plane_end)  # Restrict to the plane
    slices[axis1] = slice(cut_start1, cut_end1)  # Center along the other axis (y-axis)
    slices[axis2] = slice(cut_start2, cut_end2)  # Rectangle cut-out from the middle to the bottom (z-axis)
    array[tuple(slices)] = fill_value  # Fill the cut-out area with the specified value

    # Add annotated points
    for x, y, z, value in points:
        print(f"Cell ({x}, {y}, {z}) replaced {array[x, y, z]} with {value}")
        array[int(x), int(y), int(z)] = value

    # Ensure the output folder exists
    folder = os.path.dirname(file_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    # Save the array to a .raw file
    array.tofile(file_path + ".raw")
    print(f"Volume saved as {file_path}.raw")
    return array
# === AUXILIARY FUNCTIONS ===

def generate_angle_points_example_1(sub_cube_length):
    return [
        # Face 1
        [0, int(sub_cube_length//2),      0,  100], # Bottom
        [0, int(sub_cube_length//2),      sub_cube_length - 1, 100], # Top
        [0, 0,                            int(sub_cube_length//2), 10], #Left
        [0, sub_cube_length - 1,          int(sub_cube_length//2), 10], #Right
        
        # Face 2
        [sub_cube_length - 1, int(sub_cube_length//2),      0, 10], #Bottom
        [sub_cube_length - 1, int(sub_cube_length//2),      sub_cube_length - 1, 10], # Top
        [sub_cube_length - 1, 0,                            int(sub_cube_length//2), 100], # Left
        [sub_cube_length - 1, sub_cube_length - 1,          int(sub_cube_length//2), 100], # Right
    ]
def generate_angle_points_example_2(sub_cube_length):
    return [
        # Face 1
        [0, int(sub_cube_length//2),      0, 100] ,# Bottom
        [0, int(sub_cube_length//2),      sub_cube_length - 1, 100], # Top
        [0, 0,                            int(sub_cube_length//2), 100], #Left
        [0, sub_cube_length - 1,          int(sub_cube_length//2), 100], #Right
        
        # Face 2
        [sub_cube_length - 1, int(sub_cube_length//2),      0, 10], #Bottom
        [sub_cube_length - 1, int(sub_cube_length//2),      sub_cube_length - 1, 10], # Top
        [sub_cube_length - 1, 0,                            int(sub_cube_length//2), 10], # Left
        [sub_cube_length - 1, sub_cube_length - 1,          int(sub_cube_length//2), 10], # Right
    ]

def generate_angle_points_example_4(cube_length, thickness):
    """Gera pontos com ângulos para o exemplo 5."""
    
    return [
        # Face 1
        [cube_length-1,             (cube_length//2), 1*(cube_length//5), 10], 
        [cube_length-1,             (cube_length//2), 4*(cube_length//5), 50],
        # Face 2
        [cube_length-thickness,   (cube_length//2), 1*(cube_length//5), 100], 
        [cube_length-thickness,   (cube_length//2), 4*(cube_length//5), 20]
    ]

def generate_angle_points_example_5(cube_length):
    """Gera pontos com ângulos para o exemplo 5."""
    
    return [
        [cube_length-1, 2*(cube_length//5), 2*(cube_length//5), 100], 
        [cube_length-1, 2*(cube_length//5), 3*(cube_length//5), 50],
        [cube_length-1, 3*(cube_length//5), 2*(cube_length//5), 10], 
        [cube_length-1, 3*(cube_length//5), 3*(cube_length//5), 5]
    ]

def generate_angle_points_example_6(cube_length, thickness):
    """Gera pontos com ângulos para o exemplo 5."""
    
    return [
        # Face 1
        [cube_length-1,             (cube_length//2), 1*(cube_length//5), 10], 
        [cube_length-1,             (cube_length//2), 4*(cube_length//5), 50],
        # Face 2
        [cube_length-thickness,   (cube_length//2), 1*(cube_length//5), 20], 
        [cube_length-thickness,   (cube_length//2), 4*(cube_length//5), 100]
    ]

def generate_angle_points_example_7(cube_length, thickness):
    """Gera pontos com ângulos para o exemplo 6."""
    return [
        # Plane 1
        [0+thickness-1, 0,              0,              10], 
        [0+thickness-1, 0,              cube_length-1,  50],
        [0+thickness-1, cube_length-1,  0,              100], 
        [0+thickness-1, cube_length-1,  cube_length-1,  90],
        
        # Plane 2
        [cube_length-1, 0,              0,              40], 
        [cube_length-1, 0,              cube_length-1,  35],
        [cube_length-1, cube_length-1,  0,              10], 
        [cube_length-1, cube_length-1,  cube_length-1,  5]
    ]

def generate_angle_points_example_8(cube_length, thickness):
    """Gera pontos com ângulos para o exemplo 7."""
    return [
        # Plano 1 face 1
        [0+thickness-1,           0,             0,             100], 
        [0+thickness-1,           0,             cube_length-1, 100],
        [0+thickness-1,           cube_length-1, 0,             65],
        [0+thickness-1,           cube_length-1, cube_length-1, 10],
        
        # Plano 1 face 2
        [0,                     0,              0,             100],
        [0,                     0,              cube_length-1, 100],
        [0,                     cube_length-1,  0,             65],
        [0,                     cube_length-1,  cube_length-1, 10],
        
        # Plano 2 face 1
        [cube_length-thickness+1, 0,              0,             60],
        [cube_length-thickness+1, 0,              cube_length-1, 30],
        [cube_length-thickness+1, cube_length-1,  0,             60],
        [cube_length-thickness+1, cube_length-1,  cube_length-1, 30],
        
        # Plano 2 face 2
        [cube_length-1,         0,              0,             80],
        [cube_length-1,         0,              cube_length-1, 10],
        [cube_length-1,         cube_length-1,  0,             80],
        [cube_length-1,         cube_length-1,  cube_length-1, 10],
    ]

def generate_angle_points_example_12(cube_length, c_cut_size):
    cut_end = cube_length // 2 + c_cut_size // 2

    return   [[cube_length-1,cut_end+1,cube_length - cube_length//6, 10],
              [cube_length-1,cut_end+1,cube_length - cube_length//3, 50],
              [cube_length-1,cut_end+1,cube_length - cube_length//2, 100]]

# MAKE SURE THE SAMPLES ARE CONNECTED TO SOLID SURFACE

# === EXAMPLES ===
cube_length = 25
# Computation
volume_shape = (cube_length, cube_length, cube_length)

"""
# Example 1: Cube in the center and samples in his corners (n)
points = generate_angle_points_example_1(cube_length)
array_ex1 = create_centered_cube(domain_shape=volume_shape, cube_shape=volume_shape, points=points, file_path="Rock Volumes/Example_1")
pl.Plot_Domain(array_ex1, "Rock Volumes/Example_1_SolidRock", remove_value=[1]) 

# Example 2: Cube in the center and samples in his corners (n)
points = generate_angle_points_example_2(cube_length)
array_ex2 = create_centered_cube(domain_shape=volume_shape, cube_shape=volume_shape, points=points, file_path="Rock Volumes/Example_2")
pl.Plot_Domain(array_ex2, "Rock Volumes/Example_2_SolidRock", remove_value=[1]) 

# Example 4: Plane with 2 samples in each face (Problem: oposit sample in other face is closer than others)
points = generate_angle_points_example_4(cube_length, thickness=5)
array_ex6 = create_array_with_single_plane(points=points, shape=volume_shape, plane_axis=0, thickness=5, file_path="Rock Volumes/Example_4")
pl.Plot_Domain(array_ex6, "Rock Volumes/Example_4_SolidRock", remove_value=[1])

# Example 5: Plane with 4 centered/grouped samples
points = generate_angle_points_example_5(cube_length)
array_ex5 = create_array_with_single_plane(points=points, shape=volume_shape, plane_axis=0, thickness=5, file_path="Rock Volumes/Example_5")
pl.Plot_Domain(array_ex5, "Rock Volumes/Example_5_SolidRock", remove_value=[1])

# Example 6: Plane with 2 samples in each face (Problem solved (4))
points = generate_angle_points_example_6(cube_length, thickness=5)
array_ex6 = create_array_with_single_plane(points=points, shape=volume_shape, plane_axis=0, thickness=5, file_path="Rock Volumes/Example_6")
pl.Plot_Domain(array_ex6, "Rock Volumes/Example_6_SolidRock", remove_value=[1])

# Example 7: Parallel planes with 4 Samples each. As they too close and very thick, the parallel face influenciate too much
thickness=11
points = generate_angle_points_example_7(cube_length, thickness)
array_ex7 = create_array_with_parallel_planes(points=points, shape=volume_shape, plane_axis=0, thickness=thickness, file_path="Rock Volumes/Example_7")
pl.Plot_Domain(array_ex7, "Rock Volumes/Example_7_SolidRock", remove_value=[1])

# Example 8: Parallel planes with 4 samples on each face.
thickness = 5
plane_axis = 0
points = generate_angle_points_example_8(cube_length, thickness=thickness)
array_ex8 = create_array_with_parallel_planes(points=points, shape=volume_shape, plane_axis=plane_axis, thickness=thickness, file_path="Rock Volumes/Example_8")
pl.Plot_Domain(array_ex8, "Rock Volumes/Example_8_SolidRock", remove_value=[1])


# Example 9: Circles too close to each other, so that the kriging fails
plane = "XY"
cube_length = 50
spacing = 2
radius1 = 9
radius2 = 9
value1 = 50
value2 = 100
num_points1 = 8  # Número de pontos no perímetro do primeiro círculo
num_points2 = 8  # Número de pontos no perímetro do segundo círculo
volume_shape = (cube_length, cube_length, cube_length)
array_ex9 = create_plane_with_circles(shape=volume_shape, plane=plane, spacing=spacing,
                                      radius1=radius1, radius2=radius2, value1=value1, 
                                      value2=value2, num_points1=num_points1, num_points2=num_points2,file_path="Rock Volumes/Example_9")
pl.Plot_Domain(array_ex9, "Rock Volumes/Example_9_SolidRock", remove_value=[1])

# Example 10: Circles poorly samples, so that the kriging fails
plane = "XY"
cube_length = 50
spacing = 10
radius1 = 9
radius2 = 9
value1 = 50
value2 = 100
num_points1 = 4  # Número de pontos no perímetro do primeiro círculo
num_points2 = 4  # Número de pontos no perímetro do segundo círculo
volume_shape = (cube_length, cube_length, cube_length)
array_ex9 = create_plane_with_circles(shape=volume_shape, plane=plane, spacing=spacing,
                                      radius1=radius1, radius2=radius2, value1=value1, 
                                      value2=value2, num_points1=num_points1, num_points2=num_points2,file_path="Rock Volumes/Example_10")
pl.Plot_Domain(array_ex9, "Rock Volumes/Example_10_SolidRock", remove_value=[1])

# Example 11: Circles separated and with enough samples, so that the kriging suceed
plane = "XY"
cube_length = 50
spacing = 10
radius1 = 9
radius2 = 9
value1 = 50
value2 = 100
num_points1 = 8  # Número de pontos no perímetro do primeiro círculo
num_points2 = 8  # Número de pontos no perímetro do segundo círculo
volume_shape = (cube_length, cube_length, cube_length)
array_ex9 = create_plane_with_circles(shape=volume_shape, plane=plane, spacing=spacing,
                                      radius1=radius1, radius2=radius2, value1=value1, 
                                      value2=value2, num_points1=num_points1, num_points2=num_points2,file_path="Rock Volumes/Example_11")
pl.Plot_Domain(array_ex9, "Rock Volumes/Example_11_SolidRock", remove_value=[1])
"""
"""
# Example 12
cut_size = cube_length // 6
points = generate_angle_points_example_12(volume_shape[0], cut_size)
array_ex12 = create_array_with_c_plane(points, shape=volume_shape, plane_axis=0, thickness=4, c_cut_size=cut_size, file_path="Rock Volumes/Example_12")
pl.Plot_Domain(array_ex12, "Rock Volumes/Example_12_SolidRock", remove_value=[1])
"""

# Example 13: Circles too close to each other, so that the kriging fails
plane = "XY"
cube_length = 50
spacing = 2
radius1 = 9
radius2 = 12
value1 = 50
value2 = 100
num_points1 = 2  # Número de pontos no perímetro do primeiro círculo
num_points2 = 2  # Número de pontos no perímetro do segundo círculo
volume_shape = (cube_length, cube_length, cube_length)
array_ex9 = create_plane_with_circles(shape=volume_shape, plane=plane, spacing=spacing,
                                      radius1=radius1, radius2=radius2, value1=value1, 
                                      value2=value2, num_points1=num_points1, num_points2=num_points2,file_path="Rock Volumes/Example_13")
pl.Plot_Domain(array_ex9, "Rock Volumes/Example_13_SolidRock", remove_value=[1])

"""
# Example 14: Circles poorly samples, so that the kriging fails
plane = "XY"
cube_length = 50
spacing = 10
radius1 = 9
radius2 = 12
value1 = 50
value2 = 100
num_points1 = 2  # Número de pontos no perímetro do primeiro círculo
num_points2 = 2  # Número de pontos no perímetro do segundo círculo
volume_shape = (cube_length, cube_length, cube_length)
array_ex9 = create_plane_with_circles(shape=volume_shape, plane=plane, spacing=spacing,
                                      radius1=radius1, radius2=radius2, value1=value1, 
                                      value2=value2, num_points1=num_points1, num_points2=num_points2,file_path="Rock Volumes/Example_14")
pl.Plot_Domain(array_ex9, "Rock Volumes/Example_14_SolidRock", remove_value=[1])
"""