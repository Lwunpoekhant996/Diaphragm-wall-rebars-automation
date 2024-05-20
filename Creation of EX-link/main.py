import clr
import math

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, Transaction, XYZ, Line, Curve, ElementId)
from Autodesk.Revit.DB.Structure import (Rebar, RebarBarType, RebarStyle, RebarHookOrientation)
from System.Collections.Generic import List

# Access the document
doc = __revit__.ActiveUIDocument.Document

def select_diaphragm_wall(wall_name):
    walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    for wall in walls:
        if wall.Name == wall_name:
            return wall
    return None

def get_rebar_type_by_name(type_name):
    rebar_types = FilteredElementCollector(doc).OfClass(RebarBarType).ToElements()
    for rebar_type in rebar_types:
        if rebar_type.Name == type_name:
            return rebar_type
    return None

diaphragm_wall = select_diaphragm_wall("D-wall panel")
rebar_type = get_rebar_type_by_name("H20")

# Attributes for EX-link (Unit > mm)
d_link = 20 / 304.8
l_dwall = 6000 / 304.8
t_dwall = 1000 / 304.8
X0, Y0, Z0 = 0, 0, 0

# Points calculation
XP1 = X0 + 100 / 304.8 + d_link / 2 
YP1 = Y0 + t_dwall / 2 - 75 / 304.8
ZP1 = Z0 + 5500 / 304.8
XP1_prime = XP1 + 290 / 304.8
YP1_prime = YP1
ZP1_prime = ZP1
XP2 = XP1
YP2 = Y0 - t_dwall / 2 + 75 / 304.8 + d_link / 2
ZP2 = ZP1
XP3 = X0 + l_dwall / 2 - 450 / 304.8 - d_link / 2
YP3 = YP2
ZP3 = ZP1

# Assuming delta_x should now represent the x displacement from Y of P3 to that of P4.

angle_degrees = 20  # Angle in degrees.
d = 840 / 304.8  # perpendicular distance between P3 and P4, convert to feet.

# Convert angle to radians
angle_radians = math.radians(angle_degrees)

# Calculate the horizontal (dx) and vertical (dy) components of the slope
delta_x = d * math.tan(angle_radians)

# Calculate new XP4 and YP4
XP4 = XP3 - delta_x
YP4 = Y0 + t_dwall / 2 - 75 / 304.8 - d_link/2
ZP4 = ZP1
XP5 = XP4 - 290 / 304.8
YP5 = YP4
ZP5 = ZP1

# Creating points and curves
p1_prime = XYZ(XP1_prime, YP1_prime, ZP1_prime)
p1 = XYZ(XP1, YP1, ZP1)
p2 = XYZ(XP2, YP2, ZP2)
p3 = XYZ(XP3, YP3, ZP3)
p4 = XYZ(XP4, YP4, ZP4)
p5 = XYZ(XP5, YP5, ZP5)

curve_list = List[Curve]()
curve_list.Add(Line.CreateBound(p1_prime, p1))
curve_list.Add(Line.CreateBound(p1, p2))
curve_list.Add(Line.CreateBound(p2, p3))
curve_list.Add(Line.CreateBound(p3, p4))
curve_list.Add(Line.CreateBound(p4, p5))

def create_ex_link_rebar(doc, wall, rebar_type, curve_list):
    t = Transaction(doc, 'Create EX-Link Rebar')
    t.Start()
    try:
        rebar = Rebar.CreateFromCurves(doc, RebarStyle.Standard, rebar_type, None, None, wall, XYZ.BasisZ, curve_list, RebarHookOrientation.Left, RebarHookOrientation.Right, True, True)
        t.Commit()
        print("The EX-link rebar is created.")  # Confirmation message
    except Exception as e:
        t.RollBack()
        print("Failed to create EX-Link Rebar: {}".format(str(e)))

if diaphragm_wall and rebar_type:
    create_ex_link_rebar(doc, diaphragm_wall, rebar_type, curve_list)
else:
    print("D-wall panel or Rebar type 'H20' not found.")
