import requests
from json import load
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Batch emailing comments.")
    parser.add_argument('-cf', '--comments-file', type=str, default="comments.json")
    parser.add_argument('-aid', '--assignment-id', type=str, required=True)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    with open("../default.json", "r") as file:
        default = load(file)
    url = f"{default['base_url']}/api/v1/courses/{default['course_id']}/assignments/{args.assignment_id}/submissions/update_grades"
    headers = {"content-type" : "application/json",
               "Authorization": f"Bearer {default['token']}"
    }
    grade_data = {'grade_data': {}}
    with open(args.comments_file, "r") as file:
        comments = load(file)
    for userid in comments:
        grade_data['grade_data'][userid] = {'text_comment': comments[userid]}
    r = requests.post(url, headers=headers, json=grade_data)
    print(r.text)
