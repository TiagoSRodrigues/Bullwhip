def triangular(min, max, days):
    values = []
    slope  = 1
    x = min
    for i in range(days):
        if x == max:
            slope = -1
        if x == min:
            slope = 1
        
        values.append(x)
        if slope == 1:
            x += 1
        else:
            x-=1
    return values
            
            
print( triangular( min=-3, max= 10, days=50))


def triangular_2(min, max, days):
    values = []
    slope  = 1
    x = min
    while len(values) < days:
        values.append(x)
        x = x + 1 * slope
     
        if x == max:
            slope = -1
        elif x == min:
            slope = 1
            
    return values

print( triangular_2( min=-3, max= 10, days=50))


# dados do problema
min = -3 # exemplo
max = 10 # exemplo
days = 50 # exemplo

#proposta de resolução
daily_stock = list()   # ou list()  ou []
increasing = True

daily_stock.append( min  )                              # NOME[0] = x usa-se em dicionário
daily_stock.append( min+1  )                              # NOME[0] = x usa-se em dicionário

for i in range(1,days):
    if increasing == True:
        if daily_stock[i] == max:                       # igual -> == 
            increasing = False
        daily_stock.append(daily_stock[i-1] + 1)
    else:
        daily_stock.append(daily_stock[i-1] - 1)          # igual -> == 
        if daily_stock[i] == min:
            increasing = True
            

print(daily_stock)