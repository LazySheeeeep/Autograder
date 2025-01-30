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
        if assistance and check(hs_file):
            double_check_files.append(hs_file)
    except Exception as e:
        print(f"Failed to grade {hs_file}: {e}")

def check(hs_file: str) -> bool:
    with open(hs_file, 'r') as f:
            script_content = f.read()
    response = ollama.chat(model="qwen2.5-coder-32b-instruct-q4_k_m",
                           messages=[{"role": "user", "content": prompt + script_content}],
                           options={"temperature":0})
    return "0" in response.message.content  # True if sth is wrong

if __name__ == "__main__":
    args = parse_arguments()
    info = prepare_info(args.test_inputs, args.test_outputs)
    comments = {}
    scores = {}
    assistance = False
    double_check_files = []

    if os.path.exists("prompt.txt"):
        assistance = True
        with open("prompt.txt", 'r') as f:
            prompt = f.read()
        import ollama
    
    for hs_file in tqdm(glob.glob(os.path.join(args.submission_directory, "*.hs"))):
        grade_(hs_file)

    if len(double_check_files) > 0:
        print("Double-check the following files:")
        for f in double_check_files:
            print(f)
    
    with open(args.scores_file, "w") as file:
        json.dump(scores, file, indent=4)
    with open(args.comments_file, "w") as file:
        json.dump(comments, file, indent=4)
