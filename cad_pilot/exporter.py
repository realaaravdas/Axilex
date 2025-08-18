import cadquery as cq

def _combine_shapes(objects):
    """
    Combines a list of Shape objects into a single cadquery Workplane object.
    """
    combined_cq_object = cq.Workplane()
    for obj in objects:
        if hasattr(obj, 'cq_object') and obj.cq_object:
            combined_cq_object = combined_cq_object.add(obj.cq_object)
    return combined_cq_object

def export_to_stl(objects, output_path="output.stl"):
    """
    Exports a list of Shape objects to a single STL file using CadQuery's exporter.
    """
    if not objects:
        print("No objects to export to STL.")
        return

    combined_cq_object = _combine_shapes(objects)
    cq.exporters.export(combined_cq_object, output_path, "STL")
    print(f"Exported model to {output_path} (STL)")

def export_to_step(objects, output_path="output.step"):
    """
    Exports a list of Shape objects to a single STEP file using CadQuery's exporter.
    """
    if not objects:
        print("No objects to export to STEP.")
        return

    combined_cq_object = _combine_shapes(objects)
    cq.exporters.export(combined_cq_object, output_path, "STEP")
    print(f"Exported model to {output_path} (STEP)")