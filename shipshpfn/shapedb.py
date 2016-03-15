#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
shapedb.py
'''

try:
    import sqlite3
except ImportError:
    print "Unable to load module sqlite3"
    raise

from struct import unpack as struct_unpack


class DbReader():
    '''\
       Sqlite db reader.
    '''
    def __init__(self, shpdbfile):
        try:
            self.connection = sqlite3.connect(shpdbfile)
        except:
            print "Unable to connect to sqlite database"
            raise
        
        self.cursor = self.connection.cursor()
        self.tables = self.get_tables()
        #~ self.tables_no = len(self.tables)
        
    def check_ogr_format(self):
        try:
            query = "select f_table_name from geometry_columns;"
            table = self.select(query)[0][0]
        except:
            return False
            
        return True

    def get_tables(self):
        query = "select name from sqlite_master where type='table';"
        tables = self.select(query)
        return tables

    def select(self, query):
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        #~ self.cursor.close()
        #~ self.connection.close()
        return records
    
    def execute(self, query):
    #~ def executescript(self, query):
        self.cursor.execute(query)
        #~ self.cursor.executescript(query)
        self.connection.commit()
        #~ self.cursor.close()

    def insert(self, query):
        self.cursor.execute(query)
        newID = self.cursor.lastrowid
        self.connection.commit()
        #~ self.cursor.close()
        #~ self.connection.close()
    
    def close_db(self):
        #~ self.connection.commit()
        #~ self.cursor.close()
        self.connection.close()


class MultiShapedbReader(DbReader):
    ''''''
    pass


class GpkgReaderReader(MultiShapedbReader):
    ''''''
    pass


class ShapedbReader(DbReader):
    ''''''
    def __init__(self, shpdbfile):
        DbReader.__init__(self, shpdbfile)
        try:
            self.shpdb_name = self.get_table_name(shpdbfile)
        except:
            raise Exception("Can't retrieve valid table")
            
    def get_table_name(self, dbfile):
        query = "select f_table_name from geometry_columns;"
        table = self.select(query)[0][0]
        return table
        
    def get_tables(self):
        query = "select f_table_name from geometry_columns;"
        tables = self.select(query)[0]
        return tables
    
    def get_fields_info(self):
        query = "pragma table_info('%s');" % self.shpdb_name
        metadata = self.select(query)
        #~ [field1:name, field2:type]
        fields = list(field[1] for field in metadata[2:])
        fieldsno = len(fields)
        return fieldsno, fields
        
    def get_fields_description(self):
        query = "pragma table_info('%s');" % self.shpdb_name
        metadata = self.select(query)
        #~ [field1:name, field2:type]
        fields = list((field[1], field[2]) for field in metadata[2:])
        return fields
        
    def get_field_values(self, field_index):
        fields = self.get_fields_info()[1]
        field_name = fields[field_index]
        query = "select %s from %s;" % (field_name, self.shpdb_name)
        data = self.select(query)
        values = list(field[0] for field in data)
        return values
    
    def get_records_no(self):
        query = "select count(OGC_FID) from %s;" % self.shpdb_name
        data = self.select(query)
        return data[0][0]
    
    def get_record(self, row):
        pass

    def get_iter_records(self, from_row, to_row):
        '''\
        Adding 1 to from_row because OGC_FID autoid starts from 1 and
        query includes last row not as range().
        '''
        query = "select * from %s where OGC_FID between %s and %s;" % (self.shpdb_name, from_row + 1, to_row)
        records = self.select(query)
        for record in records:
            yield record[2:]
    
    def get_value(self, row, col):
        pass
        
    #~ def getGeomType(self)
        #~ self.geotype = self.layer.GetGeomType()

    def get_geom_type(self):
        query = "select geometry_type from geometry_columns;"
        geom_type_code = self.select(query)[0][0]
        geom_types = {
                      1:  "Point",
                      2:  "LineString",
                      3:  "Polygon",
                      17: "Triangle",
                      4:  "MultiPoint",
                      5:  "MultiLineString",
                      6:  "MultiPolygon",
                      7:  "GeometryCollection",
                      15: "PolyhedralSurface",
                      16: "TIN",
                      1001: "PointZ",
                      1002: "LineStringZ",
                      1003: "PolygonZ",
                      1017: "Trianglez",
                      1004: "MultiPointZ",
                      1005: "MultiLineStringZ",
                      1006: "MultiPolygonZ",
                      1007: "GeometryCollectionZ",
                      1015: "PolyhedralSurfaceZ",
                      1016: "TINZ",
                      2001: "PointM",
                      2002: "LineStringM",
                      2003: "PolygonM",
                      2017: "TriangleM",
                      2004: "MultiPointM",
                      2005: "MultiLineStringM",
                      2006: "MultiPolygonM",
                      2007: "GeometryCollectionM",
                      2015: "PolyhedralSurfaceM",
                      2016: "TINM",
                      3001: "PointZM",
                      3002: "LineStringZM",
                      3003: "PolygonZM",
                      3017: "TriangleZM",
                      3004: "MultiPointZM",
                      3005: "MultiLineStringZM",
                      3006: "MultiPolygonZM",
                      3007: "GeometryCollectionZM",
                      3015: "PolyhedralSurfaceZM",
                      3016: "TinZM",
                      }
                      
        return geom_type_code, geom_types[geom_type_code]
        
    def get_bounding_box(self):
        '''
        ??? once calculated add to sqlite db?
            (then add here check bbox first)
        '''
        #~ [min(x), min(y), max(x), max(y)]
        xmin, ymin, xmax, ymax = 0, 0, 0, 0
        for geom in self.get_iter_geoms():
            while geom.points:
                point = geom.points.pop()
                x, y = point[0], point[1]
                if x < xmin or xmin == 0:
                    xmin = x
                if x > xmax or xmax == 0:
                    xmax = x
                if y < ymin or ymin == 0:
                    ymin = y
                if y > ymax or ymax == 0:
                    ymax = y
        
        bbox = [xmin, ymin, xmax, ymax]
        return bbox

    def parse_blob_geometry(self, geom):
        endian = struct_unpack('B', geom[:1])[0]
        geotype = struct_unpack('I', geom[1:5])[0]
        #~ type 3 (Polygon WKB) -> 5 (Polygon shp)
        #~ type 6 (MultiPolygon WKB) -> 5 (Polygon shp) -> 
        parts = struct_unpack('I', geom[5:9])[0]

        parts_points = [0]
        points = []

        def list_points(elts, fr, calc_elts=False):
            if calc_elts:
                elts = (len(geom) - fr) // 16
                
            for i in xrange(elts):
                coord1 = struct_unpack('d', geom[fr:fr + 8])[0]
                fr += 8
                coord2 = struct_unpack('d', geom[fr:fr + 8])[0]
                fr += 8
                points.append([coord1, coord2])

        if geotype == 1:
            parts = 0
            list_points(0, 5, True)
        elif geotype == 2:
            parts = 0
            list_points(0, 9, True)

        if parts == 1:
            elts_no = struct_unpack('I', geom[9:13])[0]
            list_points(elts_no, 13)
        elif parts > 1:
            fr = 10
            for i in xrange(parts):
                '''
                1b mark, 4 type, [4 parts],
                4 number of elements (x points) (next part start)
                '''
                part_start = parts_points[-1]
                if geotype == 5:
                    offset = 8
                    frmtstr = '2I'
                else:
                    offset = 12
                    frmtstr = '3I'

                part_def = struct_unpack(frmtstr, geom[fr:fr + offset])
                part_end = part_start + part_def[-1]
                parts_points.append(part_end)
                list_points(part_def[-1], fr + offset)
                fr = fr + part_def[-1] * 16 + offset + 1
                
            parts_points.pop(-1)

        geom_obj = _Geometry(parts_points, points, geotype)
        return geom_obj
        
    #~ def get_geom(self, row):
        #~ pass

    #~ def get_iter_geoms(self, from_row, to_row):
        #~ for row in xrange(from_row, to_row):
            #~ geom = self.get_geom(row)
            #~ yield geom

    def get_iter_geoms(self):
        query = "select f_geometry_column from geometry_columns;"
        geo_col = self.select(query)[0][0]
        query = "select %s from %s;" % (geo_col, self.shpdb_name)
        geoms = self.select(query)
        for geom in geoms:
            geomstr = self.parse_blob_geometry(geom[0])
            yield geomstr
	
    def get_srs(self):
        query = "select srid, srtext from spatial_ref_sys;"
        srs_info = self.select(query)[0]
        return srs_info
    
    def set_field(self):
        pass
            
    def set_value(self, row, col, value):
        pass


class _Geometry():
    ''''''
    def __init__(self, parts, points, geom_type, bbox=None):
        self.parts = parts
        self.points = points
        self.geom_type = geom_type
        self.bbox = bbox
        
        
if __name__ == "__main__":
    pass
