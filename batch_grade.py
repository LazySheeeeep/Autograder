import os
import glob
import argparse
import csv
import json
from tqdm import tqdm
from auto_grade_hs import prepare_info, get_answerss, grade

SFUID_COL = "SIS User ID"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Batch grading script for Haskell (.hs) files.")
    parser.add_argument('-sd', '--submission-directory', type=str, required=True,
                        help="(e.g., './H1_submissions/').")
    parser.add_argument('-ti', '--test-inputs', type=str, default="in.txt")
    parser.add_argument('-to', '--test-outputs', type=str, default="out.txt")
    parser.add_argument('-sf', '--score-file', type=str, default="../Grades-CMPT383_D100.csv")
    parser.add_argument('-cf', '--comments-file', type=str, default="comments.json")
    parser.add_argument('-cn', '--column-name', type=str, required=True)
    return parser.parse_args()

def load_csv(filename):
    scores = {}

    with open(filename, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames

        for row in list(reader):
            sfuid = row.get(SFUID_COL, "")
            if sfuid:
                scores[sfuid] = row
                scores[sfuid][args.column_name] = 0.0  # initial score
            else:
                ...
    return scores, fieldnames

def save_csv(output_file, fieldnames, content_dict):
    with open(output_file, mode="w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in content_dict.values():
            writer.writerow(row)

if __name__ == "__main__":
    args = parse_arguments()
    auto_grade_script = "../auto_grade_hs.py"
    comments = {}
    scores, fieldnames = load_csv(args.score_file)
    info = prepare_info(args.test_inputs, args.test_outputs)
    
    for hs_file in tqdm(glob.glob(os.path.join(args.submission_directory, "*.hs"))):
        try:
            basename = os.path.basename(hs_file)
            sfuid = basename[-12:-3]
            if "-" in sfuid:
                sfuid = basename[-14:-5]
            if not sfuid.isdigit():
                raise Exception(f"cannot extract sfuid from {basename}.")
            elif sfuid not in scores:
                raise Exception(f"sfuid {sfuid} does not exist.")
            answerss = get_answerss(hs_file=hs_file, test_inputs=info["test_inputs"])
            score, comment = grade(answerss, info)
            scores[sfuid][args.column_name] = score
            if comment is not None:
                comments[scores[sfuid]["ID"]] = comment

        except Exception as e:
            print(f"Failed to grade {hs_file}: {e}")

    save_csv("scores.csv", fieldnames, scores) # args.score_file
    with open(args.comments_file, "w") as file:
        json.dump(comments, file, indent=4)
