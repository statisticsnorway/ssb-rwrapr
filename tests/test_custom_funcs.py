# type: ignore
import pytest
import rwrapr as wr


def test_custom_funcs():
    base = wr.library("base")
    base.__function__(name="foo_attached2namespace", expr="function(x) x * 2")
    assert base.foo_attached2namespace(2) == 4
    foo = base.function("function(x) x * 2")
    assert foo(2) == 4

    with pytest.raises(ValueError):
        foo(b=wr.lazily("2"))

    with pytest.raises(TypeError):
        base.foo_attached2namespace(wr.lazily("2"))
