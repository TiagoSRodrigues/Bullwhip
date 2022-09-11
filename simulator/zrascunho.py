a = [[1,2,3],[23,4,5],[6,7,8]]

import csv 

with open('file.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(a)