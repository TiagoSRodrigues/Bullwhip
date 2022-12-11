import os


DIRECTORY_PATH = __file__.split("Bullwhip")[0]+"Bullwhip"
#.replace('\\','//')

# ('\\','//')
# print(DIRECTORY_PATH)
# for el in os.listdir(DIRECTORY_PATH):
#     print(el)

files = os.listdir(DIRECTORY_PATH )
print(DIRECTORY_PATH)
for f in files:
    if f[-2:]=="py":
        os.system("pyreverse -o {}_classes_simples.png -A -S N:\\TESE\\Bullwhip\\{}".format(f[:-2],f))
