import sys, pathlib, pprint
import openpyxl

def get_header_indexes(line):

	headers = dict()

	for idx, header in enumerate(line):
		if header:
			headers[header] = idx
	
	return headers

def get_submission_notes(lines, headers):

	submission_notes = dict()
	
	for line in lines:

		shot = line[headers["Version Name"]]
		print(shot)
		notes = line[headers["Submission  Notes"]]
		print(notes)

		if shot and shot.lower().startswith("snl"):
			submission_notes[shot] = notes
	
	return submission_notes
		

wb = openpyxl.load_workbook(sys.argv[1])

for sheet in wb:
	print(f"Reading {sheet.title}")

	lines = sheet.values
	for line in lines:
	
		if "Version Name" in line:
			headers = get_header_indexes(line)
			print(headers)

			submission_notes = get_submission_notes(lines, headers)
			pprint.pprint(submission_notes)