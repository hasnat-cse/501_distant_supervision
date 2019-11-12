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
    def __init__(self, sentence, pos_tags, entities, incorrectly_tagged_entities):
        self.sentence = sentence  # each sentence in a relation
        self.pos_tags = pos_tags  # list of (word, tag) tuple for each word in the sentence
        self.entities = entities  # entity list in the sentence
        self.incorrectly_tagged_entities = incorrectly_tagged_entities  # incorrectly tagged entity list in the sentence


# replace '[[ Natural Gas | /m/05k4k ]]' with entity 'Natural Gas'
def remove_entity_tags_from_sentence(sentence):
    # pattern to find entity 'Natural Gas' from '[[ Natural Gas | /m/05k4k ]]'
    entity_tag_pattern = "\[\[\s*(.+?)\s+\|.+?\]\]"
    entities = re.findall(entity_tag_pattern, sentence)

    modified_sentence = sentence

    # replace all the tagged entities in a sentence with the entity only
    for entity in entities:
        # escape special characters in entity string
        escaped_entity = re.escape(entity)

        # pattern to find '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas'
        pattern = "\[\[\s*" + escaped_entity + "\s*\|.+?\]\]"

        # replace '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas' with 'Natural Gas'
        modified_sentence = re.sub(pattern, entity, modified_sentence)

    return modified_sentence, entities


# write information regarding each sentence to output file
# take random 100 sentences
def write_output(output_file, data):
    f = open(output_file, "w")

    # random sampling of 100 sentences
    if len(data) > 100:
        random_100_data = sample(data, 100)

    # no need of sampling if sentences are less than or equal to 100
    else:
        random_100_data = data

    for each in random_100_data:

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
def identify_incorrectly_tagged_entity(entities, pos_tags):
    incorrectly_tagged_entities = []

    # for each entity
    for entity in entities:

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
                    incorrectly_tagged_entities.append(entity)
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

            # process each sentence in the relation
            for each_data in json_data:

                sentence = each_data['sentence']

                # remove entity tags from the sentence
                modified_sentence, entities = remove_entity_tags_from_sentence(sentence)

                # get pos_tags for each word in the sentence
                pos_tags = tag_sentence(modified_sentence)

                # identify incorrectly tagged entities
                incorrectly_tagged_entities = identify_incorrectly_tagged_entity(entities, pos_tags)

                # store information only for the incorrectly-tagged sentences
                if len(incorrectly_tagged_entities) > 0:
                    # store information about pos tags, entities, incorrectly tagged entities for the sentence
                    sentence_info = SentenceInformation(sentence, pos_tags, entities, incorrectly_tagged_entities)
                    sentence_info_list.append(sentence_info)

            f.close()

            # write information about sampled sentences in a relation in the output file
            write_output(output_file_path, sentence_info_list)


if __name__ == "__main__":
    main()
