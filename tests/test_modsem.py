# type: ignore
import rwrapr as wr


def test_to_r_and_back_to_py_s3():
    md = wr.library("modsem", interactive=False)
    m1 = """
      # Outer Model
      X =~ x1 + x2 +x3
      Y =~ y1 + y2 + y3
      Z =~ z1 + z2 + z3

      # Inner model
      Y ~ X + Z + X:Z
    """

    est = md.modsem(m1, data=md.oneInt, method="qml")
    out1 = md.summary(est).__str__()

    est2 = est.to_py(ignore_s3_s4=True)
    out2 = md.summary(est2).__str__()
    assert out1 == out2


def test_s4_to_py():
    lav = wr.library("lavaan", interactive=False)
    md = wr.library("modsem", interactive=False)

    m1 = """
      # Outer Model
      X =~ x1 + x2 +x3
      Y =~ y1 + y2 + y3
      Z =~ z1 + z2 + z3

      # Inner model
      Y ~ X + Z
    """

    est = lav.sem(m1, data=md.oneInt)

    est2 = est.to_py(ignore_s3_s4=True)

    assert isinstance(est, wr.RView)
    assert isinstance(est2, wr.RDict)
    assert isinstance(est2["Fit"], wr.RView)  # do not convert recursively
