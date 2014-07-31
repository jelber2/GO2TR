#! /usr/bin/env python

###############################################################################
#
# GO2OME file 7
# "7_filterbedtoolsoutput.py" Python script
# created by Jean P. Elbers
# jean.elbers@gmail.com
# last edited 3 Mar 2014
#
###############################################################################
#
# Program steps:
# -------------
# 1.Input is genome.coords.merged.reformatted.txt in the format:
#   chrom start end strand	mRNAaccessionIdentifier
#   NW_004848299.1 261683 261849 +	XM_005278413.1
#   NW_004848299.1 266496 266605 +	XM_005278413.1
#
# 2.Reads through each line and makes a list of lists called rawlist with
#   the elements being each line, which is a list of subelements being:
#   subelement 0 = chrom start end strand
#   subElement 1 = mRNAaccessionIdentifier
#
# 3.Reads through each element of the rawlist list and makes each list element
#   a dictionary entry in rawdict with the subelement 0 as the key with its
#   associated subelement 1 as a value
#
# 4.All list elements are put into rawlist2, but if a list element contains
#   more than two items (i.e., rawlist[0][2] exists), then the program splits
#   the element until there are only two items per element.
#
# 5.Dumps all values of the dictionary (i.e., mRNAids) into a new list called
#   rawlist2 that is then converted to strings and finally a set called
#   dictvalues
#
# 6.Reads in accessionlistmatch.txt to filter the data by in the format:
#   mRNAaccessionIdentifier
#   mRNAaccessionIdentifier
#   then saves input to the list inputlist
#
# 7.Looks for commonalities between dictvalues and inputlist and stores
#   the commonalities in the set matches
#
# 8.Goes through each dictionary entry and writes the key
#   (i.e., chrom start end) to an output file in the same directory if the
#   associated value is within the set matches in the format:
#   chrom start end strand
#   chrom start end strand
#
###############################################################################

# creates rawlist and InFile
rawlist = []
InFile = open('genome.coords.merged.reformatted.txt', 'r')

# read through each line in the file one by one and split the each
# line into a list of two elements, the first (element 1), and the second
# (element 2)
# if multiple transcription accessions are present in the input
# (ex: NW_004848299.1 432018 432084 +	XM_005294952.1;XM_005278436.1),
# then the ';' is converted to a tab and a third list element is created
for line in InFile:
	if len(rawlist) < 1:
		x = line.strip('\n').replace(';','\t').split('\t')
		rawlist.append(x)
	# if the first line of the input file has already been added to the
	# list (i.e., rawlist[0] exists), then add the next line to the list
	else:
		y = line.strip('\n').replace(';','\t').split('\t')
		rawlist.append(y)
InFile.close()

# if a list element contains more than two items (i.e., rawlist[0][2] exists),
# then split the element until there are only two items
Element = 0
rawlist2 = []
for element in rawlist:
	Subelement = 0
	for subelement in element:
		newsubelement1 = ''
		newsubelement2 = ''
		newelement = ''
		newlist = []
		newsubelement1 = rawlist[Element][0]
		if Subelement + 1 < len(rawlist[Element]):
			Subelement+=1
			newsubelement2 = rawlist[Element][Subelement]
			newelement = newsubelement1 + '\t' + newsubelement2
			newlist = newelement.split('\t')
			rawlist2.append(newlist)
		else:
			if Element + 1 < len(rawlist):
				Element+=1

# imports defaultdict from module collections in order to have
# a dictionary of "lists"
from collections import defaultdict

# read through each element of the list (note: each element is actually
# a two item list the first being chrom start end and the
# second being mRNAaccessionIdentifier) and make each list element a dictionary
# entry with chrom start end as the key with its associated
# mRNAaccessionIdentifier as a value
# NOTE: The defaultdict option allows for the keys and values to be lists
rawdict = defaultdict(list)
for chrom, mRNAaccessionIdentifier in rawlist2:
	rawdict[chrom].append(mRNAaccessionIdentifier)

# makes outfile
OutFileName='GO2OME.coords.txt'
OutFile = open(OutFileName, 'w')

# converts all values (not keys) in rawdict into a set
dictvalues = rawdict.viewvalues()
dictvalues = set(str(rawdict.viewvalues()).replace('[','').replace(']','')\
.replace("'","").replace(';',' ').replace(',','').split())

# opens accessionlistmatch.txt and creates inputlist
f = open('accessionlistmatch.txt', 'r')
inputlist = []

# reads through each line in the input file one by one and stores
# each line in a list
for line in f:
	x = line.strip('\n')
	inputlist.append(x)
f.close()

# searches within dictvalues for matching inputvalues and saves
# result as the set matches
matches = set(inputlist).intersection(dictvalues)

# filters rawdict so that only entries with values that correspond to
# matches are returned but outputs the genomic coordinates (i.e., the keys)
for key, value in rawdict.items():
	if value[0] in matches:
		OutFile.write(key)
		OutFile.write('\n')
OutFile.close()