import xml.etree.ElementTree as et
import os,colorsys
#=====#
DEFAULT_BLUEPRINT_NAME = "name"
DEFAULT_AUTHOR_NAME = "someone"
DEFAULT_SKIN = "Weldless"
DEFAULT_GRID_SIZE = "Large"
DEFAULT_BLOCK_TYPE = "BlockArmorBlock"
DEFAULT_BLOCK_DEFINITION = "CubeBlock"
#=====#
skin_types = ['None', 'Battered_Armor', 'CarbonFibre_Armor', 'Clean_Armor', 'Concrete_Armor', 'Corrugated', 'CowMooFlage_Armor', 'DigitalCamouflage_Armor', 'Disco_Armor', 'Dust_Armor', 'Frozen_Armor', 'Glamour_Armor', 'Hazard_Armor', 'Heavy_Rust_Armor', 'Mossy_Armor', 'Neon_Colorable_Lights', 'Neon_Colorable_Surface', 'Plastic', 'Retrofuture_Armor', 'Rusty_Armor', 'SciFi_Armor', 'Wartorn', 'Weldless', 'Wood_Armor', 'WoodlandCamo_Armor']
def add_tag(element,tag):
    name,attrib,text = tag
    tag = et.SubElement(element,name)
    if attrib:
        tag.attrib = attrib
    if text:
        tag.text = text
    return tag
#==creating blueprint==#

def rgb_to_sehsv(c):
    c = [i/255 for i in c]
    if c == [0,0,0]:
        c = (0,-0.8,-0.5)
    else:
        c = colorsys.rgb_to_hsv(c[0],c[1],c[2])
        c = (c[0],c[1]-0.8,c[2]-0.5)
        c = [str(i) for i in c]
    return c
class block:
    def __init__(self,grid,pos,color,**kwargs):
        kwargs = kwargs["kwargs"]
        skin = kwargs.get("skin",DEFAULT_SKIN)
        block_type,block_definition = kwargs.get("type",(DEFAULT_BLOCK_TYPE,DEFAULT_BLOCK_DEFINITION))
        size = kwargs.get("size",grid.grid_size)
        new_block = add_tag(grid.blocks,["MyObjectBuilder_CubeBlock",{"xsi:type":f"MyObjectBuilder_{block_definition}"},""])
        add_tag(new_block,["SubtypeName","",size+block_type])
        axes = ["x","y","z"]
        add_tag(new_block,["Min",{ax:str(pos[idx]) for idx,ax in enumerate(axes)},""])
        color = rgb_to_sehsv(color)
        add_tag(new_block,["ColorMaskHSV",{ax:str(color[idx]) for idx,ax in enumerate(axes)},""])
        if skin in skin_types:
            add_tag(new_block,["SkinSubtypeId","",skin])
    
class cube_grid:
    def __init__(self,bp_file,**kwargs):
        bp = bp_file.bp
        self.grid_size = kwargs.get("grid_size",DEFAULT_GRID_SIZE)

        self.pos = kwargs.get("pos",(0,0,0))
        self.orientation = kwargs.get("orientation",(0,0,0,1))
        self.author_name = kwargs.get("author_name",DEFAULT_AUTHOR_NAME)
        ship_cube_grids = bp.find("CubeGrids")
        if not ship_cube_grids:
            ship_cube_grids = et.SubElement(bp,"CubeGrids")
        self.grid = et.SubElement(ship_cube_grids,"CubeGrid")
        #==setting blueprint position==#
        ship_transform = et.SubElement(self.grid,"PositionAndOrientation")
        axes = ["x","y","z"]
        et.SubElement(ship_transform,"Position").attrib = {ax:str(self.pos[idx]) for idx,ax in enumerate(axes)}
        et.SubElement(ship_transform,"Forward").attrib ={"x":"0","y":"0","z":"1"}
        et.SubElement(ship_transform,"Up").attrib ={"x":"0","y":"1","z":"0"}
        ship_orientation = et.SubElement(ship_transform,"Orientation")
        axes = ["X","Y","Z","W"]
        for idx,ax in enumerate(axes):
            et.SubElement(ship_orientation,ax).text = str(self.orientation[idx])
        #==setting blueprint info==#
        et.SubElement(self.grid,"GridSizeEnum").text = self.grid_size
        et.SubElement(self.grid,"DisplayName").text = self.author_name
        self.blocks = et.SubElement(self.grid,"CubeBlocks")
    def set_grid_size(self,size):
        grid_size_enum = self.grid.find("GridSizeEnum")
        grid_size_enum.text = size
    def create_block(self,pos,color,**kwargs):
        new_block = block(self,pos,color,kwargs=kwargs)
        return new_block

class blueprint_file:
    def __init__(self,name=DEFAULT_BLUEPRINT_NAME):
        definitions = et.Element("Definitions")
        definitions.attrib = {"xmlns:xsd":"http://www.w3.org/2001/XMLSchema", "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"}
        self.tree = et.ElementTree(definitions)
        self.ship_blueprints = et.SubElement(definitions,"ShipBlueprints")
        self.bp = add_tag(self.ship_blueprints,["ShipBlueprint",{"xsi:type": "MyObjectBuilder_ShipBlueprintDefinition"},""])
        add_tag(self.bp,["Id",{"Type": "MyObjectBuilder_ShipBlueprintDefinition", "Subtype":name},""])
    def save(self,output_path = "",remove_sbcb5=True):
        et.indent(self.tree)
        blueprint_path = os.path.join(output_path,"bp.sbc")
        self.tree.write(blueprint_path, encoding = "UTF-8", xml_declaration = True)
        sbcb5_path = os.path.join(output_path,"bp.sbcB5")
        if os.path.isfile(sbcb5_path) and remove_sbcb5:
            os.remove(sbcb5_path)

def set_rotation(block,a,b):
    directions_horizontal = ["Forward","Right","Backward","Left"]
    directions_vertical = ["Up","Forward","Down","Backward"]
    dir = {
    "Forward": directions_horizontal[a%len(directions_horizontal)],
    "Up": directions_vertical[b%len(directions_vertical)]
    }
    add_tag(block,["BlockOrientation",dir,""])
