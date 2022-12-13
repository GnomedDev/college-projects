use std::time::{Duration, Instant};

pub struct Interval {
    period: Duration,
    last_tick: Option<Instant>,
}

impl Interval {
    pub fn new(period: Duration) -> Interval {
        Interval {
            period,
            last_tick: None,
        }
    }

    pub fn reset_last_tick(&mut self) {
        self.last_tick = Some(Instant::now());
    }

    pub fn period(&self) -> Duration {
        self.period
    }

    // Waits period - elapsed time since last tick.
    pub fn tick(&mut self) {
        if let Some(last_tick) = self.last_tick {
            let elapsed = last_tick.elapsed();
            let to_sleep = elapsed.saturating_sub(self.period);

            if !to_sleep.is_zero() {
                std::thread::sleep(to_sleep);
                self.reset_last_tick()
            }
        } else {
            self.reset_last_tick()
        }
    }

    // Returns whether the elapsed time is greater than the period.
    pub fn try_tick(&mut self) -> bool {
        if let Some(last_tick) = self.last_tick {
            let elapsed = last_tick.elapsed();
            let to_sleep = elapsed.saturating_sub(self.period);

            if to_sleep.is_zero() {
                false
            } else {
                self.reset_last_tick();
                true
            }
        } else {
            self.reset_last_tick();
            false
        }
    }
}
