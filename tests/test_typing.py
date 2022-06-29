from gwpycore import Singleton

@Singleton
class Foo():
    def __init__(self) -> None:
        self._token = "Brand New"
    @property
    def token(self):
        """The token property."""
        return self._token
    @token.setter
    def token(self, value):
        self._token = value

def test_singleton():
    f1 = Foo()
    f2 = Foo()
    f3 = Foo()
    assert f1.token == "Brand New"
    f1.token = "Changed"
    assert f2.token == "Changed"
    assert f1 == f2
    assert f1 is f2
    assert f2 is f1
    assert f1 == f3
    assert f1 is f3
    assert not isinstance(f1, Singleton)
    assert isinstance(f1,Foo)
    assert type(f1) is not Foo
