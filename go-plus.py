# Script to convert go-plus csv to atomese representation in scheme
# Requires: file go-plus from https://bioportal.bioontology.org/ontologies/GO-PLUS
# You can also get the file from https://gitlab.com/opencog-bio/pln_mozi/blob/master/raw_data/GO-PLUS.csv.gz

import re
import wget
import metadata
import os
import pandas as pd
from datetime import date

def get_term(class_id):
    if str(class_id) == "nan":
        term = class_id
    else:
        term = class_id.split("/")[-1]
        if term.startswith("GO") or term.startswith("CL") or term.startswith("UBERON") or term.startswith("CHEBI"):
            term = term.replace("_",":")
            term = term.replace("CHEBI", "ChEBI")
    return term

def get_type(term, parent=False):
    if "ChEBI" in term: 
        if parent:
            return "ConceptNode"
        else:
            return "MoleculeNode"
    else:
        return "ConceptNode"

def evaLink(term1 , term2, predicate, parent_chebis=[]):
    if not (str(term1) == "nan" or str(term2) == 'nan'):
        return ("(EvaluationLink \n" +
            "\t (PredicateNode \""+ predicate + "\")\n" +
            "\t (ListLink \n" +
            "\t\t ({}".format(get_type(term1, parent=is_parent(term1, parent_chebis)))  + " \"" + term1 + "\")\n" +
            "\t\t ({}".format(get_type(term2, parent=is_parent(term2, parent_chebis))) + " \"" + term2 + "\")))\n" )
    else:
        return ""

def is_parent(term, parent_chebis):
    if term in parent_chebis:
        return True
    else:
        return False

def inheritLink(term1 , term2, parent_chebis=[]):
    if not (str(term1) == "nan" or str(term2) == 'nan'):
        return ("(InheritanceLink \n" +
                "\t ({}".format(get_type(term1, parent=is_parent(term1, parent_chebis))) + " \"" + term1 + "\")\n" +
                "\t ({}".format(get_type(term2, parent=is_parent(term2, parent_chebis))) + " \"" + term2 + "\"))\n")
    else:
        return ""

source = "https://bioportal.bioontology.org/ontologies/GO-PLUS"
source_csv = "https://gitlab.com/opencog-bio/pln_mozi/blob/master/raw_data/GO-PLUS.csv.gz"
source_csv_latest = "http://data.bioontology.org/ontologies/GO-PLUS/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv"

if not os.path.exists("raw_data/GO-PLUS.csv.gz"):
    dataset = wget.download(source_csv_latest, "raw_data")
df = pd.read_csv("raw_data/GO-PLUS.csv.gz", dtype=str)
# Parent CHEBI's should be a ConceptNode, not a MoleculeNode
parents = df["Parents"]
parent_chebis = []
for i in [i.split("|") for i in parents if str(i) != "nan"]:
    for c in i:
        term = get_term(c)
        if "ChEBI" in term:
            parent_chebis.append(term)

go_columns = ["negatively regulated by","negatively regulates", "positively regulated by", "positively regulates", "regulated by", "regulates", "has part", "part of"]
uberon_columns = open("raw_data/uberon_columns.txt", "r").read().splitlines()
cl_columns = ['has part', 'Parents', 'has role']

if not os.path.exists("dataset/go-plus"):
    os.mkdir("dataset/go-plus/")

go = open("dataset/go-plus/Go-Plus-GO_{}.scm".format(str(date.today())),"w")
uberon = open("dataset/go-plus/Go-Plus-UBERON_{}.scm".format(str(date.today())),"w")
cl = open("dataset/go-plus/Go-Plus-CL_{}.scm".format(str(date.today())),"w")
chebi = open("dataset/go-plus/Go-Plus-CHEBI_{}.scm".format(str(date.today())),"w")

go_with_def = open("dataset/go-plus/Go-Plus-GO_with_definition_{}.scm".format(str(date.today())),"w")
uberon_with_def = open("dataset/go-plus/Go-Plus-UBERON_with_definition_{}.scm".format(str(date.today())),"w")
cl_with_def = open("dataset/go-plus/Go-Plus-CL_with_definition_{}.scm".format(str(date.today())),"w")
chebi_with_def = open("dataset/go-plus/Go-Plus-CHEBI_with_definition_{}.scm".format(str(date.today())),"w")

meta = {}

print("Started importing")
for i in range(len(df)):
    try:
        term = get_term(df.iloc[i]["Class ID"])
        obsolete = df.iloc[i]["Obsolete"]
        definition = df.iloc[i]["definition"]
        if obsolete != "true" and "GO" in term:
            go.write(evaLink(term, get_term(df.iloc[i]["Preferred Label"]), "GO_name"))
            go_with_def.write(evaLink(term, get_term(df.iloc[i]["Preferred Label"]), "GO_name"))
            go_with_def.write(evaLink(term, definition, "GO_definition"))
            for col in go_columns:
                """
                positive/negatively regulated by is inverse of positive/negatively regulates
                has part is inverse of part of, keep the predicate the same with reverse order
                """
                if col.endswith("regulated by"):
                    col_pred = col.replace("regulated by", "regulates")
                    go.write(evaLink(get_term(df.iloc[i][col]),term, "GO_{}".format(col_pred.replace(" ", "_"))))
                    go_with_def.write(evaLink(get_term(df.iloc[i][col]), term, "GO_{}".format(col.replace(" ", "_"))))
                elif col == "part of":
                    col_pred = "has part" 
                    go.write(evaLink(get_term(df.iloc[i][col]), term, "GO_{}".format(col_pred.replace(" ", "_"))))
                    go_with_def.write(evaLink(get_term(df.iloc[i][col]), term, "GO_{}".format(col.replace(" ", "_"))))
                else:                
                    go.write(evaLink(term, get_term(df.iloc[i][col]), "GO_{}".format(col.replace(" ", "_"))))
                    go_with_def.write(evaLink(term, get_term(df.iloc[i][col]), "GO_{}".format(col.replace(" ", "_"))))

        elif obsolete != "true" and "UBERON" in term:
            uberon.write(evaLink(term, get_term(df.iloc[i]["Preferred Label"]), "has_name"))
            uberon_with_def.write(evaLink(term, get_term(df.iloc[i]["Preferred Label"]), "has_name"))
            uberon_with_def.write(evaLink(term, definition, "UBERON_definition"))
            for col in uberon_columns:
                uberon.write(evaLink(term, get_term(df.iloc[i][col]), "UBERON_{}".format(col.replace(" ", "_"))))

        elif obsolete != "true" and "CL" in term or "ChEBI" in term:
            if "CL" in term:
                file_name = cl
                file_name_with_def = cl_with_def
            else:
                file_name = chebi
                file_name_with_def = chebi_with_def

            file_name.write(evaLink(term, get_term(df.iloc[i]["Preferred Label"]), "has_name", parent_chebis=parent_chebis))
            file_name_with_def.write(evaLink(term, get_term(df.iloc[i]["Preferred Label"]), "has_name",parent_chebis=parent_chebis))
            file_name_with_def.write(evaLink(term, definition, "has_definition", parent_chebis=parent_chebis))
            for col in cl_columns:
                if col == "Parents":
                    parents = df.iloc[i][col]
                    if str(parents) != "nan":
                        for p in parents.split("|"): 
                            file_name.write(inheritLink(term,get_term(p), parent_chebis=parent_chebis))
                            file_name_with_def.write(inheritLink(term, get_term(p), parent_chebis=parent_chebis))
                else:
                    file_name.write(evaLink(term, get_term(df.iloc[i][col]), col.replace(" ", "_"), parent_chebis=parent_chebis))
                    file_name_with_def.write(evaLink(term, get_term(df.iloc[i][col]), col.replace(" ", "_"), parent_chebis=parent_chebis))
    except Exception as e:
        print(e)
        continue
print("Done")
            