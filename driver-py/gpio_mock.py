# mock library for GPIO
from time import perf_counter_ns

# constants
LOW = 0
HIGH = 1
BOARD = 'BOARD'
IN = 'IN'
OUT = 'OUT'

# local
pins = {}

# debug
def debug(*msgs):
  if False:
    print('[debug]', *msgs)

lastcheck = perf_counter_ns()
def checkin():
  global lastcheck
  now = perf_counter_ns()
  debug("diff=", (now - lastcheck) / 1000, 'us')
  lastcheck = now

def setmode(mode):
  checkin()
  debug('mode set to', mode)

def setup(pin, mode, initial=None):
  checkin()
  if mode == IN:
    pins[pin] = HIGH
  debug('pin', pin, 'set to mode', mode, 'initial=', initial)

def output(pin, value):
  checkin()
  debug('pin', pin, 'set to', value)

def input(pin):
  checkin()
  return pins[pin]

def cleanup():
  checkin()
  debug('cleanup')
