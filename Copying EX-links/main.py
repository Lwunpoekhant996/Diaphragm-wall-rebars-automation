import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import FilteredElementCollector, Transaction, ElementId, XYZ, ElementTransformUtils
from Autodesk.Revit.DB.Structure import Rebar, RebarBarType
from RevitServices.Persistence import DocumentManager

doc = __revit__.ActiveUIDocument.Document

def find_rebars_by_type(doc, type_name):
    rebar_types = FilteredElementCollector(doc).OfClass(RebarBarType).ToElements()
    target_type_id = None
    for rebar_type in rebar_types:
        if rebar_type.Name == type_name:
            target_type_id = rebar_type.Id
            break
    if target_type_id is None:
        print(f"No rebar type found with the name '{type_name}'.")
        return []
    return [rebar for rebar in FilteredElementCollector(doc).OfClass(Rebar).ToElements() if rebar.GetTypeId() == target_type_id]

def copy_rebar(doc, rebar, num_copies, spacing):
    move_vector = XYZ(0, 0, -spacing / 304.8)  # Convert mm to feet
    with Transaction(doc, "Copy Rebar") as trans:
        trans.Start()
        last_copied_id = rebar.Id
        for _ in range(num_copies - 1):  # -1 because the original rebar is already one instance
            last_copied_id = ElementTransformUtils.CopyElement(doc, last_copied_id, move_vector)[0]
        trans.Commit()
        print(f"Successfully copied rebar {num_copies} times.")

h20_rebars = find_rebars_by_type(doc, "H20")
if h20_rebars:
    print(f"Found {len(h20_rebars)} rebars of type 'H20'.")
    for rebar in h20_rebars:
        copy_rebar(doc, rebar, 243, 150)  # 243 copies, 150mm spacing
else:
    print("No rebars found of type 'H20'.")
