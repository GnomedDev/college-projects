#[derive(Debug)]
pub enum Error {
    GenericSDL2(String),
    NegativeInt(sdl2::IntegerOrSdlError),
    WindowBuild(sdl2::video::WindowBuildError),
}

impl From<String> for Error {
    fn from(msg: String) -> Self {
        Error::GenericSDL2(msg)
    }
}

impl From<sdl2::IntegerOrSdlError> for Error {
    fn from(value: sdl2::IntegerOrSdlError) -> Self {
        Error::NegativeInt(value)
    }
}

impl From<sdl2::video::WindowBuildError> for Error {
    fn from(value: sdl2::video::WindowBuildError) -> Self {
        Error::WindowBuild(value)
    }
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Error::GenericSDL2(msg) => write!(f, "SDL2 error: {msg}"),
            Error::WindowBuild(err) => write!(f, "Error building window: {err}"),
            Error::NegativeInt(_) => write!(f, "Negative integer passed to SDL2"),
        }
    }
}
