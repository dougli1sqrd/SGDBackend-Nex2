infile = 'data/ORTHOLOGY-ALLIANCE_COMBINED_29.tsv'

f = open(infile)

data = {}
sgdid2gene = {}

for line in f:
    if not line.startswith('SGD:'):
        continue
    pieces = line.split('\t')
    sgdid = pieces[0]
    gene = pieces[1]
    externalID = pieces[4]
    externalDB = pieces[4].split(':')[0]
    externalID_list = []
    if (sgdid, gene, externalDB) in data:
        externalID_list = data[(sgdid, gene, externalDB)]
    externalID_list.append(externalID)
    data[(sgdid, gene, externalDB)] = externalID_list
    
for (sgdid, gene, externalDB) in data:
    externalID_list = data[(sgdid, gene, externalDB)]
    print (sgdid + "\t" + gene + "\t" + externalDB + "\t" + '|'.join(externalID_list))
        
f.close()
exit
