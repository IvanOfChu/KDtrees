from __future__ import annotations
import json
import math
from typing import List

# Datum class.
# DO NOT MODIFY.
class Datum():
    def __init__(self,
                 coords : tuple[int],
                 code   : str):
        self.coords = coords
        self.code   = code
    def to_json(self) -> str:
        dict_repr = {'code':self.code,'coords':self.coords}
        return(dict_repr)

# Internal node class.
# DO NOT MODIFY.
class NodeInternal():
    def  __init__(self,
                  splitindex : int,
                  splitvalue : float,
                  leftchild,
                  rightchild):
        self.splitindex = splitindex
        self.splitvalue = splitvalue
        self.leftchild  = leftchild
        self.rightchild = rightchild

# Leaf node class.
# DO NOT MODIFY.
class NodeLeaf():
    def  __init__(self,
                  data : List[Datum]):
        self.data = data

# KD tree class.
class KDtree():
    def  __init__(self,
                  splitmethod : str,
                  k           : int,
                  m           : int,
                  root        : NodeLeaf = None):
        self.k    = k
        self.m    = m
        self.splitmethod = splitmethod
        self.root = root

    # For the tree rooted at root, dump the tree to stringified JSON object and return.
    # DO NOT MODIFY.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            if isinstance(node,NodeLeaf):
                return {
                    "p": str([{'coords': datum.coords,'code': datum.code} for datum in node.data])
                }
            else:
                return {
                    "splitindex": node.splitindex,
                    "splitvalue": node.splitvalue,
                    "l": (_to_dict(node.leftchild)  if node.leftchild  is not None else None),
                    "r": (_to_dict(node.rightchild) if node.rightchild is not None else None)
                }
        if self.root is None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)
    

    def insertHelp(self, node, count: int, point:tuple[int], code:str):
        if isinstance(node, NodeLeaf): #if we reach a nodeleaf
            newData = Datum(point, code)
            node.data.append(newData)

            if len(node.data) > self.m: #exceed max datums
                if self.splitmethod == "cycle": #cycle split
                    splitindex = count % self.k
                else: #spread split
                    maxIndex = 0
                    maxSpread = 0
                    for x in range(self.k):
                        minValue = float('inf')
                        maxValue = float('-inf')
                        for y in node.data:
                            if y.coords[x] > maxValue:
                                maxValue = y.coords[x]
                            if y.coords[x] < minValue:
                                minValue = y.coords[x]
                        dimSpread = maxValue - minValue

                        if dimSpread > maxSpread:
                            maxSpread = dimSpread
                            maxIndex = x

                    splitindex = maxIndex
                
                indexOrder = []
                for i in range(self.k):
                    indexOrder.append((splitindex + i) % self.k)

                coordinateSort = sorted(node.data, key = lambda d: tuple(d.coords[i] for i in indexOrder))

                medianIndex = math.floor(len(coordinateSort)/2)
                
                #nodeleaf parts

                splitvalue = float(coordinateSort[medianIndex].coords[splitindex])
                if len(coordinateSort) % 2 == 0:
                    splitvalue = (splitvalue + coordinateSort[medianIndex - 1].coords[splitindex])/2
                
                leftlist = coordinateSort[:medianIndex]
                rightlist = coordinateSort[medianIndex:]
                
                leftchild = NodeLeaf(leftlist)
                rightchild = NodeLeaf(rightlist)

                return NodeInternal(splitindex, float(splitvalue), leftchild, rightchild)
            else:
                return node
        else:
            if point[node.splitindex] >= node.splitvalue:
                node.rightchild = self.insertHelp(node.rightchild, node.splitindex + 1, point, code)
            else: 
                node.leftchild = self.insertHelp(node.leftchild, node.splitindex + 1, point, code)
            return node                      

    # Insert the Datum with the given code and coords into the tree.
    # The Datum with the given coords is guaranteed to not be in the tree.
    def insert(self,point:tuple[int],code:str):
        
        if self.root is None: #empty tree
            self.root = NodeLeaf([Datum(point, code)])
            return
        
        self.root = self.insertHelp((self.root or NodeLeaf([])), 0, point, code)
        

    def deleteHelp(self, point:tuple[int], grandparent, parent, current):
        found = False
        if isinstance(current, NodeLeaf):
            target = None
            
            for x in current.data:
                if x.coords == point:
                    target = x
            
            if target is not None:
                current.data.remove(target)
                found = True

            if not current.data:
                if (grandparent is None and parent is None):
                    self.root = None
                elif (grandparent is None and parent is not None):
                    if parent.leftchild == current:
                        parent.leftchild = None
                        self.root = parent.rightchild
                    else:
                        parent.rightchild = None
                        self.root = parent.leftchild
                else:
                    if grandparent.leftchild == parent:
                        if parent.leftchild == current:
                            grandparent.leftchild = parent.rightchild
                        else:
                            grandparent.leftchild = parent.leftchild
                    else:
                        if parent.leftchild == current:
                            grandparent.rightchild = parent.rightchild
                            
                        else:
                            grandparent.rightchild = parent.leftchild
        else:
            if point[current.splitindex] < current.splitvalue:
                self.deleteHelp(point, parent, current, current.leftchild)
            elif point[current.splitindex] == current.splitvalue:
                found = self.deleteHelp(point, parent, current, current.leftchild)

                if not found:
                    self.deleteHelp(point, parent, current, current.rightchild)
            else:
                self.deleteHelp(point, parent, current, current.rightchild)
                
        return found

    # Delete the Datum with the given point from the tree.
    # The Datum with the given point is guaranteed to be in the tree.
    def delete(self,point:tuple[int]):
        self.deleteHelp(point, None, None, self.root)


    # Find the k nearest neighbors to the point.
    def knn(self,k:int,point:tuple[int]) -> str:
        # Use the strategy discussed in class and in the notes.
        # The list should be a list of elements of type Datum.
        # While recursing, count the number of leaf nodes visited while you construct the list.
        # The following lines should be replaced by code that does the job.
        leaveschecked = 0
        knnlist = []
        knnTempList = []

        def knnFind(node):
            nonlocal leaveschecked
            nonlocal knnTempList

            if isinstance(node, NodeLeaf):
                leaveschecked += 1

                for i in node.data:
                    checkCoords(i)
            else:
                leftBox = calcBoundingBox(node.leftchild)
                rightBox = calcBoundingBox(node.rightchild)
                leftBoxDistance = calcBoundingBoxDistance(leftBox)
                rightBoxDistance = calcBoundingBoxDistance(rightBox)

                if leftBoxDistance <= rightBoxDistance:
                    if len(knnTempList) < k or leftBoxDistance <= knnTempList[-1][1]:
                        knnFind(node.leftchild)
                    
                    if len(knnTempList) < k or rightBoxDistance <= knnTempList[-1][1]:
                        knnFind(node.rightchild)
                else:
                    if len(knnTempList) < k or rightBoxDistance <= knnTempList[-1][1]:
                        knnFind(node.rightchild)
                    if len(knnTempList) < k or leftBoxDistance <= knnTempList[-1][1]:
                        knnFind(node.leftchild)

                

        def checkCoords(datum):
            nonlocal knnTempList
            distance = 0

            for i in range(len(point)):
                difference = datum.coords[i] - point[i]
                difference = difference ** 2
                distance = distance + difference

            knnTempList.append((datum, distance))
            knnTempList.sort(key=lambda d: (d[1], d[0].code))

            if len(knnTempList) > k:
                del knnTempList[-1]
                    


        def calcBoundingBox(node):
            boundBox = []

            if isinstance(node, NodeLeaf):
                maxBox = list(node.data[0].coords)
                minBox = list(node.data[0].coords)
                for i in node.data:
                    for j in range(len(i.coords)):
                        if i.coords[j] < minBox[j]:
                            minBox[j] = i.coords[j]
                        if i.coords[j] > maxBox[j]:
                            maxBox[j] = i.coords[j]
                    
                for i in range(len(minBox)):
                    boundBox.append([minBox[i], maxBox[i]])
                
                return boundBox
            
            else:
                leftbound = calcBoundingBox(node.leftchild)
                rightbound = calcBoundingBox(node.rightchild)

                for i in range(0, self.k):
                    if leftbound[i][0] < rightbound[i][0]:
                        minVal = leftbound[i][0]
                    else: 
                        minVal = rightbound[i][0]
                
                    if leftbound[i][1] > rightbound[i][1]:
                        maxVal = leftbound[i][1]
                    else:
                        maxVal = rightbound[i][1]
                    
                    boundBox.append([minVal, maxVal])
                
                return boundBox
            
            
        def calcBoundingBoxDistance(box):
            distance = 0

            for i in range(0, self.k):
                if point[i] < box[i][0]:
                    difference = (box[i][0] - point[i])
                    difference = difference ** 2
                    distance = distance + difference
                elif point[i] > box[i][1]:
                    difference = (point[i] - box[i][1])
                    difference = difference ** 2
                    distance = distance + difference
            
            return distance



        knnFind(self.root)

        temp = sorted(knnTempList, key=lambda d: d[1])
        for i in temp:
            knnlist.append(i[0])



        # The following return line can probably be left alone unless you make changes in variable names.
        return(json.dumps({"leaveschecked":leaveschecked,"points":[datum.to_json() for datum in knnlist]},indent=2))