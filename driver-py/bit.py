import time

def to_binary(byte):
  for i in range(8):
    print(((1 << i) & byte) >> i)

to_binary(170) # 153

try:
  while True:
    print('whatever')
    time.sleep(1)
finally:
  print('done!')
