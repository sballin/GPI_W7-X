import os
import koheron
from GPI_2.GPI_2 import GPI_2

GPI_host = os.getenv('HOST', 'rp2')
GPI_client = koheron.connect(GPI_host, name='GPI_2')
GPI_driver = GPI_2(GPI_client)

# d=GPI_driver.get_GPI_data()
print(GPI_driver.get_buffer_length())
print(GPI_driver.get_fifo_length())
