# MISTReSS: MLVA In Silico Typing Resource for Salmonella Strains

**Licence:      GNU General Public License v3.0 (copy provided in directory)**<br />
# Author:       Tom van Wijk - RIVM Bilthoven<br />
# Contact:      tom_van_wijk@hotmail.com / tom.van.wijk@rivm.nl<br />

### DESCRIPTION

Determines the Multi loci VNTR (Variable Number Tandem Repeat) Analysis
type of a given Salmonella Enteritidis genome assembly

### REQUIREMENTS

-	Linux operating system. This script is developed on Linux Ubuntu 16.04<br />
	**WARNING: Experiences when using different operating systems may vary.**
-	python 2.7.x
-	python libraries as listed in the import section of mistress.py
-	ncbi BLAST 2.6.0+

### INSTALLATION

-	clone the MISTReSS repository to the desired location on your system:<br />
	`git clone https://github.com/Papos92/MISTReSS.git`
-	Add the location of the MISTReSS repository to you path variable:<br />
	`export PATH=$PATH:/path/to/MISTReSS`<br />
	(it is recommended to add this command to your ~/.bashrc file)
-	Create path variable MISTRESS_REF to the reference subdirectory:<br />
	`export MISTRESS_REF=/path/to/MISTReSS/reference_files`<br />
	(it is recommended to add this command to your ~/.bashrc file)

### USAGE

Start the script with the following command:

`mistress.py -i 'inputfile' -s 'pathogen' -o 'outputdir'`

-	**'inputfile':** Location of input file. This should be a fully
	assembled Salmonella Enteritidis or Typhimurium
	genome in .fasta format.

-	**'pathogen':** The serovar of the input strain. Currently, only
	"enteritidis" is supported.<br />
	Default = "enteritidis"

-	**'outputdir':** Location of output directory. If none is specified,
	an output directory will be created in the parent directory of inputfile.
