import numpy as np
import Plotter as pl
import math
import os


# === MODULE FUNCTIONS ===

def create_centered_cube(domain_shape, cube_shape, corner_values, file_path):
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

    # Atribuir valores aos cantos
    domain[x_start, y_start, z_start] = corner_values[0]
    domain[x_start, y_end - 1, z_start] = corner_values[1]
    domain[x_start, y_start, z_end - 1] = corner_values[2]
    domain[x_start, y_end - 1, z_end - 1] = corner_values[3]
    domain[x_end - 1, y_start, z_start] = corner_values[4]
    domain[x_end - 1, y_end - 1, z_start] = corner_values[5]
    domain[x_end - 1, y_start, z_end - 1] = corner_values[6]
    domain[x_end - 1, y_end - 1, z_end - 1] = corner_values[7]

    domain.tofile(file_path + ".raw")
    print(f"Volume salvo como {file_path}.raw")
    return domain


def create_array_with_parallel_planes(points, shape, plane_axis, separation, thickness, file_path):
    """
    Cria um volume 3D com dois planos paralelos de zeros, separados por uma distância específica, e insere pontos anotados.

    Parameters:
        points (list of tuples): Lista de pontos para anotar no array, no formato (x, y, z, valor).
        shape (tuple): Dimensões do array 3D.
        plane_axis (int): Eixo ao longo do qual os planos são criados (0 para x, 1 para y, 2 para z).
        separation (int): Distância entre os dois planos.
        thickness (int): Espessura dos planos.
        file_path (str): Caminho para salvar o arquivo .raw.

    Returns:
        numpy.ndarray: O array 3D com os planos paralelos e os pontos anotados.
    """


    array = np.ones(shape, dtype=np.uint8)

    plane1_center = shape[plane_axis] // 2 - separation // 2
    plane2_center = plane1_center + separation
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
# === AUXILIARY FUNCTIONS ===

def generate_points_example_1(max_index):
    """Gera pontos para o exemplo 1."""
    return [
        [max_index, 0, max_index / 2], [max_index, max_index / 2, max_index],
        [max_index, max_index, max_index / 2], [0, max_index / 2, max_index],
        [0, max_index, max_index / 2], [0, max_index / 2, 0],
        [0, 0, max_index / 2], [max_index, max_index / 2, 0]
    ]

def generate_points_example_3(max_index):
    """Gera pontos para o exemplo 3."""
    points1 = [[i * max_index / 10, max_index / 4, 0] for i in range(1, 10)]
    points2 = [[max_index / 2, 3 * max_index / 4, i * max_index / 10] for i in range(1, 10)]
    return points1 + points2

def generate_angle_points_example_5(cube_length):
    """Gera pontos com ângulos para o exemplo 5."""
    
    return [
        # Plane 1
        [90, 125, 100, 100], 
        [90, 125, 150, 50],
        # Plane 2
        [159, 125, 100, 10], 
        [159, 125, 150, 5]
    ]

def generate_angle_points_example_6(cube_length):
    """Gera pontos com ângulos para o exemplo 6."""
    return [
        # Plane 1
        [90, 50, 100, 90], 
        [90, 50, 150, 50],
        [90, 200, 100, 100], 
        [90, 200, 150, 20],
        # Plane 2
        [159, 200, 100, 40], 
        [159, 200, 150, 10],
        [159, 50, 100, 25], 
        [159, 50, 150, 5]
    ]

def generate_angle_points_example_7(cube_length):
    """Gera pontos com ângulos para o exemplo 7."""
    return [
        [19, 0, 0, 100], 
        [19, 0, 49, 10],
        [19, 49, 0, 100],
        [19, 49, 49, 10],
        [29, 0, 0, 75], 
        [29, 0, 49, 30], 
        [29, 49, 0, 30], 
        [29, 49, 49, 55]
    ]


# MAKE SURE THE SAMPLES ARE CONNECTED TO SOLID SURFACE

# === EXAMPLES ===

cube_length = 250


# Computation
volume_shape = (cube_length, cube_length, cube_length)
max_index = cube_length - 1
"""
# Example 4
array_ex4 = create_centered_cube(domain_shape=volume_shape, cube_shape=(int(cube_length/5), int(cube_length/5), int(cube_length/5)), corner_values=[3, 4, 5, 6, 7, 8, 9, 10], file_path="Rock Volumes/Example_4")
pl.Plot_Domain(array_ex4, "Rock Volumes/Example_4_SolidRock", remove_value=[1])
"""

"""
# Example 5
points = generate_angle_points_example_5(cube_length)
array_ex5 = create_array_with_parallel_planes(points=points, shape=volume_shape, plane_axis=0, separation=50, thickness=20, file_path="Rock Volumes/Example_5")
pl.Plot_Domain(array_ex5, "Rock Volumes/Example_5_SolidRock", remove_value=[1])
"""

# Example 6
points = generate_angle_points_example_6(cube_length)
array_ex6 = create_array_with_parallel_planes(points=points, shape=volume_shape, plane_axis=0, separation=50, thickness=20, file_path="Rock Volumes/Example_6")
pl.Plot_Domain(array_ex6, "Rock Volumes/Example_6_SolidRock", remove_value=[1])

"""
# Example 7
points = generate_angle_points_example_7(cube_length)
array_ex7 = create_array_with_parallel_planes(points=points, shape=volume_shape, plane_axis=0, separation=50, thickness=20, file_path="Rock Volumes/Example_7")
pl.Plot_Domain(array_ex7, "Rock Volumes/Example_7_SolidRock", remove_value=[1])
"""
"""
# Example 8
plane = "XY"
spacing = 50
radius1 = 50
radius2 = 40
value1 = 50
value2 = 100
num_points1 = 8  # Número de pontos no perímetro do primeiro círculo
num_points2 = 16  # Número de pontos no perímetro do segundo círculo

# Criar o volume
array_ex8 = create_plane_with_circles(shape=volume_shape, plane=plane, spacing=spacing,
                                      radius1=radius1, radius2=radius2, value1=value1, 
                                      value2=value2, num_points1=num_points1, num_points2=num_points2,file_path="Rock Volumes/Example_8")
pl.Plot_Domain(array_ex8, "Rock Volumes/Example_8_SolidRock", remove_value=[1])
"""