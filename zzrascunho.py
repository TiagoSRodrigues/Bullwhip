a=[8,5,2]
b=[1,7,6]
c=[3,4,9]

cartas =["c1", "c2","c3" ]
count= 1

for ela in a:
    for elb in b:
        for elc in c:
             for carta in cartas:
                print(ela, elb, elc, carta)
                count+=1
print(count*4)
    