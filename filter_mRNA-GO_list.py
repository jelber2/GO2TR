#! /usr/bin/env python

###############################################################################
#
# "filter_mRNA-GO_list.py" Python script for GO2TR
# created by Jean P. Elbers
# jean.elbers@gmail.com
# last edited 2 August 2014
#
###############################################################################
#
# Program steps:
# -------------
# 1.Input is mRNA-GO.list.txt in the format:
#   mRNAaccessionIdentifier	GO:#######
#
# 2.Reads through each line and makes a list of lists called rawdatalist with
#   the elements being each line, which is a list of subelements being the
#   mRNA accession identifiers (hereafter mRNAids) and the Gene Ontology
#   identifiers (hereafter GOids)
#
# 3.Creates a dictionary called datadict and reads through each element of
#   rawdatalist and makes each list element into dictionary entries of datadict
#   with mRNAid as the key with its associated GOids as the value(s).
#   NOTE: There may be >1 value for each key, which is made possible by
#         importing defaultdict from the collections module
#
# 4.Reads through the file GOid.list.txt in the format:
#   GO:#######
#   GO:#######
#   and saves GOids to a list called inputlist
#
# 5.Dumps the values (i.e., GOids) for each dictionary key in datadict one at
#   a time into a set, then determines if GOid value in datadict occurs in
#   inputlist
#
# 6.If there are no GOids associated with the key (i.e., mRNAid) in inputlist,
#   then the program appends the mRNAid to the list not_retained_mRNA_list,
#   otherwise the program appends only the key with an associated matching
#   value to list retained_mRNA_list.
#
# 7.Outputs not_retained_mRNA_list and retained_mRNA_list in the same directory
#   as the input using the names not_retained_mRNA_list.txt and
#   retained_mRNA_list.txt in the format:
#   mRNAaccessionIdentifier
#   mRNAaccessionIdentifier
#
###############################################################################

# creates rawdatalist and opens InFile
rawdatalist = []
InFile = open('mRNA-GO.list.txt', 'r')

# reads through each line in the file one by one and splits each
# line into a list of two elements, the first
# (i.e., the accession number), and the second
# (i.e., the Gene ontology ID)
for line in InFile:
	if len(rawdatalist) < 1:
		x = line.strip("\n").split("\t")
		rawdatalist.append(x)
	# if there is already an element added to the list (i.e., the
	# first line of the text file), then add the next line to the list
	else:
		y = line.strip("\n").split("\t")
		rawdatalist.append(y)
InFile.close()

# imports defaultdict from module collections in order to have a dictionary
# of "lists"
from collections import defaultdict

# read through each element of the list (note: each element is actually
# a two item list the first being the accession number and the second being
# the GO ID) and make each list element a dictionary entry with the
# accession number as the key with its associated GO ID as a value
# NOTE: The defaultdict option allows for multiple values (i.e., GO IDs)
# to be associated with each key (i.e., accession numbers)
datadict = defaultdict(list)
for accession, GoID in rawdatalist:
	datadict[accession].append(GoID)
	
# creates an input called "f" from GOid.list.txt in the format:
# GO:#######
# GO:#######
# also creates inputlist
f = open('GOid.list.txt', 'r')
inputlist = []

# reads through each line in the input file one by one and stores each
# line (i.e., gene ontology id) in inputlist
for line in f:
	x = line.strip('\n')
	inputlist.append(x)
f.close()

# dumps the values for each dictionary key into a set and look for
# commonalities between the values and all 
# GO IDs (i.e., input list below)
# If there is a match, then save the accession number to a new list.

# creates empty lists and creates outfiles
retained_mRNA_list = []
not_retained_mRNA_list = []
OutFileName1 = 'not_retained_mRNA_list.txt'
OutFile1 = open(OutFileName1, 'w')
OutFileName2 = 'retained_mRNA_list.txt'
OutFile2 = open(OutFileName2, 'w')

# for each dictionary key, returns associated values and looks
# for commonalities between values and datadict of gene ontology ids
for key in datadict:
	
	# have to convert values associated with a specific key to a set
	a = set(datadict.get(key))
	
	# looks for common element to set a and inputlist
	c = a.intersection(inputlist)
	
	# if there are no elements common to sets a and inputlist, then append
	# the accession (the key associated with the values) to the
	# not_retained_mRNA_list, otherwise append key with an associated matching
	# value to retained_mRNA_list
	if len(c) == 0:
		not_retained_mRNA_list.append(key)
		OutFile1.write(key)
		OutFile1.write('\n')
	else:
		retained_mRNA_list.append(key)
		OutFile2.write(key)
		OutFile2.write('\n')
OutFile1.close()
OutFile2.close()