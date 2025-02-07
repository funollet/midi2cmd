from midi2cmd.utils import dict_to_tuples


def test_dict_to_tuples():
    d = {
        1: {
            "dog": "apple",
            "cat": {
                11: "orange",
                12: "banana",
                13: "watermelon",
            },
        }
    }
    expected_output = [
        ((1, "dog"), "apple"),
        ((1, "cat", 11), "orange"),
        ((1, "cat", 12), "banana"),
        ((1, "cat", 13), "watermelon"),
    ]
    assert dict_to_tuples(d) == expected_output


def test_empty_dict():
    assert dict_to_tuples({}) == []


def test_flat_dict():
    d = {"a": 1, "b": 2}
    expected_output = [(("a",), 1), (("b",), 2)]
    assert dict_to_tuples(d) == expected_output


def test_nested_empty_dict():
    d = {"a": {}}
    assert dict_to_tuples(d) == []
