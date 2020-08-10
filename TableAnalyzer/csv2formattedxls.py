#!/usr/bin/python2
import pandas as pd
import xlsxwriter
import csv
import sys
from openpyxl import Workbook
file = sys.argv[1]

# Create a Pandas dataframe from some data.
df = pd.read_csv(file)

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(sys.argv[2], engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='cfstats', index=False)

# Get the xlsxwriter workbook and worksheet objects.
workbook = writer.book
worksheet = writer.sheets['cfstats']

# Row count of csv file so that cell range can be dynamically populated below
row_count = len(open(file).readlines())

# Set the column width and format.
worksheet.set_column('C:T', 12)

# Set autofilter
worksheet.autofilter('C1:T11')

# Hide columns A, E, F
worksheet.set_column('A:A', None, None, {'hidden': 1})
#worksheet.set_column('E:E', None, None, {'hidden': 1})
#worksheet.set_column('F:F', None, None, {'hidden': 1})

# Apply a conditional format to the cell range.

# Read / Write
worksheet.conditional_format('E2:E{0}'.format(row_count), {'type': 'data_bar'})
worksheet.conditional_format('F2:F{0}'.format(row_count), {'type': 'data_bar'})

# Space used 
worksheet.conditional_format('G2:G{0}'.format(row_count), {'type': 'data_bar'})
worksheet.conditional_format('H2:H{0}'.format(row_count), {'type': 'data_bar'})

#Offheapmemoryusedtotal of V #3
worksheet.conditional_format('I2:I{0}'.format(row_count), {'type': 'data_bar'})

# Partition Sizes
worksheet.conditional_format('K2:K{0}'.format(row_count), {'type': '2_color_scale', 'min_color': '#FFFFFF', 'min_value': 0, 'max_color': 'red'})
worksheet.conditional_format('R2:R{0}'.format(row_count), {'type': '2_color_scale', 'min_color': '#FFFFFF', 'min_value': 0, 'max_color': 'red'})

# Numberofpartitionsestimate	
# Memtablecellcount	
worksheet.conditional_format('L2:L{0}'.format(row_count), {'type': '2_color_scale', 'min_color': '#FFFFFF', 'min_value': 0, 'max_color': 'red'})
# Memtabledatasize	
worksheet.conditional_format('M2:M{0}'.format(row_count), {'type': '3_color_scale', 'min_color': 'green', 'min_value': 0, 'max_color': 'red'})
# Memtableoffheapmemoryused
worksheet.conditional_format('N2:N{0}'.format(row_count), {'type': '3_color_scale', 'min_color': 'green', 'min_value': 0, 'max_color': 'red'})
# Memtableswitchcount	
worksheet.conditional_format('O2:O{0}'.format(row_count), {'type': '3_color_scale', 'min_color': 'green', 'min_value': 0, 'max_color': 'red'})
# Localreadcount	
worksheet.conditional_format('P2:P{0}'.format(row_count), {'type': 'data_bar'})
# Localreadlatency	
# Localwritecount	
# Localwritelatency	
# Pendingflushes	
# Percentrepaired	
# Bloomfilterfalsepositives	
# Bloomfilterfalseratio	
# Bloomfilterspaceused	
# Bloomfilteroffheapmemoryused	
# Indexsummaryoffheapmemoryused	
# Compressionmetadataoffheapmemoryused	
# Compactedpartitionminimumbytes	
# Compactedpartitionmaximumbytes	
# Compactedpartitionmeanbytes	
# Averagelivecellsperslicelastfiveminutes	
# Maximumlivecellsperslicelastfiveminutes	
# Averagetombstonesperslicelastfiveminutes	
# Maximumtombstonesperslicelastfiveminutes	
# DroppedMutations
# Close the Pandas Excel writer and output the Excel file.
writer.save()

print ('Success')

# TO DO
# Auto-sort ascending not possible in xlxswriter https://stackoverflow.com/questions/44385706/how-to-sort-a-table-in-xlsxwriter-using-filters-sort-a-to-z

