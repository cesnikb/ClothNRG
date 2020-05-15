import bpy
import os
from subprocess import call
import math
import glob
from os import listdir
from os.path import isfile, join
import bpy
from mathutils import Color

clothing_obj  = None 
clothing_obj_new  = None 
body_obj  = None 
script_location = "/home/cesnik/nrg_cloth_simulator"
simulatedData = "simulatedData"
material = None
vertex_values = []

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
        props = self.layout.operator('object.anim_time')
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

def set_shading_mode(mode="SOLID", screens=[]):

    screens = screens if screens else [bpy.context.screen]
    for s in screens:
        for spc in s.areas:
            if spc.type == "VIEW_3D":
                spc.spaces[0].shading.type = mode
                break # we expect at most 1 VIEW_3D space
            
class simulate(bpy.types.Operator):
    bl_idname = 'mesh.simulate'
    bl_label = 'Simulate'
    bl_options = {"REGISTER", "UNDO"}
    

    def execute(self, context):
        
        #context.view_layer.objects.active = None
        #bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        
        simulationFolder = os.path.join(script_location,simulatedData)
        if not os.path.exists(simulationFolder):
            os.makedirs(simulationFolder)
        else:
            folder_path = os.path.join(script_location,simulatedData)
            for file_object in os.listdir(folder_path):
                file_object_path = os.path.join(folder_path, file_object)
                if os.path.isfile(file_object_path) or os.path.islink(file_object_path):
                    os.unlink(file_object_path)
                else:
                    shutil.rmtree(file_object_path)
        

         
        export_body_obj()
        generate_custom_json()
        arcsim()
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[clothing_obj[0].id_data.name].select_set(True)
        bpy.ops.object.delete()
        

        get_vertex_value()
        color_vertex_new(clothing_obj_new.id_data.name,context)
        
        set_shading_mode("MATERIAL")
        bpy.context.view_layer.objects.active = clothing_obj_new
        ob = context.active_object
        
        mat = bpy.data.materials.get("Material")
        
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="Material")
   
        if ob.data.materials:
            # assign to 1st material slot
            ob.data.materials[0] = mat
        else:
            # no slots
            ob.data.materials.append(mat)

        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        node = nodes.new("ShaderNodeAttribute")
        node.attribute_name = "Col"
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        mat.node_tree.links.new(node.outputs[0],bsdf.inputs[0])
        
        light_data = bpy.data.lights.new(name="sunlight", type='POINT')
        light_data.energy = 20
        light_object = bpy.data.objects.new(name="sunlight", object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        bpy.context.view_layer.objects.active = light_object
        dg = bpy.context.evaluated_depsgraph_get() 
        dg.update()
        
        return {"FINISHED"}   
    
def export_body_obj():
    global body_obj
    if(body_obj):
        bpy.ops.object.select_all(action='DESELECT')
        print("BODYYY")
        print(body_obj)
        body_name = body_obj[0].id_data.name
        bpy.data.objects[body_name].select_set(True)
        bpy.ops.export_scene.obj(filepath=os.path.join(os.path.join(script_location,simulatedData),"body.obj"),use_selection=True)
    
 
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
    call("arcsim simulateoffline "+os.path.join(os.path.join(script_location,simulatedData),"conf.json") +" " + os.path.join(script_location,simulatedData),shell=True)
    call("arcsim generate "+ os.path.join(script_location,simulatedData), shell=True)
    get_last_position()
    
def generate_custom_json():
    f_time = str(round(bpy.context.window_manager.operator_properties_last("object.anim_time").frame_time,2))
    f_steps = str(bpy.context.window_manager.operator_properties_last("object.anim_time").frame_steps)
    e_time = str(bpy.context.window_manager.operator_properties_last("object.anim_time").end_time)
    print(f_time,f_steps,e_time)
    path = os.path.join(script_location,"conf_json_builder.py")
    call("python " + path + " " + script_location + " " + clothing_obj[1]+ " " + simulatedData + " " + bpy.context.scene.MyEnum + " " + f_time + " " + f_steps + " " + e_time   , shell=True)

def get_last_position():
    global clothing_obj_new
    
    f_time = round(bpy.context.window_manager.operator_properties_last("object.anim_time").frame_time,2)
    e_time = bpy.context.window_manager.operator_properties_last("object.anim_time").end_time
    n_frames = str(math.floor(e_time/f_time)).zfill(5) + "_00.obj"
    #if frame_time =0.4 and end_time=1 -> last frame is 25
    last_obj_file = os.path.join(script_location,simulatedData,n_frames)
    clothing_obj_new = handle_import(last_obj_file)
     
     

def color_vertex_new(obj,cont):
    global vertex_values
    """Paints a single vertex where vert is the index of the vertex
    and color is a tuple with the RGB values."""
    obj_d = bpy.data.objects[obj]
    obj_data  = obj_d.data
    
    mesh = obj_data 
    scn = bpy.context.scene
    
    cont.view_layer.objects.active = obj_d
    bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
    
    for polygon in mesh.polygons:
            for i, index in enumerate(polygon.vertices):
                vert_val = vertex_values[index]
                loop_index = polygon.loop_indices[i]
                mesh.vertex_colors.active.data[loop_index].color = (float(vert_val),0.0,0.0,0.4)

def get_vertex_value():
    global vertex_values
    call("python " + os.path.join(script_location,"suit_fit_calculation.py ")+ os.path.join(script_location,simulatedData),shell=True)
    
    f = open(os.path.join(script_location,simulatedData,"vertex_value.txt"), "r")
    output = []
    for x in f:
        vertex_values.append(x.strip())
    f.close()  
    
class OBJECT_OT_anim_time(bpy.types.Operator):
    bl_idname = "object.anim_time"
    bl_label = "Animation time"
    bl_options = {'REGISTER', 'UNDO'}

    frame_time: bpy.props.FloatProperty(name="frametime",default = 0.05, min = 0.01, max = 0.1, step=1)
    frame_steps: bpy.props.IntProperty(name="framesteps",default = 4, min = 1, max = 10)
    end_time: bpy.props.IntProperty(name="endtime",default = 1, min = 1, max = 10)

    def execute(self, context):
#        self.report(
#            {'INFO'}, 'F: %.2f  B: %s  S: %r' %
#            (self.frame_time, self.frame_steps, self.end_time)
#        )
        print('Frame time:', self.frame_time)
        print('Frame steps:', self.frame_steps)
        print('End time:', self.end_time)
        return {'FINISHED'}        
          
def register():
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
    bpy.utils.register_class(OBJECT_OT_anim_time)
    bpy.utils.register_class(simulate)
    bpy.utils.register_class(OPERATIONS_PANEL)
    
    bpy.utils.register_class(TestPanel)
      
      
      
def unregister():
    bpy.utils.unregister_class(TestPanel)
    del bpy.types.Scene.cloth_path
    del bpy.types.Scene.body_path
    del bpy.types.Scene.MyEnum
    bpy.utils.unregister_class(importClothing)
    bpy.utils.unregister_class(importBody)
    bpy.utils.unregister_class(OBJECT_OT_anim_time)
    bpy.utils.unregister_class(simulate)
    bpy.utils.unregister_class(OPERATIONS_PANEL)
    del bpy.types.Scene.dropdown_list
    
if __name__ == "__main__":
    register()