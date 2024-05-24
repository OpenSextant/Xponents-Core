
from opensextant.extractors.xcoord import XCoord

results = XCoord(debug=True).default_tests()
for res in results:
    print(res)