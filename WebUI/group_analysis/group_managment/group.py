class Group:
    """
    Represents a Group, including its name and member activities
    Attr:
        name str
        members list

    """

    def __init__(self, name: str, members: list):

        if name is not None:
            self.name = name

        if members is not None:
            self.members = members
