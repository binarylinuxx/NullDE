pub struct Preset {
    pub name: &'static str,
    pub temp: u32,
    pub gamma: u32,
}

pub const PRESETS: &[Preset] = &[
    Preset { name: "Default", temp: 6500, gamma: 100 },
    Preset { name: "Overcast", temp: 5500, gamma: 100 },
    Preset { name: "Warm Light", temp: 4500, gamma: 100 },
    Preset { name: "Sunset", temp: 3500, gamma: 110 },
    Preset { name: "Candlelight", temp: 2000, gamma: 120 },
    Preset { name: "Night Light", temp: 3000, gamma: 90 },
    Preset { name: "Cool White", temp: 8000, gamma: 100 },
];

pub fn apply_preset(_preset: &Preset) {
    // TODO: Call hyprsunset with preset values
}
pub fn apply_manual(temp: u32, gamma: u32) {
    // TODO: Call hyprsunset with manual values
} 