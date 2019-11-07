import glob
import json
import os
import sys
import re

from nltk import pos_tag
from nltk.tag.stanford import StanfordPOSTagger


class Output:
    def __init__(self, sentence, pos_tags, entities, incorrectly_tagged_entities):
        self.sentence = sentence
        self.pos_tags = pos_tags
        self.entities = entities
        self.incorrectly_tagged_entities = incorrectly_tagged_entities


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


# write data to output file
def write_output(output_file, data):
    f = open(output_file, "w")

    for each in data:
        f.write(each.sentence + "\n")

        for word_tag_tuple in each.pos_tags:
            f.write(word_tag_tuple[0] + ' ' + word_tag_tuple[1] + "\n")

        # For testing
        for entity in each.incorrectly_tagged_entities:
            f.write(entity + "\n")

        # two blank lines
        f.write("\n\n")

    f.close()


def identify_incorrectly_tagged_entity(entities, pos_tags):
    incorrectly_tagged_entities = []
    for entity in entities:
        words_in_entity = entity.split()

        for word in words_in_entity:
            for word_tag in pos_tags:

                if word == word_tag[0] and len(word_tag[1]) >= 2 and word_tag[1][0:2] != "NN":
                    incorrectly_tagged_entities.append(entity)
                    break

    return incorrectly_tagged_entities


def tag_sentence(stanford_tagger, sentence):
    token_list = sentence.split()
    # return stanford_tagger.tag(token_list)
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

    _path_to_model = 'stanford-postagger/english-bidirectional-distsim.tagger'
    _path_to_jar = 'stanford-postagger/stanford-postagger.jar'
    st_tagger = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)

    for filename in glob.glob(os.path.join(data_folder_path, "*.json")):

        output_file_path = "runs/" + get_file_name_excluding_extension(filename) + ".txt"

        output_list = []

        with open(filename) as f:

            json_data = json.load(f)
            # print(json.dumps(json_data, indent=4))

            for each_data in json_data:
                sentence = each_data['sentence']
                # print(sentence)

                # remove entity tags from each sentence
                modified_sentence, entities = remove_entity_tags_from_sentence(sentence)
                # print(modified_sentence)

                pos_tags = tag_sentence(st_tagger, modified_sentence)

                incorrectly_tagged_entities = identify_incorrectly_tagged_entity(entities, pos_tags)

                output = Output(modified_sentence, pos_tags, entities, incorrectly_tagged_entities)
                output_list.append(output)

            f.close()

            write_output(output_file_path, output_list)

        break


if __name__ == "__main__":
    main()
