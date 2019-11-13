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




def find_paths(sentence):
    flag = 0

    sentence = nlp(sentence)

    displacy.serve(sentence, style='dep')

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




def main():


	subject_path, object_path = find_paths("SUBJECT plays OBJECT , who has inherited the new mantle of tough-as-nails ENTITY1 .")

if __name__ == "__main__":
    main()
