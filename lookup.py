import io
import os

import numpy as np
import pandas as pd
import requests
import six
import yaml


WORKBENCH_TYPE_LOOKUP = {
    "Text": "text",
    "Number": "integer"
}


PANDAS_TYPE_LOOKUP = {
    "text": str,
    "integer": np.int64
}


def render(table, params, *, input_columns):
    columns = params["columns"]
    keys = params["keys"]
    value = params["value"]
    version = params["version"] or None

    if not columns or not value:
        return table

    if keys:
        keys = keys.split(",")

        if len(keys) != len(columns):
            return "The number of keys must match the number of columns. (Use commas to separate keys.)"
    else:
        keys = columns


    source = Source()

    try:
        metadata = source.get_metadata(keys, value, version)
    except ValueError:
        return "Unable to find lookup table for keys `{}`, value `{}`, and version `{}`".format(
            keys, value, version
        )

    pandas_types = {}

    for column, key in zip(columns, keys):
        column_type = input_columns[column].type
        key_type = WORKBENCH_TYPE_LOOKUP[metadata["columns"][key]["type"]]

        if column_type != key_type:
            return "Column `{}` has type `{}`. Key `{}` requires type `{}`.".format(
                column, column_type, key, key_type
            )

        pandas_types[key] = PANDAS_TYPE_LOOKUP[key_type]

    lookup_table = source.get_table(keys, value, version, column_types=pandas_types)

    return table.join(lookup_table, on=keys)

"""
NOTE: Below this point is a port of the original agate-lookup module.
https://github.com/wireservice/agate-lookup

This should really be in it's own module, but Workbench doesn't currently
support that.
"""

def make_table_path(keys, value, version=None):
    """
    Generate a path to find a given lookup table.
    """
    if isinstance(keys, (list, tuple)):
        keys = '/'.join(keys)

    path = '%s/%s' % (keys, value)

    if version:
        path += '.%s' % version

    path += '.csv'

    return path


def make_metadata_path(keys, value, version=None):
    """
    Generate a path to find a given lookup table.
    """
    if isinstance(keys, (list, tuple)):
        keys = '/'.join(keys)

    path = '%s/%s' % (keys, value)

    if version:
        path += '.%s' % version

    path += '.csv.yml'

    return path


class Source(object):
    """
    A reference to an archive of lookup tables. This is a remote location with
    lookup table and metadata files at a known path structure.
    :param root:
        The root URL to prefix all data and metadata paths.
    :param cache:
        A path in which to store cached copies of any tables that are used, so
        they can continue to be used offline.
    """
    def __init__(self, root='http://wireservice.github.io/lookup'):
        self._root = root

    def get_metadata(self, keys, value, version=None):
        """Fetches metadata related to a specific lookup table.

        See :meth:`Source.get_table` for parameter details.
        """
        path = make_metadata_path(keys, value, version)
        url = '%s/%s' % (self._root, path)

        r = requests.get(url)

        try:
            data = yaml.load(r.text)
        except:
            raise ValueError('Failed to read or parse YAML at %s' % url)

        return data

    def get_table(self, keys, value, version=None, column_types=None):
        """Fetches and creates an pandas table from a specified lookup table.

        The resulting table will automatically have row names created for the
        key columns, thus allowing it to be used as a lookup.

        :param keys:
            Either a single string or a sequence of keys that identify the
            "left side" of the table. For example :code:`'fips'` or
            :code:`['city', 'year']`.
        :param value:
            The value that is being looked up from the given keys. For example
            :code:`'state'` or :code:`'population'`.
        :param version:
            An optional version of the given lookup, if more than one exists.
            For instance :code:`'2007'` for the 2007 edition of the NAICS codes
            or :code:`'2012'` for the 2012 version.
        """
        path = make_table_path(keys, value, version)
        url = '%s/%s' % (self._root, path)

        r = requests.get(url)

        df = pd.read_csv(six.StringIO(r.text), dtype=column_types, index_col=False)
        df.set_index(keys, drop=True, inplace=True)

        return df