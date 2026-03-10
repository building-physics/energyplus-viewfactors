"""@author: vyk
Use: To create input for View3D program using *.epJSON file and then generate output from View3D program that can be written into another (to not replace the original file *.epJSON file as output
                                                                                                                             Written to run using command prompt
"""
# =============================================================================
# 
# =============================================================================
import json
import os
from typing import TextIO, List

class BadInputFile(Exception):
    pass

class ViewFactorEngine:
    """An object that enables view factor calculation for EnergyPlus.
    
    This object specifies a range of elements and the side number that makes up an Exodus II side set.

    Parameters
    ----------
    obj:
        EnergyPlus input data in dictionary form.
    fp:
        A file pointer (or equivalent) to JSON-formatted EnergyPlus input data.
    filename:
        The name of a file containing JSON-formatted EnergyPlus input data.
    """
    def __init__(self, obj:dict|None=None, fp:TextIO|None=None, filename:str|None=None):
        self.data = {}
        if obj is not None:
            self.data = obj
        elif fp is not None:
            self.data = json.load(fp)
        elif filename is not None:
            with open(filename, 'r') as inp:
                self.data = json.load(inp)
        # GlobalGeometryRules is required so it should be there
        message = None
        no_obj = False
        try:
            glob_geom=self.data['GlobalGeometryRules']
        except KeyError:
            no_obj = True
        if len(glob_geom) == 0:
            no_obj = True
        if no_obj:
            if filename is not None:
                raise BadInputFile(f'Input file "{filename}" does not have a "GlobalGeometryRules" object and is not a valid EnergyPlus input file.')
            else:
                raise BadInputFile('Input data does not have a "GlobalGeometryRules" object and is not valid EnergyPlus input.')
        glob_geom = next(iter(glob_geom.values()))

        try:
            self.ccw = glob_geom['vertex_entry_direction'] == 'Counterclockwise'
        except KeyError:
            if filename is not None:
                raise BadInputFile(f'Input file "{filename}" has a "GlobalGeometryRules" object that does not have "vertex_entry_direction" entry.')
            else:
                raise BadInputFile('Input data does not have a "GlobalGeometryRules" object that does not have "vertex_entry_direction" entry.')

        self.zones = {}
        try:
            self.zones = self.data['Zone']
        except KeyError:
            pass

        self.surfaces = {}
        for el in ['BuildingSurface:Detailed']: # Need to add others
            try:
                self.surfaces.update(self.data[el])
            except KeyError:
                pass

        self.subsurfaces = {}
        for el in ['FenestrationSurface:Detailed']: # Need to add others?
            try:
                self.subsurfaces.update(self.data[el])
            except KeyError:
                pass

        self._assign_surfaces()

    def _assign_surfaces(self):
        """ This function assigns surfaces of each zone to zone list-In energy plus list of surfaces of a zone is not already stored in the zone object"""
        for zone in self.zones:
            self.zones[zone]["Surface"]=[]
        
        for surface in self.surfaces:
            self.surfaces[surface]["Subsurface"]=[]
            self.surfaces[surface]["Name"]=surface
            zone_name=self.surfaces[surface]["zone_name"]
            self.zones[zone_name]["Surface"].append(self.surfaces[surface])
        
        for subsurface in self.subsurfaces:
            self.subsurfaces[subsurface]["Name"]=subsurface
            surface_name=self.subsurfaces[subsurface]["building_surface_name"]
            self.surfaces[surface_name]["Subsurface"].append(self.subsurfaces[subsurface])

    def _rev_cc(self, surface_vertices):
        if self.ccw:
            surface_vertices.reverse()
        return surface_vertices

    def extract(self, directory:str|None=None, zones:List[str]|None=None):
        surf_dict={}
        if zones is None:
            zone_list = list(self.zones.keys())
        else:
            zone_list = [el for el in zones if el in self.zones]

        # Not sure what this does
        #elif type(zones)==str:
        #    Zone_list=dict((k,v) for k,v in Zone_list_all.items() if k==args.zone)
    
        if directory is None:
            directory = '.'

        for zone in zone_list: #iterate over each zone
            Vertices=[];#X=[];Y=[];Z=[];S=[];
            Surf=[]
            i=1
            j=1
            for surface in self.zones[zone]["Surface"]: #iterate over surfaces of each zone
                surf_dict[surface["Name"]]=j
                surface["vertices"]=self._rev_cc(surface["vertices"]) #if vertex enetry is in counterclockwise reverse the vertices so it is clockwise taken by View3D program
                Vertices,Surf,i,j=append_vertices(Vertices,surface,surface_list=Surf,i=i,j=j)
                
                """The parent/base surface should be defined before subsurface"""
                if len(surface["Subsurface"])>0:
                    for subsurface in surface["Subsurface"]:
                        subsurface=get_ss_vert(subsurface)
                        subsurface["vertices"]=self._rev_cc(  subsurface["vertices"])
                        #surf_dict[subsurface["Name"]]=j
                        Vertices,Surf,i,j=append_vertices(Vertices,surface=subsurface,surface_list=Surf,supersurface=surface,i=i,j=j)      
                        
            for ele in Surf:
                if ele[6]!=0:
                    ele[6]=surf_dict[ele[6]]
            #return Vertices,Surf


    # =============================================================================
    # 
    # =============================================================================
            vertices=Vertices
            surfaces=Surf
            #vertices, surfaces=get_vertices(Zone_list_all,zones=zone)

    # =============================================================================
    # Add vertices and surfaces in view 3D format
    # =============================================================================
            #if not os.path.exists(temp_folder):
            #    os.makedirs(temp_folder)
            #V3d_input=open(temp_folder+zone+"view3d.vs3","w")
            with open(os.path.join(directory, zone+'.vs3'), 'w') as fp:
                vertices.insert(0,["!","#","x","y","z"])
                for ele in vertices:
                    for eles in ele:
                        fp.write("%s\t" %eles)
                    fp.write("\n")   
                
                surfaces.insert(0,["!","#","v1","v2","v3","v4","base","cmb","emit","name"])
                for ele in surfaces:
                    for eles in ele:
                        fp.write("%s\t" %eles)
                    fp.write("\n")
            
            #fp.close()                        

# =============================================================================
# # Now put the results for the view factor in "ZoneProperty:UserViewFactors:bySurfaceName" object
# =============================================================================

def create_list(lst,delim=" "):
    res = []
    for el in lst:
        sub = el.split(delim)
        res.append(sub) 
    return(res)

# =============================================================================
# 
# =============================================================================
def format1(value):
    return "%.2f" % value

def get_ss_vert(subsurface):
    """This is to get the vertices of subsurface and assign it the format of surface vertices i.e. V={x,y,z} format """
    subsurface["vertices"]=[]
    for i in range(1,10):
        if "vertex_"+str(i)+"_x_coordinate" in subsurface.keys():
            subsurface["vertices"].append({"vertex_"+str(i)+"_x_coordinate":subsurface["vertex_"+str(i)+"_x_coordinate"],"vertex_"+str(i)+"_y_coordinate":subsurface["vertex_"+str(i)+"_y_coordinate"],"vertex_"+str(i)+"_z_coordinate":subsurface["vertex_"+str(i)+"_z_coordinate"]})
        else:
            break
    return subsurface
            

# =============================================================================
# Code below will get all the vertices of surface/sub-surface of selected zones and append it to a list
# =============================================================================
def append_vertices(vertices_list,surface,surface_list,supersurface=None,i=1,j=1): 
    """append the vertices of the surface to the list "vertices_list" for the chosen 'surface' """
    S=[]
    for vertices in surface["vertices"]:
        V=list(map(format1,vertices.values())) # List the name of the surface, index of the vertex and vertex co-ordinates for each vertices         
        V.insert(0,i)
        #V.insert(0,surface["Name"])
        
        if supersurface != None:
            #V.append(supersurface["Name"])
            #V.insert(0,supersurface["zone_name"])
            V.insert(0,"V")
        else:
            #V.insert(0,surface["zone_name"])
            V.insert(0,"V")
        vertices_list.append(V)
        S.append(i)
        i=i+1
    S.insert(0,j)   
    S.insert(0,"S")
    if supersurface != None:
        S.append(supersurface["Name"])  
    else:
        S.append(0)
    S.append(0)
    S.append(0.5)
    S.append(surface["Name"])    
    surface_list.append(S)
    j=j+1
    return vertices_list,surface_list,i,j