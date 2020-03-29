import sys
from pathlib import Path
import csv

def is_digit(element):
  return any(i.isdigit() for i in element)

def get_next_no_number(lines, i):
  badEntry = False

  while True:
    if "******" in lines[i]:
      badEntry = True
      break

    if "TAXABLE VALUE" in lines[i] or "Fire Protection" in lines[i]:
      break

    i+=1

  if badEntry:
    badEntry = False
    return "", i

  i+=2
  return lines[i], i

def get_next_needs_number(lines, i):
  badEntry = False

  while True:
    if "******" in lines[i]:
      badEntry = True
      break

    if ("TAXABLE VALUE" in lines[i] or "Fire Protection" in lines[i]) and is_digit(lines[i+2]):
      break

    i+=1

  if badEntry:
    badEntry = False
    return "", i

  i+=2
  return lines[i], i

def get_owner_address_zip(lines, i):
  while "******" not in lines[i]:

    line = lines[i].strip()
    line_split = line.split(" ")

    if len(line_split) >= 3 and is_digit(line_split[-1]) and len(line_split[-2]) == 2 and line_split[-3][-1] == ",":
      return line, i
    i+=1
  return "",i

def split_owner_address(address):
  city = address.split(",")[0]
  state = address.split(",")[1].strip().split(" ")[0]
  zip_code = address.split(",")[1].strip().split(" ")[1]

  return city, state, zip_code

def init_csv_file(file):
  with open(file, 'w+', newline='') as outFile:
    writer = csv.writer(outFile)
    writer.writerow(["OWNER 1 LABEL NAME", "MAIL ADDRESS", "MAIL CITY", "MAIL STATE", "MAIL ZIP CODE", "PROPERTY ADDRESS", "PROPERTY CITY"])

def write_to_file(file, property_address, property_city, owner_name, owner_address, owner_po, owner_city, owner_state, owner_zip):
  if owner_po is not None:
    owner_address = owner_po + " " + owner_address

  with open(file, 'a+', newline='') as outFile:
    writer = csv.writer(outFile)
    writer.writerow([owner_name, owner_address, owner_city, owner_state, owner_zip, property_address, property_city])

def parse(file: Path):
  lines = None
  with open(file) as f:
    lines = [line.rstrip() for line in f]

  csv_file = "results/" + str(file).split("/")[1].split(".")[0] + "_results.csv"
  init_csv_file(csv_file)

  property_city = lines[3].split(" ")[1]

  in_element = False
  for i in range(0, len(lines)):
    line = lines[i]

    if in_element:
      if len(lines) > i+4 and lines[i + 3] == "411 Apartment" and lines[i + 4] != "- CONDO":

        property_address = lines[i]
        
        owner, i = get_next_no_number(lines, i)
        if (owner == ""):
          print ("ERROR: failed to parse address: ["+ property_address +"]")
          exit(1)
          continue;

        owner_address, i = get_next_needs_number(lines, i)
        if (owner_address == ""):
          print ("ERROR: failed to parse address: ["+ property_address +"]")
          exit(1)
          continue;

        owner_address_zip, i = get_owner_address_zip(lines, i)

        po_box = None
        if (owner_address_zip == ""):
          print ("ERROR: failed to parse address: ["+ property_address +"]")
          continue;

        if "PO Box" in owner_address_zip:
          po_box = owner_address_zip
          owner_address_zip, i = get_next_needs_number(lines, i)
          if (owner_address_zip == ""):
            print ("ERROR: failed to parse address: ["+ property_address +"]")
            exit(1)
            continue;

        owner_address_city, owner_address_state, owner_address_zip = split_owner_address(owner_address_zip)
        write_to_file(
          csv_file,
          property_address, property_city,
          owner, owner_address, po_box, owner_address_city, owner_address_state, owner_address_zip
        )

      in_element = False

    if "*******" in line:
      in_element = True

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print ("please enter the name of the directory that contains files you want to parse.")
    print ("example:")
    print ("  python3 parse_prince.py source")
    exit(1)

  directory = Path(sys.argv[1])

  files = list(directory.glob('**/*.txt'))
  for file in files:
    parse(file)

