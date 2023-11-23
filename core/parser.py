import functools
import inspect
import re
import logging
from typing import Callable, Dict, List, Optional, Any

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FunctionDefinitionParser:
    """
    Class responsible for parsing Python function definitions and converting them into
    a JSON-like structure for use in applications like FunctionsAgent.
    """

    @staticmethod
    def get_json_type_from_python_type(dtype) -> str:
        """
        Maps Python data types to JSON schema data types.

        :param dtype: The Python data type.
        :return: Corresponding JSON schema data type as a string.
        """
        if dtype == float:
            return "number"
        elif dtype == int:
            return "integer"
        elif dtype == str:
            return "string"
        else:
            return "string"

    @staticmethod
    def extract_param_descriptions_from_docstring(doc_str: str) -> Dict[str, str]:
        """
        Extracts parameter descriptions from a function's docstring.

        :param doc_str: The docstring of the function.
        :return: A dictionary mapping parameter names to their descriptions.
        """
        params_str = [line for line in doc_str.split("\n") if line.strip()]
        params = {}
        for line in params_str:
            if line.strip().startswith(':param'):
                param_match = re.findall(r'(?<=:param )\w+', line)
                if param_match:
                    param_name = param_match[0]
                    desc_match = line.replace(f":param {param_name}:", "").strip()
                    if desc_match:
                        params[param_name] = desc_match
        return params

    def convert_function_to_json_schema(self, func: Callable) -> Dict[str, Any]:
        """
        Converts a Python function definition to a JSON-like structure for easier handling and processing.

        :param func: The Python function to parse.
        :return: A dictionary representing the function in a JSON-like format.
        """
        try:
            # Handle functools.partial
            if isinstance(func, (functools.partial, functools.partialmethod)):
                fixed_args = func.keywords or dict(zip(func.func.__code__.co_varnames, func.args))
                func = func.func
            else:
                fixed_args = {}

            argspec = inspect.getfullargspec(func)
            func_doc = inspect.getdoc(func) or ""
            func_description = ''.join([line for line in func_doc.split("\n") if not line.strip().startswith(':')])
            param_details = self.extract_param_descriptions_from_docstring(func_doc)

            params = {
                param_name: {
                    "description": param_details.get(param_name, ""),
                    "type": self.get_json_type_from_python_type(argspec.annotations.get(param_name, type(None)))
                }
                for param_name in argspec.args if param_name not in fixed_args
            }

            required_params = [p for p in argspec.args if p not in fixed_args]
            if argspec.defaults:
                required_params = [p for p in required_params if p not in argspec.defaults]

            return {
                "name": func.__name__,
                "description": func_description,
                "parameters": {"type": "object", "properties": params},
                "required": required_params
            }
        except Exception as e:
            logger.error(f"Error in processing function {func.__name__}: {e}")
            return {}
