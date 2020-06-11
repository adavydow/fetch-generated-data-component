import argparse
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, TextIO

import cv2
import numpy as np
from argparse_path import PathType

logging.basicConfig(level=logging.INFO)

def parse_arguments():
    parser = argparse.ArgumentParser(prog="coeffs-to-synthesis",
                                     description="Builds and saves eos-compatible models based on synthesis meshes..")
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('--token', required=True, type=str,
                          help="generated.photos token")
    required.add_argument('--range', nargs=2, type=int, required=True,
                          help="range of ids to download, should be multiple of 100")
    required.add_argument('--ethnicity', required=True, type=str,
                          help="ethnicity")
    required.add_argument('--output', required=True, type=PathType(exists=None, type="dir"),
                          help="path to directory to save synthesis meshes")
    parser._action_groups.append(optional)
    return parser.parse_args()


def gen_age(age_code):
    age_map = {"elderly": np.arange(40, 79),
               "adult": np.arange(25, 40),
               "young-adult": np.arange(18, 25)}
    return np.random.choice(age_map[age_code])


def gen_ethnicity(ethnicity_code):
    ethnicity_map = {"white": "white",
                     "black": "black",
                     "asian": "asian",
                     "latino": "hisp"}
    return ethnicity_map[ethnicity_code]


def process_json(json_path: Path, id_num: int, td: Path, output: Path, csv: TextIO) -> int:
    with Path(json_path).open("r") as f:
        data = json.load(f)
    for face in data["faces"]:
        logging.info(f"processing id={id_num}")
        name = f"v{face['version']}_{face['id']}"
        url = ""
        for url_dict in face["urls"]:
            if "transparent_1024" in url_dict:
                url = url_dict["transparent_1024"]
        meta = face["meta"]
        if len(meta["age"]) == 0:
            continue
        age_code = meta["age"][0]
        if age_code in ["child", "infant"]:
            continue
        age = gen_age(age_code)
        if len(meta["gender"]) == 0:
            continue
        gender = meta["gender"][0]
        if not meta["ethnicity"] or len(meta["ethnicity"]) == 0:
            ethnicity = "white"
        else:
            ethnicity = gen_ethnicity(meta["ethnicity"][0])

        csv.write(f"{id_num},{gender},{ethnicity},{age},{name}\n")
        (output / str(id_num)).mkdir()
        subprocess.run(["curl", "--retry", "50000", "--retry-max-time",
                        "50000", url, "-o", f"{str(td / 'tmp.png')}"])
        img = cv2.imread(str(td / 'tmp.png'))
        cv2.imwrite(f"{output / str(id_num) / 'photo.jpg'}", img)
        id_num += 1
    return id_num


def main():
    args = parse_arguments()
    token: str = args.token
    rng: List[int] = args.range
    ethnicity: str = args.ethnicity
    output: Path = args.output

    output.mkdir(exist_ok=True, parents=True)

    if ethnicity == "hisp":
        ethnicity = "latino"

    range_min, range_max = rng
    assert range_min % 100 == 0
    assert range_max % 100 == 0
    id_num = 1
    with (output / "info.csv").open("wt") as csv:
        csv.write("id,gender,ethnicity,age,name\n")
        with tempfile.TemporaryDirectory() as td:
            for page in range(range_min // 100 + 1, range_max // 100 + 1):
                logging.info(f"Processing page: {page}")
                request = ["curl"]
                request.append("--header")
                request.append(f"Authorization: API-Key {token}")
                request.append("--retry")
                request.append("50000")
                request.append("--retry-max-time")
                request.append("50000")
                request.append(f"https://api.generated.photos/api/v1/faces?page="
                               f"{page}&emotion=neutral&hair_length=short&per_page=100"
                               f"&order_by=oldest&ethnicity={ethnicity}")
                request.append("-o")
                request.append(str(Path(td) / "output.json"))
                subprocess.run(request)
                id_num = process_json(Path(td) / "output.json", id_num, Path(td), output, csv)
                page += 1


if __name__ == "__main__":
    main()
