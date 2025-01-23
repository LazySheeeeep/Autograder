import requests
from json import load
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Batch uploading scores and comments.")
    parser.add_argument('-sf', '--scores-file', type=str, default="scores.json")
    parser.add_argument('-cf', '--comments-file', type=str, default="comments.json")
    parser.add_argument('-df', '--defaults-file', type=str, default="../defaults.json")
    parser.add_argument('-aid', '--assignment-id', type=str, required=True)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    with open(args.defaults_file, "r") as file:
        defaults = load(file)
    url = f"{defaults['base_url']}/api/v1/courses/{defaults['course_id']}/assignments/{args.assignment_id}/submissions/update_grades"
    headers = {"content-type" : "application/json",
               "Authorization": f"Bearer {defaults['token']}"
    }
    data_json = {'grade_data': {}}
    with open(args.scores_file, "r") as file:
        scores = load(file)
    with open(args.comments_file, "r") as file:
        comments = load(file)
    for userid in scores:
        data_json['grade_data'][userid] = {'posted_grade': scores[userid]}
        if userid in comments:
            data_json['grade_data'][userid]['text_comment'] = comments[userid]
    r = requests.post(url, headers=headers, json=data_json)
    print(r.text)
