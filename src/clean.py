#!/usr/bin/env python3

import argparse, csv
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

# Parse arguments

parser = argparse.ArgumentParser(
    description='Generate Turtle for pruned taxa')
parser.add_argument('alleles',
    type=argparse.FileType('r'),
    help='read query result CSV')
parser.add_argument('cheats',
    type=argparse.FileType('r'),
    help='extra rows')
args = parser.parse_args()

organisms = {
  'bonobo': 'bonobo (Pan paniscus)',
  'cattle': 'cattle (Bos taurus)',
  'chicken': 'chicken (Gallus gallus)',
  'chimpanzee': 'chimpanzee (Pan troglodytes)',
  'cotton-top tamarin': 'cotton-top tamarin (Saguinus oedipus)',
  'dog': 'dog (Canis lupus familiaris)',
  'gorilla': 'gorilla (Gorilla gorilla)',
  'horse': 'horse (Equus caballus)',
  'human': 'human (Homo sapiens)',
  'marmoset': 'marmoset (Callithrix jacchus)',
  'mouse': 'mouse (Mus musculus)',
  'organism': 'organism (all species)',
  'pig': 'pig (Sus scrofa)',
  'rat': 'rat (Rattus norvegicus)',
  'rhesus macaque': 'rhesus macaque (Macaca mulatta)',
  'sheep': 'sheep (Ovis aries)'
}
codes = {
  '1': 'organism',
  '9031': 'chicken',
  '9483': 'marmoset',
  '9490': 'Saoe',
  '9544': 'Mamu',
  '9593': 'Gogo',
  '9597': 'Papa',
  '9598': 'Patr',
  '9606': 'HLA',
  '9615': 'DLA',
  '9796': 'ELA',
  '9823': 'SLA',
  '9913': 'BoLA',
  '9940': 'Ovar',
  '10090': 'H2',
  '10116': 'rat'
}

def clean_code(name):
  return name.replace('BF-','') \
             .replace('BoLA-','') \
             .replace('DLA-','') \
             .replace('ELA-','') \
             .replace('Gogo-','') \
             .replace('H2-','') \
             .replace('HLA-','') \
             .replace('Mamu-','') \
             .replace('Papa-','') \
             .replace('Patr-','') \
             .replace('Saoe-','') \
             .replace('SLA-','')

# Grab the first row and use those headers.

row = csv.reader(args.alleles)
headers = next(row)

# Put the following rows in dicts.

rows = csv.DictReader(args.alleles, fieldnames=headers)

# Update the dicts selectively and print in order.

results = []
for row in rows:
  synonyms = row['synonyms'].split(', ')
  synonyms.sort()
  row['synonyms'] = ', '.join(synonyms)
  row['organism'] = organisms[row['organism']]
  row['class'] = row['class'].replace('MHC class ', '').replace(' MHC', '').replace('non-','non ')
  row['haplotype'] = row['haplotype'].replace(' haplotype', '')
  row['serotype'] = clean_code(row['serotype'].replace(' serotype', ''))
  row['chain_i_name'] = row['chain_i_name'].replace(' chain', '')
  row['chain_ii_name'] = row['chain_ii_name'].replace(' chain', '')
  row['chain_i_locus'] = clean_code(row['chain_i_locus'].replace(' locus', ''))
  row['chain_ii_locus'] = clean_code(row['chain_ii_locus'].replace(' locus', ''))

  if row['restriction_level'] == 'class':
    row['displayed_restriction'] = codes[row['organism_ncbi_tax_id']] + '-class ' + row['class']
  elif row['restriction_level'] == 'haplotype' \
      and row['organism'] not in ['chicken (Gallus gallus)']:
    row['displayed_restriction'] = codes[row['organism_ncbi_tax_id']] + '-' + row['displayed_restriction']

  values = []
  for header in headers:
    # TODO: Fix this
    if header != 'synonyms':
      values.append(row[header] or '')
  results.append(values)

rows = csv.DictReader(args.cheats, delimiter='\t')
for row in rows:
  values = []
  for header in headers:
    # TODO: Fix this
    if header != 'synonyms':
      values.append(row[header] or '')
  results.append(values)

results.sort(key=lambda x: int(x[0]))

print('\t'.join(x for x in headers if x != 'synonyms')) # TODO: Fix this
for result in results:
  print('\t'.join(result))

