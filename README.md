# MISTReSS: MLVA In Silico Typing Resource for Salmonella Strains

**Licence:      GNU General Public License v3.0 (copy provided in directory)**<br />
Author:       Tom van Wijk - RIVM Bilthoven<br />
Contact:      tom_van_wijk@hotmail.com / tom.van.wijk@rivm.nl<br />

#### DESCRIPTION

Determines the Multi loci VNTR (Variable Number Tandem Repeat) type
of a given Salmonella Enteritidis genome assembly.

#### REQUIREMENTS

-	Linux operating system. This script is developed on Linux Ubuntu 16.04<br />
	**WARNING: Experiences when using different operating systems may vary.**
-	python 2.7.x
-	python libraries as listed in the import section of mistress.py
-	ncbi BLAST 2.6.0+
-	The reference directory supplied with this repository

#### INSTALLATION

-	clone the MISTReSS repository to the desired location on your system:<br />
	`git clone https://github.com/Papos92/MISTReSS.git`
-	Add the location of the MISTReSS repository to you path variable:<br />
	`export PATH=$PATH:/path/to/MISTReSS`<br />
	(it is recommended to add this command to your ~/.bashrc file)
-	Create path variable MISTRESS_REF to the reference subdirectory:<br />
	`export MISTRESS_REF=/path/to/MISTReSS/reference_files`<br />
	(it is recommended to add this command to your ~/.bashrc file)

#### USAGE

Start the script with the following command:

`mistress.py -i 'inputfile' -s 'pathogen' -o 'outputdir'`

-	**'inputfile':** Location of input file. This should be a fully
	assembled Salmonella Enteritidis genome.
	genome in .fasta/.fsa/.fna/.fa format.<br />
	**NOTE:** To correctly determine the number of repeats,
	it is crucial to assemble your genome as accurate as possible.
	We recommend using the methods used in our paper: quality trim the fastq files
	with q=25 using erne-filter v2.1.1 and assemble with SPAdes v 3.10.0.<br/>
	**NOTE:** When a tandem repeat is so long that it is not be covered by a single read,
	the assembly with problably compress the tandem repeat by assembling
	multiple repeats as a single sequence. When using
	illumina 2x150 bp, this will happen when SENTR5 n>13 and SENTR6 n>11. These
	are rare but to also type longer genotypes correctly, we recommend using at least illumina 2x250 bp for Salmonella Enteritidis.

-	**'pathogen':** The serovar of the input strain. Currently, only
	"enteritidis" is supported.<br />
	Default = "enteritidis"

-	**'outputdir':** Location of output directory. If none is specified,
	an output directory will be created in the parent directory of inputfile.

## MULTI MISTReSS

Added in this repository is `multi_mistress.py`.
This script allows for large batches of data to be typed with a single command.
When the installation of mistress is complete, no additional dependencies have to be installed and no additional steps have to be taken,
you are ready to go.<br /><br />
This script will create an output directory with a subdirectory for each genome containing the mistress output.
Additionally `multy_mistress_output.txt` will be created with an overview of all typed genomes.

#### USAGE

Start multi_mistress with the following command:

`multi_mistress.py -i 'inputdir' -o 'outputdir'`

-	**'inputdir':**	location of input directory.<br />
			This should only contain fully assembled genomes in .fasta/.fsa/.fna/.fa format.

-	**'outputdir':**	location of output directory.<br />
			If none is specified, an output directory will be created in input directory.

## ADDING YOUR OWN PATHOGENS

You can easily add your own pathogens to this tool by doing to following:<br />
-	Add a new 'Pathogen' element for the pathogen you want to add to `reference_files/supported_pathogens.xml`<br />
-	Add a `reference_files/panel_'your_pathogen_name'.xml` file with the VNTR sizes for your pathogen.<br />
	'**your_pathogen_name**' in this file's filename, the `Serovar` attribute of the `Vntrs` element
	in this file and the 'Name' element of the added 'Pathogen' element in `reference_files/supported_pathogens.xml`
	all need to be indentical.<br />
	This file is required to be in the same format as the supplied panel file(s), including identical
	element and attribute names.<br />
-	Add a `reference_files/primers_'your_pathogen_name'.fsa` file with the primers that are used
	for your pathogen in the lab method<br />
	**'your_pathogen_name'** once again needs to be	need to be indentical.<br />
	This file needs to be in the same format as the supplied primer file(s).
	The primers in this file are named with an `_P1` and `_P2` flag for forward and
	reverse primers respectively. The headers of the primer sequences (without the `_P1` and `_P2` flags
	need to be identical to the element `vntr`'s `Name` attribute value in `reference_files/panel_'your_pathogen_name'.xml`<br />
-	Now you can run mistress or multi_mistress with using the **-s** flag.
	Use the value for this variable identical to your pathogens name
	in the panel and primer files.<br .><br />
	
**NOTE:** Please keep in mind that the VNTR sizes used in the classical methods might be biased.<br />
Also keep in mind that when the size of the total VNTR comes close or exceeds the read size of the
sequencing technology used, the VNTR is unlikely to have been assembled correctly.<br />
Testing with a set of traditionally typed samples is highly recommended.<br /><br />
	
	
