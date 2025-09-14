import sys
import os
from google import genai
from google.genai import types #type: ignore
from dotenv import load_dotenv #type: ignore
from prompts import system_prompt
from functions import (
    schemas,
    get_file_content,
    write_file_content,
    run_python,
    get_files_info
)

available_functions = types.Tool(
    function_declarations=[
        schemas.schema_get_files_info,
        schemas.schema_get_file_content,
        schemas.schema_write_file,
        schemas.schema_run_python_file
    ]
)

config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
)

function_map = {
    "get_files_info": get_files_info.get_files_info,    
    "get_file_content": get_file_content.get_file_content, 
    "write_file": write_file_content.write_file,         
    "run_python_file": run_python.run_python_file         
}

def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

        # python
    for _ in range(20):
        try:
            resp = generate_content(client, messages, verbose)
            # only finish when there are no more function calls
            if not resp.function_calls and resp.text:
                print("Final response:")
                print(resp.text)
                break
        except Exception as e:
            if verbose:
                print(f"Error: {e}")
            break



def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=config,
    )

    if response.candidates:
        messages.append(response.candidates[0].content)

    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    if response.function_calls:
        for fc in response.function_calls:
            function_call_result = call_function(fc, verbose)

            tool_resp = function_call_result.parts[0].function_response.response

            messages.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=fc.name,
                            response=tool_resp,
                        )
                    ],
                )
            )

            if verbose:
                print(f"-> {tool_resp}")

    return response


def call_function(function_call_part, verbose=False):
    if verbose: print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else: print(f" - Calling function: {function_call_part.name}")

    function_call_part.args["working_directory"] = "./calculator"

    if function_call_part.name in function_map:
        function_to_call = function_map[function_call_part.name]
        result = function_to_call(**function_call_part.args)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": result},
                )
            ],
        )
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )

if __name__ == "__main__":
    main()
