use std::time::{Duration, Instant};
struct Interval {
    duration: Duration,
    last_tick: Option<Instant>,
}

impl Interval {
    fn new(duration: Duration) -> Interval {
        Interval {
            duration,
            last_tick: None,
        }
    }

    fn tick(&mut self) {
        if !self.try_tick() {
            return;
        }

        std::thread::sleep(self.duration)
    }
}

fn interval(duration: Duration) -> Interval {}
