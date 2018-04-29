#!/usr/bin/env python


# Name:		multi_mistress.py
# Date:		26-03-2018
# Licence:	GNU General Public License v3.0 (copy provided in directory)
# Author:	Tom van Wijk - RIVM Bilthoven
# Contact:	tom_van_wijk@hotmail.com / tom.van.wijk@rivm.nl

############################## DESCRIPTION ##############################

# Script for performing automated MLVA typing on larger datasets using
# MISTReSS

############################## REQUIREMENTS #############################

# - Linux operating system. This script is developed on Linux Ubuntu
#   16.04, experiences when using different operating systems may vary.
# - python 2.7.x
# - python libraries as listed in the import section
# - ncbi BLAST 2.6.0+
# - mistress.py and it's dependencies

############################# INSTALLATION ##############################

# - Add the location of the multi_mistress.py to you path variable:
#   > export PATH=$PATH:/path/to/multi_mistress.py
#   (it is recommended to add this command to your ~/.bashrc file

################################# USAGE #################################

# Start the script with the following command:
# > multi_mistress.py -i <inputdir> -o <outputdir>

# inputfile:		location of input directory. Should contain
#			assembled entiritidis genomes in .fasta/.fsa/.fna/.fa format.

# pathogen:		The pathogen of the input strain. Currently, only
#			"enteritidis" is supported.
#			Default = "enteritidis"

# outputdir:		location of output directory. If none is specified,
#			an output directory will be created in the input
#			directory.


# import python libraries
from argparse import ArgumentParser
from xml.dom import minidom
import logging
import logging.handlers
import os
import sys
import random


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args, log):
	log.info("Parsing command line arguments...")
	parser = ArgumentParser(prog="multi_mistress.py")
	parser.add_argument("-i", "--indir", dest = "input_dir",
		action = "store", default = None, type = str,
		help = "Location of input directory (required)",
		required = True)
	parser.add_argument("-s", "--pathogen", dest = "pathogen",
		action = "store", default = 'enteritidis', type = str,
		help = """pathogen of genome: 'enteritidis'.
			(default='enteritidis')""")
	parser.add_argument("-o", "--outdir", dest = "output_dir",
		action = "store", default = 'inputdir', type = str,
		help = "Location of output directory (default=inputfile)")
	#TODO: add max cpu thread parameter for BLAST
	return parser.parse_args()


# Function to check if the given pathogen value is valid
# (present in 'reference_files/supported pathogens.xml')
# Input: pathogen (string)
# Output: status of validation: 'valid'/'invalid' (string)
def validate_pathogen(pat_input, log):
	log.info("\nChecking if given pathogen is valid...")
	status = "invalid"
	# getting list of valid pathogens from 'supported_pathogens.xml'
	xmlfile = minidom.parse("%s/supported_pathogens.xml" % (os.environ['MISTRESS_REF']))
	pathogens = xmlfile.getElementsByTagName("Pathogen")
	for pathogen in pathogens:
		if pathogen.getAttribute("Name") == pat_input:
			status = "valid"
	return(status)


# Function creates logger with handlers for both logfile and console output
# Returns logger
def create_logger(logid):
	# create logger
	log = logging.getLogger()
	log.setLevel(logging.INFO)
	# create file handler
	fh = logging.FileHandler(str(logid)+'_multi_mistress.log')
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(fh)
	# create console handler
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	ch.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(ch)
	return log


# Function creates a list of files or directories in <inputdir>
# on the specified directory depth
def list_directory(input_dir, obj_type, depth):
	dir_depth = 1
	for root, dirs, files in os.walk(input_dir):
		if dir_depth == depth:
			if obj_type ==  'files':
				return files
			elif obj_type == 'dirs':
				return dirs
		dir_depth += 1


# Function parses outputfile of mistress.py and extracts mlva type
# Input: filepath to logfile
# output: mlva type as string
def parse_logfile(filepath):
	mlva = "NA"
	c = 1
	with open(filepath,  "r") as outfile:
		for line in outfile:
			if c == 1:
				mlva = line.replace("\n", "").replace("\r", "")
			c += 1
	outfile.close()
	return mlva


# Function closes logger handlers
def close_logger(log):
	for handler in log.handlers:
		handler.close()
		log.removeFilter(handler)


# MAIN function
def main():
	# create logger
	logid = random.randint(99999, 9999999)
	log = create_logger(logid)
	# parse command line arguments
	args = parse_arguments(sys.argv, log)
	# TODO: add function to validate input, parameters etc.
	# creating output directory
	if args.output_dir == 'inputdir':
		outdir = os.path.abspath(args.input_dir)+"/multi_mistress_output"
	else:
		outdir = os.path.abspath(args.output_dir)
	log.info("Creating output directory: "+outdir)
	os.system("mkdir "+outdir)
	# check if pathogen is valid
	if validate_pathogen(args.pathogen, log) != "valid":
		log.error("ERROR:\tInvalid pathogen: '"+args.pathogen+"', exiting mulyi_mistress.py")
		os.system("mv "+str(logid)+"_multi_mistress.log "+outdir+"/multi_mistress.log")
		sys.exit()
	else:
		log.info("pathogen supported, continueing multi mistress...\n")
	# Iterate over files and run mistress
	with open(outdir+"/multi_mistress_output.txt",  "w") as outfile:
		outfile.write("File:\tMLVA-type:")
		# iterating over .fasta/.fsa/.fna/.fa files in input directory:
		for file in list_directory(args.input_dir, 'files', 1):
			if file.endswith(".fasta") or file.endswith(".fsa") or file.endswith(".fna") or file.endswith(".fa"):
                                in_path = os.path.abspath(args.input_dir)+"/"+file
                                out_path = os.path.abspath(outdir)+"/"+file.replace(".fasta", "").replace(".fna", "").replace(".fsa", "").replace(".fa", "")+"_mistress_output"
				# run the mistress.py
				log.info("\nstarting mistress for file:\n"+in_path)
				os.system("mistress.py -i "+in_path+" -o "+out_path+" -s "+args.pathogen)
				# get the MLVA type from the mistress output file and write to output file
				mlva = parse_logfile(out_path+"/mistress_output.txt")
				outfile.write("\n"+file+"\t"+mlva)
				# move mistress_output dir to multi_mistress_output/
	outfile.close()
	# close logger handlers
	log.info("\nClosing logger and finalising multi_mistress.py")
	close_logger(log)
	# move logfile and outputfile to output directory
	os.system("mv "+str(logid)+"_multi_mistress.log "+outdir+"/multi_mistress.log")


main()
