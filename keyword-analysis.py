# coding=utf-8
import sys
import pandas as pd
from os.path import isfile
from alchemyapi import AlchemyAPI
import json
import time
from watson_developer_cloud import ConceptExpansionV1Beta as ConceptExpansion

alchemyapi = AlchemyAPI()

concept_expansion = ConceptExpansion(username='380ede59-4420-4b00-8f8d-d7db9603b1dc',
                                     password='NzqtkZXTTpvZ')

def get_processed_data(data):
	df = pd.read_excel(data)
	processed_data = []
	for index, row in df.iterrows():
		story = row[1]
		processed_data.append(story)
	return processed_data

def main(data):
	processed_data = get_processed_data(data)
	i = 0
	for story in processed_data:
		print "Processing data for: "
		print story
		keyword_response = alchemyapi.keywords('text', story)
		taxonomy_response = alchemyapi.taxonomy('text', story)
		
		all_keywords = keyword_response["keywords"]
		if "taxonomy" in taxonomy_response:
			all_taxonomy = taxonomy_response["taxonomy"]
		else:
			all_taxonomy = []
		
		# seeds to be used later
		seeds = []
		j = 1
		for keyword in all_keywords:
			relevance = keyword["relevance"]
			text = keyword["text"]
			seeds.append(text)
			print "Processing keyword %s" %j
			print "%s: %s" %(text, relevance)
			j += 1
		
		if len(seeds) == 0:
			continue

		j = 1
		for taxonomy in all_taxonomy:
			score = taxonomy["score"]
			label = taxonomy["label"]
			print "Processing taxonomy %s" %j
			print "%s: %s" %(label, score)

		print "Processing Concept expansion for %s" %seeds
		job_id = concept_expansion.create_job(dataset='mtsamples', seeds=seeds)
		# print(json.dumps(job_id, indent=2))

		time.sleep(5)  # sleep for 5 seconds
		job_status = concept_expansion.get_status(job_id)

		while job_status['status'] == 'in progress' or job_status['status'] == 'awaiting work':
			time.sleep(5)  # sleep for 5 seconds
			job_status = concept_expansion.get_status(job_id)
			print(json.dumps(job_status, indent=2))

		if job_status['status'] == 'done':
			results = concept_expansion.get_results(job_id)
			print(json.dumps(results, indent=2))

		i += 1 
		if i >= 5:
			break

if __name__=="__main__":
	if len(sys.argv) != 2:
		sys.exit('Usage: %s <story file>' %sys.argv[0])
	data = sys.argv[1]
	if not isfile(data):
		sys.exit('Usage: %s <story file>' %sys.argv[0])
	main(data)