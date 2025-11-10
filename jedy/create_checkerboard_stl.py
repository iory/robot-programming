#!/usr/bin/env python3
import os
import argparse
import trimesh
import numpy as np


def create_checkerboard_mesh(rows=4, cols=7, square_size=0.02, thickness=0.003, border_width=1):
    """
    Create a checkerboard mesh with alternating black and white squares and white border.

    Parameters:
    - rows: number of rows in the checkerboard
    - cols: number of columns in the checkerboard
    - square_size: size of each square in meters (default 20mm = 0.02m)
    - thickness: thickness of the board in meters
    - border_width: width of the white border in number of squares (default 1)

    Returns:
    - black_mesh: mesh for black squares
    - white_mesh: mesh for white squares (including border)
    """

    black_meshes = []
    white_meshes = []

    # Total board dimensions including border
    total_cols = cols + 2 * border_width
    total_rows = rows + 2 * border_width
    board_width = total_cols * square_size
    board_height = total_rows * square_size

    # Create checkerboard pattern with border
    for row in range(total_rows):
        for col in range(total_cols):
            # Create a box for this square
            box = trimesh.creation.box((square_size, square_size, thickness))

            # Check if this is in the border area
            is_border = (row < border_width or row >= rows + border_width or
                        col < border_width or col >= cols + border_width)

            # Position the box
            matrix = np.eye(4)
            matrix[0, 3] = col * square_size
            matrix[1, 3] = row * square_size
            matrix[2, 3] = thickness / 2.0
            box.apply_transform(matrix)

            if is_border:
                # Border is always white
                box.visual.vertex_colors = np.array([255, 255, 255])
                white_meshes.append(box)
            else:
                # Interior checkerboard pattern
                # Adjust row/col to be relative to the checkerboard area
                inner_row = row - border_width
                inner_col = col - border_width
                is_black = (inner_row + inner_col) % 2 == 1

                if is_black:
                    box.visual.vertex_colors = np.array([0, 0, 0])
                    black_meshes.append(box)
                else:
                    box.visual.vertex_colors = np.array([255, 255, 255])
                    white_meshes.append(box)

    # Return both separate meshes and combined mesh
    black_mesh = trimesh.util.concatenate(black_meshes) if black_meshes else trimesh.Trimesh()
    white_mesh = trimesh.util.concatenate(white_meshes) if white_meshes else trimesh.Trimesh()
    all_meshes = black_meshes + white_meshes
    combined_mesh = trimesh.util.concatenate(all_meshes) if all_meshes else trimesh.Trimesh()

    return black_mesh, white_mesh, combined_mesh


# Initialize argument parser
parser = argparse.ArgumentParser(description="Generate a 3D checkerboard model.")

# Add arguments
parser.add_argument('--rows', type=int, default=4, help='Number of corner rows (inner corners). Number of square rows will be rows+1.')
parser.add_argument('--cols', type=int, default=7, help='Number of corner columns (inner corners). Number of square columns will be cols+1.')
parser.add_argument('--square-size', type=float, default=0.02, help='Size of each square in meters.')
parser.add_argument('--thickness', type=float, default=0.003, help='Thickness of the board in meters.')
parser.add_argument('--border-width', type=int, default=1, help='Width of the white border in number of squares.')

# Parse arguments
args = parser.parse_args()

# Convert corners to squares: 7 columns of corners = 8 columns of squares
# (corners are at the intersections, squares are between them)
num_square_rows = args.rows + 1
num_square_cols = args.cols + 1

# Generate meshes
black_mesh, white_mesh, combined_mesh = create_checkerboard_mesh(
    rows=num_square_rows,
    cols=num_square_cols,
    square_size=args.square_size,
    thickness=args.thickness,
    border_width=args.border_width
)

# Create output directory
base_dir = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.join(base_dir, "output")
os.makedirs(save_dir, exist_ok=True)

# Export black mesh
if not black_mesh.is_empty:
    file_path_black = os.path.join(save_dir, "checkerboard_black.stl")
    black_mesh.units = 'm'
    black_mesh_mm = black_mesh.convert_units('mm')
    black_mesh_mm.export(file_path_black)
    print(f"Saved black mesh to: {file_path_black}")

# Export white mesh
if not white_mesh.is_empty:
    file_path_white = os.path.join(save_dir, "checkerboard_white.stl")
    white_mesh.units = 'm'
    white_mesh_mm = white_mesh.convert_units('mm')
    white_mesh_mm.export(file_path_white)
    print(f"Saved white mesh to: {file_path_white}")

# Export combined mesh
if not combined_mesh.is_empty:
    # Export as STL (for Gazebo)
    file_path_stl = os.path.join(save_dir, "checkerboard.stl")
    combined_mesh.units = 'm'
    combined_mesh_mm = combined_mesh.convert_units('mm')
    combined_mesh_mm.export(file_path_stl)
    print(f"Saved combined STL mesh to: {file_path_stl}")

    # Also export as DAE with color information (alternative for Gazebo)
    file_path_dae = os.path.join(save_dir, "checkerboard.dae")
    combined_mesh_mm.export(file_path_dae)
    print(f"Saved combined DAE mesh to: {file_path_dae}")

    # Show preview
    combined_mesh.show()

total_width = (num_square_cols + 2 * args.border_width) * args.square_size * 1000
total_height = (num_square_rows + 2 * args.border_width) * args.square_size * 1000

print(f"\nCheckerboard dimensions:")
print(f"  Inner corners: {args.cols} x {args.rows}")
print(f"  Squares: {num_square_cols} x {num_square_rows}")
print(f"  Square size: {args.square_size * 1000}mm")
print(f"  Border width: {args.border_width} squares ({args.border_width * args.square_size * 1000}mm)")
print(f"  Checkerboard size: {num_square_cols * args.square_size * 1000}mm x {num_square_rows * args.square_size * 1000}mm")
print(f"  Total size (with border): {total_width}mm x {total_height}mm")
print(f"  Thickness: {args.thickness * 1000}mm")
