import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import FilteredElementCollector, Transaction, Plane, XYZ, ElementTransformUtils
from Autodesk.Revit.DB.Structure import Rebar, RebarBarType
from System.Collections.Generic import List
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
    return [rebar for rebar in FilteredElementCollector(doc).OfClass(Rebar).ToElements() if
            rebar.GetTypeId() == target_type_id]


def mirror_rebar(doc, rebar):
    with Transaction(doc, "Mirror Rebar") as trans:
        trans.Start()
        try:
            bbox = rebar.get_BoundingBox(None)
            center_point = bbox.Min + 0.5 * (bbox.Max - bbox.Min)
            mirror_plane = Plane.CreateByNormalAndOrigin(XYZ.BasisY, center_point)

            mirrored_ids = ElementTransformUtils.MirrorElement(doc, rebar.Id, mirror_plane)
            if mirrored_ids and len(list(mirrored_ids)) > 0:
                print("Mirroring did not produce any results.")
            else:
                print("Rebar mirrored successfully.")
            trans.Commit()
        except Exception as e:
            print(f"Failed to mirror rebar: {str(e)}")
            trans.RollBack()


h20_rebars = find_rebars_by_type(doc, "H20")
if h20_rebars:
    print(f"Found {len(h20_rebars)} rebars of type 'H20'.")
    for rebar in h20_rebars:
        mirror_rebar(doc, rebar)
else:
    print("No rebars found of type 'H20'.")
