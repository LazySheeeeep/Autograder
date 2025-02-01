import os
import argparse
import subprocess

ERROR_STR = "*error*"
EXCEPTION_STR = "*exception*"

class GHCI:
    def __init__(self, file: str):
        self.g = subprocess.Popen(
            ["ghci", file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.prompt = "ghci> "
        if self.flush():
            self.close()
            raise Exception(f"{file} load error")
        
    def read_out(self):
        error = True
        while True:
            line = self.g.stdout.readline()
            if "Ok, " in line:
                error = False
            if self.prompt in line:
                return error

    def run(self, command, capture_output=True):
        self.g.stdin.write(f"{command}\n")
        self.g.stdin.flush()
        if not capture_output: return
        output = self.g.stdout.readline()
        return output.removeprefix(self.prompt).strip()
    
    def close(self):
        self.run(":quit", capture_output="False")
        self.g.communicate()

    def flush(self):
        self.run('1+1', capture_output=False)
        return self.read_out()

    def test(self, commands):
        results = []
        for command in commands:
            output = self.run(command)
            if output == '':  # error occured
                self.flush()
                output = ERROR_STR
            elif "Exception" in output:
                self.flush()
                output = EXCEPTION_STR
            results.append(output)
        return results

def load_file(file_path):
    with open(file_path, 'r') as f:
        data = f.read()
    return [section.splitlines() for section in data.strip().split('\n\n')]

def write_answers(answerss, outfile):
    with open(outfile, 'w') as f:
        for answers in answerss:
            for answer in answers:
                print(answer, file=f)
            print(file=f)

def prepare_info(ti_file, to_file):
    info = {}
    info["test_outputs"] = load_file(to_file)
    test_inputs = load_file(ti_file)
    info["max_scores"] = [int(i[0]) for i in test_inputs]
    info["test_inputs"] = [i[1:] for i in test_inputs]
    info["num_cases"] = [len(i) for i in info["test_inputs"]]
    info["num_questions"] = len(info["num_cases"])
    info["case_credits"] = [info["max_scores"][i] / info["num_cases"][i]
                           for i in range(info["num_questions"])]
    return info

def get_answerss(hs_file, test_inputs):
    ghci = GHCI(hs_file)
    answerss = [ghci.test(commands) for commands in test_inputs]
    ghci.close()
    return answerss

def grade_answerss(answerss, info):
    # scoring
    score = 0
    mistakes = {}
    for i in range(info["num_questions"]): # #Q
        for j in range(info["num_cases"][i]):
            if answerss[i][j] == info["test_outputs"][i][j]:
                score += info["case_credits"][i]
            else:
                if i in mistakes:
                    mistakes[i].append(j)
                else:
                    mistakes[i] = [j]
    
    # commenting
    if len(mistakes) != 0:
        comment = "Failed Test case(s):\n"
        for i in mistakes:
            comment += f"Q{i+1}\n"
            for j in mistakes[i]:
                comment += f'(-{info["case_credits"][i]}pt) Input: {info["test_inputs"][i][j]}\tExpected: {info["test_outputs"][i][j]}\tYours: {answerss[i][j]}\n'
    else:
        comment = None
    return score, comment

def parse_arguments():
    parser = argparse.ArgumentParser(description="Auto grading script for .hs files.")
    parser.add_argument('-hf', '--hs-file', type=str, required=True,
                        help="Path to the Haskell (.hs) file to be graded.")
    parser.add_argument('-ti', '--test-inputs', type=str, default="in.txt")
    parser.add_argument('-to', '--test-outputs', type=str, default="out.txt")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if not os.path.exists(args.test_outputs):
        test_inputs = load_file(args.test_inputs)
        test_inputs = [i[1:] for i in test_inputs]
        answerss = get_answerss(args.hs_file, test_inputs)
        write_answers(answerss, args.test_outputs)
    else:
        info = prepare_info(args.test_inputs, args.test_outputs)
        answerss = get_answerss(hs_file=args.hs_file, test_inputs=info["test_inputs"])
        score, comment = grade_answerss(answerss, info)
        print(score, "\n", comment)
