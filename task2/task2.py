import glob
import json
import os
import re
import sys
from random import sample

import spacy
from spacy import *

nlp = spacy.load("en_core_web_sm")


# store information about sampled sentences in a relation
class SentenceInformation:
    """docstring for SentenceInformation"""

    def __init__(self, modified_sentence, mappings, subject_path, object_path, LCA):
        self.modified_sentence = modified_sentence    # modified sentence after preprocessing
        self.mappings = mappings    # mapping of replaced entity_tags and placeholders
        self.subject_path = subject_path    # subject entity of the sentence
        self.object_path = object_path      # object entity of the sentence
        self.LCA = LCA              # Least common ancestor of the subject and object


# find paths of subject and object in a sentence parsing tree
def find_paths(sentence):

    sentence = nlp(sentence)

    for x in sentence:

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

            else:

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

            else:

                object_path.append(b_head.text)

            b = b_head

            i = 0

        else:

            i += 1

    return subject_path, object_path


def find_LCA(subject_path, object_path):
    LCA = None

    for x in range(1, len(subject_path)):

        for y in range(1, len(object_path)):

            if (subject_path[x] == object_path[y]):
                LCA = subject_path[x]
                return LCA

    return LCA


# get file name excluding extension
def get_file_name_excluding_extension(file_path):
    # for windows machine only, replace '\' with '/' in file path
    file_path = file_path.replace("\\", '/')

    # if file path doesn't contain '/' then get the file name after splitting using '.'
    if file_path.find('/') == -1:
        filename_without_ext = file_path.rsplit('.', 1)[0]

    # if file path contains '/' then split the file name using '/' first and then using '.'
    else:
        filename = file_path.rsplit('/', 1)[1]
        filename_without_ext = filename.rsplit('.', 1)[0]

    return filename_without_ext


# replace entity_tags with placeholders
def pre_process(sentence, subject_tag, object_tag):

    mappings = []

    # pattern to find entity 'Natural Gas' from '[[ Natural Gas | /m/05k4k ]]'
    entity_pattern = "\[\[\s*(.+?)\s+\|.+?\]\]"
    entities = re.findall(entity_pattern, sentence)

    # pattern to find tag '/m/05k4k' from '[[ Natural Gas | /m/05k4k ]]'
    tag_pattern = "\[\[\s*.+?\s+\|\s+(.+?)\s+\]\]"

    tags = re.findall(tag_pattern, sentence)

    modified_sentence = sentence

    count = 1

    entity_count = 0

    for x in range(0, len(tags)):

        entity = entities[x]

        tag = tags[x]

        # escape special characters in entity string
        escaped_entity = re.escape(entity)

        # escape special characters in tag string
        escaped_tag = re.escape(tag)

        # pattern to find '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas' and tag '/m/05k4k'
        pattern = "\[\[\s*" + escaped_entity + "\s+\|\s+" + escaped_tag + "\s+\]\]"

        find = re.findall(pattern, sentence)

        if (tag == subject_tag):

            modified_sentence = re.sub(pattern, "SUBJECT", modified_sentence)

            mappings.append(tuple((find[0], "SUBJECT")))

        elif (tag == object_tag):

            modified_sentence = re.sub(pattern, "OBJECT", modified_sentence)

            mappings.append(tuple((find[0], "OBJECT")))

        else:
            modified_sentence = re.sub(pattern, "ENTITY" + str(count), modified_sentence)

            mappings.append(tuple((find[0], "ENTITY" + str(count))))

            count += 1

        entity_count += 1

    mappings = set(mappings)

    return modified_sentence, mappings


# write information regarding each sentence to output file
def write_output(output_file, data):
    f = open(output_file, "w")

    for each in data:

        f.write(each.modified_sentence + "\n")

        for mapping in each.mappings:
            f.write("\"" + mapping[1] + "\": " + mapping[0] + "\n")

        for x in range(0, len(each.subject_path)):

            if (x != len(each.subject_path) - 1):

                f.write(each.subject_path[x] + "->")


            else:

                f.write(each.subject_path[x])

        f.write("\n")

        for y in range(0, len(each.object_path)):

            if (y != len(each.object_path) - 1):

                f.write(each.object_path[y] + "->")

            else:

                f.write(each.object_path[y])

        f.write("\n")

        if (each.LCA == None):

            f.write("None")

        else:

            f.write(each.LCA)

        f.write("\n\n")


def main():

    # get data folder path from sys arg or user
    if len(sys.argv) == 1:
        data_folder_path = input("Enter Folder Path of data files: ")

    else:
        data_folder_path = sys.argv[1]

    # create 'runs' folder if not exists for output
    if not os.path.exists("runs"):
        os.mkdir("runs")

    # process each relation one by one
    for filename in glob.glob(os.path.join(data_folder_path, "*.json")):

        # get output file path
        output_file_path = "runs/" + get_file_name_excluding_extension(filename) + ".txt"

        sentence_info_list = []

        with open(filename) as f:

            # load json data from file
            json_data = json.load(f)

            # take random sample of 100 sentences
            json_data = sample(json_data, 100)

            # process each sentence in the sample
            for each_data in json_data:
                sentence = each_data['sentence']
                pair = each_data['pair']

                subject = pair['subject']

                subject_tag = subject['mid']

                object = pair['object']

                object_tag = object['mid']

                # replace entity tags in the sentence
                modified_sentence, mappings = pre_process(sentence, subject_tag, object_tag)

                # find path for subject and object in the tree
                subject_path, object_path = find_paths(modified_sentence)

                # find least common ancestor for the subject and object
                LCA = find_LCA(subject_path, object_path)

                # store information about preprocessed sentence, entity mappings, subject and object path, and lca
                sentence_info = SentenceInformation(modified_sentence, mappings, subject_path, object_path, LCA)

                sentence_info_list.append(sentence_info)

            f.close()

            # write information about the sampled sentences in a relation in the output file
            write_output(output_file_path, sentence_info_list)


if __name__ == "__main__":
    main()
