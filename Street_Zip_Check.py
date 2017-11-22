#Street Names
#In the following code, some of the the street types, places such as shops and parks which have to be corrected are identified.
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

osm_file = "pune_india.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) # regular expression to match the last word of a string 
street_types=defaultdict(set) 

#list of street types              
expected = ["Street", "Avenue", "Gate", "Town", "Block","Marg","Drive", "Place", "Square", "Lane", "Road","Path" ,
            "Trail", "Park", "Commons","Phase","World","Lake","Nagar","Circle","Centre","Society",
            "Centre","Colony","Mall","Bazaar","Plaza","Stop","Stage","Station","Bunk","Area","Annexe","City","Ridge","Apartment"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name) # Searching for the last word in Street Name. 
    if m:
        street_type = m.group() # Groups for specific street types 
        if street_type not in expected: #Checking if the last word is present in the 'expected ' list of street types.
            street_types[street_type].add(street_name)
    
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street") 


street_types = defaultdict(set)
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if is_street_name(tag): 
                audit_street_type(street_types, tag.attrib['v']) 
				

#Last words of street names which were not present in the expected List. (Most of the names in Local Language)
for i in street_types:
    print i
	
	
	
#Pin Codes:
#Pune is a city in a district of the same name. 
#Pincodes which are out of the range of city limits are filtered out.	
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
pin_code_outside=[] #List of the Pincodes not in the city limits. 
pin_code_inside=[] #List of pincodes which are within the city limits, ie. from 411001 to 411053.
i=0
white_space=re.compile(r'\S+\s+\S+') 
for event, elem in ET.iterparse(osm_file):
    if elem.tag == "node" or elem.tag == "way": 
        for tag in elem.iter("tag"):
            if tag.attrib['k'] == "postal_code" or tag.attrib['k'] == "addr:postcode": 
                #some postalcodes are wrongly entred as a string
                if tag.attrib['v']=='Paschimanagari' or tag.attrib['v'] == 'spine Road':
                    i=i+1
                    #print tag.attrib['v']
                    continue
                #finding number of postal code have white space in between ie.. "411 012"
                elif white_space.search(tag.attrib['v']):
                    #print tag.attrib['v']
                    i=i+1
                    continue
                elif int(tag.attrib['v'].strip())<411001 or int(tag.attrib['v'].strip())>411053:                  
                    pin_code_outside.append(tag.attrib['v'])
                elif int(tag.attrib['v'].strip())>411001 or int(tag.attrib['v'].strip())<411053:                  
                    pin_code_inside.append(tag.attrib['v'])
print "Number of postal codes wrongly entered :",i                    
print "Number of Postal codes which line outside the city : ",len(pin_code_outside)
print "Number of Postal codes which belong to city limits 411001-411053 :",len(pin_code_inside)