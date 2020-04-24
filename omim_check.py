hdo_path = "/home/opencog-bio/HumanDiseaseOntology/src/ontology/HumanDO.obo"
hdo_fp = open(hdo_path, "r", encoding="utf-8", errors="ignore")

hdo_omim_dict = {}
hdo_name = None
hdo_omim_id = None

for line in hdo_fp:
  line = line.replace("\n", "")
  if line == "[Term]":
    if hdo_name != None and hdo_omim_id != None:
      hdo_omim_dict[hdo_omim_id] = hdo_name
      print("Name: {}\nOMIM: {}\n".format(hdo_name, hdo_omim_id))
    hdo_name = None
    hdo_omim_id = None
  elif line.startswith("name: "):
    hdo_name = line.replace("name: ", "")
  elif line.startswith("xref: OMIM:"):
    hdo_omim_id = line.replace("xref: OMIM:", "")

hdo_fp.close()
print("Total no. of OMIM IDs in HDO = {}".format(len(hdo_omim_dict)))

# ----------
omim_path = "/home/opencog-bio/bio-data/morbidmap"
omim_fp = open(omim_path, "r", encoding="utf-8", errors="ignore")

omim_ids = []
omim_match_cnt = 0

for line in omim_fp:
  omim_id = line.replace("\n", "").split("|")[2]
  omim_ids.append(omim_id)
  if hdo_omim_dict.get(omim_id) != None:
    omim_match_cnt = omim_match_cnt + 1
#  else:
#    print("{} not found in HDO".format(omim_id))

omim_fp.close()
print("Total no. of OMIM IDs in morbidmap = {}, of which found in HDO = {}".format(len(omim_ids), omim_match_cnt))

# ----------
tcmid_path = "raw_data/ingredient_targets_disease_drug-TCMID.v2.03.txt"
tcmid_fp = open(tcmid_path, "r", encoding="utf-8", errors="ignore")

tcmid_omim_ids = []
tcmid_match_cnt = 0

for line in tcmid_fp:
  tcmid_omim_ids_str = line.replace("\n", "").split("\t")[4].split(";")
  for toid in tcmid_omim_ids_str:
    if toid != "" and toid != "NA" and toid not in tcmid_omim_ids:
      tcmid_omim_ids.append(toid)
      if hdo_omim_dict.get(toid) != None:
        tcmid_match_cnt = tcmid_match_cnt + 1
#      else:
#        print("{} not found in HDO".format(toid))

tcmid_fp.close()
print("Total no. of OMIM IDs in TCMID = {}, of which found in HDO = {}".format(len(tcmid_omim_ids), tcmid_match_cnt))
