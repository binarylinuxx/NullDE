use ini::Ini;
use std::path::PathBuf;

pub struct AppConfig {
    pub wallpaper: String,
    pub light_mode: String,
    pub volume: u8,
    pub muted: bool,
}

impl AppConfig {
    pub fn load(path: &PathBuf) -> Option<Self> {
        let ini = Ini::load_from_file(path).ok()?;
        let wallpaper = ini.section(Some("Desk")).and_then(|s| s.get("wallpaper")).unwrap_or("").to_string();
        let light_mode = ini.section(Some("Screen")).and_then(|s| s.get("light_mode")).unwrap_or("Default").to_string();
        let volume = ini.section(Some("Audio")).and_then(|s| s.get("volume")).and_then(|v| v.parse().ok()).unwrap_or(50);
        let muted = ini.section(Some("Audio")).and_then(|s| s.get("muted")).map(|m| m == "true").unwrap_or(false);
        Some(Self { wallpaper, light_mode, volume, muted })
    }
    pub fn save(&self, path: &PathBuf) {
        let mut ini = Ini::new();
        ini.with_section(Some("Desk")).set("wallpaper", &self.wallpaper);
        ini.with_section(Some("Screen")).set("light_mode", &self.light_mode);
        ini.with_section(Some("Audio")).set("volume", &self.volume.to_string()).set("muted", &self.muted.to_string());
        let _ = ini.write_to_file(path);
    }
} 