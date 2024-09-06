import Rhino
import rhinoscriptsyntax as rs
import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino.Geometry as rg
import System.Drawing

class CylinderConduit(Rhino.Display.DisplayConduit):
    def __init__(self, base_plane, height, radius):
        super(CylinderConduit, self).__init__()
        self.base_plane = base_plane
        self.height = height
        self.radius = radius
        self.material = Rhino.Display.DisplayMaterial(System.Drawing.Color.DeepPink)
        self.material.BackDiffuse = System.Drawing.Color.HotPink
        self.material.IsTwoSided = True
        self.brep_cylinder = self.create_cylinder_brep()

    def create_cylinder_brep(self):
        """Create a cylinder Brep."""
        circle = rg.Circle(self.base_plane, self.radius)
        cylinder = rg.Cylinder(circle, self.height)
        return cylinder.ToBrep(True, True)

    def CalculateBoundingBox(self, e):
        """Include the Brep bounding box in the viewport's bounding box."""
        if self.brep_cylinder:
            e.IncludeBoundingBox(self.brep_cylinder.GetBoundingBox(False))

    def PostDrawObjects(self, e):
        """Draw the Brep with shading and wires."""
        if self.brep_cylinder:
            e.Display.EnableLighting(True)
            e.Display.DrawBrepShaded(self.brep_cylinder, self.material)
            e.Display.DrawBrepWires(self.brep_cylinder, System.Drawing.Color.Black)

    def update(self, base_plane, height, radius):
        """Update cylinder parameters and trigger redraw."""
        self.base_plane = base_plane
        self.height = height
        self.radius = radius
        self.brep_cylinder = self.create_cylinder_brep()
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()

class CylinderTool(forms.Form):
    def __init__(self):
        super(CylinderTool, self).__init__()

        self.Title = 'Cylinder Tool'
        self.Padding = drawing.Padding(10)
        self.ClientSize = drawing.Size(300, 150)
        self.Resizable = True

        # Initialize the cylinder parameters
        self.base = rg.Plane.WorldXY  # Default base plane
        self.height = 25  # Default height
        self.radius = 15  # Default radius

        # Create a conduit instance
        self.conduit = CylinderConduit(self.base, self.height, self.radius)
        self.conduit.Enabled = True  # Enable the conduit to start drawing

        # Create a dropdown for the base plane selection
        self.base_dropdown = forms.DropDown()
        self.base_dropdown.DataStore = ["XY Plane", "YZ Plane", "XZ Plane"]
        self.base_dropdown.SelectedIndex = 0  # Default is "XY Plane"
        self.base_dropdown.SelectedIndexChanged += self.on_base_plane_change

        # Create a slider for height
        self.height_slider = forms.Slider()
        self.height_slider.MinValue = 20
        self.height_slider.MaxValue = 50
        self.height_slider.Value = self.height
        self.height_slider.ValueChanged += self.on_height_change

        # Create a slider for radius
        self.radius_slider = forms.Slider()
        self.radius_slider.MinValue = 5
        self.radius_slider.MaxValue = 25
        self.radius_slider.Value = self.radius
        self.radius_slider.ValueChanged += self.on_radius_change

        # Create layout and add controls
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)

        layout.AddRow(forms.Label(Text="Base Plane:"), self.base_dropdown)
        layout.AddRow(forms.Label(Text="Height:"), self.height_slider)
        layout.AddRow(forms.Label(Text="Radius:"), self.radius_slider)

        # Add layout to the dialog
        self.Content = layout

        # Set the form to be modeless
        self.Owner = Rhino.UI.RhinoEtoApp.MainWindow

        # Hook the form close event to disable the conduit
        self.Closed += self.on_form_closed

    def on_base_plane_change(self, sender, e):
        """Update the base plane parameter based on the dropdown selection."""
        selected_plane = self.base_dropdown.SelectedValue
        if selected_plane == "XY Plane":
            self.base = rg.Plane.WorldXY
        elif selected_plane == "YZ Plane":
            self.base = rg.Plane.WorldYZ
        else:
            self.base = rg.Plane.WorldZX

        self.conduit.update(self.base, self.height, self.radius)  # Trigger redraw

    def on_height_change(self, sender, e):
        """Update the height parameter when the slider moves."""
        self.height = self.height_slider.Value
        self.conduit.update(self.base, self.height, self.radius)  # Trigger redraw

    def on_radius_change(self, sender, e):
        """Update the radius parameter when the slider moves."""
        self.radius = self.radius_slider.Value
        self.conduit.update(self.base, self.height, self.radius)  # Trigger redraw

    def on_form_closed(self, sender, e):
        """Disable the conduit when the form is closed."""
        self.conduit.Enabled = False  # Disable the conduit to stop drawing

def CylinderToolDialog():
    """Display the cylinder tool dialog."""
    dialog = CylinderTool()
    dialog.Show()

# Run the dialog in Rhino script editor
CylinderToolDialog()
