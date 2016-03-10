#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
tables.py
'''

import csv


class CSVReader():
    '''\
       Csv format table reader.
    '''
    def __init__(self, csvfilename):
        csvfile = open(csvfilename)
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        if dialect:
            csvdata = csv.reader(csvfile, dialect)
        else:
            csvdata = csv.reader(csvfile)
            
        header = csv.Sniffer().has_header(csvfile.read(1024))
        csvfile.seek(0)
        
        headerfile = csvdata.next()
        if not header:
            csvfile.seek(0)

        self.csvfile = csvfile
        self.dialect = dialect
        self.header = header
        self.fields = headerfile
        self.csvdata = csvdata
        
    def get_delimiter(self):
        delimiter = self.dialect.delimiter
        return delimiter
    
    def get_fields_no(self):
        fieldsno = len(self.fields)
        return fieldsno
        
    def get_field_names(self):
        #~ fields = ['uno', 'dos', 'tres', 'cuatro']
        fields = self.fields
        return fields
        
    def get_fields_description(self):
        pass
        
    def get_records_no(self):
        csvobj = self.csvdata
        
        rows_no = 0
        while True:
            try:
                csvobj.next()
                rows_no += 1
            except StopIteration:
                break
        
        self.csvfile.seek(0)
        
        self.records_no = rows_no 
        return rows_no
        
    def get_iter_records(self, from_row, to_row):
        csvobj = self.csvdata
        row_range = to_row - from_row

        if self.header:
            csvobj.next()

        '''
        FIX: search by block? 1024 * n ?? -> not iteration-next
        (see dialect)
        record_size = ??
            bsize - header(1024?) / records_no
        from_pos = n * record_size
        csvfile.seek(from_pos)
        '''
        row_idx = 0
        while row_idx < from_row:
            try:
                csvobj.next()
            except StopIteration:
                break

            row_idx += 1
        
        records = []
        for i in range(row_range):
            try:
                row = csvobj.next()
                records.append(row)
            except StopIteration:
                break

        self.csvfile.seek(0)

        for record in records:
            yield record


if __name__ == "__main__":
    pass
