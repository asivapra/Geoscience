#!/bin/env python
import sys
import os.path
from datacube import Datacube
from subprocess import Popen, PIPE
import numpy
import re
help_displayed = 0
def print_help():
	print("****************************************************************\nUsage: /g/data/u46/users/sa9525/avs/WOfS/check_integrity.py DatasetDir Product Logfile\n")
	print("Available Dirs:\n /g/data/u46/wofs/confidence_albers/modis/tiles\n /g/data/u46/wofs/confidence_albers/MrVBF/tiles\n /g/data/u46/wofs/confidence_albers/urbanAreas/tiles\n")
	print("Available Products: modis_nc, mrvbf_nc, urban_areas_nc\n")
	print("Default Logfile = dataset_integrity_check.txt\n****************************************************************\n")
	
# Input file is the list of all datasets. It is mandatory.
try:
	path = sys.argv[1]
	print("path: ",path)
	match = re.match( r'(--help)', path, re.M|re.I)
	if(match):
		print_help()
		help_displayed = 1		
		sys.exit()
	match = re.match( r'(/$)', path, re.M|re.I)
	if(match): pass
	else:
		path += "/"
except:
	if(not help_displayed):
		print("Calling Help")
		print_help()		
	sys.exit()
try:
	product = sys.argv[2]
except:
	product = 'urban_areas_nc'

try:
	log_file = sys.argv[3]
except:
	log_file = 'dataset_integrity_check.txt'

filecontents = os.listdir(path)
n_files = len(filecontents)
# Log File is where the outputs are written. It is not mandatory, but will be created based on input file name
# Log file will be created in the CWD unless specific path is given
# Show the input and log file names
print("Input file: {}; No. of files: {}; Output file: {}".format(path,n_files,log_file))

dc = Datacube(env="confidence")

# Using a Perl script to parse the dataset file. Must convert this to a Python code later.
def get_query(ncfile):
	process = Popen(["./get_lat_lon.pl", ncfile, "remote"], stdout=PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()
	print(output)
	return output

# Read each dataset file and check the data
def check_data(dataset,j):
	ncfile = path + dataset
#	print(j,ncfile)
	size = os.path.getsize(ncfile) / (1024*1024.0)
	size = "%.2f" % size
	coordinates = get_query(ncfile)
	coord = coordinates.split()
	lat_min = coord[0].decode("utf-8")
	lat_max = coord[1].decode("utf-8")
	lon_min = coord[2].decode("utf-8")
	lon_max = coord[3].decode("utf-8")
	query = {
		'lat':(lat_min, lat_max),
		'lon':(lon_min, lon_max),
		'crs': ('EPSG:4326')
	}
	line =''
#	ds = dc.load(product='mrvbf_nc', group_by='solar_day', **query)
#	ds = dc.load(product='mrvbf_nc', group_by='solar_day', **query)
		
# The whole array must be checked. If any value is more than 255 it is a valid dataset
	try:
		print(product)
		ds = dc.load(product=product, group_by='solar_day', **query)
		if(not numpy.all(ds.band1.values == 255)):
			line = "{}. {} : Dataset has valid data. size: {}M\n".format(j, ncfile, size)
			g = open(log_file, "a")	
			g.writelines(line)
			g.close()
			line = line.replace("\n", "")
			print (line)
		else:
			line ="{}. {} : Dataset is *** Empty ***. size: {}M\n".format(j, ncfile, size) 
			g = open(log_file, "a")	
			g.writelines(line)
			g.close()
			line = line.replace("\n", "")
			print (line)
	except:
		line ="{}. {} : *** ERROR ****: Dataset has no band1. size: {}M\n".format(j, ncfile, size) 
		g = open(log_file, "a")	
		g.writelines(line)
		g.close()
		line = line.replace("\n", "")
		print (line)
		

# Remove the existing logfile of the same name.
# Open,append and close so that Ctrl_C will not leave it empty
try:
    os.remove(log_file)
except OSError:
    pass
j = 0
for dataset in filecontents:
	j += 1
	dataset = dataset.replace("\n", "")
	check_data(dataset, j)
	if(j > 4): sys.exit()
#__END__