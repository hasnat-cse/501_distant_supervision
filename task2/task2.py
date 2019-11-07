import glob
import json
import os
import sys
import re

import spacy

from spacy import *



nlp = spacy.load("en_core_web_sm")

def find_paths(sentence):

	sentence = nlp(sentence)

	a = "SUBJECT"

	b = "OBJECT"

	i = 0

	subject_path = []

	subject_path.append(a)

	object_path = []

	object_path.append(b)

	while i < len(sentence):


		if (sentence[i].text == a):

			a_head = sentence[i].head.text

			if (a == a_head):

				break

			else :

				subject_path.append(a_head)

			a = a_head

			i = 0

		else:

			i += 1


	i = 0
	while i < len(sentence):


		if (sentence[i].text == b):

			b_head = sentence[i].head.text

			if (b == b_head):

				break

			else :

				object_path.append(b_head)

			b = b_head

			i = 0

		else:

			i += 1



	
	return subject_path , object_path	

	#displacy.serve(sentence, style='dep')


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

	for tag in tags:

        # pattern to find '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas'
		pattern = "\[\[\s*.+?\s+\|\s+" + tag + "\s+\]\]"

		

		if (tag == subject_tag):

			modified_sentence = re.sub(pattern, "SUBJECT", modified_sentence)

			mappings.append(tuple((entities[entity_count], "SUBJECT")))

		elif (tag == object_tag):

			modified_sentence = re.sub(pattern, "OBJECT", modified_sentence)

			mappings.append(tuple((entities[entity_count], "OBJECT")))


        # replace '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas' with 'Natural Gas'
		else :
			modified_sentence = re.sub(pattern, "ENTITY" + str(count), modified_sentence)

			mappings.append(tuple((entities[entity_count], "ENTITY" + str(count))))

			count += 1

		entity_count += 1

	return modified_sentence, mappings


def main():

    if len(sys.argv) == 1:
        data_folder_path = input("Enter Folder Path of data files: ")

    else:
        data_folder_path = sys.argv[1]

    for filename in glob.glob(os.path.join(data_folder_path, "*.json")):


        with open(filename) as f:

            json_data = json.load(f)
            # print(json.dumps(json_data, indent=4))

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
                

                print (mappings)

                subject_path, object_path = find_paths(modified_sentence)

                print(subject_path)

                print(object_path)

                

        break        

if __name__ == "__main__":
    main()
