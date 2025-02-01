import os
import glob
import argparse
import json
from tqdm import tqdm
from auto_grade_hs import prepare_info, get_answerss, grade_answerss
from auto_check import check_ok
import shutil

def parse_arguments():
    parser = argparse.ArgumentParser(description="Batch grading script for Haskell (.hs) files.")
    parser.add_argument('-sd', '--submission-directory', type=str, required=True,
                        help="(e.g., './H1_submissions/').")
    parser.add_argument('-ti', '--test-inputs', type=str, default="in.txt")
    parser.add_argument('-to', '--test-outputs', type=str, default="out.txt")
    parser.add_argument('-sf', '--scores-file', type=str, default="scores.json")
    parser.add_argument('-cf', '--comments-file', type=str, default="comments.json")
    parser.add_argument('-pf', '--prompt-file', type=str, default="prompt.txt")
    parser.add_argument('-m', '--model', type=str, help="Model name for the ollama service.")
    return parser.parse_args()

def grade_file(hs_file):
    try:
        answerss = get_answerss(hs_file=hs_file, test_inputs=info["test_inputs"])
        score, comment = grade_answerss(answerss, info)
        userid = os.path.basename(hs_file).split("_")[1]
        scores[userid] = score
        if comment is not None:
            comments[userid] = comment
        if assistance and not check_ok(hs_file, prompt, args.model):
            double_check_files.append((userid, hs_file))
    except Exception as e:
        print(f"Failed to grade {hs_file}: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    info = prepare_info(args.test_inputs, args.test_outputs)
    comments = {}
    scores = {}
    assistance = False
    double_check_files = []

    if os.path.exists(args.prompt_file) and args.model is not None:
        assistance = True
        with open(args.prompt_file, 'r') as f:
            prompt = f.read()
    
    for hs_file in tqdm(glob.glob(os.path.join(args.submission_directory, "*.hs"))):
        grade_file(hs_file)

    if len(double_check_files) > 0:
        print(f"{len(double_check_files)} files need to double-check.")
        double_check_dir = "double_check"
        os.makedirs(double_check_dir, exist_ok=True)
        for userid, f in double_check_files:
            new_filename = os.path.join(double_check_dir, f"{userid}.hs")
            shutil.copy(f, new_filename)
    
    with open(args.scores_file, "w") as file:
        json.dump(scores, file, indent=4)
    with open(args.comments_file, "w") as file:
        json.dump(comments, file, indent=4)
