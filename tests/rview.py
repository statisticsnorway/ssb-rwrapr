# TODO: This file should be renamed. Has the same name as src/ssb_wrapr/review.py
import ssb_wrapr as wr


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
