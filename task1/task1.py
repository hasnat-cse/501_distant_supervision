import glob
import json
import os
import sys
import re


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
                # print(sentence)

                # remove entity tags from each sentence
                modified_sentence = remove_entity_tags_from_sentence(sentence)
                print(modified_sentence)


if __name__ == "__main__":
    main()
