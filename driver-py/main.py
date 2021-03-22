import math
import time
import random

from PIL import Image

try:
  import RPi.GPIO as GPIO
  print('using real GPIO')
except:
  import gpio_mock as GPIO
  print('using mock GPIO')

def sleep_us(us):
  # pass
  time.sleep(us / 1e6)

def get_upper_lower_byte(number):
  upper = number >> 8
  lower = number & 255
  return upper, lower

class VFDDriver:
  def __init__(self, **settings):
    self.width = settings["width"]
    self.height = settings["height"]
    self.gpio_mapping = settings["gpio_mapping"]
    self.address = settings.get("address", 0)

  def debug_inputs(self):
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(self.gpio_mapping["DATA"], GPIO.IN)
    GPIO.setup(self.gpio_mapping["WR"], GPIO.IN)
    GPIO.setup(self.gpio_mapping["RDY"], GPIO.IN)

    for pin in self.gpio_mapping["DATA"]:
      value = GPIO.input(pin)
      print('pin data', pin, value)

    print('pin wr', self.gpio_mapping["WR"], GPIO.input(self.gpio_mapping["WR"]))
    print('pin rdy', self.gpio_mapping["RDY"], GPIO.input(self.gpio_mapping["RDY"]))

    GPIO.cleanup()

  def debug_outputs(self):
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(self.gpio_mapping["DATA"], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(self.gpio_mapping["WR"], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(self.gpio_mapping["RDY"], GPIO.OUT, initial=GPIO.LOW)

    pins = [*reversed(self.gpio_mapping["DATA"]), self.gpio_mapping["WR"], self.gpio_mapping["RDY"]]

    try:
      while True:
        for pin in pins:
          print('lighting up pin', pin)
          GPIO.output(pin, GPIO.HIGH)
          input('press enter to continue')
          print('got here')
          GPIO.output(pin, GPIO.LOW)
    finally:
      GPIO.cleanup()

  def initialize_gpio(self):
    # "board" mode - see https://pinout.xyz
    GPIO.setmode(GPIO.BOARD)

    # DATA pins are outputs, low
    GPIO.setup(self.gpio_mapping["DATA"], GPIO.OUT, initial=GPIO.LOW)

    # WR pin is an output
    GPIO.setup(self.gpio_mapping["WR"], GPIO.OUT, initial=GPIO.LOW)

    # RDY is a signal from the display
    GPIO.setup(self.gpio_mapping["RDY"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  def cleanup(self):
    GPIO.cleanup()

  def set_byte_parallel(self, byte, debug=False):
    if debug:
      print('byte=', byte, 'hex=', hex(byte), 'chr=', chr(byte), 'bin=', bin(byte))
    for i, pin in enumerate(self.gpio_mapping["DATA"]):
      banged = (byte >> i) & 1
      GPIO.output(pin, banged)

  def set_wr(self, value):
    GPIO.output(self.gpio_mapping["WR"], value)

  def write_byte(self, byte):
    """
    Whatever is set on the 8 bits of the parallel port will
    be written to the display as a command/data when the WR
    pin moves from low => high.
    """

    # "initialize" - all data low, WR high
    self.set_byte_parallel(0)
    self.set_wr(0)
    sleep_us(10)

    # send data
    self.set_byte_parallel(byte)
    sleep_us(10)
    self.set_wr(1) # wr high

    sleep_us(10)
    # check ready
    # while not self.is_display_ready():

  def write_command_normal(self, commands):
    for cmd in commands:
      self.write_byte(cmd)

  def write_string(self, string):
    for char in string:
      self.write_byte(ord(char))

  def write_command_dma(self, commands):
    # command should always be an array of bytes
    # STX "Header"
    self.write_byte(0x02)

    # Header 2
    self.write_byte(0x44)

    # Address
    self.write_byte(self.address)

    # Command
    for cmd in commands:
      self.write_byte(cmd)

  def initialize_display(self):
    self.write_command_normal([0x1B, 0x40])
    self.write_command_normal([0x0C])

  def set_brightness_max(self):
    self.write_command_normal([0x1F, 0x58, 0x04])

  def set_brightness(self, brightness):
    # sets brightness from 0-4
    # we'll make this accept a number from 0-99, then divide by 4
    if brightness > 99:
      brightness = 99
    elif brightness < 0:
      brightness = 0

    brt = math.floor(brightness / 25)

    return self.write_command_normal([0x58, brt])

  def set_cursor_position(self, x, y):
    # TODO: just goes to top left for now
    self.write_command_normal([0x1F, 0x24, 0x30, 0, 0x30, 0])

  def set_power(self, state):
    state = int(state)
    return self.write_command_normal([0x1f, 0x28, 0x61, 0x40, state]);

  def image_to_bytes(self, file):
    with Image.open(file) as im:
      if not im.height == self.height or not im.width == self.width:
        im = im.resize((self.width, self.height))
      im = im.convert("1") # convert to 1-bit image
      image_bytes = []
      next_byte = 0
      byte_index = 0
      for x in range(image.width):
        for y in range(image.height):
          next_byte = next_byte >> byte_index & 1
          byte_index += 1
          if byte_index == 8:
            image_bytes.append(next_byte)
            next_byte = 0

      return bitmap

  def write_image_bytes_normal(self, image_bytes, width=None, height=None):
    width = width or self.width
    height = height or self.height

    height_bytes = height // 8

    xH, xL = get_upper_lower_byte(width)
    yH, yL = get_upper_lower_byte(height_bytes)

    self.write_command_normal([0x1F, 0x28, 0x66, 0x11, xL, xH, yL, yH, 0x01, *image_bytes])

  def write_image_file_normal(self, file):
    with Image.open(file) as im:
      # resize if necessary
      if im.height != self.height or im.width != self.width:
        im = im.resize((self.width, self.height))
      
      # convert to 1-bit image
      im = im.convert("1")

      # build bytes array
      image_bytes = []
      next_byte = 0
      byte_index = 0
      for x in range(self.width):
        for y in range(self.height):
          pixel_data = im.getpixel((x, y))
          if pixel_data:
            next_byte |= (1 << (8 - byte_index - 1))
          byte_index += 1
          if byte_index == 8:
            image_bytes.append(next_byte)
            byte_index = 0
            next_byte = 0

      self.write_image_bytes_normal(image_bytes)

  def write_image_dma(self, image_bytes):
    # aL bit image write address lower byte
    # aH bit image write address upper byte
    # sL bit image write size lower byte
    # sH bit image write size upper byte
    # data

    # TODO
    aL = 0
    aH = 0xFFF
    sL = 0
    sH = 0xFFF
    data = image_bytes

    return self.write_command_dma([0x46, aL, aH, sL, sH, *data])

  def is_display_ready(self):
    # ready = 1, busy = 0
    ready = GPIO.input(self.gpio_mapping["RDY"])
    # print('ready pin is', self.gpio_mapping["RDY"], ready)
    return ready == GPIO.HIGH

def get_random_bits():
  out = [math.floor(random.random() * 256) for x in range(256*128)]
  return out

if __name__ == "__main__":
  gpio_mapping = {
    # VFD parallel pins 1-8, D0-D7
    "DATA": [21, 19, 15, 13, 11, 7, 5, 3],

    # VFD parallel pin 10
    "WR": 23,

    # VFD parallel pin 12
    "RDY": 31
  }

  width = 256
  height = 128

  vfd = VFDDriver(width=width, height=height, gpio_mapping=gpio_mapping)
  
  # vfd.debug_outputs()

  ## program

  vfd.initialize_gpio()
  vfd.initialize_display()

  # # big font
  # vfd.write_command_normal([0x1F, 0x28, 0x67, 0x01, 0x02])

  # # write basic ascii characters
  # for x in range(0x20, 0xFF):
  #   vfd.write_byte(x)

  # # write some cool lines, I guess
  # checkerboard = [8] * (width * (height // 8))
  # vfd.write_image_bytes_normal(checkerboard, width, height)

  # write image
  vfd.write_image_file_normal('dadmom.bmp')

  vfd.cleanup()
