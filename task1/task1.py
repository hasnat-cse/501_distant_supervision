import glob
import json
import os
import sys
import re

from nltk import pos_tag
from nltk import word_tokenize

from random import sample


# store information about each incorrectly tagged sentence in a relation
class SentenceInformation:
    def __init__(self, sentence, pos_tags, mappings, incorrectly_tagged_entities):
        self.sentence = sentence  # each sentence in a relation
        self.pos_tags = pos_tags  # list of (word, tag) tuple for each word in the sentence
        self.mappings = mappings  # list of (entity_with_tag, entity) tuple for each entity in the sentence
        self.incorrectly_tagged_entities = incorrectly_tagged_entities  # incorrectly tagged entity list in the sentence


# replace '[[ Natural Gas | /m/05k4k ]]' with entity 'Natural Gas'
def remove_entity_tags_from_sentence(sentence):
    # pattern to find entity with tag '[[ Natural Gas | /m/05k4k ]]'
    entity_with_tag_pattern = "\[\[.*?\]\]"

    entity_with_tags = re.findall(entity_with_tag_pattern, sentence)

    # pattern to find entity 'Natural Gas' from '[[ Natural Gas | /m/05k4k ]]'
    entity_pattern = "\[\[\s*(.+?)\s+\|"

    # list of (entity_with_tag, entity) tuple for each entity in the sentence
    entity_with_tag_and_entity_mappings = []

    for entity_with_tag in entity_with_tags:

        # find entity from entity with tag
        entity = re.findall(entity_pattern, entity_with_tag)

        if len(entity) > 0:
            entity_with_tag_and_entity_mappings.append(tuple((entity_with_tag, entity[0])))

    modified_sentence = sentence

    # replace all the tagged entities in a sentence with the entity
    for mapping in entity_with_tag_and_entity_mappings:
        modified_sentence = modified_sentence.replace(mapping[0], mapping[1])

    return modified_sentence, entity_with_tag_and_entity_mappings


# write information regarding each incorrectly tagged sentence to output file
def write_output(output_file, data):
    f = open(output_file, "w")

    for each in data:

        # output the sentence
        f.write(each.sentence + "\n")

        # output pos tag for each word in the sentence
        for word_tag_tuple in each.pos_tags:
            f.write(word_tag_tuple[0] + ' ' + word_tag_tuple[1] + "\n")

        # output all the incorrectly tagged entities
        for entity in each.incorrectly_tagged_entities:
            f.write(entity + "\n")

        # output two blank lines
        f.write("\n\n")

    f.close()


# identify entity that are incorrectly tagged in a sentence
def identify_incorrectly_tagged_entity(mappings, pos_tags):
    incorrectly_tagged_entities = []

    # for each entity
    for mapping_tuple in mappings:

        # mappings is a list of (entity_with_tag, entity) tuple
        entity_with_tag = mapping_tuple[0]
        entity = mapping_tuple[1]

        # get words of the entity
        words_in_entity = word_tokenize(entity)

        non_noun_tag_found = False

        # for each word in the entity
        for word in words_in_entity:

            # find the pos tag for the word
            for word_tag in pos_tags:

                # if the word contains pos tag that is not Noun (not started with 'NN')
                # then the entity will be identified as incorrect tagged
                if word == word_tag[0] and len(word_tag[1]) >= 2 and word_tag[1][0:2] != 'NN':
                    incorrectly_tagged_entities.append(entity_with_tag)
                    non_noun_tag_found = True
                    break

            # if any non noun pos tag found then continue search for next entity
            if non_noun_tag_found:
                break

    return incorrectly_tagged_entities


# tag each word in a sentence
def tag_sentence(sentence):
    # get token list for the sentence
    token_list = word_tokenize(sentence)

    return pos_tag(token_list)


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


def main():
    # get data folder path from sys arg or user
    if len(sys.argv) == 1:
        data_folder_path = input("Enter Folder Path of data files: ")

    else:
        data_folder_path = sys.argv[1]

    # create 'runs' folder if not exists for output
    if not os.path.exists('runs'):
        os.mkdir('runs')

    # process each relation one by one
    for filename in glob.glob(os.path.join(data_folder_path, "*.json")):

        # get output file path
        output_file_path = "runs/" + get_file_name_excluding_extension(filename) + ".txt"

        sentence_info_list = []

        with open(filename) as f:

            # load json data from file
            json_data = json.load(f)

            # if data length is more than the sample size of 100
            if len(json_data) > 100:
                sampled_data = sample(json_data, 100)

            # if data length is less than or equal sample size of 100
            else:
                sampled_data = json_data

            # process each sentence in the relation
            for each_data in sampled_data:

                sentence = each_data['sentence']

                # remove entity tags from the sentence
                modified_sentence, mappings = remove_entity_tags_from_sentence(sentence)

                # get pos_tags for each word in the sentence
                pos_tags = tag_sentence(modified_sentence)

                # identify incorrectly tagged entities
                incorrectly_tagged_entities = identify_incorrectly_tagged_entity(mappings, pos_tags)

                # store information only for the incorrectly-tagged sentences
                if len(incorrectly_tagged_entities) > 0:
                    # store information about pos tags, mappings, incorrectly tagged entities for the sentence
                    sentence_info = SentenceInformation(sentence, pos_tags, mappings, incorrectly_tagged_entities)
                    sentence_info_list.append(sentence_info)

            f.close()

            # write information about sampled sentences in a relation in the output file
            write_output(output_file_path, sentence_info_list)


if __name__ == "__main__":
    main()
