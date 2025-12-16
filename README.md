# Xponents-Core
NOTE: In 2024 this API needed to split off from the evergrowing SDK project, `Xponents/`. 
This was hosted at `./Xponents/Core`, but is now its own repo.  Regarding documentation in [./doc](./doc), there are many sections devoted to the Java API extractors and utilities.  The consolidated documentation that covers the Java and Python libraries and examples is on its way summer of 2024.  Ask for help using the [issues](https://github.com/OpenSextant/Xponents-Core/issues) tab. Thanks.

Xponents is all about geography -- and many things related to it. This API provides
utilities and data classes for the foundational reference data:

- Country and major provincial boundary code books
- Feature code books
- Language codes and names, as well as language identification
- Timezone info by country

The major data classes cover geography concepts as well as data processing/extraction classes:

- **Geography:**  `org.opensextant.data` package contains Country, Coordinate, and Place to represent gazetteer entries.
  The Geocoding interface describes an inferred or interpreted location, where there may be uncertainty in location.
- **Processing:** `org.opensextant.extraction` package houses the central Extractor interface as well as the base class
  `TextEntity` to represent a span of text, and then `TextMatch` building on top of that to carry the extraction 
   metadata.  Two important subclasses are downstream from `TextMatch`:  pattern matches such as `PoliMatch` or `GeocoordMatch`, 
   and then more advanced maches such as `PlaceCandidate` in the tagger SDK. 

The `opensextant` python libary offers a similar collection of classes although its not on parity with the Java core here.

Additional utilities under `org.opensextant.util`

* `FileUtility` - dictionary loading, filename tests and tools.  Such things are beyond common resources such as Apache Commons. 
* `GeodeticUtility` - a convenience library for validating Basics objects and other primitives checks for XY-coordinate systems. 
  Limited support for geohashing, as the main use of geohashing in extraction work is inferring precision.
* `GeonamesUtility` - a library of tools for testing Geonames-like metadata (e.g., feature codes, types, etc). 
* `TextUtils` - a wide range of text scrubbing routines not commonly found in other open source libraries.

## Usage

The typical usage of this library is just that -- as a library.  The command line demo, `./script/demo.sh` offers
a convenient way to play with the test tools

## Building Core APIs 

After checkout, first build Xponents Core API (opensextant-xponents-core)
This is the foundation and utilities for the tagger/geocoder SDK (oensextant-xponents)

1. Setup project.

```
  # If using virtual env, activate that before
  pip install hatch uv

  # Set up Core API with independent reference data
  ./setup.sh

```

2. Setup Core API to build and test:

```
  mvn install
```

## Publishing a Release

Update RELEASE.md, the push the Maven artifacts:

```
  mvn javadoc:javadoc
  mvn clean deploy -P release
  
  # Repeat above until successful -- Javadoc or other errors should be ironed out before final commit.
  cp -r ./target/site/apidocs ./doc/
  # then commit;  github site updates in 10 min
```

Finally, create a release tag and document the release.

```shell
   git tag v3.x.x 
   git push origin v3.x.x 
   # Visit releases page
```

