from xmlrpc.client import ServerProxy

proxy = ServerProxy('http://localhost:50000', verbose=True)
# print(proxy.multiply(3, 24))
print(proxy.test())
