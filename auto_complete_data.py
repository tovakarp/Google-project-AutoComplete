from dataclasses import dataclass
from init_data import get_line

@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int

    def __init__(self, src, line, score):
        self.completed_sentence = get_line(src, line)
        self.source_text = src
        self.offset = line
        self.score = score

