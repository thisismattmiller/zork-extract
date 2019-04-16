import json
import re


debug = False

all_data = []

tell_regex = re.compile(r'<TELL.*?CR>|<TELL.*?">',re.MULTILINE|re.DOTALL)
jigsup_regex = re.compile(r'<JIGS-UP.*?">',re.MULTILINE|re.DOTALL)
tables_regex = re.compile(r'<TABLE.*?">',re.MULTILINE|re.DOTALL)
quotes_regex = re.compile(r'".*?"')
verb_extract_regex = re.compile(r'VERB\?\s(.*?)>')
replace_something_regex = re.compile(r'"\s+D\s.*?"')


def replace_vars(line):

	line = line.replace('" D ,PRSI "','object')
	line = line.replace('" D .AV "','wooden bucket')	
	line = line.replace('" D .V "','villan')	
	line = line.replace('" D .VILLAIN "','villan')	
	line = line.replace('" D .VILLAIN "','villan')	
	line = line.replace('" D .W "','steel')	
	line = line.replace('" D ,PRSO "','object')	
	line = line.replace('" D .OBJ "','object')	
	line = line.replace('" D .X "','object')	
	line = line.replace('" D .NWEAPON "','weapon')	
	line = line.replace('" .STR "','things')	

	return line


# data from https://github.com/historicalsource/
for file in ['1actions.zil','2actions.zil','3actions.zil']:

	used_line_numbers = {}
	line_to_line_number_lookup = {}


	raw_text = ""
	with open(file) as file_in:
		raw_text = file_in.read()

	# some <0x0c> chars lurking in these files messing up python line spliting
	raw_text = raw_text.replace("\f",'')
	raw_text = raw_text.replace('\\"',"'")


	split_text = raw_text.splitlines()

	all_tells = tell_regex.findall(raw_text)
	for t in all_tells:
		if debug:
			raw_text = raw_text.replace(t,'--\n')

		replace_with = ' '.join(t.replace('\n',' ').split())

		longest_part = max(t.splitlines(), key=len)
		pos_from_start=t.splitlines().index(longest_part)


		for i, l in enumerate(split_text):
			if longest_part in l and i not in used_line_numbers:
				used_line_numbers[i] = True
				line_to_line_number_lookup[replace_with] = i-pos_from_start+1
				break
		raw_text = raw_text.replace(t,"\n" + replace_with)


	all_jigs = jigsup_regex.findall(raw_text)
	for j in all_jigs:

		if debug:
			raw_text = raw_text.replace(j,'--\n')

		replace_with = ' '.join(j.replace('\n',' ').split())
		longest_part = max(j.splitlines(), key=len)
		pos_from_start=j.splitlines().index(longest_part)


		for i, l in enumerate(split_text):
			if longest_part in l and i not in used_line_numbers:
				used_line_numbers[i] = True
				line_to_line_number_lookup[replace_with] = i-pos_from_start+1
				break

		raw_text = raw_text.replace(j,"\n" + replace_with)


	raw_text = raw_text.replace("<TELL","\n<TELL")


	if debug:
		with open(file+'.debug','w') as outfile:
			outfile.write(raw_text)

	split_text = raw_text.splitlines()
	# json.dump(line_to_line_number_lookup,open('tmp.json','w'),indent=2)

	for i, line in enumerate(split_text):

		if 'TELL' in line or 'JIGS-UP' in line:



			found = False
			for key in line_to_line_number_lookup.keys():
				if line.strip()[0:len(line)-10] in key:
					found = line_to_line_number_lookup[key]
					


			if found != False:

				line = replace_vars(line)
				texts = quotes_regex.findall(line)

				text_filtered = []
				for x in texts:
					if len(x) > 12:
						text_filtered.append(x)

				verbs = []
				if len(split_text) > i+2:						
					for x in range(i, i+2):
						if "VERB" in split_text[x] and '<COND' not in split_text[x]:
							v = verb_extract_regex.findall(split_text[x])
							verbs = verbs + v
							break

				if len(verbs) > 0:
					verbs = verbs[0].split()

				if len(''.join(text_filtered)) > 15:

					type = "jigs-up"
					if 'TELL' in line:
						type = 'tell' 

					zork = '1'
					if '2' in file:
						zork = '2'
					if '3' in file:
						zork = '3'
					all_data.append({'id': len(all_data)+1, 'zork':zork,'type':type, 'text':text_filtered, 'verbs':verbs,'line':found  })



json.dump(all_data,open('data.json','w'),indent=2)
