import bpy
import os
from subprocess import call
import math

clothing_obj  = None 
body_obj  = None 
script_location = "/home/cesnik/nrg_cloth_simulator"
simulatedData = "simulatedData"


class TestPanel(bpy.types.Panel):
    bl_label = "Wearing Scenario"
    bl_idname = "PT_TestPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Wearing Scenario"
    
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text = "Prepare environment")
        row = layout.row()
        row.label(text = "Clothing", icon="MATCLOTH")
        
        layout = self.layout
        col = layout.column()
        col.prop(context.scene, 'cloth_path')
        layout.prop(context.scene, 'MyEnum')
        self.layout.operator("mesh.import_clothing", icon='MESH_CUBE', text="Import Clothing")
        row = layout.row()
        row.label(text = "Body", icon="USER")
        col = layout.column()
        col.prop(context.scene, 'body_path')
        row = layout.row()
        self.layout.operator("mesh.import_body", icon='MESH_CUBE', text="Import Body")
        
        row = layout.row()
        row.label(text = "Parameters", icon="FILE")
        row = layout.row()
        self.layout.operator("mesh.simulate", icon='PLAY', text="Simulate")
        
        
class OPERATIONS_PANEL(bpy.types.Panel):
    bl_label = "Label"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"                                                                                                    


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.props(context.scene, "dropdown_list")
        
class PanelOne(TestPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_1"
    bl_label = "Panel One"

    def draw(self, context):
   
        self.layout.label(text="Small Class")

def handle_import(file_loc):
    for obj in bpy.data.objects:
        obj.tag = True

    bpy.ops.import_scene.obj(filepath=file_loc)

    imported_objects = [obj for obj in bpy.data.objects if obj.tag is False]
    return imported_objects[0]

class importClothing(bpy.types.Operator):
    bl_idname = 'mesh.import_clothing'
    bl_label = 'Add Clothing'
    bl_options = {"REGISTER", "UNDO"}
        
    def execute(self, context):
        global clothing_obj
        file_loc = os.path.abspath(bpy.path.abspath(context.scene.cloth_path))
        if(clothing_obj):
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[clothing_obj[0].id_data.name].select_set(True)
            bpy.ops.object.delete()
        clothing_obj = (handle_import(file_loc),file_loc)
        
        return {"FINISHED"}    
    


class importBody(bpy.types.Operator):
    bl_idname = 'mesh.import_body'
    bl_label = 'Add Clothing'
    bl_options = {"REGISTER", "UNDO"}
    

    def execute(self, context):
        global body_obj
        file_loc = os.path.abspath(bpy.path.abspath(context.scene.body_path))
        
        if(body_obj):
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[body_obj[0].id_data.name].select_set(True)
            bpy.ops.object.delete()
        body_obj = (handle_import(file_loc),file_loc)
        return {"FINISHED"}      


class simulate(bpy.types.Operator):
    bl_idname = 'mesh.simulate'
    bl_label = 'Simulate'
    bl_options = {"REGISTER", "UNDO"}
    

    def execute(self, context):
        simulationFolder = os.path.join(script_location,simulatedData)
        if not os.path.exists(simulationFolder):
            os.makedirs(simulationFolder)
        export_body_obj()
        generate_custom_json()
        return {"FINISHED"}   
    
def export_body_obj():
    global body_obj
    if(body_obj):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[body_obj[0].id_data.name].select_set(True)
        bpy.ops.export_scene.obj(filepath=os.path.join(os.path.join(script_location,simulatedData),"body.obj"),use_selection=True)
    
def gather_transformations():
    body_location = body_obj[0].location
    body_rotation = body_obj[0].rotation_euler
    body_rotation_deg = [round( math.degrees(r) ,0 )  for r in body_rotation]
    body_location_out = " ".join(map(str,body_location))
    body_rotation_deg_out = " ".join(map(str,body_rotation_deg))
    return (body_location_out,body_rotation_deg_out)
       
def get_materials():

    materials_folder = os.listdir(os.path.join(script_location,"materials"))
    materials = []
    for m in materials_folder:
        if(m[-4:] == "json" and m[0] != "."):
            materials.append((m,m,m))
    return materials


class EnumPanel(bpy.types.Panel):
    bl_idname = "EnumPanel"
    bl_label = "Panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "TOOLS"    
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        enumval = scene.enumval
        layout.prop(enumval, "enumv")
        
class PropVal(bpy.types.PropertyGroup):
    enumv = bpy.props.EnumProperty(
        name="my_enum_name:",
        description="my_enum_description",
        items=get_materials())

def delete_scene_objects():
    """Delete a scene and all its objects."""

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete() 
    
def arcsim():
    #call("arcsim simulateoffline ")
    #call("arcsim generate simulationData/")
    pass
    
def generate_custom_json():
    transform_body = gather_transformations()
    print(transform_body)
    path = os.path.join(script_location,"conf_json_builder.py")
    print(path + " " + script_location + " " + clothing_obj[1] + " " + body_obj[1] + " " + transform_body[0] + " " + transform_body[1])
    call("python " + path + " " + os.path.join(script_location,simulatedData) + " " + clothing_obj[1] + " " + body_obj[1] + " " + transform_body[0] + " " + transform_body[1] , shell=True)
    pass

    
def register():
   # generate_custom_json()
    delete_scene_objects()
    bpy.types.WindowManager.clothing_obj = bpy.props.StringProperty()
    bpy.types.WindowManager.clothing_obj = ""
    bpy.types.Scene.cloth_path = bpy.props.StringProperty \
      (
      name = "Clothing path",
      default="*.obj",
      options={'HIDDEN'},
      description = "Select .Obj file of clothing",
      subtype = 'FILE_PATH'
      )
    bpy.types.Scene.body_path = bpy.props.StringProperty \
      (
      name = "Body path",
      default="*.obj",
      options={'HIDDEN'},
      description = "Select .Obj file of body",
      subtype = 'FILE_PATH'
      )
    bpy.types.Scene.MyEnum = bpy.props.EnumProperty(
        items = get_materials(),
        name="Clothing Material")
    bpy.utils.register_class(importClothing)
    bpy.utils.register_class(importBody)
    bpy.utils.register_class(simulate)
    bpy.utils.register_class(OPERATIONS_PANEL)
    
    bpy.utils.register_class(TestPanel)
      
      
      
def unregister():
    bpy.utils.unregister_class(TestPanel)
    del bpy.types.Scene.cloth_path
    del bpy.types.Scene.body_path
    bpy.utils.unregister_class(importClothing)
    bpy.utils.unregister_class(importBody)
    bpy.utils.unregister_class(OPERATIONS_PANEL)
    del bpy.types.Scene.dropdown_list
if __name__ == "__main__":
    register()