import sys, pathlib, io, re
from pprint import pprint
from pymediainfo import MediaInfo, Track
from timecode import Timecode, TimecodeRange
from . import parse_memo

PAT_ALE_CHARACTERS_REJECT = re.compile(r"[\r\n\t]+")

ALE_HEADER = """Heading
FIELD_DELIM	TABS
VIDEO_FORMAT	1080
FILM_FORMAT	35mm, 4 perf
AUDIO_FORMAT	48khz
FPS	24
"""

def write_ale(ale_data:list[dict], file_stream:io.TextIOBase):



	print(ALE_HEADER, file=file_stream)

	cols = []
	for shot in ale_data:
		cols.extend(list(shot.keys()))
	ale_columns = set(cols)
	
	print("Column", file=file_stream)
	print("\t".join(str(c) for c in ale_columns), file=file_stream, end="\t\n\n")

	print("Data", file=file_stream)
	for shot in ale_data:
		print("\t".join(
			PAT_ALE_CHARACTERS_REJECT.sub("  ",str(shot.get(c,""))) for c in ale_columns
		), file=file_stream, end="\t\n")




def get_timecode_track(mediainfo:MediaInfo) -> Track:
	"""Discern the Timecode track from mediainfo"""
	for track in mediainfo.other_tracks:
		if track.type.lower() == "time code":
			return track
	return None

def get_timecode_range(mediainfo:MediaInfo) -> TimecodeRange:
	"""Generate a `TimecodeRange` from the mediainfo"""
	tc_track = get_timecode_track(mediainfo)
	
	if not tc_track:
		raise ValueError(f"No timecode track in file")
	
	frame_rate = int(float(tc_track.frame_rate))
	
	return TimecodeRange(
		start=Timecode(tc_track.time_code_of_first_frame, rate=frame_rate),
		duration=int(tc_track.frame_count)
	)

for pkg in {pathlib.Path(x) for x in sys.argv[1:] if pathlib.Path(x).is_dir()}:

	ale_data = []
	submission_notes = dict()

	for notes in pkg.glob("*.xls*"):
		if notes.name.startswith("."):
			print(f"Skipping {notes.name}")
			continue

		try:
			print(f"Reading notes from {notes.name}...")
			package_notes = parse_memo.parse_notes_from_memo(notes)
		except Exception as e:
			print(f"Skipping {notes.name}: {e}")
		
		for comp, comp_note in package_notes.items():
			if comp in submission_notes:
				print(f"{comp} already noted...")
				continue
			submission_notes[comp] = comp_note


	for comp in pkg.glob("*.mov"):
		
		if comp.name.startswith("."):
			print(f"Skipping {comp.name}")
			continue

		mediainfo = MediaInfo.parse(comp)

		vfx_id, vfx_version = pathlib.Path(comp).stem.split("_Comp_",1)
		tc_range = get_timecode_range(mediainfo)

		ale_data.append({
			"Name": pathlib.Path(comp).stem,
			"Source File": pathlib.Path(comp).name,
			"Start": tc_range.start,
			"Duration": tc_range.duration-1, #...investigate
			"Labroll": vfx_id,
			"Auxiliary TC1": tc_range.start,
			"VFX ID": vfx_id,
			"VFX Version": vfx_version,
			"Frame Count Start": tc_range.start.frame_number,
			"VFX": "FRM-" + str(tc_range.start.frame_number).zfill(9),
			"VFX Package": pathlib.Path(comp).parent.name,
			"VFX Submission Notes": submission_notes.get(pathlib.Path(comp).stem, "")
		})

		print(ale_data)

	output_path = pathlib.Path(pkg, pkg.name+".ale")

	with open(output_path,"w") as output_file:
		write_ale(ale_data, output_file)
	
	print(f"Written to {output_path}")