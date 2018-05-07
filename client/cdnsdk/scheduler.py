"""
import time
import sched

schedule = sched.scheduler(time.time, time.sleep)

def func(string1,float1):
    print "now is",time.time()," | output=",string1,float1

print time.time()
schedule.enter(2,0,func,("test1",time.time()))
# schedule.enter(2,0,func,("test1",time.time()))
# schedule.enter(3,0,func,("test1",time.time()))
# schedule.enter(4,0,func,("test1",time.time()))
schedule.run()
print time.time()
"""

#!/usr/bin/env python
from threading import Timer
import time
timer_interval=1

def delayrun():
    print 'running'

t=Timer(timer_interval,delayrun)
t.start()
while True:
    time.sleep(3)
    print 'main execute per 3 seconds'