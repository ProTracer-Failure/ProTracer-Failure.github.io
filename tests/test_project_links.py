from html.parser import HTMLParser
from pathlib import Path
import unittest


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append(("".join(self._text).strip(), self._href))
            self._href = None
            self._text = []


class ProjectLinksTest(unittest.TestCase):
    def test_failtime_hugging_face_dataset_is_linked(self):
        parser = LinkParser()
        parser.feed(Path("index.html").read_text(encoding="utf-8"))

        self.assertIn(
            ("Hugging Face", "https://huggingface.co/datasets/ChangUoA/FailTime"),
            parser.links,
        )


if __name__ == "__main__":
    unittest.main()
