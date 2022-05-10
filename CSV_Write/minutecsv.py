import leap4csv as LF
import time
from backports import csv
import io
import copy
f = io.open('minute_val.csv', 'w', newline='', encoding='utf-8')
writer = csv.writer(f)

listener = LF.SampleListener()
controller = LF.Leap.Controller()
controller.add_listener(listener)

end = time.time() + 60
data = []
timestamp = 0
print("start")
while  time.time() < end:
    list = copy.deepcopy(listener.value)
    stp = [str(timestamp)]
    list = stp + list
    list = [unicode(v, 'utf8') for v in list]
    writer.writerow(list)
    timestamp = timestamp + 1
    time.sleep(0.017)
print("end")
f.close()


