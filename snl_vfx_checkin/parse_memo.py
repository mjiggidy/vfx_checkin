"""
Read the VFX Submission Memos delivered with a VFX package, and associate each comp with its submission note
"""

import pathlib
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
		#print(shot)
		notes = line[headers["Submission  Notes"]]
		#print(notes)

		if shot and shot.lower().startswith("snl"):
			submission_notes[shot] = notes
	
	return submission_notes
		

def parse_notes_from_memo(path_memo:str|pathlib.Path) -> dict[str,str]:
	wb = openpyxl.load_workbook(path_memo)

	for sheet in wb:
		#print(f"Reading {sheet.title}")

		lines = sheet.values
		for line in lines:
		
			if "Version Name" in line:
				headers = get_header_indexes(line)
				#print(headers)

				submission_notes = get_submission_notes(lines, headers)
				#pprint.pprint(submission_notes)
				return submission_notes