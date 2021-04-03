# import sys
# from scripts.loading.database_session import get_session
from src.models import Locusdbentity, Dnasequenceannotation, Taxonomy, Contig, So,\
                       Proteinsequenceannotation

__author__ = 'sweng66'

VERSION = '64-3-1'

def format_fasta(seq):

    return "\n".join([seq[i:i+60] for i in range(0, len(seq), 60)])
    
def reverse_complement(seq):

    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    bases = list(seq)
    bases = reversed([complement.get(base,base) for base in bases])
    bases = ''.join(bases)
    return bases

def get_chr_letter():

    return { 'I': 'A', 'II': 'B', 'III': 'C', 'IV': 'D', 'V': 'E', 'VI': 'F', 'VII': 'G',
             'VIII': 'H', 'IX': 'I', 'X': 'J', 'XI': 'K', 'XII': 'L', 'XIII': 'M',
             'XIV': 'N', 'XV': 'O', 'XVI': 'P', 'Mito': 'Q' }

def generate_protein_seq_file(nex_session, taxonomy_id, dbentity_id_to_defline, seqFile, seq_format):

    fw = open(seqFile, "w")

    for x in nex_session.query(Proteinsequenceannotation).filter_by(taxonomy_id=taxonomy_id).all():
        if x.dbentity_id not in dbentity_id_to_defline:
            continue
        fw.write(dbentity_id_to_defline[x.dbentity_id] + "\n")
        if seq_format == 'fasta':
            fw.write(format_fasta(x.residues) + "\n")
        else:
            fw.write(x.residues + "\n")

    fw.close

def generate_not_feature_seq_file(nex_session, taxonomy_id, dbentity_id_to_data, so_id_to_display_name, seqFile, seq_format):

    fw = open(seqFile, "w")
     
    found = {}
    prevRow = None
    prevContigId = None
    contig_id_to_seq = {}
    contig_id_to_display_name = {}
    defline_to_seq = {}
    chr2letter = get_chr_letter()
    
    for x in nex_session.query(Dnasequenceannotation).filter_by(dna_type='GENOMIC', taxonomy_id=taxonomy_id).order_by(Dnasequenceannotation.contig_id, Dnasequenceannotation.start_index, Dnasequenceannotation.end_index).all():
        if x.dbentity_id not in dbentity_id_to_data:
            continue
        type = so_id_to_display_name.get(x.so_id)

        (name, gene_name, sgdid, qualifier, desc) = dbentity_id_to_data[x.dbentity_id]
        
        if prevContigId is None or prevContigId != x.contig_id:
            prevRow = (name, x.start_index, x.end_index)
            prevContigId = x.contig_id
            continue

        (prevName, prevStart, prevEnd) = prevRow
        if x.start_index >= prevStart and x.end_index <= prevEnd:
            continue
        
        start = prevEnd + 1
        end = x.start_index - 1
        
        if end <= start:
            prevRow = (name, x.start_index, x.end_index)
            prevContigId = x.contig_id
            continue
        
        if x.contig_id not in contig_id_to_seq:
            contig = nex_session.query(Contig).filter_by(contig_id=x.contig_id).one_or_none()
            if contig is None:
                print ("The contig_id=", x.contig_id, " is not in the database.")
                exit()
            contig_id_to_seq[x.contig_id] = contig.residues;
            contig_id_to_display_name[x.contig_id] = contig.display_name;

        chr = contig_id_to_display_name[x.contig_id].replace('Chromosome ', '')
        if chr not in chr2letter:
            continue
        seqID =	str(start) + "-" + str(end)
        seq = contig_id_to_seq[x.contig_id][start-1:end]
        
        if seqID in found:
            print ("The seqID is already in the file.", seqID)
            continue
        found[seqID] = 1
        defline = ">" + chr2letter[chr] + ":" + seqID + ", Chr " + chr + " from " + seqID + ", Genome Release " + VERSION + ", between " + prevName + " and " + name 
        
        fw.write(defline + "\n")
        if seq_format == 'fasta':
            fw.write(format_fasta(seq) + "\n")
        else:
            fw.write(seq + "\n")

        prevRow = (name, x.start_index, x.end_index)
        prevContigId = x.contig_id

    fw.close()

def generate_dna_seq_file(nex_session, taxonomy_id, dbentity_id_to_data, contig_id_to_chr, so_id_to_display_name, seqFile, dna_type, seq_format, file_type, dbentity_id_to_defline=None):

    feature_to_include = ['ORF', 'transposable_element_gene', 'pseudogene', 'blocked_reading_frame']
    if file_type == 'RNA':
        feature_to_include = ['ncRNA_gene', 'snoRNA_gene', 'snRNA_gene', 'tRNA_gene', 'rRNA_gene', 'telomerase_RNA_gene']
    
    fw = open(seqFile, "w")
    
    for x in nex_session.query(Dnasequenceannotation).filter_by(taxonomy_id=taxonomy_id, dna_type=dna_type).order_by(Dnasequenceannotation.contig_id, Dnasequenceannotation.start_index, Dnasequenceannotation.end_index).all():
        if x.contig_id not in contig_id_to_chr:
            continue
        if x.dbentity_id not in dbentity_id_to_data:
            continue
        type = so_id_to_display_name[x.so_id]
        if type not in feature_to_include:
            continue
        (systematic_name, gene_name, sgdid, qualifier, desc) = dbentity_id_to_data[x.dbentity_id]
        chr = contig_id_to_chr[x.contig_id].replace('Chromosome ', 'Chr ')
        if gene_name is None:
            if seq_format == 'fasta':
                gene_name = systematic_name
            else:
                gene_name = ''
        start_index = x.start_index
        end_index = x.end_index
        if x.strand == '-':
            (start_index, end_index) = (end_index, start_index)
        coords = str(start_index) + "-" + str(end_index)
        if dna_type == 'CODING':
            coords = x.file_header.split(' ')[3].split(':')[1].replace('..', '-')
        defline = ">" + systematic_name + " " + gene_name + " SGDID:" + sgdid + ", " + chr + " from " + coords + ", Genome Release " + VERSION + ", "
        if x.strand == '-':
            defline = defline + "reverse complement, "
        if qualifier is not None:
            defline = defline + qualifier + " " + type + ", "
        else:
            defline = defline + type + ", "
        if desc is not None:
            defline = defline + '"' + desc + '"'
        if dbentity_id_to_defline is not None:
            dbentity_id_to_defline[x.dbentity_id] = defline
        fw.write(defline + "\n")
        if seq_format == 'fasta':
            fw.write(format_fasta(x.residues) + "\n")
        else:
            fw.write(x.residues + "\n")
    
    fw.close()

        
        
