use std::time::Duration;

pub const FRAME_SLEEP: Duration = Duration::new(0, NANOS_IN_SEC / FPS);
const NANOS_IN_SEC: u32 = 1_000_000_000;
const FPS: u32 = 60;

pub const TILE_SIZE: i32 = 8;
pub const SCALE_FACTOR: u8 = 4;
pub const BOARD_OFFSET: (i32, i32) = (96 * SCALE_FACTOR as i32, 41 * SCALE_FACTOR as i32);
