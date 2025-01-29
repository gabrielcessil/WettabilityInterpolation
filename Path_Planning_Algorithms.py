#import dijkstra3d
import Plotter as pl
import numpy as np
from Array_Utilities import Separate_NonFluid_Connections


import numpy as np
import heapq
import heapq
import numpy as np


class Dijkstra3D:
    """
    Custom implementation of Dijkstra's algorithm for 3D grids.
    """

    @staticmethod
    def parental_field(volume, source, connectivity=26):
        """
        Computes the parental field for the given source point in the 3D grid.

        Args:
            volume (np.ndarray): 3D grid representing the volume.
            source (tuple): Coordinates of the source cell (x, y, z).
            connectivity (int): Connectivity for neighbors (6, 18, or 26).

        Returns:
            np.ndarray: Parental field indicating the parent of each cell.
        """
        
        # Step 0: Auxiliary variables
        directions = Dijkstra3D.get_directions(connectivity)
        distance_map = Dijkstra3D.get_distance_map(directions)
        shape = volume.shape
        
        # Step 1: Initialize the unvisited set, distance, and parents
        # Distance array: Infinity for all except source (set to 0)
        distances = np.full(shape, np.inf)
        distances[source] = 0
        # Parent array: Store the parent coordinate for each cell
        parents = np.full(shape + (3,), -1, dtype=int)
        # Priority queue for unvisited nodes
        priority_queue = [(0, source)]  # (distance, node)

        # Step 2–6: Dijkstra's main loop
        while priority_queue:
            # Step 3: Select the current node with the smallest distance
            current_distance, current = heapq.heappop(priority_queue)
            if current_distance > distances[current]:
                continue  # Skip if the distance is already updated

            # Step 4: Update distances to neighbors
            for direction, direction_distance in zip(directions, distance_map):
                neighbor = tuple(np.add(current, direction))
                if Dijkstra3D.is_valid(neighbor, shape) and volume[neighbor] != 1:  # Skip blocked cells
                    new_distance = current_distance + direction_distance
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        parents[neighbor] = current
                        heapq.heappush(priority_queue, (new_distance, neighbor))

            # Step 5: The current node is now visited; it remains final
            # Implicitly handled since `current` is not re-added to the queue

        # Step 6: Return the parental field
        return parents

    @staticmethod
    def path_from_parents(parents, target):
        """
        Reconstructs the path from the target to the source using the parental field.

        Args:
            parents (np.ndarray): Parental field from the `parental_field` method.
            target (tuple): Coordinates of the target cell (x, y, z).

        Returns:
            list: List of coordinates representing the path from source to target.
        """
        path = []
        current = target
        while all(coord >= 0 for coord in current):  # Continue until the source is reached
            path.append(current)
            current = tuple(parents[current])

        path.reverse()
        return path

    @staticmethod
    def get_directions(connectivity):
        """
        Returns the neighbor directions based on the connectivity.

        Args:
            connectivity (int): 6, 18, or 26 connectivity.

        Returns:
            list: List of 3D vectors representing neighbor directions.
        """
        if connectivity == 6:
            return [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        elif connectivity == 18:
            directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
            for dx in [-1, 1]:
                for dz in [-1, 1]:
                    directions.extend([(dx, 0, dz), (0, dx, dz), (dx, dz, 0)])
            return directions
        elif connectivity == 26:
            return [(dx, dy, dz) for dx in [-1, 0, 1] for dy in [-1, 0, 1] for dz in [-1, 0, 1] if (dx, dy, dz) != (0, 0, 0)]
        else:
            raise ValueError("Invalid connectivity: choose 6, 18, or 26")

    @staticmethod
    def get_distance_map(directions):
        """
        Calculates the distance for each direction.

        Args:
            directions (list): List of 3D vectors representing neighbor directions.

        Returns:
            list: List of distances for each direction.
        """
        return [np.linalg.norm(direction) for direction in directions]

    @staticmethod
    def is_valid(coord, shape):
        """
        Checks if a coordinate is within the bounds of the grid.

        Args:
            coord (tuple): Coordinate to check.
            shape (tuple): Shape of the grid.

        Returns:
            bool: True if valid, False otherwise.
        """
        return all(0 <= c < s for c, s in zip(coord, shape))

    
def FindPaths(volume, fluid_default_value=1, solid_default_value=0):
    dijkstra3d = Dijkstra3D()

    sub_solid_arrays, connected_labels, labels = Separate_NonFluid_Connections(volume, fluid_default_value)

    print("Running FindPaths")
    print(f"Domain spliited into {len(sub_solid_arrays)} sub-arrays")
    
    for group_i,solid_array in enumerate(sub_solid_arrays):
        print(f"\nSub-Array {group_i} under analysis: ")
        # Celulas Source - Pontos de Medida
        source_cells = np.argwhere((solid_array != fluid_default_value) & (solid_array != solid_default_value))
        source_cells = [tuple(cell) for cell in source_cells] # Conversao para formato usado na implementacao Djikstra
        
        
        # Celulas Target - Qualquer ponto solido (nao fluido)
        target_cells = np.argwhere(solid_array != fluid_default_value)
        target_cells = [tuple(cell) for cell in target_cells] # Conversao para formato usado na implementacao Djikstra
        
        
        # Gerar o campo parental para cada fonte e calcular os caminhos
        all_paths = []
        print("Pontos de medicao: ", len(source_cells), " source cells")
        print("Celulas solidas: ", len(target_cells), " target cells")
        
        # Para cada source
        for source in source_cells:
            # Gerar o campo parental para a fonte atual: 
            print("- Analysis source: ", source)
            
            parents = dijkstra3d.parental_field(solid_array, source=source, connectivity=26)
        
            source_paths = { "source": source,
                             "target_paths": []}

            for it, target in enumerate(target_cells):
                
                if int(100 * it / len(target_cells)) % 10 == 0 and int(100 * (it - 1) / len(target_cells)) % 10 != 0: print(f"-- Dijkstra run: {int(100 * it / len(target_cells))}% of {len(target_cells)} runs")

                target = tuple(target)
                if target != source:  
                    
                    # Reconstroi o caminho ate cada target
                    path = dijkstra3d.path_from_parents(parents, target)
                    # Registra caminho
                    source_paths["target_paths"].append({"target":target,"path": path})
                    
     
            all_paths.append(source_paths)
            
        return all_paths
    
def PlotPath_fromSources(volume, all_paths, target, fill_value=10):
    
    path = []
    for path_info in all_paths:
        source = path_info["source"]
        
        for target_path_dict in path_info["target_paths"]:
            
            if target_path_dict["target"] == target:
                path = target_path_dict["path"]            
                
    final_volume = volume.copy()
    for point in path:
        i,j,k = point
        final_volume[i,j,k] = fill_value
    
    final_volume[path[0][0],path[0][1],path[0][2]] = fill_value*20
    final_volume[target[0],target[1],target[2]] = fill_value*10
        
    pl.Plot_Domain(final_volume, "TESTE", remove_value=[1]) 
    