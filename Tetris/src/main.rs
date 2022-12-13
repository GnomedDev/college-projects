#![deny(rust_2018_idioms)]

mod assets;
mod board;
mod constants;
mod error;
mod interval;
mod randomizer;

use std::time::Duration;

use board::Board;
use randomizer::Randomizer;
use sdl2::{
    event::Event,
    image::{self, InitFlag, LoadTexture},
    keyboard::Keycode,
    rect::Rect,
    render::{Texture, WindowCanvas},
    EventPump,
};

use constants::{BOARD_OFFSET, SCALE_FACTOR, TILE_SIZE};
use error::Error;
use interval::Interval;

struct Textures<'c> {
    tile: Texture<'c>,
    board: Texture<'c>,
}

/// A single tile, with the original piece colour.
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum Tile {
    I = 0,
    O = 1,
    T = 2,
    S = 3,
    Z = 4,
    L = 5,
    J = 6,
    #[default]
    None = 7,
}

enum GameState {
    /// Next tick, spawn a new piece
    Placed,
    /// Next tick, drop current piece down
    Dropping(Tile, (i32, i32)),
}

struct Tetris<'c> {
    current_state: GameState,
    ticker: Interval,
    board: Board,

    rng: Randomizer,
    textures: Textures<'c>,
}

impl<'c> Tetris<'c> {
    fn render_tile(
        &self,
        canvas: &mut WindowCanvas,
        x: i32,
        y: i32,
        tile: Tile,
    ) -> Result<(), String> {
        let (x_offset, y_offset) = BOARD_OFFSET;

        let src = Rect::new(
            tile as u8 as i32 * TILE_SIZE,
            0,
            TILE_SIZE as u32,
            TILE_SIZE as u32,
        );

        let dst = Rect::new(
            x_offset + (x * TILE_SIZE * SCALE_FACTOR as i32),
            y_offset + (y * TILE_SIZE * SCALE_FACTOR as i32),
            TILE_SIZE as u32 * SCALE_FACTOR as u32,
            TILE_SIZE as u32 * SCALE_FACTOR as u32,
        );

        canvas.copy(&self.textures.tile, src, dst)
    }

    fn render(&self, canvas: &mut WindowCanvas) -> Result<(), String> {
        canvas.clear();
        canvas.copy(&self.textures.board, None, None)?;

        for y in 0..20_i32 {
            for x in 0..10_i32 {
                let tile = self.board.index(x, y).unwrap();
                self.render_tile(canvas, x, y, tile)?;
            }
        }

        if let GameState::Dropping(tile, (x, y)) = self.current_state {
            self.render_tile(canvas, x, y, tile)?;
        }

        canvas.present();
        Ok(())
    }

    pub fn game_tick(&mut self) {
        match &mut self.current_state {
            GameState::Dropping(_, (x, y)) => {
                if let Some(next_tile) = self.board.index(*x, *y + 1) {
                    if next_tile != Tile::None {
                        self.current_state = GameState::Placed;
                    } else {
                        *y += 1;
                    }
                } else {
                    self.current_state = GameState::Placed;
                }
            }
            GameState::Placed => {
                let tile = self.rng.next();

                self.current_state = GameState::Dropping(tile, (5, 0));
            }
        }
    }

    pub fn start_render_loop(
        mut self,
        mut canvas: WindowCanvas,
        mut events: EventPump,
    ) -> Result<(), Error> {
        loop {
            for event in events.poll_iter() {
                match event {
                    Event::Quit { .. } => {
                        return Ok(());
                    }
                    Event::KeyDown {
                        keycode, repeat, ..
                    } => match keycode {
                        Some(Keycode::Escape) => return Ok(()),
                        Some(Keycode::Left) => {
                            if let GameState::Dropping(tile, (x, y)) = &mut self.current_state {
                                *x -= 1;
                            }
                        }
                        Some(Keycode::Delete) => {
                            self.board = Board::default();
                            self.current_state = GameState::Placed;
                        }
                        _ => {}
                    },
                    _ => {}
                }
            }

            if self.ticker.try_tick() {
                self.game_tick();
            }

            self.render(&mut canvas)?;
        }
    }
}

fn main() -> Result<(), Error> {
    let sdl_context = sdl2::init()?;
    let _image_handle = image::init(InitFlag::PNG)?;

    let canvas = sdl_context
        .video()?
        .window(
            "Hello World",
            256 * SCALE_FACTOR as u32,
            224 * SCALE_FACTOR as u32,
        )
        .build()?
        .into_canvas()
        .present_vsync()
        .build()?;

    let texture_creator = canvas.texture_creator();
    let tile_tex = texture_creator.load_texture_bytes(assets::TILES)?;
    let board_tex = texture_creator.load_texture_bytes(assets::PLAYFIELD)?;

    let tetris = Tetris {
        board: Board::default(),
        current_state: GameState::Placed,
        ticker: Interval::new(Duration::from_millis(1000)),

        rng: Randomizer::new(),
        textures: Textures {
            tile: tile_tex,
            board: board_tex,
        },
    };

    tetris.start_render_loop(canvas, sdl_context.event_pump()?)
}
