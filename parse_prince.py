import sys
from pathlib import Path
import csv

def get_next_no_number(lines, i):
  badEntry = False

  while "TAXABLE VALUE" not in lines[i] and "Fire Protection" not in lines[i]:
    i+=1
    
    if "******" in lines[i]:
      badEntry = True
      break

    if badEntry:
      badEntry = False
      print ("BAD ENTRY FOUND")
      return "", i

  i+=2
  return lines[i], i

def get_next_needs_number(lines, i):
  badEntry = False

  while ("TAXABLE VALUE" not in lines[i] and "Fire Protection" not in lines[i]) or not any(j.isdigit() for j in lines[i+2]):
    i+=1
    
    if "******" in lines[i]:
      badEntry = True
      break

    if badEntry:
      badEntry = False
      print ("BAD ENTRY FOUND")
      return "", i

  i+=2
  return lines[i], i

def split_owner_address(address):
  city = address.split(",")[0]
  state = address.split(",")[1].strip().split(" ")[0]
  zip_code = address.split(",")[1].strip().split(" ")[1]
  print (address)
  print (city)
  print (state)
  print (zip_code)
  print ()

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

  csv_file = str(file).split(".")[0] + "_results.csv"
  init_csv_file(csv_file)

  property_city = lines[3].split(" ")[1]

  in_element = False
  for i in range(0, len(lines)):
    line = lines[i]

    if in_element:
      if lines[i + 3] == "411 Apartment":

        property_address = lines[i]
        owner, i = get_next_no_number(lines, i)
        owner_address, i = get_next_needs_number(lines, i)

        po_box = None
        owner_address_zip, i = get_next_needs_number(lines, i)
        if "PO Box" in owner_address_zip:
          po_box = owner_address_zip
          owner_address_zip, i = get_next_needs_number(lines, i)

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
    print ("please enter the name of the file you would like the parse prince to parse.")
    print ("example:")
    print ("  python3 parse_prince.py Alden.txt")
    exit(1)

  file = Path(sys.argv[1])
  if not file.is_file():
    print (sys.argv[1] + " is not a valid file :(. Did you enter the file name exactly?")
    exit(1)

  parse(file)

