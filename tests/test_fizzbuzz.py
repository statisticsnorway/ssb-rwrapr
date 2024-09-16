from functions.fizzbuzz import buzz
from functions.fizzbuzz import fizz
from functions.fizzbuzz import fizzbuzz


def test_fizz():
    assert fizz(3) == "fizz"
    assert fizz(4) == ""


def test_buzz():
    assert buzz(5) == "buzz"
    assert buzz(6) == ""


def test_fizzbuzz():
    assert fizzbuzz([15]) == ["fizzbuzz"]
    assert fizzbuzz([3]) == ["fizz"]
    assert fizzbuzz([5]) == ["buzz"]
    assert fizzbuzz([2]) == [2]
