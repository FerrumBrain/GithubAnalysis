from typing import Dict
from InputOutput import InputOutput


class CLIInputOutput(InputOutput):
    def __init__(self, greeting_text: str, retry_text: str, statistics_names: Dict[str, str]):
        self.greeting_text = greeting_text
        self.retry_text = retry_text
        self.statistics_names = statistics_names
        self.first_input = True

    def get_link(self) -> str:
        link = input(self.greeting_text if self.first_input else self.retry_text)
        self.first_input = False
        return link

    def print_results(self, results):
        for statistics in results.keys():
            print(self.statistics_names[statistics], ':', results[statistics])
