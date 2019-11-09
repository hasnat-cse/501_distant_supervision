import glob
import json
import os
import sys
import re
import os
import spacy
import random
from spacy import *
from random import sample
nlp = spacy.load("en_core_web_sm")

class SentenceInformation:
	"""docstring for SentenceInformation"""
	def __init__(self, modified_sentence, mappings, subject_path, object_path, LCA):
		self.modified_sentence = modified_sentence
		self.mappings = mappings
		self.subject_path = subject_path
		self.object_path = object_path
		self.LCA = LCA
		

def find_paths(sentence):


	flag = 0

	sentence = nlp(sentence)

	for x in sentence :

		if (x.text == "SUBJECT"):

			a = x

		if (x.text == "OBJECT"):

			b = x



	i = 0

	subject_path = []

	subject_path.append("SUBJECT")

	object_path = []

	object_path.append("OBJECT")

	while i < len(sentence):


		if (sentence[i] == a):

			a_head = sentence[i].head

			if (a == a_head):

				break

			else :


				subject_path.append(a_head.text)

			a = a_head

			i = 0

		else:

			i += 1


	i = 0
	while i < len(sentence):


		if (sentence[i] == b):

			b_head = sentence[i].head

			if (b == b_head):

				break

			else :

				object_path.append(b_head.text)

			b = b_head

			i = 0

		else:

			i += 1



	
	return subject_path , object_path	

	#displacy.serve(sentence, style='dep')


def find_LCA(subject_path, object_path):


	LCA = None

	for x in range (1, len(subject_path)):

		for y in range (1, len(object_path)):

			if (subject_path[x] == object_path[y]):

				LCA = subject_path[x]
				return LCA


	return LCA



# get file name excluding extension
def get_file_name_excluding_extension(file_path):
    # for windows machine
	file_path = file_path.replace("\\", '/')

	if file_path.find('/') == -1:
		filename_without_ext = file_path.rsplit('.', 1)[0]
	else:
		filename = file_path.rsplit('/', 1)[1]
		filename_without_ext = filename.rsplit('.', 1)[0]

	return filename_without_ext

# replace '[[ Natural Gas | /m/05k4k ]]' with 'Natural Gas'
def pre_process(sentence, subject_tag, object_tag):

    # pattern to find '[[ Natural Gas | /m/05k4k ]]'

	mappings = []


	entity_pattern = "\[\[\s*(.+?)\s+\|.+?\]\]"
	entities = re.findall(entity_pattern, sentence)

	

	tag_pattern = "\[\[\s*.+?\s+\|\s+(.+?)\s+\]\]"

	tags = re.findall(tag_pattern, sentence)



	modified_sentence = sentence

	count =	 1

	entity_count = 0

	for x in range(0,len(tags)):

		entity = entities[x]

		tag = tags[x]

		print(tag  + " " + entity + "\n")

        # pattern to find '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas'
		pattern = "\[\[\s*" + entity + "\s+\|\s+" + tag + "\s+\]\]"


		find = re.findall(pattern, sentence)

		

		if (tag == subject_tag):

			modified_sentence = re.sub(pattern, "SUBJECT", modified_sentence)

			mappings.append(tuple((find[0], "SUBJECT")))

		elif (tag == object_tag):

			modified_sentence = re.sub(pattern, "OBJECT", modified_sentence)

			mappings.append(tuple((find[0], "OBJECT")))


        # replace '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas' with 'Natural Gas'
		else :
			modified_sentence = re.sub(pattern, "ENTITY" + str(count), modified_sentence)

			mappings.append(tuple((find[0], "ENTITY" + str(count))))

			count += 1

		entity_count += 1


	mappings = set(mappings)

	return modified_sentence, mappings


def write_output(output_file, data):

	
	LCA_dictionary = {}

	f = open(output_file, "w")

	for each in data:

		if (each.LCA == None):

			continue;

		f.write(each.modified_sentence + "\n")

		for mapping in each.mappings:

			f.write("\""+mapping[1] + "\": " + mapping[0] + "\n")

		for x in range (0, len(each.subject_path)):

			if (x != len(each.subject_path)-1):

				f.write(each.subject_path[x] + "->")


			else:

				f.write(each.subject_path[x])

		f.write("\n")

		for y in range (0, len(each.object_path)):

			if (y != len(each.object_path)-1):

				f.write(each.object_path[y] + "->")

			else:

				f.write(each.object_path[y])

		f.write("\n")

		if (each.LCA == None):

			f.write ("None")

		else :

			f.write(each.LCA)

		f.write("\n\n")

		each.LCA = each.LCA.lower()

		if (each.LCA in LCA_dictionary):

			LCA_dictionary[each.LCA] = LCA_dictionary.get(each.LCA) + 1

		else :

			LCA_dictionary[each.LCA] = 1


	
	for x in LCA_dictionary:

		print(x+ " & " + str(LCA_dictionary[x]) + "\\\\\n")



def main():

	if len(sys.argv) == 1:
		data_folder_path = input("Enter Folder Path of data files: ")

	else:
		data_folder_path = sys.argv[1]


	if not os.path.exists("runs"):

		os.mkdir("runs")

	for filename in glob.glob(os.path.join(data_folder_path, "*.json")):

		output_file_path = "runs/" + get_file_name_excluding_extension(filename) + ".txt"

		sentence_info_list = []

		with open(filename) as f:

			json_data = json.load(f)
            # print(json.dumps(json_data, indent=4))

			#json_data = sample (json_data, 100)

			for each_data in json_data:

			

				sentence = each_data['sentence']
				pair = each_data['pair']

				subject = pair ['subject']

				subject_name = subject['name']

				subject_tag = subject ['mid']

				object = pair['object']

				object_name = object['name']

				object_tag = object ['mid']

				relation = each_data ['relation']
                # print(sentence)

                # remove entity tags from each sentence
				modified_sentence, mappings = pre_process(sentence, subject_tag, object_tag)

				print(modified_sentence)

				subject_path, object_path = find_paths(modified_sentence)

				print(subject_path)

				LCA = find_LCA(subject_path,object_path)

				if (LCA == None):

					print("None")

				else:

					print(LCA)

				sentence_info = SentenceInformation(modified_sentence,mappings,subject_path,object_path,LCA)

				sentence_info_list.append(sentence_info)


				

				

			
			f.close()

			write_output(output_file_path, sentence_info_list)	

		     

if __name__ == "__main__":
    main()
