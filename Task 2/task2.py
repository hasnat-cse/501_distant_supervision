import glob
import json
import os
import sys
import re
import os
import spacy
import random
from spacy import *
from random import sample

nlp = spacy.load("en_core_web_sm")

#A class to store all the information for each sentence
class SentenceInformation:


    def __init__(self, modified_sentence, mappings, subject_path, object_path, LCA):
        self.modified_sentence = modified_sentence
        self.mappings = mappings
        self.subject_path = subject_path
        self.object_path = object_path
        self.LCA = LCA


def find_paths(sentence):
    

    sentence = nlp(sentence) #Builds the dependency tree. 

    #Take the subject token into variable "a" and the object token into variable "b"
    for x in sentence:

        if (x.text == "SUBJECT"):
            a = x

        if (x.text == "OBJECT"):
            b = x

    i = 0

    subject_path = []

    #subject path starts with "SUBJECt"
    subject_path.append("SUBJECT")

    object_path = []

    #object path starts with "OBJECT"
    object_path.append("OBJECT")

    #Traverse the tokens of a sentence to find the "SUBJECT" token
    while i < len(sentence):

        if (sentence[i] == a): #If we find the subject token

            a_head = sentence[i].head #Go to it's head. That will be the next token in the path

            if (a == a_head): #If head is equal to the token itself, that means the token is the root.

                break #So we stop here

            else:

                subject_path.append(a_head.text) #otherwise add the token to subject path

            a = a_head

            i = 0

        else:

            i += 1

    i = 0

    #Traverse the tokens of a sentence to find the "OBJECT" token
    while i < len(sentence):

        if (sentence[i] == b): #if we find the object token

            b_head = sentence[i].head #go to its head. That will be the next token in the path 

            if (b == b_head): #if the head is equal to the token itself, that means token is the root

                break #so we stop here

            else:

                object_path.append(b_head.text) #otherwise add the token to object path

            b = b_head

            i = 0

        else:

            i += 1

    return subject_path, object_path




def find_LCA(subject_path, object_path):
    LCA = None

    for x in range(1, len(subject_path)): #we start from the 2nd element of the path. Because 1st element is "SUBJECT"

        for y in range(1, len(object_path)): #similarly for object, we start from the 2nd element of the path

            if (subject_path[x] == object_path[y]): #the first match is the LCA
                LCA = subject_path[x]
                return LCA

    return LCA


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


# replace '[[ Natural Gas | /m/05k4k ]]' with 'Natural Gas' and get all the mappings
def pre_process(sentence, subject_tag, object_tag):
   

    mappings = []

    entity_pattern = "\[\[\s*(.+?)\s+\|.+?\]\]" #pattern to find all the entities
    entities = re.findall(entity_pattern, sentence)

    tag_pattern = "\[\[\s*.+?\s+\|\s+(.+?)\s+\]\]" #patter to find all the tags
    tags = re.findall(tag_pattern, sentence)

    modified_sentence = sentence

    count = 1

    entity_count = 0

    #iterate over all the tags
    for x in range(0, len(tags)):

        entity = entities[x] #get the corresponding entity of the tag

        tag = tags[x]
        

        # escape special characters in entity string
        escaped_entity = re.escape(entity)

        # escape special characters in tag string
        escaped_tag = re.escape(tag)

        # pattern to find '[[ Natural Gas | /m/05k4k ]]' for entity 'Natural Gas' and tag '/m/05k4k'
        pattern = "\[\[\s*" + escaped_entity + "\s+\|\s+" + escaped_tag + "\s+\]\]"

        find = re.findall(pattern, sentence) #actually we will get only 1 match, as we are checking entity,tag pairs

        if (tag == subject_tag): #if the tag matches the subject tag. then we replace the pattern match with "SUBJECT"

            modified_sentence = re.sub(pattern, "SUBJECT", modified_sentence)

            mappings.append(tuple((find[0], "SUBJECT")))

        elif (tag == object_tag): #if the tag matches the object tag. then we replace the pattern match with "OBJECT"

            modified_sentence = re.sub(pattern, "OBJECT", modified_sentence)

            mappings.append(tuple((find[0], "OBJECT")))


        
        else: #otherwise we replace the pattern match with ENTITY1, ENTITY2, ENTITY3 etc
            modified_sentence = re.sub(pattern, "ENTITY" + str(count), modified_sentence)

            mappings.append(tuple((find[0], "ENTITY" + str(count))))

            count += 1

        entity_count += 1

    mappings = set(mappings)

    return modified_sentence, mappings


def write_output(output_file, data):

    f = open(output_file, "w")

    #data is a list of objects. We iterate over the objects
    for each in data:

        

        f.write(each.modified_sentence + "\n") #First we write the modified sentence

        #Then writes the mappings between actual entities and their surrogates
        for mapping in each.mappings:
            f.write("\"" + mapping[1] + "\": " + mapping[0] + "\n")


        #Then we write the path from subject to root
        for x in range(0, len(each.subject_path)):

            if (x != len(each.subject_path) - 1):

                f.write(each.subject_path[x] + "->")


            else:

                f.write(each.subject_path[x])

        f.write("\n")

        #Then we write the path from object to root
        for y in range(0, len(each.object_path)):

            if (y != len(each.object_path) - 1):

                f.write(each.object_path[y] + "->")

            else:

                f.write(each.object_path[y])

        f.write("\n")

        #If the LCA is None (when subject/object is the root), then we write None
        if (each.LCA == None):

            f.write("None")

        #Otherwise we write the LCA
        else:

            f.write(each.LCA)

        f.write("\n\n\n") #One new line and two blank lines

        

def main():
    if len(sys.argv) == 1:
        data_folder_path = input("Enter Folder Path of data files: ")

    else:
        data_folder_path = sys.argv[1]

    if not os.path.exists("runs"): #if a folder called runs does not exist
        os.mkdir("runs") #make a folder called runs

    for filename in glob.glob(os.path.join(data_folder_path, "*.json")): #iterate over files in the data folder

        output_file_path = "runs/" + get_file_name_excluding_extension(filename) + ".txt" #output file name

        sentence_info_list = []

        with open(filename) as f:

            json_data = json.load(f) #reads all the json data in a file

            json_data = sample (json_data, 100) #Takes 100 random samples from the json data

            for each_data in json_data:

                sentence = each_data['sentence']
                pair = each_data['pair']

                subject = pair['subject']

                subject_name = subject['name']

                subject_tag = subject['mid']

                object = pair['object']

                object_name = object['name']

                object_tag = object['mid']

                relation = each_data['relation']
                

                # remove entity tags from each sentence
                modified_sentence, mappings = pre_process(sentence, subject_tag, object_tag)


                #Finds the paths from subject to root, and object to root
                subject_path, object_path = find_paths(modified_sentence)

                #Finds the LCA of subject and object
                LCA = find_LCA(subject_path, object_path)

                #Forms a class object with all the gathered information
                sentence_info = SentenceInformation(modified_sentence, mappings, subject_path, object_path, LCA)

                #The class object is appended to a list of objects
                sentence_info_list.append(sentence_info)

            f.close() #Close the file after 1 file is done

            write_output(output_file_path, sentence_info_list) #writes output for 1 file


if __name__ == "__main__":
    main()
