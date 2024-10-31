# type: ignore
import numpy as np
import pytest
from rpy2.rinterface_lib.embedded import RRuntimeError

import rwrapr as wr


st = wr.library("SSBtools")
gs = wr.library("GaussSuppression")
bs = wr.library("base")

printInc = False


def test_gausssuppressionfromdata_works():
    m = gs.GaussSuppressionFromData(
        st.SSBtoolsData("z1"), np.array([1, 2]), 3, printInc=printInc
    )
    assert np.all(gs.which(m["suppressed"]) == [12, 13, 22, 23, 42, 43])


# Sample with seed inside test_that do not work
z3 = st.SSBtoolsData("z3")
upper = z3["region"].str.isupper()
z3["region"][upper] = z3["region"][upper] + "2"
z3["region"][~upper] = z3["region"][~upper].str.upper() + "1"
z3["fylke"] = z3["fylke"].astype("int")
z3["kostragr"] = z3["kostragr"].astype("int")
z3["ant"] = z3["ant"].astype("int")

mm = st.ModelMatrix(z3.iloc[:, np.arange(0, 6)], crossTable=True, sparse=False)

x_p = mm["modelMatrix"]
k = np.arange(20000)

bs.set_seed(123)
sample_k = bs.sample(k)
y = x_p.flatten(order="F")
y[k] = y[sample_k]
x = y.reshape(x_p.shape, order="F")


# test_that("Advanced with integer overflow", {
def test_advanced_with_integer_overflow():
    # This test will not pass on all platforms, ask the original author for more information
    a = gs.GaussSuppressionFromData(
        z3,
        np.arange(1, 7),
        7,
        x=mm["modelMatrix"],
        crossTable=mm["crossTable"],
        maxN=5,
        singletonMethod="anySumOld",
        printInc=printInc,
    )
    assert bs.sum(bs.which(a["suppressed"])) == 599685

    a = gs.GaussSuppressionFromData(
        z3,
        np.arange(1, 7),
        7,
        x=x,
        crossTable=mm["crossTable"],
        singletonMethod="anySumOld",
        printInc=printInc,
    )
    assert bs.sum(bs.which(a["suppressed"])) == 525957

    # This test involves integer overflow in AnyProportionalGaussInt
    a = gs.GaussSuppressionFromData(
        z3,
        np.arange(1, 7),
        7,
        x=x,
        crossTable=mm["crossTable"],
        protectZeros=False,
        secondaryZeros=True,
        singletonMethod="anySumNOTprimaryOld",
        printInc=printInc,
    )
    assert bs.sum(bs.which(a["suppressed"])) == 411693

    # This test involves all ways of updating A["r[[i]]"], A$x[[i]], B$r[[i]], B$x[[i]]  (Including integer overflow)
    a = gs.GaussSuppressionFromData(
        z3,
        np.arange(1, 7),
        7,
        x=x,
        crossTable=mm["crossTable"],
        protectZeros=False,
        secondaryZeros=True,
        testMaxInt=10,
        singletonMethod="anySumNOTprimaryOld",
        printInc=printInc,
    )
    assert bs.sum(bs.which(a["suppressed"])) == 411693

    a = gs.GaussSuppressionFromData(
        z3,
        np.arange(1, 7),
        7,
        x=x,
        crossTable=mm["crossTable"],
        protectZeros=False,
        secondaryZeros=True,
        allNumeric=True,
        singletonMethod="anySumNOTprimaryOld",
        printInc=printInc,
    )
    assert bs.sum(bs.which(a["suppressed"])) == 411693

    # This test involves True return in AnyProportionalGaussInt after ReduceGreatestDivisor (identical length 3 vectors)
    x[:, np.arange(200, 300)] = np.round(
        0.6 * x[:, np.arange(200, 300)] + 0.6 * x[:, np.arange(300, 400)]
    )
    a = gs.GaussSuppressionFromData(
        z3,
        np.arange(1, 7),
        7,
        x=x,
        crossTable=mm["crossTable"],
        singletonMethod="anySumOld",
        printInc=printInc,
    )
    assert bs.sum(bs.which(a["suppressed"])) == 576555


def test_structural_empty_and_remove_empty():
    a1 = gs.GaussSuppressionFromData(
        z3.iloc[np.arange(100, 300)], np.arange(1, 7), 7, printInc=printInc
    )
    a2 = gs.GaussSuppressionFromData(
        z3.iloc[np.arange(100, 300)],
        np.arange(1, 7),
        7,
        printInc=printInc,
        structuralEmpty=True,
    )
    a3 = gs.GaussSuppressionFromData(
        z3.iloc[np.arange(100, 300)],
        np.arange(1, 7),
        7,
        printInc=printInc,
        removeEmpty=True,
    )
    k = a1["suppressed"] != a2["suppressed"]
    assert np.all(a1.loc[~k, :].reset_index(drop=True) == a3.reset_index(drop=True))
    assert np.all(a2.loc[~k, :].reset_index(drop=True) == a3.reset_index(drop=True))
    assert np.all(a1.loc[k, "ant"] == 0)


def test_extend0_and_various_hierarchy_input():
    z2 = st.SSBtoolsData("z2")

    with wr.ToggleRView(True):  # add warnings for these unexpected results
        dimLists = st.FindDimLists(z2.drop("ant", axis=1))
        hi = bs.list(
            bs.c("region", "fylke", "kostragr"), hovedint=dimLists.to_py()["hovedint"]
        )

    a1 = gs.GaussSuppressionFromData(z2, np.arange(1, 5), 5, printInc=printInc)
    a2 = gs.GaussSuppressionFromData(
        z2, freqVar="ant", hierarchies=dimLists, printInc=printInc
    )
    a3 = gs.GaussSuppressionFromData(
        z2, freqVar="ant", hierarchies=hi, printInc=printInc
    )

    assert np.all(a1.reset_index(drop=True) == a2.reset_index(drop=True))
    assert np.all(a3.reset_index(drop=True) == a2.reset_index(drop=True))

    z2_ = z2.iloc[z2["ant"].to_numpy() != 0]

    a1 = gs.GaussSuppressionFromData(
        z2_, np.arange(1, 5), 5, extend0=True, output="publish_inner", printInc=printInc
    )

    assert np.all(a1["publish"].reset_index(drop=True) == a2.reset_index(drop=True))

    a2 = gs.GaussSuppressionFromData(
        z2_,
        freqVar="ant",
        hierarchies=dimLists,
        extend0=True,
        output="publish_inner",
        printInc=printInc,
    )
    a3 = gs.GaussSuppressionFromData(
        z2_,
        freqVar="ant",
        hierarchies=hi,
        extend0=True,
        output="publish_inner",
        printInc=printInc,
    )

    assert np.all(
        a1["publish"].reset_index(drop=True) == a2["publish"].reset_index(drop=True)
    )
    assert np.all(
        a3["publish"].reset_index(drop=True) == a2["publish"].reset_index(drop=True)
    )

    assert np.all(
        a1["inner"][a2["inner"].columns].reset_index(drop=True)
        == a2["inner"].reset_index(drop=True)
    )
    assert np.all(
        a3["inner"][a1["inner"].columns].reset_index(drop=True)
        == a1["inner"].reset_index(drop=True)
    )

    a1_ = gs.GaussSuppressionFromData(
        z2_,
        np.arange(1, 5),
        5,
        extend0="all",
        output="publish_inner",
        printInc=printInc,
    )
    a2_ = gs.GaussSuppressionFromData(
        z2_,
        freqVar="ant",
        hierarchies=dimLists,
        extend0="all",
        output="publish_inner",
        printInc=printInc,
    )
    a3_ = gs.GaussSuppressionFromData(
        z2_,
        freqVar="ant",
        hierarchies=hi,
        extend0="all",
        output="publish_inner",
        printInc=printInc,
    )

    assert np.all(
        a1["publish"].reset_index(drop=True) == a1_["publish"].reset_index(drop=True)
    )
    assert np.all(
        a1["inner"].reset_index(drop=True) == a1_["inner"].reset_index(drop=True)
    )
    assert np.all(
        a2["publish"].reset_index(drop=True) == a2_["publish"].reset_index(drop=True)
    )
    assert np.all(
        a2["inner"].reset_index(drop=True) == a2_["inner"].reset_index(drop=True)
    )
    assert np.all(
        a3["publish"].reset_index(drop=True) == a3_["publish"].reset_index(drop=True)
    )
    assert np.all(
        a3["inner"].reset_index(drop=True) == a3_["inner"].reset_index(drop=True)
    )

    z2__ = z2_.loc[z2_["hovedint"] != "trygd"]

    a2 = gs.GaussSuppressionFromData(
        z2__,
        freqVar="ant",
        hierarchies=dimLists,
        extend0="all",
        output="publish_inner",
        printInc=printInc,
    )
    a3 = gs.GaussSuppressionFromData(
        z2__,
        freqVar="ant",
        hierarchies=hi,
        extend0="all",
        output="publish_inner",
        printInc=printInc,
    )

    assert np.all(
        a2["publish"].reset_index(drop=True) == a3["publish"].reset_index(drop=True)
    )
    assert np.all(
        a3["inner"][a2["inner"].columns].reset_index(drop=True)
        == a2["inner"].reset_index(drop=True)
    )

    assert np.all(a2["publish"].shape == a2_["publish"].shape)
    assert np.all(a2["inner"].shape == a2_["inner"].shape)
    assert np.all(a3["publish"].shape == a3_["publish"].shape)
    assert np.all(a3["inner"].shape == a3_["inner"].shape)

    z2___ = z2__.loc[z2__["fylke"] != 10]

    a2_ = gs.GaussSuppressionFromData(
        z2___,
        freqVar="ant",
        hierarchies=dimLists,
        extend0="all",
        output="publish_inner",
        printInc=printInc,
    )
    a3_ = gs.GaussSuppressionFromData(
        z2___,
        freqVar="ant",
        hierarchies=hi,
        extend0="all",
        output="publish_inner",
        printInc=printInc,
    )

    assert np.all(a2["publish"].shape == a2_["publish"].shape)
    assert np.all(a2["inner"].shape == a2_["inner"].shape)

    assert a3_["inner"].shape[0] < a3["inner"].shape[0]
    assert a3_["publish"].shape[0] < a3["publish"].shape[0]


def dominancerule_and_ncontributorsrule_CandidatesNum_singleton_forced_unsafe():
    bs.set_seed(123)
    z = st.MakeMicro(st.SSBtoolsData("z2"), "ant")
    z["char"] = bs.sample(bs.paste0("char", np.arange(1, 11)), bs.nrow(z), replace=True)
    z["value"] = bs.rnorm(bs.nrow(z)) ** 2

    CandidatesNum = gs.reval("CandidatesNum", rview=True)
    DominanceRule = gs.reval("DominanceRule", rview=True)
    a = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        candidates=CandidatesNum,
        primary=DominanceRule,
        singletonMethod="sub2Sum",
        n=bs.c(1, 2),
        k=bs.c(65, 85),
        printInc=printInc,
    )

    NContributorsRule = gs.reval("NContributorsRule", rview=True)
    b = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        candidates=CandidatesNum,
        primary=NContributorsRule,
        singletonMethod="none",
        removeCodes=bs.paste0("char", np.arange(1, 3)),
        printInc=printInc,
    )

    assert np.all(
        bs.as_numeric(bs.which(a["primary"]))
        == bs.c(8, 17, 18, 23, 52, 53, 58, 63, 73, 77, 78, 80, 83, 87, 90, 92, 97, 98)
    )
    assert np.all(
        bs.as_numeric(bs.which(b["primary"]))
        == bs.c(8, 18, 23, 53, 63, 78, 83, 87, 90, 97, 98)
    )

    z["seq2"] = (np.arange(z.shape[0]) + 1) ** 2

    aseq2 = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar=bs.c("seq2", "value"),
        candidatesVar="value",
        dominanceVar="value",
        charVar="char",
        candidates=CandidatesNum,
        primary=DominanceRule,
        singletonMethod="sub2Sum",
        n=bs.c(1, 2),
        k=bs.c(65, 85),
        printInc=printInc,
    )

    assert np.all(a[bs.names(a)] == aseq2[bs.names(a)])

    z["char"] = bs.paste0("char", np.arange(bs.nrow(z)) + 1)
    NcontributorsRule = gs.reval("NcontributorsRule", rview=True)
    d1 = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        candidates=CandidatesNum,
        primary=NcontributorsRule,
        singletonMethod="none",
        removeCodes=bs.paste0("char", np.arange(1, 21)),
        printInc=printInc,
        freqVar="ant",
        preAggregate=False,
        maxN=10,
        whenEmptyUnsuppressed="stop",
    )

    d2 = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        candidates=CandidatesNum,
        primary=NContributorsRule,
        singletonMethod="none",
        removeCodes=np.arange(1, 21),
        printInc=printInc,
        preAggregate=False,
        maxN=10,  # Empty freq in CandidatesNum
        whenEmptyUnsuppressed="stop",
    )

    assert np.all(d1.loc[:, bs.names(d1) != "ant"] == d2)

    bs.set_seed(123)
    z["value"] = (
        bs.rnorm(bs.nrow(z)) ** 2
    )  # Need to generate again ... not same as above
    bs.set_seed(1986)  # Seed is not randomly chosen
    z["char"] = bs.sample(
        bs.paste0("char", bs.c(1, 1, 1, 1, 1, 2, 2, 2, 3, 4)), bs.nrow(z), replace=True
    )
    SingletonUniqueContributor = gs.reval("SingletonUniqueContributor", rview=True)
    b0 = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        maxN=2,
        candidates=CandidatesNum,
        primary=NcontributorsRule,
        printInc=printInc,
        singleton=SingletonUniqueContributor,
        singletonMethod="none",
    )
    b1 = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        maxN=2,
        candidates=CandidatesNum,
        primary=NcontributorsRule,
        printInc=printInc,
        singleton=SingletonUniqueContributor,
        singletonMethod="sub2Sum",
    )
    b2 = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        maxN=2,
        candidates=CandidatesNum,
        primary=NcontributorsRule,
        printInc=printInc,
        singleton=SingletonUniqueContributor,
        singletonMethod="numFTT",
    )
    b3 = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        maxN=2,
        candidates=CandidatesNum,
        primary=bs.c(
            63, 73, 77
        ),  # primary = bs.c(8, 18, 23, 53, 63, 73, 77, 78, 90, 97, 98, 100),
        forced=bs.c(11, 13, 18, 20, 40),
        printInc=printInc,
        singleton=SingletonUniqueContributor,
        singletonMethod="numFTT",
    )
    b4 = gs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        maxN=2,
        candidates=CandidatesNum,
        primary=bs.c(8, 18, 23, 53, 63, 73, 77, 78, 90, 97, 98, 100),
        forced=bs.c(11, 13, 18, 20, 40),
        printInc=printInc,
        singleton=SingletonUniqueContributor,
        singletonMethod="numFTT",
    )

    b5 = bs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        maxN=2,
        candidates=CandidatesNum,
        primary=bs.c(8, 18, 23, 53, 63, 73, 77, 78, 90, 97, 98, 100),
        forced=bs.c(11, 13, 18, 20, 40),
        printInc=printInc,
        protectZeros=True,
    )

    b6 = bs.GaussSuppressionFromData(
        z,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        maxN=2,
        candidates=CandidatesNum,
        primary=bs.c(8, 18, 23, 53, 63, 73, 77, 78, 90, 97, 98, 100),
        forced=np.arange(1, 30 + 1),
        printInc=printInc,
        protectZeros=False,
    )

    assert np.all(bs.sum(b0["suppressed"]) == 32)
    assert np.all(bs.sum(b1["suppressed"]) == 33)
    assert np.all(bs.sum(b2["suppressed"]) == 35)
    assert np.all(bs.sum(b3["suppressed"]) == 12)
    assert np.all(bs.sum(b4["suppressed"]) == 32)
    assert np.all(bs.sum(b5["suppressed"]) == 27)
    assert np.all(bs.sum(b6["suppressed"]) == 19)
    assert np.all(bs.sum(b3["unsafe"]) == 0)
    assert np.all(bs.sum(b4["unsafe"]) == 1)
    assert np.all(bs.sum(b5["unsafe"]) == 1)
    assert np.all(bs.sum(b6["unsafe"]) == 3)

    # Code to see differences:
    # "sub2Sum" solves G-problem
    # "numFTT" needed to solve K-problem.
    sn = bs.c(
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        2,
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
    )
    sf = bs.c(
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
    )
    sum_suppressed = bs.integer(0)

    for m1 in bs.c("none", "anySumNOTprimary"):
        for m2 in bs.c("none", "sub2Sum", "numFTT"):
            b = bs.GaussSuppressionFromData(
                z,
                dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
                numVar="value",
                charVar="char",
                maxN=2,
                candidates=CandidatesNum,
                primary=NcontributorsRule,
                printInc=printInc,
                singleton=bs.list(freq=bs.as_logical(sf), num=bs.as_integer(sn)),
                singletonMethod=bs.c(freq=m1, num=m2),
            )
            sum_suppressed = bs.c(sum_suppressed, bs.sum(b["suppressed"]))

    assert np.all(sum_suppressed == bs.c(32, 33, 35, 35, 38, 40))

    sample_int = bs.function("sample.int")
    bs.set_seed(1138)
    sum_suppressed = bs.integer(0)
    zz = z.iloc[sample_int(bs.nrow(z), 100, replace=True) - 1, :]
    for c2 in bs.c("F", "T"):
        for c3 in bs.c("F", "T", "H"):
            for c4 in bs.c("F", "T"):
                b = bs.GaussSuppressionFromData(
                    zz,
                    dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
                    numVar="value",
                    charVar="char",
                    maxN=2,
                    printInc=printInc,
                    candidates=CandidatesNum,
                    primary=NcontributorsRule,
                    singleton=SingletonUniqueContributor,
                    singletonMethod=bs.paste0("numF", c2, c3, c4),
                )
                sum_suppressed = bs.c(sum_suppressed, bs.sum(b["suppressed"]))

    assert np.all(
        sum_suppressed == bs.c(49, 55, 51, 55, 53, 55, 49, 57, 52, 57, 55, 57)
    )

    # Why extra primary needed for 5:Total when "numFTH"
    # can be seen by looking at
    # b[b["region"] == 5, ]
    # zz[zz["fylke"] == 5 & zz$hovedint == "annet", ]
    # zz[zz["fylke"] == 5 & zz$hovedint == "arbeid", ]
    # zz[zz["fylke"] == 5 & zz$hovedint == "soshjelp", ]

    sum_suppressed = bs.integer(0)
    for singletonMethod in bs.c(
        "numFFF", "numtFF", "numTFF", "numtTT", "numtTH", "numtTFT", "numtTHT"
    ):
        b = bs.GaussSuppressionFromData(
            zz,
            dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
            numVar="value",
            charVar="char",
            maxN=2,
            printInc=printInc,
            candidates=CandidatesNum,
            primary=NcontributorsRule,
            singleton=SingletonUniqueContributor,
            singletonMethod=singletonMethod,
            inputInOutput=bs.c(False, True),
        )  # singleton not in publish and therefore not primary suppressed
        sum_suppressed = bs.c(sum_suppressed, bs.sum(b["suppressed"]))

    assert np.all(sum_suppressed == bs.c(17, 18, 18, 19, 19, 23, 23))

    # To make non-suppressed singletons
    SUC = gs.reval(
        "function(..., removeCodes, primary) SingletonUniqueContributor(..., removeCodes = character(0), primary = integer(0))",
        rview=True,
    )
    sum_suppressed = bs.integer(0)
    for singletonMethod in bs.c("numFFF", "numtFF", "numTFF"):
        b = bs.GaussSuppressionFromData(
            zz,
            dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
            numVar="value",
            charVar="char",
            maxN=2,
            printInc=printInc,
            candidates=CandidatesNum,
            primary=NcontributorsRule,
            removeCodes="char1",
            singleton=SUC,
            singletonMethod=singletonMethod,
        )
        sum_suppressed = bs.c(sum_suppressed, bs.c(59, 59, 67))

    zz["char"][np.arange(1, 16)] = "char5"
    b = bs.GaussSuppressionFromData(
        zz,
        dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
        numVar="value",
        charVar="char",
        maxN=2,
        printInc=printInc,
        candidates=CandidatesNum,
        primary=NcontributorsRule,
        singleton=SingletonUniqueContributor,
        singletonMethod="numFTFW",
    )
    assert np.all(
        sum(b["suppressed"]) == 51
    )  # Here "if (s_unique == primarySingletonNum[i])" in SSBtools::GaussSuppression matters.

    bs.set_seed(193)
    zz["A"] = bs.sample(
        bs.paste0("A", bs.c(1, 1, 1, 1, 1, 2, 2, 2, 3, 4)), bs.nrow(zz), replace=True
    )
    zz["B"] = bs.sample(
        bs.paste0("B", bs.c(1, 1, 1, 1, 1, 2, 2, 2, 3, 4)), bs.nrow(zz), replace=True
    )
    rcd = bs.data_frame(char="char2", A=bs.c("A1", "A2"), B="B1")
    removeCodes = bs.list(None, rcd, bs.as_list(rcd))
    k = bs.integer(0)
    for specialMultiple in bs.c(False, True):
        for i in np.arange(1, 3):
            b = bs.GaussSuppressionFromData(
                zz,
                dimVar=bs.c("region", "fylke", "kostragr", "hovedint"),
                numVar="value",
                charVar=bs.c("char", "A", "B"),
                maxN=2,
                printInc=printInc,
                candidates=CandidatesNum,
                primary=NcontributorsRule,
                singleton=SingletonUniqueContributor,
                singletonMethod="numTTTTT",
                output="inputGaussSuppression",
                specialMultiple=specialMultiple,
                removeCodes=removeCodes[i],
            )
            k = bs.function(
                "function(b, k) c(k, 0L, as.vector(table(b$singleton)[as.character(unique(b$singleton))]))"
            )(b, k)

    assert np.all(
        k,
        bs.c(
            0,
            1,
            1,
            1,
            1,
            1,
            2,
            19,
            1,
            1,
            1,
            1,
            0,
            1,
            1,
            1,
            1,
            1,
            2,
            20,
            1,
            1,
            1,
            0,
            1,
            29,
            0,
            2,
            6,
            3,
            9,
            9,
            1,
            0,
            2,
            5,
            3,
            9,
            10,
            1,
            0,
            2,
            5,
            1,
            1,
            2,
            17,
            2,
        ),
    )


def interpret_primary_output_correctly():
    x = st.SSBtoolsData("sprt_emp_withEU").iloc[:, bs.c(0, 1, 4, 2, 3)]

    p1 = gs.reval("function(num, ...) round(10 * num[, 1])%%10 == 3", rview=True)
    p2 = gs.reval("function(num, ...) round(10 * num)%%10 == 3", rview=True)
    p3 = gs.reval(
        "function(num, ...) as.data.frame(round(10 * num)%%10 == 3)", rview=True
    )
    p4 = gs.reval(
        """
        function(num, ...)
            list(primary = as.data.frame(round(10 * num)%%10 == 3),
                 numExtra = data.frame(numExtra = round(10 * num[, 1])%%10))
    """,
        rview=True,
    )

    p12 = gs.reval(
        """
    function(...) {
      p2 = function(num, ...) round(10 * num)%%10 == 3
      p  = p2(...)
      p[] = as.integer(p)
      p
    }""",
        rview=True,
    )

    G = gs.function(
        """
    function(x, primary, printInc, formula = ~eu * year + age:geo) {
      which(GaussSuppressionFromData(data = x, formula = formula, numVar = "ths_per",
                                     primary = primary, singleton = NULL,
                                     output = "inputGaussSuppression",
                                     printInc = printInc)$primary)
    }"""
    )

    # Case when x is square
    gp1 = G(x, p1, printInc=printInc)
    assert np.all(G(x, p2, printInc=printInc) == gp1)
    assert np.all(G(x, p3, printInc=printInc) == gp1)
    assert np.all(G(x, p4, printInc=printInc) == gp1)
    assert np.all(
        len(G(x, p12, printInc=printInc)) == 0
    )  # since interpret as xExtraPrimary

    # Case when x is not square
    gp1_ = G(x, p1, printInc=printInc, formula="~age * geo")
    assert np.all(G(x, p2, printInc=printInc, formula="~age * geo") == gp1_)
    assert np.all(G(x, p3, printInc=printInc, formula="~age * geo") == gp1_)
    assert np.all(G(x, p4, printInc=printInc, formula="~age * geo") == gp1_)

    with pytest.raises(RRuntimeError):
        G(
            x, p12, printInc=printInc, formula="~age * geo"
        )  #  Error 0 index found in primary output (change to logical?)

    # Single column xExtraPrimary, Matrix and matrix
    x["freq"] = bs.round(
        bs.sqrt(x["ths_per"])
        + bs.as_integer(x["year"])
        - 2014
        + 0.2 * np.arange(-7, 11)
    )
    z = x.loc[x["year"] == "2014"].drop(["ths_per", "year"], axis=1)

    K = gs.function(
        """function(z, primary, printInc = FALSE) {
      GaussSuppressionFromData(data = z, formula = ~geo + age, freqVar = "freq", coalition=7,
                               primary = primary,
                               mc_hierarchies = NULL, upper_bound = Inf,
                               protectZeros = FALSE, secondaryZeros = TRUE,
                               output ="outputGaussSuppression_x",
                               printInc = printInc)$xExtraPrimary
    }"""
    )

    KDisclosurePrimary = gs.reval("KDisclosurePrimary", rview=True)
    e1 = K(z, KDisclosurePrimary)
    e2 = K(z, gs.reval("function (...) as.matrix(KDisclosurePrimary(...))"))

    assert np.all(bs.max(bs.abs(e2 - bs.as_matrix(e1))) == 0)
    e3 = K(
        z, gs.reval("function (...) round(1 + 0.1*as.matrix(KDisclosurePrimary(...)))")
    )  # Warning message: Primary output interpreted as xExtraPrimary (rare case of doubt)
    assert np.all(e3.shape == bs.c(6, 1))


def more_numsingleton():
    sum_suppressed = bs.integer(0)
    for seed in bs.c(116162, 643426):
        bs.set_seed(seed)
        z = st.SSBtoolsData("magnitude1")
        bs.set_seed(seed)
        z["company"] = z["company"].iloc[bs.sample_int(20) - 1].to_numpy()
        z["value"] = z["value"][bs.sample_int(20) - 1].to_numpy()

        dataset = st.SortRows(
            bs.aggregate(
                z.filter(["value"]), z.iloc[:, np.arange(0, 5)], bs.reval("sum")
            )
        )
        for c3 in bs.c("F", "T", "H"):
            for c4 in bs.c("F", "t", "T"):
                for c5 in bs.c("F", "t", "T"):
                    if not (c4 == "F" and c5 != "F"):
                        singletonMethod = bs.paste0("numTt", c3, c4, c5)
                        output = gs.SuppressDominantCells(
                            data=dataset,
                            numVar="value",
                            dimVar=bs.c("sector4", "geo"),
                            contributorVar="company",
                            n=1,
                            k=80,
                            singletonMethod=singletonMethod,
                            printInc=False,
                        )
                        sum_suppressed = bs.c(
                            sum_suppressed, bs.sum(output["suppressed"])
                        )

    assert np.all(
        sum_suppressed
        == bs.c(
            8,
            11,
            13,
            13,
            11,
            13,
            13,
            10,
            11,
            13,
            13,
            11,
            13,
            13,
            10,
            11,
            13,
            13,
            11,
            13,
            13,
            7,
            9,
            10,
            12,
            10,
            11,
            12,
            8,
            10,
            10,
            12,
            11,
            11,
            12,
            8,
            10,
            10,
            12,
            11,
            11,
            12,
        )
    )
