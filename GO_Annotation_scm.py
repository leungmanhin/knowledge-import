# imports Go Annotation to atomese
# Requires: file gene_association.goa_ref_human.gz from http://geneontology.org/gene-associations/gene_association.goa_ref_human.gz
import wget
import gzip
import os
import metadata
from datetime import date

source = "http://current.geneontology.org/annotations/goa_human.gaf.gz"
if not os.path.exists("raw_data/goa_human.gaf.gz"):
    dataset = wget.download(source, "raw_data")
with gzip.open("raw_data/goa_human.gaf.gz", "rb") as f:
    lines = f.readlines()
lines = [l.decode("utf-8") for l in lines]
line_no = []
print("Started importing")

for num, line in enumerate(lines , 1):
  if "UniProtKB" in line :
      line_no.append(num)

lines_annotate = lines[line_no[0] -1 : len(lines)]

###### function to write on file

def memberLink(gene, goID, qualifier):
    if qualifier == 'NOT':
        f_annotation.write("(MemberLink (stv 0.0 1.0)\n")
        g_annotation.write("(MemberLink (stv 0.0 1.0)\n")
    else:
        f_annotation.write("(MemberLink\n")
        g_annotation.write("(MemberLink\n")
    f_annotation.write("\t(GeneNode \"" + gene.upper().strip() + "\")\n")
    f_annotation.write("\t(ConceptNode \"GO:" + goID + "\"))\n")
    g_annotation.write("\t(GeneNode \"" + gene.upper().strip() + "\")\n")
    g_annotation.write("\t(ConceptNode \"GO:" + goID + "\"))\n")

def evaLink(gene , name, qualifier):
    if qualifier == 'NOT' :
        f_annotation.write("(EvaluationLink (stv 0.0 0.0)\n")
    else :
    	f_annotation.write("(EvaluationLink \n")
    f_annotation.write("\t (PredicateNode \""+ "has_name"+ "\")\n")
    f_annotation.write("\t (ListLink \n")
    f_annotation.write("\t\t (GeneNode"  + " \"" + gene.upper().strip() + "\")\n")
    f_annotation.write("\t\t (ConceptNode" + " \"" + name + "\")\n")
    f_annotation.write("\t )\n")
    f_annotation.write(")\n\n")


#open file to write
if not os.path.exists(os.path.join(os.getcwd(), 'gene-level')):
      os.makedirs('gene-level')
if not os.path.exists(os.path.join(os.getcwd(), 'dataset')):
      os.makedirs('dataset') 
f_annotation = open('dataset/GO_annotation_{}.scm'.format(str(date.today())), 'a')
g_annotation = open('gene-level/GO_annotation_gene-level_{}.scm'.format(str(date.today())), 'a')

#add GOC Validation Date
f_annotation.write(";"+((lines[0]).split('!')[1]).split('$')[0]+ "\n")
f_annotation.write(";"+((lines[1]).split('!')[1]).split('$')[0]+ "\n\n")

genes = []
go = []
#loop through lines
for l in lines_annotate:
    db_object_symbol =l.split('\t')[2]
    go_id = (l.split('\t')[4]).split(':')[1]
    qualifier = l.split('\t')[3]
    gene_name = l.split('\t')[9]
    memberLink(db_object_symbol,go_id,qualifier)
    go.append(go_id)
    if not db_object_symbol in genes:
        genes.append(db_object_symbol)
        evaLink(db_object_symbol,gene_name, qualifier)
f_annotation.close()
g_annotation.close()
script = "https://github.com/MOZI-AI/knowledge-import/GO_Annotation_scm.py"
metadata.update_meta("GO_Annotation:latest", source,script,genes=len(genes), goterms={"go-terms":len(set(go))})
print("Done, check dataset/GO_annotation.scm and gene-level/GO_annotation.scm")


