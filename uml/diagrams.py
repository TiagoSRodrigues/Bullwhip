import os


DIRECTORY_PATH = "/mnt/n/tese/bullwhip/simulator/" #__file__.replace("/","\\")            #split("\\",maxsplit=2, ) #

('\\','//')
# print(DIRECTORY_PATH)
# for el in os.listdir(DIRECTORY_PATH):
#     print(el)

files = os.listdir(DIRECTORY_PATH )

for f in files:
    if f[-2:]=="py":
        os.system("pyreverse -o {}.png -A -S /mnt/n/tese/bullwhip/simulator/{}".format(f[:-2],f))
