# import wrapr as wr
# 
# 
# m1 = """                                                                        
#   # Outer Model                                                                 
#   X =~ x1 + x2 +x3                                                              
#   Y =~ y1 + y2 + y3                                                             
#   Z =~ z1 + z2 + z3                                                             
#                                                                                 
#   # Inner model                                                                 
#   Y ~ X + Z + X:Z
# """                                                                            
# 
# md = wr.library("modsem")
# 
# est = md.modsem(m1, data = md.oneInt, method = "qml")
# md.summary(est)
