import pygame
import numpy as np

# Configurações do ambiente
GRID_SIZE = 16  # Tamanho da grade 3D (16x16x16 por padrão)
VOXEL_SIZE = 20  # Tamanho de cada célula no display 2D
SCREEN_SIZE = (GRID_SIZE * VOXEL_SIZE, GRID_SIZE * VOXEL_SIZE)

# Função para carregar o arquivo .raw
def load_raw(filename, shape):
    """Carrega um arquivo .raw e converte em um np.array com o shape fornecido."""
    data = np.fromfile(filename, dtype=np.uint8)
    return data.reshape(shape)

# Inicializa o array 3D com valores carregados de um arquivo .raw
array_name = "Rock Volumes/Example_5.raw"
try:
    array_3d = load_raw("array_3d.raw", (GRID_SIZE, GRID_SIZE, GRID_SIZE))
    print("Arquivo .raw carregado com sucesso.")
except FileNotFoundError:
    print("Arquivo .raw não encontrado. Inicializando com valores padrão.")
    array_3d = np.ones((GRID_SIZE, GRID_SIZE, GRID_SIZE), dtype=np.uint8)  # Inicializa com valores 1

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Editor Interativo de Array 3D")
clock = pygame.time.Clock()

# Cores
COLOR_BACKGROUND = (30, 30, 30)
COLOR_VOXEL = (100, 200, 255)
COLOR_EMPTY = (50, 50, 50)
COLOR_SELECTED = (255, 100, 100)

# Variáveis de controle
selected_layer = 0  # Camada inicial visível (Z)
running = True

def draw_grid():
    """Desenha a grade 2D baseada na camada Z selecionada."""
    screen.fill(COLOR_BACKGROUND)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            value = array_3d[x, y, selected_layer]
            color = COLOR_EMPTY if value == 0 else COLOR_VOXEL
            pygame.draw.rect(screen, color, (x * VOXEL_SIZE, y * VOXEL_SIZE, VOXEL_SIZE, VOXEL_SIZE))
            pygame.draw.rect(screen, COLOR_BACKGROUND, (x * VOXEL_SIZE, y * VOXEL_SIZE, VOXEL_SIZE, VOXEL_SIZE), 1)

def get_voxel_at_mouse(pos):
    """Retorna as coordenadas do voxel clicado baseado na posição do mouse."""
    x, y = pos
    grid_x = x // VOXEL_SIZE
    grid_y = y // VOXEL_SIZE
    return grid_x, grid_y

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            voxel_x, voxel_y = get_voxel_at_mouse(mouse_pos)
            
            if event.button == 1:  # Botão esquerdo do mouse
                if 0 <= voxel_x < GRID_SIZE and 0 <= voxel_y < GRID_SIZE:
                    array_3d[voxel_x, voxel_y, selected_layer] = 0  # Define o voxel como 0
            elif event.button == 3:  # Botão direito do mouse
                if 0 <= voxel_x < GRID_SIZE and 0 <= voxel_y < GRID_SIZE:
                    array_3d[voxel_x, voxel_y, selected_layer] = 1  # Altera o voxel para 1
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_layer = min(selected_layer + 1, GRID_SIZE - 1)  # Muda para a camada superior
            elif event.key == pygame.K_DOWN:
                selected_layer = max(selected_layer - 1, 0)  # Muda para a camada inferior
            elif event.key == pygame.K_RETURN:
                # Salva o array em .raw
                array_3d.tofile("array_3d.raw")
                print("Array salvo como 'array_3d.raw'.")

    # Atualiza a tela
    draw_grid()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
