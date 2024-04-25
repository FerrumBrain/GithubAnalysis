from typing import Dict
class InputOutput:
    def get_link(self) -> str:
        raise NotImplementedError

    def print_results(self, results: Dict):
        raise NotImplementedError
