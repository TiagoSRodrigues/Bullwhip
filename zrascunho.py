









cookbook={1001: {'2001': 1}, 2001: {'3001': 1,"5001":3}, 3001: {'4001': 1}, 4001: {'5001': 1}}

def x(product, quantity):
    recepe = cookbook[int(product)]
    row_material = []
    for  ingredient in recepe:
        row_material.append([ingredient, recepe[ingredient] * quantity ])
    print(row_material,len(recepe))
    return True

if x(2001,80):
    print("primeiro")
else:
    print("else")
raise