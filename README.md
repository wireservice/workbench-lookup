# workbench-lookup

A workbench module for joining lookup tables from the [wireservice-lookup](https://github.com/wireservice/lookup) repository.

This is mostly a port of [agate-lookup](https://github.com/wireservice/agate-lookup)

## Wishlist

* Unit tests should not mock the lookup "API"
* Fetch/cache list of valid lookups from repository (auto-fill)
* Resolve ambiguity between agate `Number` type and pandas `int`/`float`.
* Convert value lookup value columns to types declared in the lookup YAML.
* Update the [lookup](https://github.com/wireservice/lookup) repository with fresher source data.

## Authors

* Chris Groskopf [chrisgroskopf@gmail.com](mailto:chrisgroskopf@gmail.com)