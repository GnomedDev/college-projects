mod assets;
mod constants;
mod error;
mod interval;

use sdl2::{
    event::Event,
    image::{self, InitFlag, LoadTexture},
    keyboard::Keycode,
    rect::Rect,
    render::{Texture, WindowCanvas},
};

use constants::{BOARD_OFFSET, FRAME_SLEEP, SCALE_FACTOR, TILE_SIZE};
use error::Error;

/// A single tile, with the original piece colour.
#[derive(Clone, Copy)]
#[repr(u8)]
enum Tile {
    I = 0,
    O = 1,
    T = 2,
    S = 3,
    Z = 4,
    L = 5,
    J = 6,
    None = 7,
}

fn render(
    canvas: &mut WindowCanvas,
    board_texture: &Texture,
    tile: &Texture,
    board: &[Tile; 10 * 20],
) -> Result<(), String> {
    canvas.clear();
    canvas.copy(board_texture, None, None)?;

    let (x_offset, y_offset) = BOARD_OFFSET;
    for y in 0..20_i32 {
        for x in 0..10_i32 {
            let colour = board[(y * 10 + x) as usize] as u8;
            let src = Rect::new(
                colour as i32 * TILE_SIZE,
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

            canvas.copy(tile, src, dst)?;
        }
    }

    canvas.present();

    Ok(())
}

fn main() -> Result<(), Error> {
    let sdl_context = sdl2::init()?;
    let _image_handle = image::init(InitFlag::PNG)?;

    let video_subsystem = sdl_context.video()?;

    let mut canvas = video_subsystem
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

    let mut board = [Tile::None; 10 * 20];
    let mut event_pump = sdl_context.event_pump()?;

    loop {
        for event in event_pump.poll_iter() {
            match event {
                Event::Quit { .. }
                | Event::KeyDown {
                    keycode: Some(Keycode::Escape),
                    ..
                } => {
                    return Ok(());
                }
                _ => {}
            }
        }

        render(&mut canvas, &board_tex, &tile_tex, &board)?;
        std::thread::sleep(FRAME_SLEEP);
    }
}
