import os
x= os.system('cmd /k "docker ps -f "name=bullwhip""  &')
print(len(x))