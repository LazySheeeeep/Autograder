from email.utils import formataddr
import yagmail
from json import load
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Auto grading script for .hs files.")
    parser.add_argument('-cf', '--comments-file', type=str, default="comments.json")
    parser.add_argument('-an', '--assignment-name', type=str, required=True)
    parser.add_argument('-nt', '--not-test', action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    with open("../default.json", "r") as file:
        default = load(file)
    with open(args.comments_file, "r") as file:
        comments = load(file)
    yag = yagmail.SMTP(user=default["addr"], password=default["password"], host=default["host"])
    subject_ = f"{default['subject']} {args.assignment_name}"
    for computingID in comments:
        if args.not_test:
            to = computingID+'@sfu.ca'
            subject = subject_
        else:
            to = default["receiver2"]
            subject = subject_ + f" to {computingID+'@sfu.ca'}"
        contents = comments[computingID] + default["contents"]
        yag.send(to=to, subject=subject, contents=contents,
                 headers={"From": formataddr((default["name"], default["addr"]))})
        print(f"Comment for {computingID} has been sent to {to}.")
    yag.close()