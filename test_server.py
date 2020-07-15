from xmlrpc.client import ServerProxy
import time

proxy = ServerProxy('http://127.0.0.1:50000', verbose=False)
# print(proxy.multiply(3, 24))
while True:
    start = time.time()
    a = proxy.getPressureData()
    print('Requests took %f' % (time.time()-start))
    time.sleep(1)
