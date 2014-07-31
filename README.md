GO2TR - Gene Ontology to Target Region
=====

GO2TR: a gene ontology-based workflow to specify target regions for target enrichment experiments

Installation:


Workflow steps:

Step 1. Get gene annotations

    -Navigate to ftp://ftp.ncbi.nlm.nih.gov/genomes/
    -Click on folder for organism of interest
    -Click on GFF folder
    -Select and download *top_level.gff3.gz file
    -Example terminal command to download a gff3 automatically to the current working directory:
        curl ftp://ftp.ncbi.nlm.nih.gov/genomes/Myotis_lucifugus/GFF/ref_Myoluc2.0_top_level.gff3.gz \
        > genome.gff3.gz

    -Place gene annotation file in GO2TR directory and rename genome.gff3.gz
        *For more information on NCBI Eukaryotic Genome Annotation see:
        http://www.ncbi.nlm.nih.gov/genome/annotation_euk
        
    -Run process_gene_annotations.sh script
    
        What the script does:
    
        >Keeps only mRNA exons, how it works:
             i.Extracts compressed genome.gff3.gz file using gunzip
            ii.Keeps only rows with "Gnomon", "exon", and "XM_" using grep
           iii.Uses perl to modify the GFF3 file to put mRNA transcript accession number in 3rd column
            iv.Uses sort for proper input to bedtools, and saves file as genome.modified.gff3
           Terminal command for i-iv:
                gunzip -c genome.gff3.gz | grep "Gnomon" | grep "exon" | grep "XM_" | perl -pe 's/(NW_.+)\t(Gnomon)\texon\t(\d+)\t(\d+)\t(.)\t(.)\t(.)\t(.+)(XM_\d+\.\d)(.+)\n/$1\t$2\t$9\t$3\t$4\t$5\t$6\t$7\t$8$9$10\n/' | sort -k 1,1 -k2,2n > genome.modified.gff3

        >Merge overlapping exons with Bedtools
           Terminal command:
                bedtools merge -i genome.modified.gff3 -s -nms > genome.coords.merged.bed

        >Makes the provisional exome, how it works:
             i.Uses awk to change from 0-based to 1-based coordinates
            ii.Use Perl to reformat Bedtools output into provisional exome format
           Terminal command for i-ii:
                awk -v OFS='\t' '{a=$2+1;print $1,a,$3,$4,$5,$6;}' genome.coords.merged.bed | perl -pe "s/(NW_\d+\.\d)\t(\d+)\t(\d+)\t(.+)\t(.)\t\n/\1 \2 \3 \5\t\4\n/" > genome.coords.merged.reformatted.txt

        >Makes the mRNA list
           Terminal command:
                cut -f 3 genome.modified.gff3 | uniq > mRNA.list.txt

        >Processs mRNA list for input into GOanna
            i.Splits list into files with <5000 ids per file
           ii.Appends ".txt" to each split file
          Terminal command for i-ii:
              split -l 4999 mRNA.list.txt mRNA.list
              for f in mRNA.lista*; do mv $f ${f}.txt; done

    -Assign gene ontology using GOanna

        >Navigate to http://www.agbase.msstate.edu/cgi-bin/tools/GOanna.cgi
        >Parameters for search
            Program	blastx
            Email Address	your_email_address
            Input File format	ACCESSIONS/GI
            Select Accession Type	GenBank Accession
            File to Upload	mRNA.lista
            Database	SwissProt, TrEMBL, UniProt
            Filter sequences and annotations from the selected databases to remove sequences with no GO annotations or with IEA or ND annotations only	Selected
            Filter	Low complexity	not selected
            Expect	10e-20
            Word Size	3
            Matrix	Blosum62
            Gap Costs	Existence11 Extension1
            Nbr. of Descriptions	3
            Nbr. of Alignments	3
            Type of Evidence to Return	Experimental Evidence Codes(EXP,IDA,IPI,IMP,IGI,IEP)
        >Repeat search using above parameters for all mRNA.lista*.txt files
        >Can only submit 3 searches at a time with a single email account
        
        >Save raw results from email as mRNA-GOid.lista*.zip and place in GO2TR directory

        >Process GOanna output to make mRNA-GO list, how it works:
            i.Unzips files combining all ".sliminput.txt" files
           ii.Renames the combined files
          iii.Uses grep to get only rows with "XM"
           iv.Uses cut to remove domain data (i.e., column 3)
       Terminal command (i-iv):
        unzip -ca \*.zip \*.txt | tee mRNA-GOid.list.txt | grep "XM" | cut -f 1-2 > mRNA-GOid.list.edited.txt

Step 2. Select GO term

    -Determine Descendants of Gene Ontology term of interest
    -Navigate browser to GO Online SQL Environment	http://www.berkeleybop.org/goose
    -In the "Enter your SQL query" box entered following, except replace text 'term of interest' with the GO term you want to find the descendants for

        SELECT DISTINCT descendant.acc, descendant.name, descendant.term_type
        FROM
         term
         INNER JOIN graph_path ON (term.id=graph_path.term1_id)
         INNER JOIN term AS descendant ON (descendant.id=graph_path.term2_id)
        WHERE term.name='term of interest' AND distance <> 0 ;

    -Next For "Limit the number of results returned" select unlimited

    -Leave "Download results directly in tab-delimited format" unselected

    -Under "Mirrors" select EBI or other appropriate server

    -Click on "Query!"

    -Results such as "Your query generated 776 result(s)." will appear

    -Click on "Download as tab-delimited format"

    -Save file as GOid.results.txt

    -To get only GOids open the file in Excel to select only first column or use Unix cut command
       Terminal command:
        cut -f 1 GOid.results.txt > GOid.list.txt

    -Insert a new line a the top of GOid.list.txt and enter the GO term of interest

    -Save the file and place it in the GO2TR directory

3.Filter mRNA-GO list by GO term list

    -Run filter_mRNA-GO_list.py to make retained mRA list

4.Filter mRNA-GO list by GO term list

    -Run filter_provisional_exome.py to make target region

    -Reformats target region using Perl into a tab delimited format file
        Terminal command:
            perl -pe "s/(\w+\.\d) (\d+) (\d+) (.)\n/\1\t\2\t\3\t\4\n/" GO2TR.coords.txt > GO2TR.coords.tabdel.txt
    
    -Calculates target regions size with Perl
        Terminal command:
            perl -ane '$sum += $F[2] - $F[1]; END { print "\n"; print "There are "; print $sum; print " bp in the target regions."; print "\n"; print "\n"}' GO2TR.coords.tabdel.txt
