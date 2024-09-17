from collections import UserList


a = UserList([1, 2, 3, 4])
setattr(a, "rowstart", 1)
a.rowstart
