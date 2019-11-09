import glob
import json
import os
import sys
import re

from nltk import pos_tag


# store information about each sentence in a relation
class SentenceInformation:
    def __init__(self, sentence, pos_tags, entities, incorrectly_tagged_entities):
        self.sentence = sentence  # each sentence in a relation
        self.pos_tags = pos_tags  # list of (word, tag) tuple for each word in the sentence
        self.entities = entities  # entity list in the sentence
        self.incorrectly_tagged_entities = incorrectly_tagged_entities  # incorrectly tagged entity list in the sentence


# replace '[[ Natural Gas | /m/05k4k ]]' with 'Natural Gas'
def remove_entity_tags_from_sentence(sentence):
    # pattern to find '[[ Natural Gas | /m/05k4k ]]'
    entity_tag_pattern = "\[\[\s*(.+?)\s+\|.+?\]\]"
    entities = re.findall(entity_tag_pattern, sentence)

    modified_sentence = sentence
    for entity in entities:
        # pattern to find '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas'
        pattern = "\[\[\s*" + entity + "\s*\|.+?\]\]"

        # replace '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas' with 'Natural Gas'
        modified_sentence = re.sub(pattern, entity, modified_sentence)

    return modified_sentence, entities


# write information regarding each sentence to output file
def write_output(output_file, data):
    f = open(output_file, "w")

    for each in data:
        f.write(each.sentence + "\n")

        for word_tag_tuple in each.pos_tags:
            f.write(word_tag_tuple[0] + ' ' + word_tag_tuple[1] + "\n")

        for entity in each.incorrectly_tagged_entities:
            f.write(entity + "\n")

        # two blank lines
        f.write("\n\n")

    f.close()


# identify entity that are incorrectly tagged in a sentence
def identify_incorrectly_tagged_entity(entities, pos_tags):
    incorrectly_tagged_entities = []
    for entity in entities:
        words_in_entity = entity.split()

        non_noun_tag_found = False
        for word in words_in_entity:
            for word_tag in pos_tags:

                # if any word of the entity contains pos tag that is not Noun or not started with 'N' than it will be identified as incorrect
                if word == word_tag[0] and len(word_tag[1]) >= 1 and word_tag[1][0:1] != 'N':
                    incorrectly_tagged_entities.append(entity)
                    non_noun_tag_found = True
                    break

            if non_noun_tag_found:
                break

    return incorrectly_tagged_entities


# tag each word in a sentence
def tag_sentence(sentence):
    token_list = sentence.split()
    return pos_tag(token_list)


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


def main():
    if len(sys.argv) == 1:
        data_folder_path = input("Enter Folder Path of data files: ")

    else:
        data_folder_path = sys.argv[1]

    # create 'runs' folder if not exists for output
    if not os.path.exists('runs'):
        os.mkdir('runs')

    # process each relation one by one
    for filename in glob.glob(os.path.join(data_folder_path, "*.json")):

        output_file_path = "runs/" + get_file_name_excluding_extension(filename) + ".txt"

        sentence_info_list = []

        with open(filename) as f:

            json_data = json.load(f)
            count = 1

            # process each sentence in the relation
            for each_data in json_data:

                # consider first 100 sentences
                if count > 100:
                    break

                sentence = each_data['sentence']
                # print(sentence)

                # remove entity tags from the sentence
                modified_sentence, entities = remove_entity_tags_from_sentence(sentence)
                # print(modified_sentence)

                # get pos_tags for each word in the sentence
                pos_tags = tag_sentence(modified_sentence)

                # identify incorrectly tagged entities
                incorrectly_tagged_entities = identify_incorrectly_tagged_entity(entities, pos_tags)
                if len(incorrectly_tagged_entities) > 0:
                    count += 1
                    # store information for each sentence
                    sentence_info = SentenceInformation(sentence, pos_tags, entities, incorrectly_tagged_entities)
                    sentence_info_list.append(sentence_info)

            f.close()

            # write information about all the sentence in a relation in output file
            write_output(output_file_path, sentence_info_list)


if __name__ == "__main__":
    main()
