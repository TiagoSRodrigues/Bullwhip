

a=[ [1, 4,  7,  17//1  ],
    [2, 18, 200, 200//18],
    [3, 3,  18, 13//5 ],
    [4, 4,  18, 18//4 ]]



print(min)

def get_max_production(matrix):
    min=a[0][-1]
    id=0

    for el in a:
        if el[-1] < min:
            min=el[-1]
            id=el[0]
    return min , id

print("\nid",id, min, "\n")

for linha in a:
    print(linha)