import glob
import json
import os
import sys


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
                print(each_data['sentence'])


if __name__ == "__main__":
    main()
