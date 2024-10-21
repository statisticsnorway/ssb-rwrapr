# type: ignore
import rwrapr as wr


def test_toR_AndBackToPyS3():
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

    est2 = est.toPy(ignoreS3=True)
    out2 = md.summary(est2).__str__()
    assert out1 == out2
