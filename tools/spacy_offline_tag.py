#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 The Wenchen Li. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
spacy NER offline tagging into the brat .ann format

"""
from argparse import ArgumentParser
from os.path import dirname, join as path_join

import spacy

try:
	from json import dumps
except ImportError:
	# likely old Python; try to fall back on ujson in brat distrib
	from sys import path as sys_path

	sys_path.append(path_join(dirname(__file__), '../../server/lib/ujson'))
	from ujson import dumps
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

### Constants
ARGPARSER = ArgumentParser(description='XXX')  # XXX:
ARGPARSER.add_argument('-p', '--port', type=int, default=47111,
                       help='port to run the HTTP service on (default: 47111)')
TAGGER = None
MODEL = 'en'


def tag_to_json(nlp, text):
	doc = nlp(text)

	annotations = {}

	def _add_ann(start, end, _type):
		annotations[len(annotations)] = {
			'type': _type,
			'offsets': ((start, end),),
			'texts': ((text[start:end]),),
		}

	for ent in doc.ents:
		if u'\n' in text[ent.start_char:ent.end_char]: continue  # currently spacy recognize \n as GPE
		_add_ann(ent.start_char, ent.end_char, ent.label_)

	return annotations


def load_text_from_file(file_path):
	with open(file_path, "r") as fi:
		result = fi.readlines()

	return "".join(result).decode("utf-8")


def offline_annotate_to_ann_file(file_path):
	"""
	annotate text file offline and save annotated file as brat .ann file for NER

	For example:
	entity number, type, start_char, end_char, corresponding str
	T1	CARDINAL 105 108	362
	T2	PERSON 33 48	Selloff Worsens
	:param tag_json:
	"""
	# spacy config
	MODEL = 'en'

	# writer config
	entity_start = "T"
	start_entity_index = 0
	tab = "\t"
	space = " "

	KEY_TEXT = "texts"
	KEY_TYPE = "type"
	KEY_OFFSETS = "offsets"

	# annotate first
	text = load_text_from_file(file_path)
	tagger = spacy.load(MODEL)
	tag_result = tag_to_json(tagger, text)

	# write to file as .ann file

	ann_filename = file_path.replace("txt", "ann")
	with open(ann_filename, 'w') as fo:
		for k in sorted(tag_result.keys()):
			_type = tag_result[k][KEY_TYPE]
			_offsets = tag_result[k][KEY_OFFSETS]
			_text = unicode(tag_result[k][KEY_TEXT][0]).replace('\u', " ")

			line = entity_start + str(k) + tab + _type + space + str(_offsets[0][0]) + space + str(
				_offsets[0][1]) + tab + _text
			fo.write(line + "\n")


def check_exists_ann_file(text_file_path):
	"""
	check whether exists annotated file
	:param text_file_path: .txt file to be annotated
	:return:bool | whether the corresponding annotation file exists
	"""
	return os.path.isfile(text_file_path.replace(".txt", ".ann"))


def check_ann_file_annotated(text_file_path):
	"""
	check whether ann file annotated
	:param text_file_path:.txt file to be annotated
	:return:bool | whether the corresponding annotation file has been annotated
	"""
	return os.stat(text_file_path.replace(".txt", ".ann")).st_size > 0


def walk_directory_get_unannotated(seed_path):
	"""
	walk through the dir under seed path and find all unannotated file
	:param seed_path: str| under which directory the files will be annotated
	:return: text_need_ann, list of str| unannotated files, path start from the seed_path(so relative)
	"""
	text_need_ann = []

	for root, dirs, files in os.walk(seed_path):
		path = root.split(os.sep)
		# print((len(path) - 1) * '---', os.path.basename(root))
		for file in files:
			# print(len(path) * '---', file)
			if file.endswith(".txt"): # is the text file to be annotated
				# check .ann
				full_file_path = root + '/' + file
				if check_exists_ann_file(full_file_path) and check_ann_file_annotated(full_file_path):continue
				else: #need annotation
					text_need_ann.append(full_file_path)

	return text_need_ann

if __name__ == '__main__':
	# example annotate single file
	# file_path = '/home/wenchen/projects/brat/data/news/bloomberg/1.txt'
	# offline_annotate_to_ann_file(file_path)

	# example walk through given directory
	seed_path = '/home/wenchen/projects/brat/data/news'
	print (walk_directory_get_unannotated(seed_path))
