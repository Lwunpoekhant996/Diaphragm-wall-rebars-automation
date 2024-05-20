import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, XYZ, Line
from Autodesk.Revit.DB.Structure import Rebar, RebarBarType, RebarStyle, RebarHookOrientation
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Initialize document
doc = __revit__.ActiveUIDocument.Document

# Constants and conversions
mm_to_feet = 1 / 304.8  # Conversion factor from mm to feet
t_dwall = 1000 * mm_to_feet  # Thickness of D-wall in feet
d_main = 40 * mm_to_feet  # Diameter of main bar in feet
d_link = 20 * mm_to_feet  # Diameter of link in feet
r1 = 8200 * mm_to_feet  # Length of the rebar in feet

# Calculate the starting point based on the given conditions
X0, Y0, Z0 = 0, 0, 0  # Original coordinates at the top center of 'D-wall panel'
X1 = X0 + 100 * mm_to_feet + d_link + (d_main / 2)
Y1 = Y0 - (t_dwall / 2) + 75 * mm_to_feet + d_link + (d_main / 2)
Z1 = Z0 + 6400 * mm_to_feet  # Z1 located 6400 mm above the original point at ground level.
starting_point = XYZ(X1, Y1, Z1)

# Calculate the end point based on the rebar's length extending in the negative Z direction
end_point_r1 = XYZ(X1, Y1, Z1 - r1)


# Helper functions for element selection
def select_element_by_name(category, name):
    elements = FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
    for element in elements:
        if element.Name == name:
            return element
    return None


def get_element_by_name(class_filter, name):
    elements = FilteredElementCollector(doc).OfClass(class_filter).ToElements()
    for element in elements:
        if element.Name == name:
            return element
    return None


# Selecting 'D-wall panel' and 'H40' rebar type
d_wall_panel = select_element_by_name(BuiltInCategory.OST_Walls, "D-wall panel")
rebar_type = get_element_by_name(RebarBarType, "H40")

# Ensure selection success
if not d_wall_panel:
    print("D-wall panel not found.")
elif not rebar_type:
    print("Rebar type 'H40' not found.")
else:
    # Transaction for rebar creation
    t = Transaction(doc, "Create Custom Rebar")
    t.Start()

    try:
        # Define the rebar curve, r1
        rebar_curve_r1 = Line.CreateBound(starting_point, end_point_r1)

        # Create the rebar
        new_rebar_r1 = Rebar.CreateFromCurves(
            doc,
            RebarStyle.Standard,
            rebar_type,
            None,  # Start hook
            None,  # End hook
            d_wall_panel,
            XYZ.BasisY,  # Normal
            [rebar_curve_r1],
            RebarHookOrientation.Left,
            RebarHookOrientation.Right,
            True,
            False
        )
        print("Rebar (r1) is created successfully.")
    except Exception as e:
        print("Failed to create rebar (r1):", str(e))

    # Commit the transaction
    t.Commit()


    # Constants and conversions for rebar r2
    mm_to_feet = 1 / 304.8  # Conversion factor from mm to feet
    d_main = 40 * mm_to_feet  # Diameter of main bar in feet
    r2_length = 8200 * mm_to_feet  # Length of the second rebar in feet
    overlap_length = 1227 * mm_to_feet  # Overlapping length in feet

    # Define the Y offset for the starting point of r2 due to the diameter of the rebar H40
    y_offset = d_main  # 40 mm in feet

    # Calculate the starting point of r2 based on the end point of r1 and the overlapping requirement
    X2 = X1  # Aligned with r1 in the X direction
    Y2 = Y1 + y_offset  # Offset by the diameter of the rebar in the Y direction
    Z2 = end_point_r1.Z + overlap_length  # Starting Z point of r2 is above the end point of r1 by the overlap length

    # Calculate the end point of r2 by extending it from Z2 in the negative Z direction by its length, including the overlap
    end_point_r2 = XYZ(X2, Y2, Z2 - r2_length)

    # Transaction for the second rebar creation
    t2 = Transaction(doc, "Create Second Rebar")
    t2.Start()

    try:
        # Define the curve for the second rebar
        rebar_curve_r2 = Line.CreateBound(XYZ(X2, Y2, Z2), end_point_r2)

        # Create the second rebar
        new_rebar_r2 = Rebar.CreateFromCurves(
            doc,
            RebarStyle.Standard,
            rebar_type,  # Using the same rebar type 'H40'
            None,  # Start hook
            None,  # End hook
            d_wall_panel,  # Host element
            XYZ.BasisY,  # Normal vector to the plane of the rebar shape
            [rebar_curve_r2],  # Curve defining the shape and placement of r2
            RebarHookOrientation.Left,  # Start hook orientation
            RebarHookOrientation.Right,  # End hook orientation
            True,  # Use existing shape
            False  # Deform shape in 3D
        )
        print("Second rebar (r2) created successfully with the correct overlap and extension.")
    except Exception as e:
        print("Failed to create the second rebar (r2):", str(e))

    # Commit the transaction
    t2.Commit()

    # Constants and conversions for rebar r3
    mm_to_feet = 1 / 304.8  # Conversion factor from mm to feet
    d_main = 40 * mm_to_feet  # Diameter of main bar in feet
    r3_length = 8200 * mm_to_feet  # Length of the second rebar in feet
    overlap_length = 1227 * mm_to_feet  # Overlapping length in feet

    # Define the Y offset for the starting point of r3 due to the diameter of the rebar H40
    y_offset = d_main  # 40 mm in feet

    # Calculate the starting point of r3 based on the end point of r2 and the overlapping requirement
    X3 = X2  # Aligned with r1 in the X direction
    Y3 = Y2 - y_offset  # Offset by the diameter of the rebar in the Y direction
    Z3 = end_point_r2.Z + overlap_length  # Starting Z point of r3 is above the end point of r2 by the overlap length

    # Calculate the end point of r3 by extending it from Z3 in the negative Z direction by its length, including the overlap
    end_point_r3 = XYZ(X3, Y3, Z3 - r3_length)

    # Transaction for the third rebar creation
    t3 = Transaction(doc, "Create Third Rebar")
    t3.Start()

    try:
        # Define the curve for the third rebar
        rebar_curve_r3 = Line.CreateBound(XYZ(X3, Y3, Z3), end_point_r3)

        # Create the third rebar
        new_rebar_r3 = Rebar.CreateFromCurves(
            doc,
            RebarStyle.Standard,
            rebar_type,  # Using the same rebar type 'H40'
            None,  # Start hook
            None,  # End hook
            d_wall_panel,  # Host element
            XYZ.BasisY,  # Normal vector to the plane of the rebar shape
            [rebar_curve_r3],  # Curve defining the shape and placement of r3
            RebarHookOrientation.Left,  # Start hook orientation
            RebarHookOrientation.Right,  # End hook orientation
            True,  # Use existing shape
            False  # Deform shape in 3D
        )
        print("Third rebar (r3) created successfully with the correct overlap and extension.")
    except Exception as e:
        print("Failed to create the third rebar (r3):", str(e))

    # Commit the transaction
    t3.Commit()

    # Constants for r4
    r4_length = 8600 * mm_to_feet  # Length of the fourth rebar in feet
    new_lapping_length = 1081 * mm_to_feet  # New lapping length for r4 in feet

    # Get the rebar type 'H32' for r4
    rebar_type_r4 = get_element_by_name(RebarBarType, "H32")
    if not rebar_type_r4:
        print("Rebar type 'H32' not found.")
    else:
        # Calculate the starting point of r4 based on the end point of r3 and the new lapping requirement
        X4 = X3  # Aligned with r3 in the X direction
        Y4 = Y3 + y_offset  # Offset by the diameter of the previous rebar in the Y direction
        Z4 = end_point_r3.Z + new_lapping_length  # Starting Z point of r4 is above the end point of r3 by the new lapping length

        # Calculate the end point of r4 by extending it from Z4 in the negative Z direction by its length, including the new lapping length
        end_point_r4 = XYZ(X4, Y4, Z4 - r4_length)

        # Transaction for the fourth rebar creation
        t4 = Transaction(doc, "Create Fourth Rebar")
        t4.Start()

        try:
            # Define the curve for the fourth rebar
            rebar_curve_r4 = Line.CreateBound(XYZ(X4, Y4, Z4), end_point_r4)

            # Create the fourth rebar
            new_rebar_r4 = Rebar.CreateFromCurves(
                doc,
                RebarStyle.Standard,
                rebar_type_r4,  # Using the rebar type 'H32' for r4
                None,  # Start hook
                None,  # End hook
                d_wall_panel,  # Host element
                XYZ.BasisY,  # Normal vector to the plane of the rebar shape
                [rebar_curve_r4],  # Curve defining the shape and placement of r4
                RebarHookOrientation.Left,  # Start hook orientation
                RebarHookOrientation.Right,  # End hook orientation
                True,  # Use existing shape
                False  # Deform shape in 3D
            )
            print("Fourth rebar (r4) created successfully with the correct overlap and extension.")
        except Exception as e:
            print("Failed to create the fourth rebar (r4):", str(e))

        # Commit the transaction
        t4.Commit()

# Constants for r5
r5_length = 8600 * mm_to_feet  # Length of the fifth rebar in feet
r5_lapping_length = 985 * mm_to_feet  # Lapping length for r5 in feet

# Calculate the starting point of r5 based on the end point of r4 and the lapping requirement
X5 = X4  # Aligned with r4 in the X direction
Y5 = Y4 - y_offset  # Offset by the diameter of the previous rebar in the negative Y direction
Z5 = end_point_r4.Z + r5_lapping_length  # Starting Z point of r5 is above the end point of r4 by the lapping length

# Calculate the end point of r5 by extending it from Z5 in the negative Z direction by its length
end_point_r5 = XYZ(X5, Y5, Z5 - r5_length)

# Transaction for the fifth rebar creation
t5 = Transaction(doc, "Create Fifth Rebar")
t5.Start()

try:
    # Define the curve for the fifth rebar
    rebar_curve_r5 = Line.CreateBound(XYZ(X5, Y5, Z5), end_point_r5)

    # Create the fifth rebar using 'rebar_type_r4' for the 'H32' rebar type
    new_rebar_r5 = Rebar.CreateFromCurves(
        doc,
        RebarStyle.Standard,
        rebar_type_r4,  # Using 'H32' rebar type for r5
        None,  # Start hook
        None,  # End hook
        d_wall_panel,  # Host element
        XYZ.BasisY,  # Normal vector to the plane of the rebar shape
        [rebar_curve_r5],  # Curve defining the shape and placement of r5
        RebarHookOrientation.Left,  # Start hook orientation
        RebarHookOrientation.Right,  # End hook orientation
        True,  # Use existing shape
        False  # Deform shape in 3D
    )
    print("Fifth rebar (r5) created successfully with the correct overlap and extension.")
except Exception as e:
    print("Failed to create the fifth rebar (r5):", str(e))

# Commit the transaction
t5.Commit()

# Copying the rebar layer A with provided spacing, quantity, and direction.
from System.Collections.Generic import List
from Autodesk.Revit.DB import ElementId

# Assuming you have the Rebar objects for r1, r2, r3, r4 and r5 stored in variables
# like new_rebar_r1, new_rebar_r2, new_rebar_r3, new_rebar_r4, new_rebar_r5
# Initialize a .NET List to hold the ElementIds
rebar_ids = List[ElementId]()

# Add the ElementIds of the rebars to the .NET List
rebar_ids.Add(new_rebar_r1.Id)
rebar_ids.Add(new_rebar_r2.Id)
rebar_ids.Add(new_rebar_r3.Id)
rebar_ids.Add(new_rebar_r4.Id)
rebar_ids.Add(new_rebar_r5.Id)

# Define the spacing and the number of copies
spacing = 119 * mm_to_feet  # Convert spacing to feet
num_copies = 19  # Number of additional copies needed to make a total of 20 sets

# Start a new transaction for copying the rebars
t_copy = Transaction(doc, "Copy Rebar Layer")
t_copy.Start()

try:
    for i in range(1, num_copies + 1):
        # Calculate the X offset for the current copy
        x_offset = i * spacing

        # Create a translation transformation with the X offset
        translation = Transform.CreateTranslation(XYZ(x_offset, 0, 0))

        # Corrected call to CopyElements with proper argument order
        ElementTransformUtils.CopyElements(
            doc,  # Source document
            rebar_ids,  # Collection of ElementIds to copy
            doc,  # Destination document (same as source)
            translation,  # Transform to apply
            None  # CopyPasteOptions (None if not needed)
        )

    print(f"{num_copies} copies of the rebar layer created successfully.")
except Exception as e:
    print(f"Failed to copy the rebar layer: {str(e)}")

# Commit the transaction
t_copy.Commit()

