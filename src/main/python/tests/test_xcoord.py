from opensextant.extractors.xcoord import XCoord

tester = XCoord(debug=True)
# focused tests:
mgrs = "10 JAN 94"
matches = tester.extract(mgrs)
for m in matches:
    print(m, m.filtered_out)

dms = ["'18 51.1S 34 38.8W'",
       "08 00.4S 30 35.2W",   # DM
       "08.00.4S 30.35.2W"    # DMS pattern
       ]
for text in dms:
    matches = tester.extract(text)
    for m in matches:
        print(f"Text=[{m.text}]", m.pattern_id, "Filtered=", m.filtered_out, "Duplicate", m.is_duplicate)

results = XCoord(debug=True).default_tests()
for res in results:
    print(res)
