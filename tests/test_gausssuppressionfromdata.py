# type: ignore
import numpy as np

import rwrapr as wr


ST = wr.library("SSBtools")
GS = wr.library("GaussSuppression")
bs = wr.library("base")

printInc = False


def test_GaussSuppressionFromData_works():
    m = GS.GaussSuppressionFromData(
        ST.SSBtoolsData("z1"), np.array([1, 2]), 3, printInc=printInc
    )
    assert np.all(GS.which(m["suppressed"]) == [12, 13, 22, 23, 42, 43])


# Sample with seed inside test_that do not work
z3 = ST.SSBtoolsData("z3")
upper = z3["region"].str.isupper()
z3["region"][upper] = z3["region"][upper] + "2"
z3["region"][~upper] = z3["region"][~upper].str.upper() + "1"
z3["fylke"] = z3["fylke"].astype("int")
z3["kostragr"] = z3["kostragr"].astype("int")
z3["ant"] = z3["ant"].astype("int")

mm = ST.ModelMatrix(z3.iloc[:, np.arange(0, 6)], crossTable=True, sparse=False)

get_x = GS.function(
    """function(mm) {
    x = mm$modelMatrix
    k = 1:20000
    set.seed(123)
    sample_k = sample(k)
    x[k] = x[sample_k]
    x
}"""
)
x = get_x(mm)


# test_that("Advanced with integer overflow", {
def test_Advanced_with_integer_overflow():
    # This test will not pass on all platforms, ask the original author for more information
    a = GS.GaussSuppressionFromData(
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

    a = GS.GaussSuppressionFromData(
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
    a = GS.GaussSuppressionFromData(
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
    a = GS.GaussSuppressionFromData(
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

    a = GS.GaussSuppressionFromData(
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
    a = GS.GaussSuppressionFromData(
        z3,
        np.arange(1, 7),
        7,
        x=x,
        crossTable=mm["crossTable"],
        singletonMethod="anySumOld",
        printInc=printInc,
    )
    assert bs.sum(bs.which(a["suppressed"])) == 576555


def test_structuralEmpty_and_removeEmpty():
    a1 = GS.GaussSuppressionFromData(
        z3.iloc[np.arange(100, 300)], np.arange(1, 7), 7, printInc=printInc
    )
    a2 = GS.GaussSuppressionFromData(
        z3.iloc[np.arange(100, 300)],
        np.arange(1, 7),
        7,
        printInc=printInc,
        structuralEmpty=True,
    )
    a3 = GS.GaussSuppressionFromData(
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


#
#
#
# test_that("extend0 and various hierarchy input", {
#   z2 = SSBtoolsData("z2")
#   dimLists = SSBtools::FindDimLists(z2[, -5])
#   hi = list(c("region", "fylke", "kostragr"), hovedint = dimLists["hovedint"])
#
#   a1 = GaussSuppressionFromData(z2, np.arange(1, 4+1), 5, printInc = printInc)
#   a2 = GaussSuppressionFromData(z2, freqVar = "ant", hierarchies = dimLists, printInc = printInc)
#   a3 = GaussSuppressionFromData(z2, freqVar = "ant", hierarchies = hi, printInc = printInc)
#
#   expect_identical(a1, a2)
#   expect_identical(a3, a2)
#
#   z2_ = z2[z2["ant"] != 0, ]
#
#   a1 = GaussSuppressionFromData(z2_, np.arange(1, 4+1), 5, extend0 = True, output = "publish_inner", printInc = printInc)
#
#   expect_identical(a1["publish"], a2)
#
#   a2 = GaussSuppressionFromData(z2_, freqVar = "ant", hierarchies = dimLists, extend0 = True, output = "publish_inner", printInc = printInc)
#   a3 = GaussSuppressionFromData(z2_, freqVar = "ant", hierarchies = hi, extend0 = True, output = "publish_inner", printInc = printInc)
#
#   if (False) { # Include code that shows differences
#     tail(a1["inner"])
#     tail(a2["inner"])
#     tail(a3["inner"])
#   }
#
#   expect_identical(a1["publish"], a2$publish)
#   expect_identical(a3["publish"], a2$publish)
#
#   expect_equal(a1["inner[names"](a2$inner)], a2$inner, ignore_attr = True)
#   expect_equal(a3["inner[names"](a1$inner)], a1$inner, ignore_attr = True)
#
#   a1_ = GaussSuppressionFromData(z2_, np.arange(1, 4+1), 5, extend0 = "all", output = "publish_inner", printInc = printInc)
#   a2_ = GaussSuppressionFromData(z2_, freqVar = "ant", hierarchies = dimLists, extend0 = "all", output = "publish_inner", printInc = printInc)
#   a3_ = GaussSuppressionFromData(z2_, freqVar = "ant", hierarchies = hi, extend0 = "all", output = "publish_inner", printInc = printInc)
#
#   expect_identical(a1, a1_)
#   expect_identical(a2, a2_)
#   expect_identical(a3, a3_)
#
#   z2__ = z2_[z2_["hovedint"] != "trygd", ]
#
#   a2 = GaussSuppressionFromData(z2__, freqVar = "ant", hierarchies = dimLists, extend0 = "all", output = "publish_inner", printInc = printInc)
#   a3 = GaussSuppressionFromData(z2__, freqVar = "ant", hierarchies = hi, extend0 = "all", output = "publish_inner", printInc = printInc)
#
#   expect_identical(a3["publish"], a2$publish)
#   expect_equal(a3["inner[names"](a2$inner)], a2$inner, ignore_attr = True)
#
#   expect_identical(lapply(c(a2, a3), dim), lapply(c(a2_, a3_), dim))
#
#   z2___ = z2__[z2__["fylke"] != 10, ]
#
#   a2_ = GaussSuppressionFromData(z2___, freqVar = "ant", hierarchies = dimLists, extend0 = "all", output = "publish_inner", printInc = printInc)
#   a3_ = GaussSuppressionFromData(z2___, freqVar = "ant", hierarchies = hi, extend0 = "all", output = "publish_inner", printInc = printInc)
#
#   expect_identical(lapply(a2, dim), lapply(a2_, dim))
#
#   expect_true(nrow(a3_["inner"]) < nrow(a3$inner))
#   expect_true(nrow(a3_["publish"]) < nrow(a3$publish))
# })
#
#
#
# test_that("DominanceRule and NcontributorsRule + CandidatesNum + singleton + forced/unsafe", {
#   set.seed(123)
#   z = SSBtools::MakeMicro(SSBtoolsData("z2"), "ant")
#   z["char"] = sample(paste0("char", np.arange(1, 10+1)), nrow(z), replace = True)
#   z["value"] = rnorm(nrow(z))^2
#
#   a = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                 candidates = CandidatesNum, primary = DominanceRule, singletonMethod = "sub2Sum",
#                                 n = c(1, 2), k = c(65, 85), printInc = printInc)
#
#
#   b = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                 candidates = CandidatesNum, primary = NcontributorsRule, singletonMethod = "none",
#                                 removeCodes = paste0("char", np.arange(1, 2+1)), printInc = printInc)
#
#   expect_identical(as.numeric(which(a["primary"])), c(8, 17, 18, 23, 52, 53, 58, 63, 73, 77, 78, 80, 83, 87, 90, 92, 97, 98))
#   expect_identical(as.numeric(which(b["primary"])), c(8, 18, 23, 53, 63, 78, 83, 87, 90, 97, 98))
#
#
#   z["seq2"] = (1:nrow(z))^2
#
#   aseq2 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"),
#                                     numVar = c("seq2", "value"),
#                                     candidatesVar = "value",
#                                     dominanceVar = "value",
#                                     charVar = "char", candidates = CandidatesNum,
#                                     primary = DominanceRule, singletonMethod = "sub2Sum",
#                                     n = c(1, 2), k = c(65, 85), printInc = printInc)
#
#   expect_identical(a[names(a)], aseq2[names(a)])
#
#
#   z["char"] = paste0("char", 1:nrow(z))
#   d1 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                 candidates = CandidatesNum, primary = NcontributorsRule, singletonMethod = "none",
#                                 removeCodes = paste0("char", np.arange(1, 20+1)), printInc = printInc,
#                                 freqVar = "ant", preAggregate = False, maxN = 10,
#                                 whenEmptyUnsuppressed = "stop")
#
#   d2 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value",
#                                  candidates = CandidatesNum, primary = NContributorsRule, singletonMethod = "none",
#                                  removeCodes = np.arange(1, 20+1), printInc = printInc,
#                                  preAggregate = False, maxN = 10, # Empty freq in CandidatesNum
#                                  whenEmptyUnsuppressed = "stop")
#
#   expect_equal(d1[names(d1) != "ant"], d2, ignore_attr = True)
#
#
#   if(True){
#     set.seed(123)
#     z["value"] = rnorm(nrow(z))^2  # Need to generate again ... not same as above
#     set.seed(1986) # Seed is not randomly chosen
#     z["char"] = sample(paste0("char", c(1, 1, 1, 1, 1, 2, 2, 2, 3, 4)), nrow(z), replace = True)
#     b0 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                    maxN = 2, candidates = CandidatesNum, primary = NcontributorsRule, printInc = printInc,
#                                    singleton = SingletonUniqueContributor,
#                                    singletonMethod = "none")
#     b1 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                    maxN = 2, candidates = CandidatesNum, primary = NcontributorsRule, printInc = printInc,
#                                    singleton = SingletonUniqueContributor,
#                                    singletonMethod = "sub2Sum")
#     b2 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                    maxN = 2, candidates = CandidatesNum, primary = NcontributorsRule, printInc = printInc,
#                                    singleton = SingletonUniqueContributor,
#                                    singletonMethod = "numFTT")
#     suppressWarnings({b3 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                    maxN = 2, candidates = CandidatesNum,
#                                    primary = c(63, 73, 77),   # primary = c(8, 18, 23, 53, 63, 73, 77, 78, 90, 97, 98, 100),
#                                    forced = c(11, 13, 18, 20, 40),
#                                    printInc = printInc,
#                                    singleton = SingletonUniqueContributor,
#                                    singletonMethod = "numFTT")})
#     suppressWarnings({b4 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                    maxN = 2, candidates = CandidatesNum,
#                                    primary = c(8, 18, 23, 53, 63, 73, 77, 78, 90, 97, 98, 100),
#                                    forced = c(11, 13, 18, 20, 40),
#                                    printInc = printInc,
#                                    singleton = SingletonUniqueContributor,
#                                    singletonMethod = "numFTT")})
#
#     suppressWarnings({b5 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                                      maxN = 2, candidates = CandidatesNum,
#                                                      primary = c(8, 18, 23, 53, 63, 73, 77, 78, 90, 97, 98, 100),
#                                                      forced =  c(11, 13, 18, 20, 40),
#                                                      printInc = printInc,
#                                                      protectZeros = True)})
#
#
#     suppressWarnings({b6 = GaussSuppressionFromData(z, dimVar = c("region", "fylke", "kostragr", "hovedint"), numVar = "value", charVar = "char",
#                                                      maxN = 2, candidates = CandidatesNum,
#                                                      primary = c(8, 18, 23, 53, 63, 73, 77, 78, 90, 97, 98, 100),
#                                                      forced = np.arange(1, 30+1),
#                                                      printInc = printInc,
#                                                      protectZeros = False)})
#
#
#     expect_equal(sum(b0["suppressed"]), 32)
#     expect_equal(sum(b1["suppressed"]), 33)
#     expect_equal(sum(b2["suppressed"]), 35)
#     expect_equal(sum(b3["suppressed"]), 12)
#     expect_equal(sum(b4["suppressed"]), 32)
#     expect_equal(sum(b5["suppressed"]), 27)
#     expect_equal(sum(b6["suppressed"]), 19)
#     expect_equal(sum(b3["unsafe"]), 0)
#     expect_equal(sum(b4["unsafe"]), 1)
#     expect_equal(sum(b5["unsafe"]), 1)
#     expect_equal(sum(b6["unsafe"]), 3)
#
#     skip_on_cran()
#
#     # Code to see differences:
#     #"sub2Sum" solves G-problem
#     #"numFTT" needed to solve K-problem.
#     if (False) for (myChar in c("G", "K")) {
#       kp = b0[b0["region"] == myChar & b0$primary, ]
#       k0 = b0[b0["region"] == myChar & b0$suppressed, ]
#       k1 = b1[b2["region"] == myChar & b1$suppressed, ]
#       k2 = b2[b2["region"] == myChar & b2$suppressed, ]
#       cat("===============", myChar, "=============== \n")
#       for (kk in c("kp", "k0", "k1", "k2")) {
#         cat("   -----", kk, "-----\n")
#         ma = Match(z[c("region", "hovedint")], get(kk)[c("region", "hovedint")])
#         print(z[!is.na(ma), ])
#       }
#     }
#     sn = c(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 1, 0, 1,
#            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0)
#     sf = c(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1,
#       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0)
#     sum_suppressed = integer(0)
#     for (m1 in c("none", "anySumNOTprimary"))
#       for (m2 in c("none", "sub2Sum", "numFTT")) {
#         b = GaussSuppressionFromData(z,
#                                     dimVar = c("region", "fylke", "kostragr", "hovedint"),
#                                     numVar = "value", charVar = "char", maxN = 2,
#                                     candidates = CandidatesNum,
#                                     primary = NcontributorsRule,
#                                     printInc = printInc,
#             singleton = list(freq = as.logical(sf), num = as.integer(sn)),
#             singletonMethod = c(freq = m1, num = m2))
#             sum_suppressed = c(sum_suppressed, sum(b["suppressed"]))
#       }
#     expect_equal(sum_suppressed, c(32, 33, 35, 35, 38, 40))
#
#
#     set.seed(1138)
#     sum_suppressed = integer(0)
#     zz = z[sample.int(nrow(z), 100, replace = True), ]
#     for (c2 in c("F", "T"))
#       for (c3 in c("F", "T", "H"))
#        for (c4 in c("F", "T")) {
#         b = GaussSuppressionFromData(zz,
#                                       dimVar = c("region", "fylke", "kostragr", "hovedint"),
#                                       numVar = "value", charVar = "char",
#                                       maxN = 2, printInc = printInc,
#                                       candidates = CandidatesNum,
#                                       primary = NcontributorsRule,
#                                       singleton = SingletonUniqueContributor,
#                                       singletonMethod = paste0("numF", c2, c3, c4))
#         sum_suppressed = c(sum_suppressed, sum(b["suppressed"]))
#       }
#     expect_equal(sum_suppressed, c(49, 55, 51, 55, 53, 55, 49, 57, 52, 57, 55, 57))
#
#     # Why extra primary needed for 5:Total when "numFTH"
#     # can be seen by looking at
#     # b[b["region"] == 5, ]
#     # zz[zz["fylke"] == 5 & zz$hovedint == "annet", ]
#     # zz[zz["fylke"] == 5 & zz$hovedint == "arbeid", ]
#     # zz[zz["fylke"] == 5 & zz$hovedint == "soshjelp", ]
#
#     sum_suppressed = integer(0)
#     for (singletonMethod  in c("numFFF", "numtFF","numTFF", "numtTT", "numtTH", "numtTFT", "numtTHT")) {
#         b = GaussSuppressionFromData(zz,
#                                       dimVar = c("region", "fylke", "kostragr", "hovedint"),
#                                       numVar = "value", charVar = "char",
#                                       maxN = 2, printInc = printInc,
#                                       candidates = CandidatesNum,
#                                       primary = NcontributorsRule,
#                                       singleton = SingletonUniqueContributor,
#                                       singletonMethod = singletonMethod,
#           inputInOutput = c(False, True)) # singleton not in publish and therefore not primary suppressed
#         sum_suppressed = c(sum_suppressed, sum(b["suppressed"]))
#       }
#     expect_equal(sum_suppressed, c(17, 18, 18, 19, 19, 23, 23))
#
#
#     # To make non-suppressed singletons
#     SUC = function(..., removeCodes, primary) SingletonUniqueContributor(..., removeCodes = character(0), primary = integer(0))
#     sum_suppressed = integer(0)
#     for (singletonMethod  in c("numFFF", "numtFF","numTFF")) {
#       b = GaussSuppressionFromData(zz,
#                                   dimVar = c("region", "fylke", "kostragr", "hovedint"),
#                                   numVar = "value", charVar = "char",
#                                   maxN = 2, printInc = printInc,
#                                   candidates = CandidatesNum,
#                                   primary = NcontributorsRule,
#                                   removeCodes = "char1",
#                                   singleton = SUC,
#                                   singletonMethod = singletonMethod)
#       sum_suppressed = c(sum_suppressed, c(59, 59, 67))
#     }
#
#     zz["char[np.arange"](1,15)] = "char5"
#     expect_warning({b = GaussSuppressionFromData(zz,
#                                   dimVar = c("region", "fylke", "kostragr", "hovedint"),
#                                   numVar = "value", charVar = "char",
#                                   maxN = 2, printInc = printInc,
#                                   candidates = CandidatesNum,
#                                   primary = NcontributorsRule,
#                                   singleton = SingletonUniqueContributor,
#                                   singletonMethod = "numFTFW")})
#     expect_equal(sum(b["suppressed"]), 51)  # Here "if (s_unique == primarySingletonNum[i])" in SSBtools::GaussSuppression matters.
#
#
#     set.seed(193)
#     zz["A"] = sample(paste0("A", c(1, 1, 1, 1, 1, 2, 2, 2, 3, 4)), nrow(zz), replace = True)
#     zz["B"] = sample(paste0("B", c(1, 1, 1, 1, 1, 2, 2, 2, 3, 4)), nrow(zz), replace = True)
#     rcd = data.frame(char = "char2", A = c("A1", "A2"), B = "B1")
#     removeCodes = list(NULL, rcd, as.list(rcd))
#     k = integer(0)
#     for (specialMultiple in c(False, True)) for (i in np.arange(1, 3+1)) {
#       b = GaussSuppressionFromData(zz,
#                                     dimVar = c("region", "fylke", "kostragr", "hovedint"),
#                                     numVar = "value", charVar = c("char","A","B"),
#                                     maxN = 2, printInc = printInc,
#                                     candidates = CandidatesNum,
#                                     primary = NcontributorsRule,
#                                     singleton = SingletonUniqueContributor,
#                                     singletonMethod = "numTTTTT", output = "inputGaussSuppression",
#                                     specialMultiple = specialMultiple,
#                                     removeCodes = removeCodes[[i]])
#       k = c(k, 0, as.vector(table(b["singleton"])[as.character(unique(b$singleton))]))
#     }
#     expect_equal(k, c(0, 1, 1, 1, 1, 1, 2, 19, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1,
#                       2, 20, 1, 1, 1, 0, 1, 29, 0, 2, 6, 3, 9, 9, 1, 0, 2,
#                       5, 3, 9, 10, 1, 0, 2, 5, 1, 1, 2, 17, 2))
#   }
# })
#
#
#
# test_that("Interpret primary output correctly", {
#   x = SSBtoolsData("sprt_emp_withEU")[, c(1, 2, 5, 3, 4)]
#
#   p1 = function(num, ...) round(10 * num[, 1])%%10 == 3
#   p2 = function(num, ...) round(10 * num)%%10 == 3
#   p3 = function(num, ...) as.data.frame(round(10 * num)%%10 == 3)
#   p4 = function(num, ...) list(primary = as.data.frame(round(10 * num)%%10 == 3),
#                                 numExtra = data.frame(numExtra = round(10 * num[, 1])%%10))
#
#   p12 = function(...) {
#     p = p2(...)
#     p[] = as.integer(p)
#     p
#   }
#
#   G = function(primary, formula = ~eu * year + age:geo) {
#     which(GaussSuppressionFromData(data = x, formula = formula, numVar = "ths_per",
#                                    primary = primary, singleton = NULL,
#                                    output = "inputGaussSuppression",
#                                    printInc = printInc)["primary"])
#   }
#
#   # Case when x is square
#   gp1 = G(p1)
#   expect_identical(G(p2), gp1)
#   expect_identical(G(p3), gp1)
#   expect_identical(G(p4), gp1)
#   expect_identical(length(G(p12)), 0)  # since interpret as xExtraPrimary
#
#   # Case when x is not square
#   gp1_ = G(p1, formula = ~age * geo)
#   expect_identical(G(p2, formula = ~age * geo), gp1_)
#   expect_identical(G(p3, formula = ~age * geo), gp1_)
#   expect_identical(G(p4, formula = ~age * geo), gp1_)
#   expect_error(G(p12, formula = ~age * geo)) #  Error 0 index found in primary output (change to logical?)
#
#
#   # Single column xExtraPrimary, Matrix and matrix
#
#   x["freq"] = round(sqrt(x$ths_per) + as.integer(x$year) - 2014 + 0.2 * (-np.arange(7, 10+1)))
#   z = x[x["year"] == "2014", -(np.arange(4, 5+1))]
#
#
#   K = function(primary) {
#     GaussSuppressionFromData(data = z, formula = ~geo + age, freqVar = "freq", coalition=7,
#                              primary = primary,
#                              mc_hierarchies = NULL, upper_bound = Inf,
#                              protectZeros = False, secondaryZeros = True,
#                              output ="outputGaussSuppression_x",
#                              printInc = printInc)["xExtraPrimary"]
#   }
#
#   e1 = K(KDisclosurePrimary)
#   e2 = K(function (...) as.matrix(KDisclosurePrimary(...)))
#
#   expect_equal(max(abs(e2 - e1)), 0)
#   expect_warning({e3 = K(function (...) round(1 + 0.1*as.matrix(KDisclosurePrimary(...))))}) # Warning message: Primary output interpreted as xExtraPrimary (rare case of doubt)
#   expect_true(all(dim(e3) == c(6, 1)))
#
# })
#
#
# test_that("More NumSingleton", {
#
#   sum_suppressed = integer(0)
#   for (seed in c(116162, 643426)) {
#     set.seed(seed)
#     z = SSBtoolsData("magnitude1")
#     set.seed(seed)
#     z["company"] = z$company[sample.int(20)]
#     z["value"] = z$value[sample.int(20)]
#     dataset = SSBtools::SortRows(aggregate(z["value"], z[np.arange(1, 5+1)], sum))
#     for (c3 in c("F", "T", "H")) for (c4 in c("F", "t", "T")) for (c5 in c("F", "t", "T")) {
#       if (!(c4 == "F" & c5 != "F")) {
#         singletonMethod = paste0("numTt", c3, c4, c5)
#         output = SuppressDominantCells(data = dataset, numVar = "value", dimVar = c("sector4", "geo"), contributorVar = "company", n = 1, k = 80, singletonMethod = singletonMethod,
#                                         printInc = False)
#         sum_suppressed = c(sum_suppressed, sum(output["suppressed"]))
#       }
#     }
#
#   }
#
#   expect_equal(sum_suppressed, c(8, 11, 13, 13, 11, 13, 13, 10, 11, 13, 13, 11, 13, 13, 10,
#                                  11, 13, 13, 11, 13, 13, 7, 9, 10, 12, 10, 11, 12, 8, 10, 10,
#                                  12, 11, 11, 12, 8, 10, 10, 12, 11, 11, 12))
#
# })
