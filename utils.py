# Utility code to create JSON annotations of your custom functions (below) that the OpenAI API can accept
# You will likely not need to modify this

# Warning: this code is somewhat hacky and not tested against edge cases
# Currently, it only supports functions wtih str, list, int, and bool as argument types

def stringify_name(item):
    # Name substitutions, since the OpenAI API uses, string, array, and integer instead of str, list, int
    type_mapping = {
        str: "string",
        list: "array",
        int: "integer",
        float: "number",
        bool: "boolean"
    }
    
    if item in type_mapping:
        return type_mapping[item]
    
    raise ValueError(f"Unsupported type: {item}")
    
def get_function_schema(agent_functions):
    tool_schema = []
    tool_name_to_func = {}

    for function, description in agent_functions:
        properties = {}
        required = []
        for param_name, param_annotation in function.__annotations__.items():
            if param_name != "return":
                properties[param_name] = {
                        "type": stringify_name(param_annotation.__origin__),
                        "description": param_annotation.__metadata__[0]
                        }
                if param_annotation.__origin__.__name__ in ("list",):
                    properties[param_name]["items"] = {"type": stringify_name(param_annotation.__origin__.__args__[0])}

                required.append(param_name)

        schema = {
            "type": "function",
            "function": {
                "name": function.__name__,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
                }
        }

        tool_schema.append(schema)
        tool_name_to_func[function.__name__] = function
    
    return tool_schema, tool_name_to_func