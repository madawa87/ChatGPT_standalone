import argparse
from pathlib import Path
import json
import openai


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as jfile:
        return json.load(jfile)

def save_json(file_path, json_content):
    with open(file_path, 'w', encoding='utf-8') as jfile:
        json.dump(json_content, jfile, ensure_ascii=False, sort_keys=True, indent=2)


def open_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def chatgpt_completion(conversation, model="gpt-3.5-turbo"):
    """
    Takes in a conversation (list of strings) and a model (defaults to gpt-3.5-turbo) 
    and returns a response from OpenAI's ChatCompletion API.
    
    Parameters:
        conversation (list of strings): A list of strings representing the conversation.
        model (string): The model to use for the response. Defaults to gpt-3.5-turbo.
    
    Returns:
        response (openai.openai_object.OpenAIObject): The response from OpenAI's ChatCompletion API.
    """
    response = openai.ChatCompletion.create(model=model, messages = conversation)
    return response


def print_response_end():
    print(f"--------------------------------------------------------")



def get_conversation_from_prompt_file(prompt_file):
    prompt = prompt_file.read()
    print(f"ss:{prompt}")
    return prompt

def get_new_conversation():
    """
    Creates a new conversation between a user and a system.

    Parameters:
        None

    Returns:
        conversation (list): A list containing a single line of conversation from the system.
    """
    sys_content = "I am a helpful assistant."
    sys_line = {'role': 'system', 'content': sys_content}
    conversation = list()
    conversation.append(sys_line)
    return conversation

def append_user_prompt(conversation, user_prompt):
    conversation.append({'role': 'user', 'content': user_prompt})

def get_response_print(conversation, model):
    response = chatgpt_completion(conversation, model)
    resp_text = response['choices'][0]['message']['content']
    conversation.append({'role': 'assistant', 'content': resp_text})
    prompt_t = response['usage']['prompt_tokens']
    completion_t = response['usage']['completion_tokens']
    total_t = response['usage']['total_tokens']

    print(f"\n\nASSISTANT\n: {resp_text}")
    print(f"{total_t} = c:{completion_t} + p:{prompt_t}")

def run_conversation_loop(conversation, model): 
    while True:
        user_in = input("\n\nUSER: ")

        if user_in == '':
            print(f"Say something!")
            continue

        # if first leter of the user_ in is !, start an new conversation
        if user_in[0] == '!':
            conversation= get_new_conversation()
            user_in = user_in[1:]

        append_user_prompt(conversation, user_in)
        get_response_print(conversation, model)
        print_response_end()
        

def main():
    secrets_path = Path("secrets")
    secrets_file = secrets_path / "secrets.json" 
    secrets = load_json(secrets_file)
    openai.api_key = secrets['openai_key']

    parser = argparse.ArgumentParser()
    parser.add_argument("prompt_file", nargs='?', 
                        help="Path to the file contains initial promt")
    parser.add_argument('-m', '--model', 
                        help="ChatGPT model: [3: for GPT3.5] or [4: for GPT4]",
                        default='3')
    args = parser.parse_args()

    prompt_file = args.prompt_file
    if args.model == '4':
        model = 'gpt-4'
        print(f"Using GPT-4")
    else:
        model = 'gpt-3.5-turbo'
        print(f"Using GPT-3.5")

    conversation = get_new_conversation()

    # get prompt from file if provided and run it once
    if prompt_file:
        with open(prompt_file, 'r') as pf:
            prompt = get_conversation_from_prompt_file(pf)
            append_user_prompt(conversation, prompt)
            get_response_print(conversation, model)

    # main conversation loop
    run_conversation_loop(conversation, model)

    
if __name__ == "__main__":
    main()