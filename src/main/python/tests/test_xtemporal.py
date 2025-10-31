import copy
import os
import unittest

from opensextant.extractors.xtemporal import XTemporal
from opensextant.utility import get_csv_writer, ensure_dirs


class TestXTemporal(unittest.TestCase):
    def test_xtemp_euro(self):
        datex = XTemporal(debug=True, locale="Euro")

        euro_tests = [
            ("text text 04/05/2025", "2025-05-04"),
            ("text text 30/05/2025", "2025-05-30"),
            ("text text 12/05/2025", "2025-05-12"),
            ("text text 12/12/2025", "2025-12-12"),
            ("text text 05/12/2025", "2025-12-05")
        ]
        for tst, expected in euro_tests:
            for date_match in datex.extract(tst):
                result = date_match.attrs.get("datenorm")
                print(date_match.text, result, "Expected", expected)
                self.assertEqual(expected, result)

    def test_full_run(self):
        print("Run Default Tests")

        datex = XTemporal(debug=True)
        test_results = datex.default_tests()

        print("Save Test Results")
        libdir = os.path.dirname(os.path.abspath(__file__))
        output = os.path.abspath(os.path.join(libdir, "..", "..", "results", "xtemporal-tests.csv"))
        ensure_dirs(output)
        print("... output file at ", output)

        with open(output, "w", encoding="UTF-8") as fh:
            header = ["TEST", "TEXT", "RESULT", "MATCH_TEXT", "MATCH_ATTRS"]
            csvout = get_csv_writer(fh, header)
            csvout.writeheader()
            for result in test_results:

                baserow = {
                    "TEST": result["TEST"],
                    "TEXT": result["TEXT"],
                    "RESULT": result["PASS"],
                    "MATCH_TEXT": "",
                    "MATCH_ATTRS": ""
                }
                for m in result["MATCHES"]:
                    row = copy.copy(baserow)
                    row["MATCH_TEXT"] = m.text
                    row["MATCH_ATTRS"] = repr(m.attrs)
                    csvout.writerow(row)


if __name__ == "__main__":
    unittest.main()
