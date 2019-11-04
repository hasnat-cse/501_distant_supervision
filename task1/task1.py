import glob
import json
import os
import sys
import re
from nltk.tag.stanford import StanfordPOSTagger


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

    return modified_sentence


# write data to output file
def write_output(output_file, data):
    f = open(output_file, "w")

    for sentence in data:
        f.write(sentence + "\n")

    f.close()


def tag_sentences(sentence_list):
    _path_to_model = 'stanford-postagger/english-bidirectional-distsim.tagger'
    _path_to_jar = 'stanford-postagger/stanford-postagger.jar'
    st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)

    for sentence in sentence_list:
        token_list = sentence.split()

        print(st.tag(token_list))
        break


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

    for filename in glob.glob(os.path.join(data_folder_path, "*.json")):

        output_file_path = "runs/" + get_file_name_excluding_extension(filename) + ".txt"

        modified_sentence_list = []

        with open(filename) as f:

            json_data = json.load(f)
            # print(json.dumps(json_data, indent=4))

            for each_data in json_data:
                sentence = each_data['sentence']
                # print(sentence)

                # remove entity tags from each sentence
                modified_sentence = remove_entity_tags_from_sentence(sentence)
                # print(modified_sentence)

                modified_sentence_list.append(modified_sentence)

            f.close()

            tag_sentences(modified_sentence_list)

            write_output(output_file_path, modified_sentence_list)

        break


if __name__ == "__main__":
    main()
