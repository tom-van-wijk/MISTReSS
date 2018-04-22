#!/usr/bin/env python


# Name:		mistress.py
# Date:		08-02-2018
# Licence:	GNU General Public License v3.0 (copy provided in directory)
# Author:	Tom van Wijk - RIVM Bilthoven
# Contact:	tom_van_wijk@hotmail.com / tom.van.wijk@rivm.nl

############################## DESCRIPTION ##############################

# MISTReSS: MLVA In Silico Typing Resource for Salmonella Strains.
# Determines the Multi loci VNTR (Variable Number Tandem Repeat) type
# of a given Salmonella Enteritidis genome.

############################## REQUIREMENTS #############################

# - Linux operating system. This script is developed on Linux Ubuntu
#   16.04, experiences when using different operating systems may vary.
# - python 2.7.x
# - python libraries as listed in the import section
# - ncbi BLAST 2.6.0+

############################# INSTALLATION ##############################

# - clone the MISTReSS repository to the desired location on your system:
#   > git clone https://github.com/Papos92/MISTReSS.git
# - Add the location of the MISTReSS repository to you path variable:
#   > export PATH=$PATH:/path/to/MISTReSS
#   (it is recommended to add this command to your ~/.bashrc file
# - Create path variable MISTRESS_REF to the reference subdirectory:
#   > export MISTRESS_REF=/path/to/MISTReSS/reference_files
#   (it is recommended to add this command to your ~/.bashrc file

################################# USAGE #################################

# Start the script with the following command:
# > mistress.py -i <inputfile> -s <pathogen> -o <outputdir>

# inputdir:		location of input file. This should be a fully
#			assembled Salmonella Enteritidis genome.
#			genome in .fasta/.fsa/.fna/.fa format.

# pathogen:		The pathogen of the input strain. Currently, only
#			"enteritidis" is supported.
#			Default = "enteritidis"

# outputdir:		location of output directory. If none is specified,
#			an output directory will be created in the directory
#			containing the inputfile.


# import python libraries
from argparse import ArgumentParser
from xml.dom import minidom
import logging
import logging.handlers
import os
import sys
import subprocess
import re
import random

# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args, log):
	log.info("Parsing command line arguments...")
	parser = ArgumentParser(prog="mistress.py")
	parser.add_argument("-i", "--infile", dest = "input_file",
		action = "store", default = None, type = str,
		help = "Location of input .fasta/.fsa/.fna/.fa file (required)",
		required = True)
	parser.add_argument("-s", "--pathogen", dest = "pathogen",
		action = "store", default = 'enteritidis', type = str,
		help = """pathogen of genome: 'enteritidis'.
			(default='enteritidis')""")
	parser.add_argument("-o", "--outdir", dest = "output_dir",
		action = "store", default = 'inputfile', type = str,
		help = "Location of output directory (default=inputfile)")
	#TODO: add max cpu thread parameter for BLAST
	return parser.parse_args()


# Function creates logger with handlers for both logfile and console output
# Returns logger
def create_logger(logid):
	# create logger
	log = logging.getLogger()
	log.setLevel(logging.INFO)
	# create file handler
	fh = logging.FileHandler(str(logid)+'_mistress.log')
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(fh)
	# create console handler
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	ch.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(ch)
	return log


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


# Function that parses the blastn results
# Input: blastn results file, primer reference file, blastdb, logger
# Output: vntr profile
def parse_blastn_output(blast_results_file, reference_file, blastdb, pathogen, log):
	# create a dictionary blast_results of the results in the blast results file
	blast_results = {}
	with open(blast_results_file,  "r") as file:
		for line in file:
			blast_results[line.split("\t")[0]]=str(line)
	file.close
	# iterate over reference file to extract most extreme primer loci boundaries,
	# Is both primer loci available and on the same contig: extract sequence using blast
	vntr_numbers = []
	current_repeat = "NA"
	with open(reference_file,  "r") as infile:
		for line in infile:
			if line.startswith(">") and line.replace("\n", "").replace("\r", "").endswith("_P1"):
				vntr = line.replace(">", "").replace("_P1", "").replace("\n", "").replace("\r", "")
				log.info("Processing VNTR: "+vntr+"...")
				if vntr+"_P1" in blast_results.keys() and vntr+"_P2" in blast_results.keys():
					p1_contig = blast_results.get(vntr+"_P1").split("\t")[1]
					p1_locus1 = int(float(blast_results.get(vntr+"_P1").split("\t")[8]))
					p1_locus2 = int(float(blast_results.get(vntr+"_P1").split("\t")[9]))
					p2_contig = blast_results.get(vntr+"_P2").split("\t")[1]
					p2_locus1 = int(float(blast_results.get(vntr+"_P2").split("\t")[8]))
					p2_locus2 = int(float(blast_results.get(vntr+"_P2").split("\t")[9]))
					if p1_contig == p2_contig:
						low_pos = min([p1_locus1, p1_locus2, p2_locus1, p2_locus2])
						high_pos = max([p1_locus1, p1_locus2, p2_locus1, p2_locus2])
						log.info("'%s' found on: '%s': %s-%s"
							% (vntr, p1_contig, low_pos, high_pos))
						vntr_size = high_pos-low_pos+1
						# Function to determine length based vntr number
						vntr_no = determine_length_vntr_number(vntr, vntr_size, pathogen, log)
						vntr_numbers.append(str(vntr_no))
						pcr_sequence = (subprocess.check_output(("blastdbcmd -db %s -range %s-%s -entry %s"
							% (blastdb, low_pos, high_pos, p1_contig)), shell=True))
						log.info("vntr size: %s, vntr number: %s\n%s"
							% (str(vntr_size), str(vntr_no), pcr_sequence))
					else:
						log.warning("""primers of VNTR: %s where not found on the same contig.\nprimer 1 found on contig: %s.\nprimer 2 found on contig: %s\n"""
							% (vntr, p1_contig, p2_contig))
						vntr_numbers.append("NA")
				else:
					log.warning("VNTR: "+vntr+" not found in sequence.\n")
					vntr_numbers.append("NA")
	infile.close()
	return vntr_numbers


# Function to determine the vntr number based on sequence size
# Input: vntr name, vntr sequence size, pathogen, logger
# Output: vntr number bij sequence size
def determine_length_vntr_number(vntr_name, vntr_seqsize, pathogen, log):
	xmlfile = minidom.parse("%s/panel_%s.xml" % (os.environ['MISTRESS_REF'], pathogen))
	loci = xmlfile.getElementsByTagName("Vntr")
	for locus in loci:
		locusname = locus.getAttribute('Name')
		if locusname == vntr_name:
			alleles = locus.getElementsByTagName("Bin")
			for allele in alleles:
				number = allele.getAttribute('Value')
				start = allele.getAttribute('Start')
				stop = allele.getAttribute('Stop')
				if float(start) <= vntr_seqsize <= float(stop):
					return number
	return('NA')


# MAIN function
def main():
	# create logger
	logid = random.randint(99999, 9999999)
	log = create_logger(logid)
	# parse command line arguments
	args = parse_arguments(sys.argv, log)
	# creating output directory
	if args.output_dir == 'inputfile':
		outdir = os.path.abspath(args.input_file).replace(".fasta", "").replace(".fna", "").replace(".fsa", "").replace(".fa", "")+"_mistress_output"
	else:
		outdir = os.path.abspath(args.output_dir)
	log.info("output directory: "+outdir)
	os.system("mkdir -p "+outdir+"/blastdb")
	# check if pathogen is valid
	if validate_pathogen(args.pathogen, log) != "valid":
		log.error("ERROR:\tInvalid pathogen: '"+args.pathogen+"', exiting mistress.py")
		os.system("mv "+str(logid)+"_mistress.log "+outdir+"/mistress.log")
		sys.exit()
	else:
		log.info("pathogen supported, continueing mistress...\n")
	# create a blast db of the query genome
	log.info("creating a blast db of the query genome: "+args.input_file+"...")
	log.info(subprocess.check_output("makeblastdb -in %s -parse_seqids -dbtype nucl -out %s"
		% (args.input_file, outdir+"/blastdb/query"), shell=True))
	# map primers to query genome db
	log.info("mapping primers of reference genome: "+"primers_"+args.pathogen.lower()+".fsa...\n")
	os.system("blastn -db %s -query %s -task 'blastn-short' -perc_identity 80 -outfmt 6 -num_threads 8 -qcov_hsp_perc 80 | sort -u -k1,1 --merge > %s"
		% (outdir+"/blastdb/query", os.environ['MISTRESS_REF']+"/primers_"+args.pathogen.lower()+".fsa", outdir+"/blastn_results.txt"))
	# parse blastn output and retrieve vntr numbers
	vntr_numbers = parse_blastn_output(outdir+"/blastn_results.txt",
		os.environ['MISTRESS_REF']+"/primers_"+args.pathogen.lower()+".fsa", outdir+"/blastdb/query", args.pathogen, log)
	log.info("MLVA profile: "+str(vntr_numbers).replace("[","").replace("]","").replace(", ","-").replace("'",""))
	# mlva-patterns to output file
	with open(outdir+"/mistress_output.txt", "w") as outfile:
		outfile.write(str(vntr_numbers).replace("[","").replace("]","").replace(", ","-").replace("'",""))
	outfile.close()
	os.system("mv "+str(logid)+"_mistress.log "+outdir+"/mistress.log")


main()
