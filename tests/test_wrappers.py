import wrapr as wr
import pandas as pd
import numpy as np
import pytest
 
st = wr.library("SSBtools")
gs = wr.library("GaussSuppression")
bs = wr.library("base")

printInc = False

def test_Wrappers():
    dataset = st.SSBtoolsData("magnitude1")
    dataset["seq2"] = np.tile(np.arange(1, bs.nrow(dataset)-9)^2, 2)

    # Table 3 in vignette  
    a1 = gs.SuppressFewContributors(data=dataset, 
                          numVar = "value", 
                          dimVar= np.array(["sector4", "geo"]), 
                          maxN=1,
                          printInc = printInc)

    a2 = gs.SuppressFewContributors(data=dataset, 
                                numVar = np.array(["seq2", "value"]),  
                                dimVar = np.array(["sector4", "geo"]), 
                                maxN=1,
                                remove0 = "value",
                                candidatesVar = "value",
                                printInc = printInc)
    compare_by_names = bs.function("function(x, y) all(x[names(x)] == y[names(x)])")
    assert compare_by_names(a1, a2)



    a3 = gs.SuppressFewContributors(data=dataset, 
                                numVar = np.array(["seq2", "value"]),  
                                dimVar= np.array(["sector4", "geo"]), 
                                maxN=1,
                                remove0 = "value",
                                candidatesVar = "seq2",
                                printInc = printInc)

    assert not np.all(a1["suppressed"] == a3["suppressed"])

    a4 = gs.SuppressFewContributors(data=dataset, 
                                dimVar = np.array(["sector4", "geo"]), 
                                maxN=1,
                                remove0 = "seq2",
                                candidatesVar = "value",
                                printInc = printInc)


    assert not np.all(a1["nAll"] == a4["nAll"])

    assert np.all(a1[["primary", "suppressed"]], a4[["primary", "suppressed"]])


    # A test of removeCodes in CandidatesNum with multiple charVar
    dataset["char2"] = dataset["company"]
    dataset["char2"][6:15] = "a"
    a5 = gs.SuppressFewContributors(data=dataset, 
                                dimVar = np.array(["sector4", "geo"]), 
                                maxN=1,
                                numVar = "value",
                                contributorVar = np.array(["company", "char2"]),
                                removeCodes = {"company": "B", 
                                               "char2": np.array(["B","a"])},
                                printInc = printInc)

    # FALSE when removeCodesForCandidates = FALSE
    assert not np.all(a5["sector4"] == "Entertainment" & a5["geo"] == "Iceland", "suppressed")



    # Table 3 in vignette  
    b1 = gs.SuppressDominantCells(data=dataset, 
                        numVar = "value", 
                        dimVar= np.array(["sector4", "geo"]), 
                        n = 1, k = 80, allDominance = TRUE,
                        printInc = printInc)

    b2 = gs.SuppressDominantCells(data=dataset, 
                              numVar = np.array(["seq2", "value"]), 
                              dimVar= np.array(["sector4", "geo"]), 
                              n = 1, k = 80, allDominance = TRUE,
                              candidatesVar = "value",
                              dominanceVar = "value",
                              printInc = printInc)

    assert compare_by_names(b1, b2)
       
    b3 = gs.SuppressDominantCells(data=dataset, 
                              numVar = np.array(["seq2", "value"]), 
                              dimVar= np.array(["sector4", "geo"]), 
                              n = 1, k = 80, allDominance = TRUE,
                              candidatesVar = "seq2",
                              dominanceVar = "value",
                              printInc = printInc)

    assert not np.all(b1["suppressed"] == b3["suppressed"])


    dataset["value2"] = dataset["value"]
    dataset["value2"[dataset["sector4"]] == "Governmental"] <- 0
    dataset["value2"[dataset["sector4"]] == "Agriculture"] <- 0
    
    b4 = gs.SuppressDominantCells(data=dataset, 
                              numVar = "value2", 
                              dimVar= np.array(["sector4", "geo"]), 
                              n = 1, k = 70, allDominance = TRUE,
                              singletonZeros = TRUE,
                              printInc = printInc)
    
    assert np.all(b4["sector4"] == "Governmental" & b4["geo"] == "Total", "suppressed")
    # With singletonZeros = FALSE, the result is FALSE 
    # and revealing suppressed 0 cells is easy since Total=0  
