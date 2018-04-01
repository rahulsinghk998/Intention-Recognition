#---------------------------------------------------------------------------------------------------------------------------#
# Input Data Format: 1) --    2)      3)       4)        5)         6)    
#
#Make folder with date automatically
#using a fixed sampling rate
#
#Segmentation fault (core dumped)
#
#---------------------------------------------------------------------------------------------------------------------------#

import time
import serial
import argparse
import datetime
import numpy as np
from pylab import *
from collections import deque
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt


v1 = deque([0]*500)
v2 = deque([0]*500)
v3 = deque([0]*500)	
v4 = deque([0]*2000)
v5 = deque([0]*500)
v6 = deque([0]*500)

plt.figure(1)
plt.subplot(311)
plt.ylim([-1000,1000])
plt.ion()
line1, = plt.plot(v1)
plt.show(block=False)

plt.subplot(312)
plt.ion()
plt.ylim([-1000,1000])
line2,  = plt.plot(v2)
plt.show(block=False)

plt.subplot(313)
plt.ion()
plt.ylim([-1000,1000])
line3,  = plt.plot(v3)
plt.show(block=False)

plt.figure(2)
plt.subplot(311)
plt.ylim([-1000000,1000000])
plt.ion()
line4, = plt.plot(v4)
plt.show(block=False)

plt.subplot(312)
plt.ion()
plt.ylim([-1000000,1000000])
line5,  = plt.plot(v5)
plt.show(block=False)

plt.subplot(313)
plt.ion()
plt.ylim([-1000000,1000000])
line6,  = plt.plot(v6)
plt.show(block=False)




parser = argparse.ArgumentParser(description='Argument Parsing description')
# Required positional argument
parser.add_argument('port_val', type=int, help='A required integer positional argument')
# Optional positional argument
parser.add_argument('file_name', type=str, nargs='?', help='An optional integer positional argument')
args = parser.parse_args()

now = datetime.datetime.now()
if args.file_name:
	dirsave='./test_data/'+args.file_name+'_ecg_100hz'+' '+now.isoformat()+'.csv'
else:
	dirsave='./test_data/'+'ecg_100hz'+' '+now.isoformat()+'.csv'

port='/dev/ttyACM'+str(args.port_val)
print("Serial Port: ", port)	
print("Save Directory: ", dirsave)
fhandle = open(dirsave, 'ab')
ser1 = serial.Serial(port, 115200)
plt.pause(1)




# start data collection
i=0
j=0
arr = []
x = np.linspace(0, 1, 100)
start=time.time()
ser1.flush()
if __name__ == '__main__':
  while True:
    try:
      data = ser1.readline().rstrip()
      data = data.split()
      if (len(data) == 6):
        v4.appendleft(int(data[0]))
        datatoplot = v4.pop()
        v5.appendleft(int(data[1]))
        datatoplot = v5.pop()
        v6.appendleft(int(data[2]))
        datatoplot = v6.pop()
        v1.appendleft(int(data[3]))
        datatoplot = v1.pop()
        v2.appendleft(int(data[4]))
        datatoplot = v2.pop()
        v3.appendleft(int(data[5]))
        datatoplot = v3.pop()

        arr.append([float(time.time()), int(data[0]), int(data[1]), int(data[2]), int(data[3]), int(data[4]), int(data[5])])
        if(i%250)==0:
          plt.figure(1)
          plt.subplot(311)
          plt.ylim([np.array(v1).min(),np.array(v1).max()])
          plt.ion()
          line1.set_ydata(v1)
          plt.subplot(312)
          plt.ylim([np.array(v2).min(),np.array(v2).max()])
          plt.ion()
          line2.set_ydata(v2)
          plt.subplot(313)  
          plt.ylim([np.array(v3).min(),np.array(v3).max()])
          plt.ion()
          line3.set_ydata(v3)

          plt.figure(2)
          plt.subplot(311)
          plt.ylim([np.array(v4).min(),np.array(v4).max()])
          plt.ion()        
          line4.set_ydata(v4)
          plt.subplot(312)        #plt.title('%f' % int(data[1]))
          plt.ylim([np.array(v5).min(),np.array(v5).max()])
          plt.ion()
          line5.set_ydata(v5)
          plt.subplot(313)        #plt.title('%f' % int(data[1]))
          plt.ylim([np.array(v6).min(),np.array(v6).max()])
          plt.ion()
          line6.set_ydata(v6)

          plt.draw()
          plt.pause(0.0001)

          if i>7500:
          	np.savetxt(fhandle, np.array(arr),delimiter=",")
          	arr.clear()
          	i=0

        i=i+1
        j=j+1
    except KeyboardInterrupt:
      np.savetxt(fhandle, np.array(arr),delimiter=",")
      fhandle.close()
      print(np.array(arr))
      end=time.time()
      d_time=end-start
      print("Frequency is :: ", j/d_time)
      print(i,'exiting\n')
      ser1.flush()
      ser1.close()
      exit(1)
      
      #np.savetxt("data.csv", np.array(arr), delimiter=",")
      #np.savetxt('data.txt', np.array(arr), fmt='%i', )
      #f.write(str(arr))      # str() converts to string
      #f.close()