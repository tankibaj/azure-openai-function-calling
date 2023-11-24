import json
import logging
from typing import Optional, Callable, List, Dict

from openai import AzureOpenAI

from core.parser import FunctionDefinitionParser

# Configure logger for better debugging and monitoring
logger = logging.getLogger(__name__)


class AzureOpenAIFunctions:
    def __init__(
            self,
            azure_openai_endpoint: str,
            azure_openai_key_key: str,
            azure_api_version: str,
            model: str,
            functions: Optional[List[Callable]] = None
    ):
        self.azure_openai_endpoint = azure_openai_endpoint
        self.azure_openai_key_key = azure_openai_key_key
        self.azure_api_version = azure_api_version
        self.model = model
        self.client = AzureOpenAI(
            azure_endpoint=self.azure_openai_endpoint,
            api_key=self.azure_openai_key_key,
            api_version=self.azure_api_version,
        )
        self.function_parser = FunctionDefinitionParser()  # Initialize the parser first
        self.functions = self._parse_functions(functions)  # Then use it in _parse_functions
        self.func_mapping = self._create_func_mapping(functions)
        self.internal_thoughts = []

    def _parse_functions(self, functions: Optional[List[Callable]]) -> Optional[List[Dict]]:
        """Converts the 'python functions' list into a JSON-serializable list."""
        if functions is None:
            return None
        return [self.function_parser.convert_function_to_json_schema(func) for func in functions]

    def _create_func_mapping(self, functions: Optional[List[Callable]]) -> Dict[str, Callable]:
        """Creates a mapping between the function names and function definitions."""
        if functions is None:
            return {}
        return {func.__name__: func for func in functions}

    def _create_chat_completion(self, messages: List[Dict], use_functions: bool = True):
        """Calls the OpenAI API to create a chat completion, using the functions if specified."""
        try:
            logger.debug(f"Creating chat completion with messages: {messages} and use_functions: {use_functions}")
            if use_functions and self.functions:
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    functions=self.functions
                )
            else:
                return self.client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    messages=messages
                )
        except Exception as e:
            logger.error(f"Error in creating chat completion with messages: {messages}, error: {e}", exc_info=True)
            raise

    def _generate_response(self, chat_history: List[Dict]):
        """Generates a response from the OpenAI API."""
        try:
            logger.debug(f"Generating response with chat_history: {chat_history}")
            while True:
                response = self._create_chat_completion(chat_history + self.internal_thoughts)
                finish_reason = response.choices[0].finish_reason

                if finish_reason == 'stop' or len(self.internal_thoughts) > 3:
                    final_thought = self._final_thought_answer()
                    final_res = self._create_chat_completion(
                        chat_history + [final_thought],
                        use_functions=False
                    )
                    return final_res
                elif finish_reason == 'function_call':
                    self._handle_function_call(response)
                else:
                    raise ValueError(f"Unexpected finish reason: {finish_reason}")
        except Exception as e:
            logger.error(f"Error in generating response with chat_history: {chat_history}, error: {e}", exc_info=True)
            raise

    def _handle_function_call(self, response):
        """Handles when a function is called within the chat."""
        try:
            logger.debug(f"Handling function call with response: {response}")
            choice = response.choices[0]
            function_call = choice.message.function_call
            func_name = function_call.name
            args = function_call.arguments  # This should be already in dictionary format or JSON string

            # Ensure args is a dictionary
            if isinstance(args, str):
                args = json.loads(args)

            result = self._call_function(func_name, args)
            res_msg = {'role': 'function', 'name': func_name, 'content': str(result)}
            self.internal_thoughts.append(res_msg)
        except Exception as e:
            logger.error(f"Error in handling function call with response: {response}, error: {e}", exc_info=True)
            raise

    def _call_function(self, func_name: str, args: Dict):
        """Calls the actual function when invoked in _handle_function_call."""
        try:
            logger.debug(f"Calling function '{func_name}' with arguments: {args}")
            func = self.func_mapping.get(func_name)
            if func:
                result = func(**args)
                logger.debug(f"Function '{func_name}' returned: {result}")
                return result
            else:
                raise ValueError(f"Function {func_name} not implemented")
        except Exception as e:
            logger.error(f"Error in calling function {func_name} with arguments: {args}, error: {e}", exc_info=True)
            raise

    def _final_thought_answer(self) -> Dict[str, str]:
        """Creates the final thought answer."""
        thoughts = "To answer the question I will use these step by step instructions.\n\n"
        for thought in self.internal_thoughts:
            if 'function_call' in thought.keys():
                thoughts += (f"I will use the {thought['function_call']['name']} "
                             "function to calculate the answer with arguments "
                             f"{thought['function_call']['arguments']}.\n\n")
            else:
                thoughts += thought["content"] + "\n\n"
        final_thought = {
            'role': 'assistant',
            'content': f"{thoughts} Based on the above, I will now answer the "
                       "question, this message will only be seen by me so answer with "
                       "the assumption that the user has not seen this message. If possible I will provide the source "
                       "of the information url to user."
        }
        return final_thought

    def ask(self, messages: List[Dict]):
        """Asks a question to the OpenAI API. The main method to interact with the OpenAI GPT-4 model."""
        self.internal_thoughts = []
        chat_history = messages
        response = self._generate_response(chat_history)
        return response
