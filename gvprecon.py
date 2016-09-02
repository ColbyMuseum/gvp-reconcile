'''
GVPRecon - Reconcile embARK fields to the Getty Vocabs
'''

import argparse, json, gvpquery
from pprint import pprint

# V0.1, Just do "Display_Obj_Type" fields to the AAT.

# FUTURE V0.2, bounce reconciliation choices to disk.

# FUTURE V0.3, Take "Artist" and reconcile to the AAT.

# FUTURE V0.5, Take "Material" and "Support" (or "Display_Material" if those don't exist) and reconcile to the AAT.

def results_prompt(results):
	print '\n----------------------------------------'
	print 'Received reconcilliation results for "%s": ' % obj_type

	user_choice = 0
	new_term = ''
	
	if len(results) > 0:
		for i,result in enumerate(query.query_results):
			print "%d: %s" % (i,result['label']['value'])
		
		raw_choice = raw_input('Choose a reconcilliation result ([ENTER] accepts 0): ')
		
		try:
			user_choice = int(raw_choice)
			if user_choice >= len(results):
				print "Got out of range user_choice"
		except:
			print 'Int cast failed, insert 0'
			user_choice = 0
	else:
		new_term = raw_input('No results found, please enter new search term or s(k)ip:')

	return user_choice, new_term

#-1: Take the filename from arg0 of the command-line call
parser = argparse.ArgumentParser(description='Reconcile CCMA json to the Getty Vocabulary.')
parser.add_argument('json_file', metavar='file', type=argparse.FileType('rb', 0)) 
# TODO: Add an optional reconciliation mapping file 
args = parser.parse_args()

# TODO: Check if there is a reconciliation map and load it if it exists

#0: Read the JSON file into a JSON object
objects_artists_exhibs = json.load(args.json_file)

#1: Iterate through the objects and add their Display_Obj_Type as a key to a dict
object_types = dict()
for obj in objects_artists_exhibs['objects']:
	obj_type = obj['Disp_Obj_Type']
	if not obj_type in object_types.keys():
		object_types[obj_type] = dict()

#2: Iterate dict keys and ask the GVP for each, saving the results in a dict
aat_dict = dict()
for obj_type in object_types.keys():
	query = gvpquery.AATQuery(obj_type)
	query.reconcile()

	user_choice, new_term = results_prompt(query.query_results)

	if new_term is 'k':
		print 'Skipping "%s"' % obj_type
	elif not new_term is '':
		query = gvpquery.AATQuery(new_term)
		query.reconcile()
		user_choice, new_term = results_prompt(query.query_results)

		if user_choice < len(query.query_results):
			print "Input type is %s and term is %s" % (obj_type, query.query_results[user_choice]['label']['value'])
			object_types[obj_type]['term'] = query.query_results[user_choice]['label']['value']
			object_types[obj_type]['url'] = query.query_results[user_choice]['entry']['value']

 	else: # new_term is an empty string, use user_choice
		if user_choice < len(query.query_results):
			print "Input type is %s and term is %s" % (obj_type, query.query_results[user_choice]['label']['value'])
			object_types[obj_type]['term'] = query.query_results[user_choice]['label']['value']
			object_types[obj_type]['url'] = query.query_results[user_choice]['entry']['value']

#4: Iterate objects, adding field to each object for "Obj_Type_Link" field (or something)
for obj in objects_artists_exhibs['objects']:
	object_type = obj['Disp_Obj_Type']
	if object_types[object_type] in aat_dict.keys():
		term = object_types[object_type]['term']
		url = object_types[object_type]['url']
		obj[u'Obj_Type_AAT'] = term
		obj[u'Obj_Type_AAT_URL'] = url
	else:
		obj[u'Obj_Type_AAT'] = u''
		obj[u'Obj_Type_AAT_URL'] = u''
		
#5: Bounce to disk
f = open('reconciled.json','w')
json.dump(objects_artists_exhibs,f)
f.close()

f = open('map.json','w')
json.dump(object_types,f)
f.close()
