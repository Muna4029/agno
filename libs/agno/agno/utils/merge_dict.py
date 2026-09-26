from typing import Any, Dict, Optional


def merge_dictionaries(a: Optional[Dict[str, Any]], b: Optional[Dict[str, Any]]) -> None:
    """
    Recursively merges two dictionaries.
    If there are conflicting keys, values from 'b' will take precedence.

    Args:
        a (Optional[Dict[str, Any]]): The first dictionary to be merged.
        b (Optional[Dict[str, Any]]): The second dictionary, whose values will take precedence.

    Returns:
        None: The function modifies the first dictionary in place.
    """
    if a is None or b is None:
        return
    for key in b:
        if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
            merge_dictionaries(a[key], b[key])
        else:
            a[key] = b[key]
