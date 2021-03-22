use std::fmt;



#[derive(Debug, Copy, Clone)]
pub struct GridSize {
  pub height: usize,
  pub width: usize
}

impl GridSize {
  pub fn len(&self) -> usize {
    self.height * self.width
  }
}

pub struct VFDController {
  pub dimensions: GridSize,
  pub driver: GPIODriver,
  pub address: usize,
}

impl VFDController {
  pub fn create_default(&self) -> VFDController {
    let dimensions = GridSize {
      width: 256,
      height: 128
    };

    let gpio_conf = GPIOConf {
      d0: 0,
      d1: 1,
      d2: 2,
      d3: 3,
      d4: 4,
      d5: 5,
      d6: 6,
      d7: 7,
      wr: 8,
      rdy: 9
    };

    let driver = GPIODriver {
      gpio_conf
    };
    driver.init();

    VFDController {
      dimensions,
      driver,
      address: 0,
    }
  }

  pub 
}
