from collections import namedtuple
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from lookup import render


Column = namedtuple("Column", "name, type")


def params_fixture(columns=None, keys=None, value=None, version=None):
    """Helper to build params."""
    return {
        "columns": columns,
        "keys": keys,
        "value": value,
        "version": version  
    }


def table_fixture(with_values=None, types=str):
    df = pd.DataFrame({
        "year": ["2006", "2008", "2009"],
        "month": ["1", "3", "5"],
    }, dtype=types)

    if with_values == "year":
        df["cpi"] = [201.592, 215.303, 214.537]
    elif with_values == "month.nsa":
        df["cpi"] = [198.3, 213.528, 213.856]
    elif with_values == "month.sa":
        df["cpi"] = [199.3, 213.448, 213.022]

    return df


def input_fixture(types="text"):
    return {
        "year": Column("year", types),
        "month": Column("month", types),
    }


class LookupTest(unittest.TestCase):
    def test_no_column(self):
        result = render(
            table_fixture(),
            params_fixture(),
            input_columns=input_fixture()
        )
        expected = pd.DataFrame(table_fixture())
        
        assert_frame_equal(result, expected)

    def test_no_metadata(self):
        result = render(
            table_fixture(),
            params_fixture(["year"], [], "non-existant"),
            input_columns=input_fixture()
        )

        assert result.startswith("Unable to find")

    def test_one_key(self):
        result = render(
            table_fixture(),
            params_fixture(["year"], None, "cpi"),
            input_columns=input_fixture()
        )
        expected = table_fixture(with_values="year")
        
        assert_frame_equal(result, expected)

    def test_two_keys_and_version(self):
        result = render(
            table_fixture(),
            params_fixture(["year", "month"], None, "cpi", "sa"),
            input_columns=input_fixture()
        )
        expected = table_fixture(with_values="month.sa")
        
        assert_frame_equal(result, expected)

    def test_key_names(self):
        df = table_fixture()
        df.rename({"year": "foo"}, inplace=True)

        inputs = input_fixture()
        inputs["foo"] = inputs["year"]

        result = render(
            df,
            params_fixture(["foo", "month"], "year,month", "cpi", "sa"),
            input_columns=inputs
        )
        expected = table_fixture(with_values="month.sa")
        
        assert_frame_equal(result, expected)

    def test_wrong_number_of_key_names(self):
        result = render(
            table_fixture(),
            params_fixture(["foo", "month"], "year", "cpi", "sa"),
            input_columns=input_fixture()
        )

        assert "number of keys" in result

    def test_wrong_types(self):
        result = render(
            table_fixture(types="int64"),
            params_fixture(["year"], None, "cpi"),
            input_columns=input_fixture("integer")
        )

        assert "requires type" in result


if __name__ == '__main__':
    unittest.main()
