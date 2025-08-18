from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRep_Builder import BRep_Builder

def _combine_shapes(objects):
    """
    Combines a list of Shape objects into a single TopoDS_Compound.
    """
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)

    for obj in objects:
        if hasattr(obj, 'occt_shape') and obj.occt_shape:
            builder.Add(compound, obj.occt_shape)
    return compound

def export_to_stl(objects, output_path="output.stl"):
    """
    Exports a list of Shape objects to a single STL file.
    """
    if not objects:
        print("No objects to export to STL.")
        return

    combined_shape = _combine_shapes(objects)

    writer = StlAPI_Writer()
    writer.SetASCIIMode(False) # Export as binary STL
    writer.Write(combined_shape, output_path)
    print(f"Exported model to {output_path} (STL)")

def export_to_step(objects, output_path="output.step"):
    """
    Exports a list of Shape objects to a single STEP file.
    """
    if not objects:
        print("No objects to export to STEP.")
        return

    combined_shape = _combine_shapes(objects)

    writer = STEPControl_Writer()
    Interface_Static.SetCVal("write.step.schema", "AP203") # or AP214
    writer.Transfer(combined_shape, STEPControl_AsIs)
    status = writer.Write(output_path)

    if status == 1: # IFSelect_RetDone
        print(f"Exported model to {output_path} (STEP)")
    else:
        print(f"Failed to export model to {output_path} (STEP). Status: {status}")
