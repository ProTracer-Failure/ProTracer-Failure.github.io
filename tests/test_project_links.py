from html.parser import HTMLParser
from pathlib import Path
import unittest


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._text = []
        self._has_icon = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []
            self._has_icon = False
        elif tag == "svg" and self._href is not None:
            self._has_icon = True

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append(
                (" ".join("".join(self._text).split()), self._href, self._has_icon)
            )
            self._href = None
            self._text = []
            self._has_icon = False


class ProjectLinksTest(unittest.TestCase):
    def test_failtime_hugging_face_dataset_is_linked(self):
        parser = LinkParser()
        parser.feed(Path("index.html").read_text(encoding="utf-8"))

        self.assertIn(
            (
                "Hugging Face",
                "https://huggingface.co/datasets/ChangUoA/FailTime",
                True,
            ),
            parser.links,
        )

    def test_hero_has_five_icon_pills_including_paper(self):
        source = Path("index.html").read_text(encoding="utf-8")
        project_links = source.split('<nav class="project-links"', 1)[1].split(
            "</nav>", 1
        )[0]
        parser = LinkParser()
        parser.feed(project_links)

        self.assertEqual(5, project_links.count('class="pill'))
        self.assertEqual(5, project_links.count("<svg"))
        self.assertIn(("Paper", "paper/", True), parser.links)

    def test_paper_page_embeds_the_pdf_and_offers_open_and_download(self):
        paper_page = Path("paper/index.html").read_text(encoding="utf-8")

        self.assertIn('data="ProTracer_Arxiv.pdf"', paper_page)
        self.assertIn('href="ProTracer_Arxiv.pdf"', paper_page)
        self.assertIn("download", paper_page)


if __name__ == "__main__":
    unittest.main()
