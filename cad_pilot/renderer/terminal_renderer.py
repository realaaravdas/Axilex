import numpy as np
import os
import pyvista as pv

def render(shape_obj, objects=None, width=80, height=25):
    """
    Renders a Shape object as an ASCII wireframe in the terminal.
    """
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    if objects:
        print("--- Objects in Scene ---")
        for i, obj in enumerate(objects):
            print(f"{i+1}. {type(obj).__name__}")
        print("------------------------")

    if shape_obj is None:
        print("No shape to render.")
        return

    # Convert Shape object to PyVista mesh
    pv_mesh = shape_obj.to_pyvista_mesh()

    if pv_mesh is None or pv_mesh.n_points == 0:
        print("No renderable mesh found for terminal display.")
        return

    # Get vertices and edges from PyVista mesh
    vertices = pv_mesh.points
    # PyVista does not directly expose 'edges_unique' like trimesh.
    # We can derive edges from faces, but for simple wireframe, we'll just project vertices.
    # For a true wireframe, we'd need to iterate through cells and get their edges.
    # For simplicity in ASCII, we'll just connect projected vertices if they are part of a face.
    
    # Simple orthographic projection (using only X and Y for 2D terminal view)
    proj_vertices = vertices[:, :2]

    # Scale and shift to fit the terminal screen
    min_coord = proj_vertices.min(axis=0)
    max_coord = proj_vertices.max(axis=0)
    
    range_x = max_coord[0] - min_coord[0]
    range_y = max_coord[1] - min_coord[1]

    if range_x == 0 or range_y == 0:
        print("Cannot render: object is flat or a single point in 2D projection.")
        return

    scale_x = (width - 1) / range_x
    scale_y = (height - 1) / range_y
    
    proj_vertices = (proj_vertices - min_coord) * np.array([scale_x, scale_y])

    # Create a canvas
    canvas = np.full((height, width), ' ', dtype=str)

    # Draw the edges (simplified: connect vertices of each face)
    # This is a very basic approximation of a wireframe for ASCII
    for face_indices in pv_mesh.faces.reshape(-1, 4)[:, 1:]:
        # For each triangle (assuming triangular faces from meshing)
        p1_idx, p2_idx, p3_idx = face_indices[0], face_indices[1], face_indices[2]
        
        p1 = proj_vertices[p1_idx].astype(int)
        p2 = proj_vertices[p2_idx].astype(int)
        p3 = proj_vertices[p3_idx].astype(int)

        draw_line(canvas, p1[0], p1[1], p2[0], p2[1], '*')
        draw_line(canvas, p2[0], p2[1], p3[0], p3[1], '*')
        draw_line(canvas, p3[0], p3[1], p1[0], p1[1], '*')

    # Print the canvas
    for i in range(canvas.shape[0]):
        print(''.join(canvas[i]))

def draw_line(canvas, x0, y0, x1, y1, char):
    """
    Draws a line on the canvas using Bresenham's line algorithm.
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= y0 < canvas.shape[0] and 0 <= x0 < canvas.shape[1]:
            canvas[y0, x0] = char
        if x0 == x1 and y0 == y1: 
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
