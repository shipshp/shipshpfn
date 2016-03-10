#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
shape.py
Shapefile Managing using pyshp
'''

import pyshp


class ShapeReader():
    ''''''
    def __init__(self, shapefile):
        try:
            reader = pyshp.Reader(shapefile)
        except:
            print "Unable to read shapefile"
            '''
            ???: in case shx damage: delete or rename .shx file
                 shp and dbf could be readed.
            '''
            raise

        self.reader = reader

    def get_shape_data(self):
        '''
        Gets information string of fields and features of the
        shapefile.
        '''
        fieldsno = self.get_fields_no
        featsno = self.get_records_no
        self.shpinfo = ' %s fields, %s features' % (fieldsno, featsno)
        return self.shpinfo
    
    def get_fields_no(self):
        return len(self.reader.fields) - 1
    
    def get_fields(self):
        return self.reader.fields
        
    def get_field_names(self):
        #~ field_names = []
        #~ fields_def = self.reader.fields[1:]
        #~ for field in fields_def:
            #~ field_names.append(field[0])
        #~ return field_names
        
        #~ ???: map instead expresion:
        return list(field[0] for field in self.reader.fields[1:])

    def get_field_values(self, field_index):
        feats_no = self.get_records_no()
        values = []
        for record in self.get_iter_records(0, feats_no):
            values.append(record[field_index])
            
        return values
        
    def get_records_no(self):
        return self.reader.numRecords
        
    def get_record(self, row):
        return self.reader.record(row)

    def get_iter_records(self, from_row, to_row):
        for row in xrange(from_row, to_row):
            record = self.get_record(row)
            yield record
    
    def get_value(self, row, col):
        feature = self.reader.record(row)
        value = feature[col]
        return value

        #~ if value is not None:
            #~ return value
        #~ else:
            #~ return 'Null'  

    def get_geom_type(self):
        shape_type_code = self.reader.shapeType
        shape_types = {0: "Null", 1: "Point", 3: "Polyline", 5: "Polygon",
                       8: "Multipoint", 11: "Point Z", 13: "Polyline Z",
                       15: "Polygon Z", 18: "Multipoint Z", 21: "Point M",
                       23: "Polyline M", 25: "Polygon M", 28: "Multipoint M",
                       31: "Multipatch"}

        return shape_type_code, shape_types[shape_type_code]
            
    def get_bounding_box(self):
        #~ [min(x), min(y), max(x), max(y)]
        return self.reader.bbox

    def get_iter_geoms(self):
        for geom in self.reader.iterShapes():
            yield geom
            
#~ ---------------------------------------------------------------
    #~ def getGeomType(self)
        #~ self.geotype = self.layer.GetGeomType()
	
    #~ def getSRef(self,itemdata):
        #~ self.setShapeDS(itemdata)
        #~ sr = self.layer.GetSpatialRef()
        #~ self.srinfo = sr
#~ ---------------------------------------------------------------


class ShapeEditor():
    ''''''
    def set_field(self):
        pass
            
    def set_value(self, row, col, value):
        #~ self.data[(row, col)] = value
        pass


if __name__ == "__main__":
    pass
