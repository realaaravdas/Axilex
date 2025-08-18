import numpy as np
import os

def render(mesh, objects=None, width=80, height=25):
    """
    Renders a trimesh object as an ASCII wireframe in the terminal.
    """
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    if objects:
        print("--- Objects in Scene ---")
        for i, obj in enumerate(objects):
            print(f"{i+1}. {type(obj).__name__}")
        print("------------------------")

    if mesh is None:
        print("No mesh to render.")
        return

    # Get vertices and edges
    vertices = mesh.vertices
    edges = mesh.edges_unique

    # Simple orthographic projection
    proj_vertices = vertices[:, :2]

    # Scale and shift to fit the terminal screen
    min_coord = proj_vertices.min(axis=0)
    max_coord = proj_vertices.max(axis=0)
    
    # Handle cases where min_coord equals max_coord (e.g., a single point or line)
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

    # Draw the edges
    for edge in edges:
        p1 = proj_vertices[edge[0]].astype(int)
        p2 = proj_vertices[edge[1]].astype(int)
        draw_line(canvas, p1[0], p1[1], p2[0], p2[1], '*')

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
        if x0 == x1 and y0 == y1: # Corrected condition for loop termination
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy