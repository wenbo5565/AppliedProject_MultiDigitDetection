"""
Define class and method to load .mat file and dump into JSON
"""
import h5py
import tqdm
import json

class DigitStructFile:
    def __init__(self,h5file):
        """ class constructor """
        self.file = h5py.File(h5file,'r')
        self.digitStructName = self.file['/digitStruct/name']
        self.digitStructBbox = self.file['/digitStruct/bbox']
        
    def getName(self,i):
        """ extract i-th image file name from HDF5 group "name" """
        return [''.join([chr(file_char[0]) for file_char in self.file[self.digitStructName[i][0]].value])]
        
    def getValue(self,attr_vector):
        """
        Extract attribute value for the i-th image. The attribute could be
        'height','width','top','left' and 'label'. 
        
        Parameters
        ---------
        
        attr_vector: vector of references of an attribute. If i-th image has j bounding box,
                     then attr_vector is in shape [j,1]
                     
        """
        if len(attr_vector) > 1:
            attr_value = [self.file[attr_vector.value[j].item()].value[0][0] for j in range(len(attr_vector))]
        else:
            attr_value = [attr_vector.value[0].item()]
        return attr_value
    
    def getBbox(self,i):
        """
        Extract bounding box information for i-th image and store it to a dict
        """
        bbox = {}
        bb = self.digitStructBbox[i].item()
        bbox['height'] = self.getValue(self.file[bb]["height"])
        bbox['label'] = self.getValue(self.file[bb]["label"])
        bbox['left'] = self.getValue(self.file[bb]["left"])
        bbox['top'] = self.getValue(self.file[bb]["top"])
        bbox['width'] = self.getValue(self.file[bb]["width"])
        
        return bbox
    
    def getDigitStructure(self,i):
        """
        return image name and bounding box value for i-th image
        """
        d = self.getBbox(i)
        d['name'] = self.getName(i)
        
        return d
        
    def getAlldigit(self):
        """
        extract bounding box information for all image
        """
        print("start parsing data...")
        return [self.getDigitStructure(i) for i in tqdm.tqdm(range(len(self.digitStructName)))]
    
    
    def getAllDigit_ByDigit(self):
        """
        Accept returned object from getAlldigit(), re-organize it and output a list.
        
        The output is a list of dicts each of which includes information for every bounding box
        for that image.
        """
        pictDat = self.getAlldigit()
        output_list = []
        print('Starting pack josn dict')
        for i in tqdm.tqdm(range(len(pictDat))):
            item = {'filename': pictDat[i]["name"] }
            figures = []
            for j in range(len(pictDat[i]['height'])):
                figure = dict()
                figure['height'] = pictDat[i]['height'][j]
                figure['label']  = pictDat[i]['label'][j]
                figure['left']   = pictDat[i]['left'][j]
                figure['top']    = pictDat[i]['top'][j]
                figure['width']  = pictDat[i]['width'][j]
                figures.append(figure) # append signle bounding box info
            item['boxes'] = figures # add all bounding box info for one image
            output_list.append(item) # add bounding box info and file name for one image
        return output_list   
    
    
""" Parse data and dump it to json """        
dsf = DigitStructFile("digitStruct.mat")
dataset = dsf.getAllDigit_ByDigit()
output = open('output.txt','w')
output.write(json.JSONEncoder(indent=True).encode(dataset))
output.close()
 
        
        
    
        
