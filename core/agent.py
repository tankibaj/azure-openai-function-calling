import json
from typing import Optional
import openai
import config
# import function_definition_parse  # Import the function_definition_parse module
from core.function_definition_parse import func_to_json  # Import the function_definition_parse module
import logging


logger = logging.getLogger(__name__)


class FunctionsAgent:
    def __init__(
            self,
            api_type: str,
            api_base: str,
            api_key: str,
            api_version: str,
            engine: str,
            functions: Optional[list] = None
    ):
        openai.api_type = api_type
        openai.api_version = api_version
        openai.api_base = api_base
        openai.api_key = api_key
        self.engine = engine
        self.functions = self._parse_functions(functions)
        self.func_mapping = self._create_func_mapping(functions)


    def _parse_functions(self, functions: Optional[list]) -> Optional[list]:
        """Converts the 'python functions' list into a JSON-serializable list

        :param functions: A list of python functions
        :return: A list of JSON-serializable python functions
        """
        if functions is None:
            return None
        return [func_to_json(func) for func in functions]

    def _create_func_mapping(self, functions: Optional[list]) -> dict:
        """Creates a mapping between the function names and function definitions.

        :param functions: A list of python functions
        :return: A dictionary mapping the function name to the function object
        """
        if functions is None:
            return {}
        return {func.__name__: func for func in functions}

    def _create_chat_completion(self, messages: list, use_functions: bool = True) -> openai.ChatCompletion:
        """Calls the OpenAI API to create a chat completion, using the functions if specified.

        :param messages: A list of messages to send to the API
        :param use_functions: A boolean indicating whether to use the functions or not
        :return: A chat completion object
        """
        if use_functions and self.functions:
            res = openai.ChatCompletion.create(
                engine=self.engine,
                messages=messages,
                temperature=0,
                functions=self.functions
            )
        else:
            res = openai.ChatCompletion.create(
                engine=self.engine,
                temperature=0,
                messages=messages
            )
        return res

    def _generate_response(self, chat_history) -> openai.ChatCompletion:
        """Generates a response from the OpenAI API.

        :param chat_history: A list of messages to send to the API
        :return: A chat completion object
        """
        while True:
            print('.', end='')
            res = self._create_chat_completion(
                chat_history + self.internal_thoughts
            )
            finish_reason = res.choices[0].finish_reason

            if finish_reason == 'stop' or len(self.internal_thoughts) > 3:
                # create the final answer
                final_thought = self._final_thought_answer()
                final_res = self._create_chat_completion(
                    chat_history + [final_thought],
                    use_functions=False
                )
                return final_res
            elif finish_reason == 'function_call':
                self._handle_function_call(res)
            else:
                raise ValueError(f"Unexpected finish reason: {finish_reason}")

    def _handle_function_call(self, res: openai.ChatCompletion):
        """Handles when a function is called within the chat.

        :param res: A chat completion object
        :return: None
        """
        self.internal_thoughts.append(res.choices[0].message.to_dict())
        func_name = res.choices[0].message.function_call.name
        args_str = res.choices[0].message.function_call.arguments
        result = self._call_function(func_name, args_str)
        res_msg = {'role': 'function', 'name': func_name, 'content': (f"{result}")}
        self.internal_thoughts.append(res_msg)

    def _call_function(self, func_name: str, args_str: str):
        """Calls the actual function when invoked in _handle_function_call.

        :param func_name: The name of the function to call
        :param args_str: The arguments to pass to the function
        :return: The result of the function call
        """
        args = json.loads(args_str)
        func = self.func_mapping[func_name]
        res = func(**args)
        return res

    def _final_thought_answer(self):
        """Creates the final thought answer.

        :return: A dictionary containing the final thought answer
        """
        thoughts = ("To answer the question I will use these step by step instructions."
                    "\n\n")
        for thought in self.internal_thoughts:
            if 'function_call' in thought.keys():
                thoughts += (f"I will use the {thought['function_call']['name']} "
                             "function to calculate the answer with arguments "
                             + thought['function_call']['arguments'] + ".\n\n")
            else:
                thoughts += thought["content"] + "\n\n"
        self.final_thought = {
            'role': 'assistant',
            'content': (f"{thoughts} Based on the above, I will now answer the "
                        "question, this message will only be seen by me so answer with "
                        "the assumption with that the user has not seen this message.")
        }
        return self.final_thought

    def ask(self, message: list) -> openai.ChatCompletion:
        """Asks a question to the OpenAI API. The main method to interact with the OpenAI GPT-4 model.

        :param message: A list of messages to send to the API
        :return: A chat completion object
        """
        self.internal_thoughts = []
        chat_history = message
        response = self._generate_response(chat_history)
        return response
        # return response.choices[0].message['content']
