import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompt import system_prompt
from call_functions import available_functions, call_function


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    for _ in range(20):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            ),
        )

        candidate = response.candidates[0]
        messages.append(candidate.content)

        function_calls = response.function_calls
        
        if function_calls is None or len(function_calls) <= 0:
            if args.verbose:
                print("User prompt: ", args.user_prompt)
                print("Prompt tokens:", response.usage_metadata.prompt_token_count)
                print("Response tokens:", response.usage_metadata.candidates_token_count)
            
            print(response.text)
            exit(0)

        try:
            for function_call in function_calls:
                function_call_result = call_function(function_call, args.verbose)

                if function_call_result.parts is None or len(function_call_result.parts) <= 0:
                    raise Exception("Function call result has no parts")

                function_response = function_call_result.parts[0].function_response

                if function_response is None:
                    raise Exception("Function response is None")

                result = function_response.response

                if args.verbose:
                    print(f"-> {result}")
                
                messages.append(function_call_result)
        except Exception as e:
            print(f"Error calling function: {e}")
            exit(1)

    print("Maximum iterations reached")
    exit(1)


if __name__ == "__main__":
    main()
