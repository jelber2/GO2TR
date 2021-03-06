GO2TR - Gene Ontology to Target Region
=====

NOTE: GOanna no longer accepts Accession numbers and requires FASTA files, thus GOanna
instructions below do not work. PLEASE USE rGO2TR (https://github.com/jelber2/rGO2TR) instead of GO2TR.


GO2TR: a gene ontology-based workflow to specify target regions for target enrichment experiments

Installation/Setup

    -Decide where you want to create a "GO2TR" folder

        >For example on MacOSX you might want to open the terminal and create
         a GO2TR folder in your home directory: /Users/your_username/GO2TR

            Terminal commands (don't enter lines beginning with ##):
              pwd
              ## for "print working directory" tells you what directory you are in ##
              ## if the system returns /Users/your_username/, you are in right place ##

              mkdir GO2TR
              ## makes a folder called GO2TR ##

              cd GO2TR
              ## changes current working directory to GO2TR ##

    -Install bedtools: see https://github.com/arq5x/bedtools2/releases

        >I recommend downloading the newest version of bedtools and saving it
         to the GO2TR directory as bedtools.tar.gz.
         At the time of writing it is bedtools-2.20.1, so that's what I will use in the code below.

            Terminal commands once bedtools-2.20.1.tar.gz is in GO2TR directory
              cd /Users/your_username/GO2TR
              ## navigates to GO2TR directory if not already current working directory ##

              tar -zxvf bedtools-2.20.1.tar.gz
              ## unzips the compressed archive and creates a directory called bedtools2-2.20.1 ##

              mv bedtools2-2.20.1 bedtools
              ## the mv ("move") command renames the "bedtools2-2.20.1" directory to "bedtools" for simplicity ##

              cd bedtools
              make
              ## the make command compiles the bedtools code ##
              ## cross your fingers that everything compiles correctly! ##
              ## compiling should be under 5 minutes ##
              ## if compiliing worked, then you can test the install using following ##

              cd bin
              ./bedtools
              ## the program should display a usage message if it was correctly compiled ##

              cd ..
              ## changes the directory from bin to directory above called bedtools

              cd ..
              ## changes the directory from bedtools to GO2TR ##

    -Download the process_gene_annotations.sh, filter_mRNA-GO_list.py, and filter_provisional_exome.py files from github
            Terminal commands:
              cd /Users/your_username/GO2TR
              curl -k https://raw.githubusercontent.com/jelber2/GO2TR/master/process_gene_annotations.sh > process_gene_annotations.sh
              curl -k https://raw.githubusercontent.com/jelber2/GO2TR/master/filter_mRNA-GO_list.py > filter_mRNA-GO_list.py
              curl -k https://raw.githubusercontent.com/jelber2/GO2TR/master/filter_provisional_exome.py > filter_provisional_exome.py
              ## use "-k" option to ignore security certificate ##

    -You are now ready to use GO2TR!!

Step 1. Get gene annotations

    -Note: An example dataset for the dog (Canis_lupus_familiaris) using the gene ontology term 'immune response' 
     is available at https://raw.githubusercontent.com/jelber2/GO2TR/master/example_dataset.zip

    -Navigate your web browser to ftp://ftp.ncbi.nlm.nih.gov/genomes/
    -Click on folder for organism of interest (e.g., Canis_lupus_familiaris)
    -Click on GFF folder
    -Left click on the top_level.gff3.gz file and save it as genome.gff3.gz to your GO2TR directory
    -Example terminal command to download the gff3.gz file for Canis_lupus_familiaris
     automatically to the GO2TR directory:
        curl ftp://ftp.ncbi.nlm.nih.gov/genomes/Canis_lupus_familiaris/GFF/ref_CanFam3.1_top_level.gff3.gz \
        > /Users/your_username/GO2TR/genome.gff3.gz

    -Run process_gene_annotations.sh script
        Terminal command:
            cd /Users/your_username/GO2TR
            bash process_gene_annotations.sh
    
        What the script does:
    
        >Keeps only mRNA exons, how it works:
             i.Extracts compressed genome.gff3.gz file using gunzip
            ii.Keeps only rows with "Gnomon", "exon", and "XM_" using grep
           iii.Uses perl to modify the GFF3 file to put mRNA transcript accession number in 3rd column
            iv.Uses sort for proper input to Bedtools, and saves file as genome.modified.gff3
           Terminal command for i-iv:
                gunzip -c genome.gff3.gz | grep "Gnomon" | grep "exon" | grep "XM_" | perl -pe 's/(\w+_.+)\t(Gnomon)\texon\t(\d+)\t(\d+)\t(.)\t(.)\t(.)\t(.+)(XM_\d+)\.\d(.+)\n/$1\t$2\t$9\t$3\t$4\t$5\t$6\t$7\t$8$9$10\n/' | sort -k 1,1 -k4,4n > genome.modified.gff3

        >Merge overlapping exons with Bedtools
           Terminal command if Bedtools was installed in /Users/your_username/GO2TR
           and your current working directory is GO2TR:
                ./bedtools/bin/bedtools merge -i genome.modified.gff3 -s -c 3,7 -o distinct -delim ";" > genome.coords.merged.bed

        >Makes the provisional_exome, how it works:
             i.Uses awk to change from 0-based to 1-based coordinates
            ii.Use Perl to reformat Bedtools output into provisional_exome format
           Terminal command for i-ii:
                awk -v OFS='\t' '{a=$2+1;print $1,a,$3,$4,$5,$6;}' genome.coords.merged.bed | perl -pe "s/(\w+_\d+\.\d)\t(\d+)\t(\d+)\t(.+)\t(.)\t\n/\1 \2 \3 \5\t\4\n/" > provisional_exome.txt

        >Makes the mRNA list
           Terminal command:
                cut -f 3 genome.modified.gff3 | sort | uniq > mRNA_list.txt

        >Processs mRNA list for input into GOanna
            i.Splits list into files with <5000 ids per file
           ii.Appends ".txt" to each split file
          Terminal command for i-ii:
              split -l 4999 mRNA_list.txt mRNA.list
              for f in mRNA.list*; do mv $f ${f}.txt; done

    -Assign gene ontology using GOanna

        >Navigate to http://www.agbase.msstate.edu/cgi-bin/tools/GOanna.cgi
        >Parameters for search
            Program	blastx
            Email Address	your_email_address
            Input File format	ACCESSIONS/GI
            Select Accession Type	GenBank Accession
            File to Upload	mRNA.listaa
            Database	AgBase-UniProt
            Filter sequences and annotations from the selected databases to remove sequences with no GO annotations or with IEA or ND annotations only	Selected
            Expect	10e-20
            Matrix	Blosum62
            Gap Costs	Existence11 Extension1
            Word Size	3
            Filter	Low complexity not selected
            Nbr. Target Seqs	3
            Pct Id. Filter	70
            Query Coverage Fil	70
            Blast results format selection	TSV format
            Type of Evidence to Return	Experimental Evidence Codes(EXP,IDA,IPI,IMP,IGI,IEP)
        >Click on BLAST
        >Repeat search using above parameters for all mRNA.lista*.txt files
        >Can only submit 3 searches at a time with a single email account
        >Save raw results from email as mRNA-GO.lista*.zip and place in GO2TR directory

        >Process GOanna output to make mRNA-GO list, how it works:
            i.Unzips files combining all ".sliminput.txt" files
           ii.Renames the combined files
          iii.Uses grep to get only rows with "XM"
           iv.Uses cut to remove domain data (i.e., column 3)
          Terminal command for i-iv:
              unzip -ca \*.zip \*.txt | grep "XM" | cut -f 1-2 > mRNA-GO.list.txt

Step 2. Select GO term

    -Determine Descendants of Gene Ontology term of interest
    -Navigate browser to GO Online SQL Environment	http://amigo.geneontology.org/goose
    -In the "Enter your SQL query" box entered following, except replace text
     'term of interest' with the GO term you want to find the descendants for
     (e.g., 'immune response')

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
    -Download the file to your GO2TR directory and save it as GOid.results.txt
    -To get only GOids (i.e., data in first column) use Unix cut command
        Terminal command:
            cut -f 1 GOid.results.txt > GOid.results.column1.txt

    -Use terminal commands below to add GO id for the GO term of interest to
     GOid.results.column1.txt but save the new file as GOid.list.txt

    -NOTE: You need to know your GO term's id (e.g., immune response = GO:0006955)
     before using the commands below!
         Searching the gene ontology database, 
         (http://amigo1.geneontology.org/cgi-bin/amigo/go.cgi), for your
         GO term (e.g., immune response) can help you get its id!

        Terminal command for first step of adding GO id to GOid.results.column1.txt:
            echo && echo Enter gene ontology identifier for GO term you want to\
            add to GOid.results.column1.txt in the form GO:1234567 && echo && read GOid
        Terminal command for the second step:
            echo && echo adding $GOid to GOid.results.colum1.txt and saving files as GOid.list.txt \
            echo && awk -v n=1 -v GOid="$GOid" 'NR == n {print GOid} {print}' GOid.results.column1.txt > GOid.list.txt

Step 3.Filter mRNA-GO list by GO id list

    -Run filter_mRNA-GO_list.py to make retained_mRNA_list
        Terminal command:
            python filter_mRNA-GO_list.py

Step 4.Filter provisional_exome by retained_mRNA_list

    -Run filter_provisional_exome.py to make target region
        Terminal command:
            python filter_provisional_exome.py

    -Reformats target region using Perl into a tab delimited file in bed6 format
     Note: Awk is used to change from 1-based to 0-based coordinates used
     by bed files.
        Terminal command:
            perl -pe "s/(\w+) (\d+) (\d+) (.)\n/\1\t\2\t\3\t.\t.\t\4\n/" GO2TR.coords.txt | awk -v OFS='\t' '{a=$2-1;print $1,a,$3,$4,$5,$6;}' > GO2TR.target_region.bed

    -Calculates target region size with Perl
        Terminal command:
            perl -ane '$sum += $F[2] - $F[1]-1; END { print "\n"; print "There are "; print $sum; print " bp in the target region."; print "\n"; print "\n"}' GO2TR.target_region.bed
