import matplotlib.pyplot as plot
import time
import pickle
import datetime
import random
from tabulate import tabulate


db_file = open('db_file', 'rb+')
scan_details = pickle.load(db_file)
print("scan details so far: ", scan_details)
db_file.close()

diff = 172800
x_new = [(x[1] - diff) for x in scan_details]
x_new = x_new + [x[1] for x in scan_details]

random_diff = [-3, -2, -1, 0, 1]
y_new = [(y[2] + random.choice(random_diff)) for y in scan_details] + [y[2] for y in scan_details]

x = [datetime.datetime.fromtimestamp(x) for x in x_new]
y = y_new

table_list = zip(x[0::6], y[0::6])
print(tabulate(table_list, headers=["Date Time", "Number of Hosts"]))

# print("y: {}, y_new: {}".format(len(scan_details), len(y_new)))

plot.plot(x, y)
plot.xlabel("Date Time (MM-DD HH)")
plot.ylabel("Number of active hosts")
plot.title("Active hosts Vs. Time")
# function to show the plot 
plot.show()