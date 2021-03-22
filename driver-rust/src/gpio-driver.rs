extern crate sysfs_gpio;

use sysfs_gpio::{Direction, Pin};

pub struct GPIOConf {
  pub d0: u8,
  pub d1: u8,
  pub d2: u8,
  pub d3: u8,
  pub d4: u8,
  pub d5: u8,
  pub d6: u8,
  pub d7: u8,
  pub wr: u8,
  pub rdy: u8
}

pub struct GPIODriver {
  pub config: GPIOConf
}

impl GPIODriver {
  pub initialize(&self) {
    // create each pin
    self.
  }

  pub put_byte(byte: u8) {

  }
}
