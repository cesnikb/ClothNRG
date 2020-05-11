import bpy
import os

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
        
class importClothing(bpy.types.Operator):
    bl_idname = 'mesh.import_clothing'
    bl_label = 'Add Clothing'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        file_loc = os.path.abspath(bpy.path.abspath(context.scene.cloth_path))
        imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
        print(file_loc)
        return {"FINISHED"}      

class importBody(bpy.types.Operator):
    bl_idname = 'mesh.import_body'
    bl_label = 'Add Clothing'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        file_loc = os.path.abspath(bpy.path.abspath(context.scene.body_path))
        imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
        print(file_loc)
        return {"FINISHED"}      

def register():
    bpy.utils.register_class(TestPanel)
    
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
      
    bpy.utils.register_class(importClothing)
    bpy.utils.register_class(importBody)
    bpy.utils.register_class(OPERATIONS_PANEL)
    bpy.types.Scene.dropdown_list = EnumProperty(
        name="Selection",
        items=(
               ('1', 'Skeleton', 'Export Skeleton to JSON-file'),
               ('2', 'Animation', 'Export Animation to JSON-file'),
            ),
        )
      
      
      
def unregister():
    bpy.utils.unregister_class(TestPanel)
    del bpy.types.Scene.cloth_path
    del bpy.types.Scene.body_path
    bpy.utils.unregister_class(importClothing)
    bpy.utils.unregister_class(importBody)
if __name__ == "__main__":
    register()