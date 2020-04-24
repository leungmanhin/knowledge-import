# PYTHONIOENCODING=utf-8 python3 chebi_check.py

import csv
import re

chebi_dict = {}
not_match = open("id_not_match.txt", "w", encoding="utf-8", errors="ignore")
not_found = open("not_found.txt", "w", encoding="utf-8", errors="ignore")

# From: ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo
chebi_path = "raw_data/chebi.obo"
chebi_fp = open(chebi_path, "r", encoding="utf-8", errors="ignore")

chebi_obo_dict = {}
chebi_name = []
chebi_id = None

for line in chebi_fp:
  # print("Reading line -- " + line)
  line = line.replace("\n", "")
  if line == "[Term]":
    if len(chebi_name) > 0 and chebi_id != None:
      for name in chebi_name:
        chebi_dict[name] = chebi_id
        chebi_obo_dict[name] = chebi_id
      print("(chebi.obo) ID: {}\nName: {}\n".format(chebi_id, chebi_name))
    chebi_name = []
    chebi_id = None
  elif line.startswith("id: "):
    chebi_id = line.replace("id: CHEBI:", "").strip()
  elif line.startswith("name: "):
    chebi_name.append(line.replace("name: ", "").lower())
  elif line.startswith("synonym: ") and "EXACT" in line:
    name = re.match(".+\"(.+)\".+", line).group(1).lower().strip()
    if name not in chebi_name:
      chebi_name.append(name)

chebi_fp.close()

# ----------
chebi_path = "raw_data/names.tsv"
chebi_fp = open(chebi_path, "r", encoding="utf-8", errors="ignore")
chebi_names_dict = {}

for line in chebi_fp:
  # print("Reading line -- " + line)
  if line.startswith("ID"):
    continue
  contents = line.replace("\n", "").split("\t")
  eid = contents[1].strip()
  id_source = contents[3].strip()
  name = contents[4].lower().strip()
  if id_source == "ChEBI":
    if chebi_dict.get(name) != None and eid != chebi_dict[name]:
      print("XXXXXXXXXXXXXXXXXX ChEBI IDs don't match for: " + name)
      not_match.write("\nChEBI IDs don't match for: {}\n".format(name))
      if chebi_dict.get(name) != None:
        print("In chebi.obo: " + chebi_dict[name])
        not_match.write("In chebi.obo: {}\n".format(chebi_dict[name]))
      print("In names.tsv: {}\n".format(eid))
      not_match.write("In names.tsv: {}\n".format(eid))
    else:
      chebi_dict[name] = eid
      chebi_names_dict[name] = eid
      print("(names.tsv) ID: {}\nName: {}\n".format(eid, name))

chebi_fp.close()

# ----------
chebi_path = "raw_data/compounds.tsv"
chebi_fp = open(chebi_path, "r", encoding="utf-8", errors="ignore")
chebi_compounds_dict = {}

for line in chebi_fp:
  # print("Reading line -- " + line)
  if line.startswith("ID"):
    continue
  contents = line.replace("\n", "").split("\t")
  chebi_id = contents[2].replace("CHEBI:", "").strip()
  name = contents[5].lower().strip()
  if chebi_dict.get(name) != None and chebi_id != chebi_dict[name]:
    print("XXXXXXXXXXXXXXXXXX ChEBI IDs don't match for: " + name)
    not_match.write("\nChEBI IDs don't match for: {}\n".format(name))
    if chebi_dict.get(name) != None:
      print("In chebi.obo: " + chebi_dict[name])
      not_match.write("In chebi.obo: {}\n".format(chebi_dict[name]))
    if chebi_names_dict.get(name) != None:
      print("In names.tsv: " + chebi_names_dict[name])
      not_match.write("In names.tsv: {}\n".format(chebi_names_dict[name]))
    print("In compounds.tsv: {}\n".format(chebi_id))
    not_match.write("In compounds.tsv: {}\n".format(chebi_id))
  elif name == "null":
    continue
  else:
    chebi_dict[name] = chebi_id
    chebi_compounds_dict[name] = chebi_id
    print("(compounds.tsv) ID: {}\nName: {}\n".format(chebi_id, name))

chebi_fp.close()

# ----------
chebi_path = "raw_data/structure links.csv"
chebi_fp = open(chebi_path, "r", encoding="utf-8", errors="ignore")
csv = csv.reader(chebi_fp)
chebi_sl_dict = {}

for line in csv:
  # print("Reading line -- " + line)
  if line[0] == "DrugBank":
    continue
  chebi_id = line[12].strip()
  name = line[1].lower().strip()
  if name != "" and chebi_id != "":
    if chebi_dict.get(name) != None and chebi_id != chebi_dict[name]:
      print("XXXXXXXXXXXXXXXXXX ChEBI IDs don't match for: " + name)
      not_match.write("\nChEBI IDs don't match for: {}\n".format(name))
      if chebi_dict.get(name) != None:
        print("In chebi.obo: " + chebi_dict[name])
        not_match.write("In chebi.obo: {}\n".format(chebi_dict[name]))
      if chebi_names_dict.get(name) != None:
        print("In names.tsv: " + chebi_names_dict[name])
        not_match.write("In names.tsv: {}\n".format(chebi_names_dict[name]))
      if chebi_compounds_dict.get(name) != None:
        print("In compounds.tsv: " + chebi_compounds_dict[name])
        not_match.write("In compounds.tsv: {}\n".format(chebi_compounds_dict[name]))
      print("In structure links.csv: {}\n".format(chebi_id))
      not_match.write("In structure links.csv: {}\n".format(chebi_id))
    else:
      chebi_dict[name] = chebi_id
      chebi_sl_dict[name] = chebi_id
      print("(structure links.csv) ID: {}\nName: {}\n".format(chebi_id, name))

chebi_fp.close()

# ----------
tcmid_path = "raw_data/ingredient_targets_disease_drug-TCMID.v2.03.txt"
tcmid_fp = open(tcmid_path, "r", encoding="utf-8", errors="ignore")

tcmid_herbs = []
tcmid_match_cnt = 0

for line in tcmid_fp:
  tcmid_herb = line.replace("\n", "").split("\t")[0].strip().lower()
  if tcmid_herb not in tcmid_herbs:
    tcmid_herbs.append(tcmid_herb)
    if chebi_dict.get(tcmid_herb) != None:
      tcmid_match_cnt = tcmid_match_cnt + 1
    else:
      print("!!! NOT found: {}".format(tcmid_herb))
      not_found.write(tcmid_herb + "\n")

tcmid_fp.close()

print("Total no. of herbs in TCMID = {}, of which found in ChEBI = {}".format(len(tcmid_herbs), tcmid_match_cnt))

not_match.close()
not_found.close()

# Default:
# Total no. of herbs in TCMID = 2711, of which found in ChEBI = 374

# Lower ChEBI:
# Total no. of herbs in TCMID = 2711, of which found in ChEBI = 418

# Both Lower:
# Total no. of herbs in TCMID = 2693, of which found in ChEBI = 492

# +names.tsv, all lower:
# Total no. of herbs in TCMID = 2693, of which found in ChEBI = 550

# +names.tsv +compounds.tsv, all lower:
# Total no. of herbs in TCMID = 2693, of which found in ChEBI = 562

# +names.tsv +compounds.tsv +structure links.csv, all lower:
# Total no. of herbs in TCMID = 2693, of which found in ChEBI = 581
