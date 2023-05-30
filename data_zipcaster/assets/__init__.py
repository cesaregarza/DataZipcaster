import json
import pathlib

path = pathlib.Path(__file__).parent / "gear_hashes.json"
with open(path, "r") as f:
    GEAR_HASHES = json.load(f)
