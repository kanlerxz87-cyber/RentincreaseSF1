"""Adversarial regression tests for the independent row-citation census."""
import unittest

from verify_public_rows import audit_html, is_first_party_url


class FirstPartyURLTests(unittest.TestCase):
    def test_known_official_publishers(self):
        for url in (
            "https://www.sf.gov/rent-board-housing-inventory",
            "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=827",
            "https://www.hud.gov/helping-americans/fair-housing-act-overview",
            "https://sftreasurer.org/information-lessors-residential-real-estate",
            "https://sfgov.legistar.com/LegislationDetail.aspx?ID=1",
            "https://portal.sfrb.org/",
            "https://github.com/kanlerxz87-cyber/RentincreaseSF1/branches",
            "https://docs.github.com/en/repositories",
        ):
            with self.subTest(url=url):
                self.assertTrue(is_first_party_url(url))

    def test_relative_links_and_impostors_are_not_official_sources(self):
        for url in (
            "../hub/sources.html#S01", "../hub/flags.html#H-01",
            "http://www.sf.gov/notice", "https://www.sf.gov.evil.example/",
            "https://sftreasurer.org.evil.example/", "https://evil.sftreasurer.org/",
            "https://github.com/example/another-repo", "https://github.com/kanlerxz87-cyber/RentincreaseSF1-evil",
            "https://user@www.sf.gov/", "https://www.sf.gov:444/", "https://[malformed/",
        ):
            with self.subTest(url=url):
                self.assertFalse(is_first_party_url(url))


class RowTests(unittest.TestCase):
    def test_header_and_neighbor_source_do_not_cover_another_row(self):
        document = """<table><thead><tr><td><a href='https://www.sf.gov/x'>heading</a></td></tr></thead>
          <tbody><tr id='first'><td><a href='https://www.sf.gov/x'>official</a></td></tr>
          <tr id='second'><td><a href='../hub/sources.html#S01'>registry only</a></td></tr>
          <tr><th>Header only</th></tr></tbody></table>"""
        result = audit_html(document)
        self.assertEqual(result.rows, 2)
        self.assertEqual(len(result.missing_lines), 1)

    def test_html_entity_and_single_quotes(self):
        document = """<table><tr id='r'><td><a href='https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&amp;sectionNum=827'>code</a></td></tr></table>"""
        result = audit_html(document)
        self.assertEqual(result.rows, 1)
        self.assertEqual(result.missing_lines, [])

    def test_nested_table_link_does_not_satisfy_outer_row(self):
        document = """<table><tr><td>Outer<table><tr><td><a href='https://www.sf.gov/x'>inner</a></td></tr></table></td></tr></table>"""
        result = audit_html(document)
        self.assertEqual(result.rows, 2)
        self.assertEqual(len(result.missing_lines), 1)

    def test_plain_url_is_not_a_clickable_source(self):
        result = audit_html("<table><tbody><tr><td>https://www.sf.gov/</td></tr></tbody></table>")
        self.assertEqual(result.rows, 1)
        self.assertEqual(len(result.missing_lines), 1)

    def test_rows_outside_tables_are_ignored(self):
        result = audit_html("<tr><td>No enclosing table</td></tr><table><tr><th>header</th></tr></table>")
        self.assertEqual(result.rows, 0)
        self.assertEqual(result.missing_lines, [])


if __name__ == "__main__":
    unittest.main()
