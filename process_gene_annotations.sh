#! /bin/bash

###############################################################################
#
# "process_gene_annotations.sh" bash script for GO2TR
# created by Jean P. Elbers
# jean.elbers@gmail.com
# last edited 10 November 2014
#
###############################################################################
# What the script does:

#     >Keeps only mRNA exons, how it works:
#          i.Extracts compressed genome.gff3.gz file using gunzip
#         ii.Keeps only rows with "Gnomon", "exon", and "XM_" using grep
#        iii.Uses perl to modify the GFF3 file to put mRNA transcript accession number in 3rd column
#         iv.Uses sort for proper input to Bedtools, and saves file as genome.modified.gff3
#        Terminal command for i-iv:
            gunzip -c genome.gff3.gz | grep "Gnomon" | grep "exon" | grep "XM_" | perl -pe 's/(\w+_.+)\t(Gnomon)\texon\t(\d+)\t(\d+)\t(.)\t(.)\t(.)\t(.+)(XM_\d+)\.\d(.+)\n/$1\t$2\t$9\t$3\t$4\t$5\t$6\t$7\t$8$9$10\n/' | sort -k 1,1 -k4,4n > genome.modified.gff3
            echo ""
            echo "Done extracting genome.gff3.gz and sorting for input to bedtools"

#     >Merge overlapping exons with Bedtools
#        Terminal command if Bedtools was installed in /Users/your_username/GO2TR
#        and your current working directory is GO2TR:
            ./bedtools/bin/bedtools merge -i genome.modified.gff3 -s -c 3,7 -o distinct -delim ";" > genome.coords.merged.bed
            echo "Done with bedtools merge"

#     >Makes the provisional_exome, how it works:
#          i.Uses awk to change from 0-based to 1-based coordinates
#         ii.Use Perl to reformat Bedtools output into provisional_exome format
#        Terminal command for i-ii:
            awk -v OFS='\t' '{a=$2+1;print $1,a,$3,$4,$5,$6;}' genome.coords.merged.bed | perl -pe "s/(\w+_\d+)\.\d\t(\d+)\t(\d+)\t(.+)\t(.)\t\n/\1 \2 \3 \5\t\4\n/" > provisional_exome.txt

#     >Makes the mRNA list
#        Terminal command:
            cut -f 3 genome.modified.gff3 | sort | uniq > mRNA_list.txt

#     >Processs mRNA list for input into GOanna
#         i.Splits list into files with <5000 ids per file
#        ii.Appends ".txt" to each split file
#       Terminal command for i-ii:
          split -l 4999 mRNA_list.txt mRNA.list
          for f in mRNA.list*; do mv $f ${f}.txt; done
          echo "Done splitting mRNA.list files"
          echo "Ready to submit files to GOanna"
          echo ""