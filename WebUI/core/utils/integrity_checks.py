import json
import traceback


def import_pattern_json(path):
    """
    Returns the pattern.json specified in the path argument
    """
    patterns = None
    try:
        json_data = open(path, "r").read()
        patterns = json.loads(json_data)
        if not is_valid_user_input(patterns):
            print(
                "There apears to be an error in the provided user patterns. Patterns will not be abstracted"
            )
    except Exception as e:
        print("User Patterns could not be loaded. Patterns will not be abstracted")
        print(traceback.format_exc())
        print(e)
        return

    return patterns


def is_valid_user_input(patterns):
    """given the input of a pattern.json file it returns
    a trruth value of weather or not it is a valid patter input"""
    if type(patterns) != list:
        return False

    ids = []
    names = []
    for element in patterns:

        if type(element) != dict:
            return False

        if "ID" not in element.keys():
            return False
        if type(element["ID"]) != int:
            return False
        ids.append(element["ID"])

        if "Name" not in element.keys():
            return False
        if type(element["Name"]) != str:
            return False
        names.append(element["Name"])

        if "Pattern" not in element.keys():
            return False
        if type(element["Pattern"]) != list:
            return False
        for event in element["Pattern"]:
            if type(event) != str:
                return False

    if len(set(ids)) != len(ids):
        return False
    if len(set(names)) != len(names):
        return False

    return True
