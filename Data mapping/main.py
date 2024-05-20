import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import FilteredElementCollector, ElementType, Transaction, UnitUtils, ForgeTypeId

# Define your mapping of rebar types to unit weights here (in kg/m)
unit_weight_mapping = {
    'H40': 9.864,
    'H32': 6.313,
    'H25': 3.854,
    'H20': 2.470,
    'H16': 1.580,
    'H13': 1.040,
    # ... include other rebar types and their unit weights as needed
}

# Get the current document (the open Revit model)
doc = __revit__.ActiveUIDocument.Document

# Start a transaction to modify the model
t = Transaction(doc, 'Update Rebar Unit Weights')
t.Start()

try:
    element_types = FilteredElementCollector(doc).OfClass(ElementType)
    for element_type in element_types:
        type_name = element_type.Name
        if type_name in unit_weight_mapping:
            print("Found rebar type: " + type_name)

            # Get the unit weight in kg/m from the mapping and convert it to internal units
            unit_weight_internal_units = UnitUtils.ConvertToInternalUnits(unit_weight_mapping[type_name], UnitTypeId.KilogramsPerMeter)

            param = element_type.LookupParameter('Unit weight')
            if param is not None:
                # Set the value of the shared parameter in internal units
                param.Set(unit_weight_internal_units)
                print("Set unit weight for " + type_name + " to: " + str(unit_weight_internal_units) + " internal units")

    t.Commit()
except Exception as e:
    t.RollBack()
    print("Error: " + str(e))


