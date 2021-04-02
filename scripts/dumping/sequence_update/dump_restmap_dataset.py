from scripts.loading.database_session import get_session
from src.models import Locusdbentity, Dnasequenceannotation, Taxonomy, Contig
import sys

__author__ = 'sweng66'

datafile = "scripts/dumping/sequence_update/data/restrictionMapper/orf_genomic.seq"

TAXON = "TAX:559292"

def dump_data():

    nex_session = get_session()

    fw = open(datafile, "w")
    
    taxonomy = nex_session.query(Taxonomy).filter_by(taxid=TAXON).one_or_none()
    taxonomy_id = taxonomy.taxonomy_id

    dbentity_id_to_data = dict([(x.dbentity_id, (x.systematic_name, x.gene_name, x.sgdid, x.qualifier, x.description)) for x in nex_session.query(Locusdbentity).all()])

    contig_id_to_chr = dict([(x.contig_id, x.display_name) for x in nex_session.query(Contig).filter(Contig.display_name.like('Chromosome %')).all()])

    for x in nex_session.query(Dnasequenceannotation).filter_by(taxonomy_id=taxonomy_id, dna_type='GENOMIC').all():
        if x.contig_id not in contig_id_to_chr:
            continue
        if x.dbentity_id not in dbentity_id_to_data:
            continue
        (systematic_name, gene_name, sgdid, qualifier, desc) = dbentity_id_to_data[x.dbentity_id]
        chr = contig_id_to_chr[x.contig_id].replace('Chromosome ', 'Chr ')
        if gene_name is None:
            gene_name = ''
        start_index = x.start_index
        end_index = x.end_index
        if x.strand == '-':
            (start_index, end_index) = (end_index, start_index)
        defline = ">" + systematic_name + " " + gene_name + " SGDID:" + sgdid + ", " + chr + " from " + str(start_index) + "-" + str(end_index) + ", Genome Release 64-3-1, "
        if x.strand == '-':
            defline = defline + "reverse complement, "
        if qualifier is not None:
            defline = defline + qualifier + " ORF, "
        if desc is not None:
            defline = defline + '"' + desc + '"'
        fw.write(defline + "\n")
        fw.write(x.residues + "\n")
    
    fw.close()

    nex_session.close()

if __name__ == '__main__':

    dump_data()
