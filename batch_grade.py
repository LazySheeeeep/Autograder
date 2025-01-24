import os
import glob
import argparse
import json
from tqdm import tqdm
from auto_grade_hs import prepare_info, get_answerss, grade

def parse_arguments():
    parser = argparse.ArgumentParser(description="Batch grading script for Haskell (.hs) files.")
    parser.add_argument('-sd', '--submission-directory', type=str, required=True,
                        help="(e.g., './H1_submissions/').")
    parser.add_argument('-ti', '--test-inputs', type=str, default="in.txt")
    parser.add_argument('-to', '--test-outputs', type=str, default="out.txt")
    parser.add_argument('-sf', '--scores-file', type=str, default="scores.json")
    parser.add_argument('-cf', '--comments-file', type=str, default="comments.json")
    return parser.parse_args()

def grade_(hs_file):
    try:
        answerss = get_answerss(hs_file=hs_file, test_inputs=info["test_inputs"])
        score, comment = grade(answerss, info)
        userid = os.path.basename(hs_file).split("_")[1]
        scores[userid] = score
        if comment is not None:
            comments[userid] = comment
    except Exception as e:
        print(f"Failed to grade {hs_file}: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    info = prepare_info(args.test_inputs, args.test_outputs)
    comments = {}
    scores = {}
    for hs_file in tqdm(glob.glob(os.path.join(args.submission_directory, "*.hs"))):
        grade_(hs_file)
        
    
    with open(args.scores_file, "w") as file:
        json.dump(scores, file, indent=4)
    with open(args.comments_file, "w") as file:
        json.dump(comments, file, indent=4)
