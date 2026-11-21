[CONFIG]
page_tuples 100
read_cost 1
write_cost 1

[RELATIONS]
# name  card      pages
A       200000    2000
B       150000    1500
C       100000    1000
D        80000     800
E        50000     500
F        50000     500
G        30000     300
H        30000     300
I        20000     200
J        20000     200
K        10000     100
L        10000     100
M         8000      80
N         5000      50
O         5000      50
P         2000      20
Q         2000      20
R         1000      10

[PREDICATES]
A B 0.000001
B C 0.0002
C D 0.00005
D E 0.00001
E F 0.00001
F G 0.0002
G H 0.00002
H I 0.00005
I J 0.00005
J K 0.00001
K L 0.0001
L M 0.0002
M N 0.00005
N O 0.0005
O P 0.00002
P Q 0.002
Q R 0.005