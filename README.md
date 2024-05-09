# Xponents-Core

In 2024 this API needed to split off from the ever growing SDK projects, ./Xponents/



Building Xponents 
==================

After checkout, first build Xponents Core API (opensextant-xponents-core)
This is the foundation and utilities for the tagger/geocoder SDK (oensextant-xponents)


1. Setup project.

```
  # Set up Core API with independent reference data
  ./setup.sh

```


2. Setup Core API to build and test:

```
  mvn install
```

3. Publish Release

- update RELEASE.md here

```
  mvn clean deploy -P release
```


