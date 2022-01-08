
import itertools

# leters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z' ]

# alphabets = []
# for i in leters:
#     alphabets.append(i)
#     alphabets.append(i.upper())
# alphabets.sort()



# name_list=[]

# for (a,b,c,d,e,f) in combinations_with_replacement(alphabets, 3):
#     name_list.append(str((a+b+c+d+e+f)))
# print(name_list)
# print(len(name_list))



chars_l =range(ord('a'), ord('z')+1)
l= [chr(a) + chr(b) +chr(c) +chr(d) +chr(e) +chr(f) for a in chars_l for b in chars_l for c in chars_l for d in chars_l for e in chars_l for f in chars_l]

# chars_u =range(ord('A'), ord('Z')+1)
# u= [chr(a) + chr(b) +chr(c) +chr(d) +chr(e) +chr(f)  for a in chars_u for b in chars_u for c in chars_u for d in chars_u for e in chars_u for f in chars_u]

# a=l+u
with open("alphabet.txt","w") as file:
    file.write(str(l))

print(len(l))