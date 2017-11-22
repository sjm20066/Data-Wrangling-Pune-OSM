#After auditing is complete the next step is to prepare the data to be inserted into a SQL database.
#The codes in this cell will update the street names and postal codes and convert them from XLM to CSV 
#These csv files can then easily be imported to a SQL database as tables.
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs
import csv
import schema
import cerberus
SCHEMA=schema.schema
OSMFILE='sample.osm' #using sample as a OSM file
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Make sure the fields order in the csv matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

#This function update the street names and postal codes by calling update_street_names and update_pincode functions
def shape_element(element, default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = [] 
    node_tags={}
    # checking if the tag is "Node"
    if element.tag == 'node':
        for k in element.attrib:
            #checking if 'K ' is in NODE_FIELDS
            if k in NODE_FIELDS:
                node_attribs[k]=element.attrib[k]
        for x in element:
            # Checking if the element has the child tag "tag"
            if x.tag=='tag':
                # searching for problematic charecters
                if PROBLEMCHARS.search(x.attrib["k"]):
                    continue
                elif LOWER_COLON.match(x.attrib['k']) :
                    node_tags['id']=element.attrib['id']
                    #spliting "key" and "type"  in 'K' attribute
                    node_tags['key']=x.attrib['k'].split(":",1)[1] #
                    node_tags['type']=x.attrib['k'].split(":",1)[0]
# update_street_name" function will equate the cleaned street name  
                    if x.attrib['k']=='addr:street':
                        node_tags['value']=update_street_name(x.attrib['v'],mapping)
# update_pincode" function will equate the filtered postal codes  
                    elif x.attrib['k']=='addr:postcode':
                        if update_pincode(x.attrib['v']):
                            node_tags['value']=update_pincode(x.attrib['v'])
                        else:
                            continue
# If the value of k is " postal_code" and by calling "update_pincode" function will equate the filtered postal codes 
#The 'type' here, will be 'regular'
                elif x.attrib['k']=='post_code':
                    if update_postalcode(x.attrib['v']):
                        node_tags["value"]=update_postalcode(x.attrib["v"])
                        node_tags["type"]='regular'
                        node_tags["key"]=x.attrib["k"]
                        node_tags["id"]=element.attrib["id"]
                    else:
                        continue
#Now for the remaining k values.
                else:
                    node_tags["type"]='regular'
                    node_tags["key"]=x.attrib["k"]
                    node_tags["id"]=element.attrib["id"]
                    node_tags["value"]=x.attrib["v"]
                tags.append(node_tags)
        return {'node': node_attribs, 'node_tags': tags}
# Now for Way,
    elif element.tag == 'way':
        for x in element.attrib:
            if x in WAY_FIELDS:
                way_attribs[x]=element.attrib[x]
        count=0
        for l in element.iter("nd"):
            way_nodes.append({'id':element.attrib['id'],'node_id':l.attrib['ref'],'position':count})
            count+=1
        for y in element:
            if y.tag=='tag':
                if PROBLEMCHARS.search(y.attrib["k"]):
                    continue
                elif LOWER_COLON.match(y.attrib['k']):
                    node_tags['id']=element.attrib['id']
                    node_tags['key']=y.attrib['k'].split(":",1)[1]
                    node_tags['type']=y.attrib['k'].split(":",1)[0]
                    if y.attrib['k']=='addr:street':
                        node_tags['value']=update_street_name(y.attrib['v'], mapping)
                    elif y.attrib['k']=='addr:postcode':
                        node_tags['value']=update_pincode(y.attrib['v'])
                elif y.attrib['k']=='post_code':
                    node_tags["value"]=update_postalcode(y.attrib["v"])
                    node_tags["type"]='regular'
                    node_tags["key"]=y.attrib["k"]
                    node_tags["id"]=element.attrib["id"]
                else:
                    node_tags["type"]='regular'
                    node_tags["key"]=y.attrib["k"]
                    node_tags["id"]=element.attrib["id"]
                    node_tags["value"]=y.attrib["v"]
                tags.append(node_tags) 
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}   
    
#THE FOLLOWING CODE IS TO CONVERT THE XML INTO CSV 
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem           
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(OSMFILE, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'wb') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'wb') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(OSMFILE, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(osm_file, validate=False)