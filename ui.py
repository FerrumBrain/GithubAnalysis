import json
from CLIInputOutput import CLIInputOutput

_input_output_processor = None


def set_input_output():
    global _input_output_processor

    json_path = 'settings.json'
    with open(json_path, 'r') as settings_file:
        args = json.load(settings_file)

    if args['input_output_type'] == 'CLI':
        _input_output_processor = CLIInputOutput(**args['input_output_settings'])
    else:
        raise ValueError(f'Not supported {args["type"]} as input-output type')


def get_link():
    if _input_output_processor is None:
        set_input_output()
    return _input_output_processor.get_link()


def print_results(results):
    _input_output_processor.print_results(results)
