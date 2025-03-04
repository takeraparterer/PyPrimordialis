# u32 version (use 4)
# u32 cellcount
# u32 orientation (32 bit lmao)
# u32 combo count (doesnt exist in v3)
# 
# 32 celltype
# f32 red
# f32 green
# f32 blue
# f32 alpha
# i32 ? x
# i32 ? y
#Hex grids use axial coordinates (q, r), where adding 1 to q moves one hex to the right, and adding 1 to r moves one hex up-right. 
#eg:
#(-3,+2)---(-2,+2)---(-1,+2)---(+0,+2)---(+1,+2)
#     \    /    \    /    \    /    \    /    \
#    (-2,+1)---(-1,+1)---(+0,+1)---(+1,+1)---(+2,+1)
#     /    \    /    \    /    \    /    \    /
#(-2,+0)---(-1,+0)---(+0,+0)---(+1,+0)---(+2,+0)
#     \    /    \    /    \    /    \    /    \
#    (-1,-1)---(+0,-1)---(+1,-1)---(+2,-1)---(+3,-1)
#
import struct
class PrimordialisCell:
    def __init__(self,cellType:str,r:float,g:float,b:float,a:float,x:int=0,y:int=0,mystery=None):
        self.cellType = cellType
        self.mystery = mystery
        self.col = (r,g,b,a)
        self.pos = (x,y)
        self.pos_norm = (0,0)
    def __str__(self):
        return f"Cell of type {self.cellType} at {self.pos}"
    def __repr__(self):
        return self.__str__()
class PrimordialisOrganism:
    def __init__(self,size:tuple[int,int]=(0,0),offset:tuple[int,int]=(0,0)):
        self.fileVersion = 3
        self.cellCount = 0
        self.orientation = 0
        self.combinationCount = None
        self.idx_array = None
        self.cells:list[PrimordialisCell] = []
        self.size = size
        self.offset = offset
    def build_idxs(self):
        w = self.size[0]
        h = self.size[1]
        self.idx_array = [[None for width in range(w)] for height in range(h)]
        for cell_idx,cell in enumerate(self.cells):
            cpx = cell.pos_norm[0]
            cpy = cell.pos_norm[1]
            self.idx_array[cpy][cpx] = cell_idx
    def get_cell(self,x:int,y:int) -> PrimordialisCell:
        return self.cells[self.idx_array[y][x]]
    def set_cell(self,x:int,y:int,cell:PrimordialisCell,auto_pos:bool = True):
        if auto_pos:
            cell.pos_norm = (x,y)
            cell.pos = (x+self.offset[0],y+self.offset[1])
        if self.idx_array[y][x] is None:
            self.cells.append(None)
            self.idx_array[y][x] = len(self.cells)-1
        self.cells[self.idx_array[y][x]] = cell
        self.cellCount = len(self.cells)
    def load(self,fp:str):
        with open(fp,"rb") as f:
            self.fileVersion = struct.unpack("I",f.read(4))[0]
            #print(self.fileVersion)
            self.cellCount = struct.unpack("I",f.read(4))[0]
            if self.fileVersion > 1:
                self.orientation = struct.unpack("I",f.read(4))[0]
            if self.fileVersion > 3:
                self.combinationCount = struct.unpack("I",f.read(4))[0]
            
            min_x,min_y = 0,0
            max_x,max_y = 0,0
            for cell_idx in range(self.cellCount):
                celltype = f.read(4).decode()
                r = struct.unpack("f",f.read(4))[0]
                g = struct.unpack("f",f.read(4))[0]
                b = struct.unpack("f",f.read(4))[0]
                a = struct.unpack("f",f.read(4))[0]
                x = struct.unpack("i",f.read(4))[0]
                y = struct.unpack("i",f.read(4))[0]
                mys = None
                if self.fileVersion < 3:
                    mys = f.read(4) # TODO: what is this extra value?
                min_x = min(min_x,x)
                min_y = min(min_y,y)
                max_x = max(max_x,x)
                max_y = max(max_y,y)
                self.cells.append(PrimordialisCell(celltype,r,g,b,a,x,y,mys))
            for cell_idx in range(len(self.cells)):
                self.cells[cell_idx].pos_norm = (self.cells[cell_idx].pos[0]-min_x,self.cells[cell_idx].pos[1]-min_y)
            max_x -= min_x
            max_y -= min_y
            self.size = (max_x+1,max_y+1)
            self.offset = (min_x,min_y)
        self.build_idxs()
    def save(self,path:str):
        with open(path, "wb") as f:
            f.write(struct.pack("I",self.fileVersion))
            f.write(struct.pack("I",self.cellCount))
            if self.fileVersion > 1:
                f.write(struct.pack("I",self.orientation))
            if self.fileVersion > 3:
                f.write(struct.pack("I",self.combinationCount))
            for cell in self.cells:
                f.write(cell.cellType.encode())
                f.write(struct.pack("f",cell.col[0]))
                f.write(struct.pack("f",cell.col[1]))
                f.write(struct.pack("f",cell.col[2]))
                f.write(struct.pack("f",cell.col[3]))
                f.write(struct.pack("i",cell.pos[0]))
                f.write(struct.pack("i",cell.pos[1]))
                if self.fileVersion < 3:
                    f.write(cell.mystery)
    def __str__(self):
        return f"Organism with {self.cellCount} cells (version {self.fileVersion})"
    def __repr__(self):
        return self.__str__()

# simple loading and saving
snail = PrimordialisOrganism()
snail.load("snail.bod")
print(snail.fileVersion)
print(snail.cellCount)
print(snail.orientation)
print(snail.combinationCount)
print([cell.cellType for cell in snail.cells])
print(snail)
print(snail.size)
snail.save("snail2.bod")

# mass convert files to pngs (very scuffed, converts hex into square grid)
#import matplotlib.pyplot as plt
#from PIL import Image
#import numpy as np
#import os
#for file in os.listdir("enemies"):
#    print(f"Loading {file}")
#    organism = PrimordialisOrganism(f"enemies/{file}")
#    print(organism)
#    arr = np.zeros((organism.size[1],organism.size[0],4))
#    for cell in organism.cells:
#        x,y = cell.pos_norm
#        arr[y][x][:3] = cell.col[:3]
#        arr[y][x][3] = 1
#    Image.fromarray((arr*255).astype(np.uint8)).save(f"render/{file[:-4]}.png")

# convert png to file
#from PIL import Image
#import numpy as np
#size = 100
#imarr = np.array(Image.open(r"image.png").convert("RGBA").resize((size,size)))/255
#
#image = PrimordialisOrganism((2*size,size),(-(size),-(size//2)))
#image.build_idxs()
#for x in range(size):
#    for y in range(size):
#        r,g,b,a = imarr[-(x+1)][-(y+1)]
#        if a > 0.5:
#            image.set_cell(x+(list(reversed(list(range(size))))[y]//2),y,PrimordialisCell("SPIK",r,g,b,1.0))
#image.save(r"image.bod")
