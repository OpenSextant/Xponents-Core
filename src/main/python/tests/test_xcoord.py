
from opensextant.extractors.xcoord import XCoord

tester = XCoord(debug=True)
# focused tests:
mgrs = "10 JAN 94"
matches = tester.extract(mgrs)
for m in matches:
    print (m, m.filtered_out)

results = XCoord(debug=True).default_tests()
for res in results:
    print(res)