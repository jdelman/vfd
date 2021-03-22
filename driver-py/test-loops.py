import time
start = time.time()
loops = 0
while True:
  loops += 1
  print('loops/sec', loops / (time.time() - start))
