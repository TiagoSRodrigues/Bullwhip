import os


directory_path = "/mnt/n/tese/bullwhip/simulator/" #__file__.replace("/","\\")            #split("\\",maxsplit=2, ) #

('\\','//')
# print(directory_path)
# for el in os.listdir(directory_path):
#     print(el)
    
files = os.listdir(directory_path )

for f in files:
    if f[-2:]=="py":
        os.system("pyreverse -o {}.png -A -S /mnt/n/tese/bullwhip/simulator/{}".format(f[:-2],f))
