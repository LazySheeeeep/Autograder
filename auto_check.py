import argparse
import ollama
from pydantic import BaseModel

class RetType(BaseModel):
    output: list[bool]
    
    def good(self):
        return all(self.output)
    
def parse_arguments():
    parser = argparse.ArgumentParser(description="Script for LLM to check Haskell (.hs) file.")
    parser.add_argument('-hf', '--hs-file', type=str, required=True,
                        help="Path to the Haskell (.hs) file to be checked.")
    parser.add_argument('-pf', '--prompt-file', type=str, default="prompt.txt")
    parser.add_argument('-m', '--model', type=str, default="qwen2.5-coder-32b-instruct-q4_k_m",
                        help="Model name for the ollama service.")
    return parser.parse_args()

def check_ok(hs_file: str, prompt: str, model: str, debug=False) -> bool:
    with open(hs_file, 'r') as f:
        script_content = f.read()
    response = ollama.chat(model=model,
                           messages=[{"role": "user", "content": prompt + script_content}],
                           format=RetType.model_json_schema(),
                           options={"temperature":0})
    if debug:
        return RetType.model_validate_json(response.message.content)
    return RetType.model_validate_json(response.message.content).good()

if __name__ == "__main__":
    args = parse_arguments()
    with open(args.prompt_file, 'r') as f:
        prompt = f.read()
    print(check_ok(args.hs_file, prompt, args.model, debug=True))
