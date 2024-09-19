import wrapr as wr

if __name__ == "__main__":
    wr.settings.set_Rview(False)
    bs = wr.library("base")
    dt = wr.library("datasets")

    l1 = bs.list([1, 2, 3, 4])
    iris1 = dt.iris

    bs = wr.library("base")
    dt = wr.library("datasets")

    wr.settings.set_Rview(True)
    l2 = bs.list([1, 2, 3, 4])
    iris2 = dt.iris
    iris2.to_py()
