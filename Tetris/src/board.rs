use crate::Tile;

#[derive(Debug)]
pub struct Board([Tile; 10 * 20]);

impl Default for Board {
    fn default() -> Self {
        Self([Tile::None; 10 * 20])
    }
}

impl Board {
    pub fn index(&self, x: i32, y: i32) -> Option<Tile> {
        let index = ((y * 10) + x) as usize;

        if index <= 200 {
            Some(self.0[index])
        } else {
            None
        }
    }

    pub fn set(&mut self, x: i32, y: i32, tile: Tile) {
        self.0[((y * 10) + x) as usize] = tile;
    }
}
