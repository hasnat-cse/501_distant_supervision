import glob
import json
import os
import sys
import re

import spacy

from spacy import *



nlp = spacy.load("en_core_web_sm")

def dependency_parsing(sentence, subject_name, object_name, relation):

	sentence = nlp(sentence)

	a = "SUBJECT"

	b = "OBJECT"

	for token in sentence :


		if (token.text == a):

			a_head = token.head.text

			print (a_head)


		if (token.text == b):

			b_head = token.head.text

			print (b_head)

		


	#displacy.serve(sentence, style='dep')


# replace '[[ Natural Gas | /m/05k4k ]]' with 'Natural Gas'
def pre_process(sentence, subject_tag, object_tag):

    # pattern to find '[[ Natural Gas | /m/05k4k ]]'
	entity_pattern = "\[\[\s*(.+?)\s+\|.+?\]\]"
	entities = re.findall(entity_pattern, sentence)

	tag_pattern = "\[\[\s*.+?\s+\|\s+(.+?)\s+\]\]"

	tags = re.findall(tag_pattern, sentence)



	modified_sentence = sentence

	count =	 1
	for tag in tags:

        # pattern to find '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas'
		pattern = "\[\[\s*.+?\s+\|\s+" + tag + "\s+\]\]"

		if (tag == subject_tag):

			modified_sentence = re.sub(pattern, "SUBJECT", modified_sentence)

		elif (tag == object_tag):

			modified_sentence = re.sub(pattern, "OBJECT", modified_sentence)

        # replace '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas' with 'Natural Gas'
		else :
			modified_sentence = re.sub(pattern, "ENTITY" + str(count), modified_sentence)

			count += 1

	return modified_sentence


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
                modified_sentence = pre_process(sentence, subject_tag, object_tag)
                

                dependency_parsing(modified_sentence, subject_name, object_name, relation)

                break;

        break        

if __name__ == "__main__":
    main()
