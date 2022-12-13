use rand::Rng;

use crate::Tile;

pub struct Randomizer {
    state: rand::rngs::ThreadRng,
}

impl Randomizer {
    pub fn new() -> Randomizer {
        Randomizer {
            state: rand::thread_rng(),
        }
    }

    pub fn next(&mut self) -> Tile {
        match self.state.gen_range(0..7) {
            0 => Tile::I,
            1 => Tile::O,
            2 => Tile::T,
            3 => Tile::S,
            4 => Tile::Z,
            5 => Tile::L,
            6 => Tile::J,
            _ => unreachable!(),
        }
    }
}
