class Identifier:
    """
    Abstract identifier class.
    Implementation should make each instance unique to the object it represents.
    """

    pass


class UserId(Identifier):
    pass


class CustomerId(UserId):
    pass


class OrderId(Identifier):
    pass


class ProductId(Identifier):
    pass


class ProductVersionId(Identifier):
    pass
