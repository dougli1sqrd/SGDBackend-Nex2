domain_file = 'data/orf_trans_all.fasta_full.tvs'

f = open(domain_file)

found = {}
for line in f:
    items = line.strip().split("\t")
    display_name = items[4]
    format_name = items[4].replace(' ', '_')
    if format_name in found:
        continue
    found[format_name] = 1
    source = items[3]
    if source.startswith('ProSite'):
        source = 'PROSITE'
    elif source == 'Hamap':
        source = 'HAMAP'
    interspro_id = None
    desc = None
    if len(items) > 11:
        interpro_id = items[11]
    if len(items) > 12:
        if items[5] and items[5] != '-' and items[12]:
            desc = items[5] + "; " + items[12]
        elif items[5]:
            desc = items[5]
        elif items[12]:
            desc = items[12]
    elif len(items) > 5:
        desc = items[5]
            
    print (format_name + "\t" + display_name + "\t" + source + "\t" + str(interpro_id) + "\t" + desc)

