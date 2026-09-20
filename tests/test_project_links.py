from html.parser import HTMLParser
import hashlib
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
    def test_failtime_data_is_linked(self):
        parser = LinkParser()
        parser.feed(Path("index.html").read_text(encoding="utf-8"))

        self.assertIn(
            (
                "Data",
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

    def test_overview_video_uses_the_nine_second_poster(self):
        poster = Path("assets/ProTracer_project_page_video_frame_0009.jpg")
        digest = hashlib.sha256(poster.read_bytes()).hexdigest()
        source = Path("index.html").read_text(encoding="utf-8")

        self.assertEqual(
            "386c50ef71884d3606e88ad58ff0fbf6777bf3fde5b1e715199c4f907297b459",
            digest,
        )
        self.assertIn(
            'poster="assets/ProTracer_project_page_video_frame_0009.jpg?v=9s"',
            source,
        )

    def test_project_and_paper_pages_show_the_full_affiliation(self):
        affiliation = (
            "Australian Institute for Machine Learning, Adelaide University"
        )

        self.assertIn(affiliation, Path("index.html").read_text(encoding="utf-8"))
        self.assertIn(
            affiliation, Path("paper/index.html").read_text(encoding="utf-8")
        )

    def test_project_logo_precedes_protracer_prefix_and_is_the_favicon(self):
        logo_path = "assets/protracer-logo.png"
        title = "Proprioception-Guided Failure Diagnosis in Robot Manipulation"
        logo_digest = hashlib.sha256(Path(logo_path).read_bytes()).hexdigest()

        self.assertEqual(
            "3acfad9ee3cea06de423289137fed53bd94b174a037c02f71b20ef735038bd04",
            logo_digest,
        )
        for page in (Path("index.html"), Path("paper/index.html")):
            source = page.read_text(encoding="utf-8")
            self.assertIn('rel="icon"', source)
            self.assertIn("protracer-logo.png", source)
            self.assertIn(f'alt="ProTracer"', source)
            self.assertIn(title, source)
            self.assertIn('<span class="title-brand">ProTracer:</span>', source)


if __name__ == "__main__":
    unittest.main()
