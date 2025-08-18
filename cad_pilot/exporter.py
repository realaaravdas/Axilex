import trimesh

def export_to_stl(objects, output_path="output.stl"):
    combined_mesh = trimesh.Trimesh()
    for obj in objects:
        if hasattr(obj, 'mesh') and obj.mesh is not None:
            combined_mesh = trimesh.util.concatenate([combined_mesh, obj.mesh])
    
    if combined_mesh.vertices.shape[0] > 0:
        combined_mesh.export(output_path)
        print(f"Exported model to {output_path}")
    else:
        print("No objects to export.")