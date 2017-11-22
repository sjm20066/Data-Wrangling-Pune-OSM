#1.Street Name Cleaning
#Updating the wrongly entred street names
from collections import defaultdict
import re
import pprint
import xml.etree.cElementTree as ET
#Let us create a dictionary to correct the wrongly entered street names.
mapping = { "St": "Saint","udyog":"Udyog","pedestrian":"Pedestrian","chaulk":"Chowk",
            "St.": "Street",
            "Ave":"Avenue","chowk":"Chowk","J13":'',
            "Rd":"Road","cross":"Cross",
            "Rd.":"Road",
            "nagar":"Nagar","road":"Road","raod":"Road",
           "apartment":"Apartment","no.":""," , Pune":""
               
            }
keys=mapping.keys() #creating a list of keys present in mapping dictionary
#print keys
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
PROBLEMCHARS = re.compile(r'[=\+/&-<>;\'"\?%#$@\,\. \t\r\n]') #regular expression to identify problematic charecters in a string
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+') #regular expression to match or search "abc:def"

def update_street_name(name, mapping):#function to update wrongly entred street names
#To check if the last word is in the key list, and if it is, then coreccting it and returning the whole word.
        m = street_type_re.search(name)
        if m:
            street_type=m.group()
    
            if street_type in keys:
                value=mapping[street_type]
                y=name.find(street_type)#finds the index of wrongly entred street type in street name
                z=name[:y]+value # street name + updated street type
                return z
# There are some street names which ends with numbers such as "Phase 2,Avenue 5 etc...", The following codes will remove the numnerical values.
            else:
                try: 
                    type(int(street_type))
                    position=name.find(street_type)
                    remove_numbers=name[:position]
                    return remove_numbers
            #If street names have "," ,")" in the last word they are replaced with ""
                except ValueError:
                    x = name.replace(", "," ").replace(" ,"," ").replace("No. 34/2","").replace(" No.","").replace(" no.","").replace(",","")
                    return x
					
					
					
#Street names after cleaning
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way": 
        for tag in elem.iter("tag"):
            if is_street_name(tag):#checking if it is a street name
                #print "Before:",tag.attrib['v']
                #print "After:",update_street_name(tag.attrib['v'], mapping) 
				
				
				

				
#2. Postal Code Cleaning
#Correcting wrongly entered pincodes.
white_space=re.compile(r'\S+\s+\S+')
COLON= re.compile(r'^([a-z]|_)+:')
def update_pincode(pincode):
    if white_space.search(pincode):
        x=pincode.replace(" ","") #replacing the white space in pincodes "411 210 " with "411210"
        #returning the corrected value
        return x 
#below codes returns None if the Postal code is wrongly entred  or the Postal codes lie outside the city pincode range 
    elif pincode=='Paschimanagari' or pincode== 'spine Road': #after testing it's found that some postal code value is entred as string
        return None
    elif int(pincode)<411001 or int(pincode)>411053:
        return None
    elif COLON.search(pincode):#after testing it's found that some pincode is entred as "en:Talegaon railway station" 
        return None
    else:
        return pincode 
		
		
#Postal codes after cleaning
for event, elem in ET.iterparse(osm_file):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if tag.attrib['k'] == "postal_code" or tag.attrib['k'] == "addr:postcode":
                #print "Before :",tag.attrib['v']
                #print "After :",update_pincode(tag.attrib['v'])