// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use tauri::{Manager, Window};

#[tauri::command]
fn toggle_always_on_top(window: Window) -> Result<bool, String> {
    let state = window.is_always_on_top().map_err(|e| e.to_string())?;
    window.set_always_on_top(!state).map_err(|e| e.to_string())?;
    Ok(!state)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            if let Some(window) = app.get_webview_window("main") {
                // Programmatically configure and verify window transparency/always-on-top
                // Set the window decoration and transparency programmatically in addition to tauri.conf.json
                #[cfg(target_os = "windows")]
                {
                    use window_vibrancy::{apply_acrylic, apply_mica};
                    // Try to apply Mica (Windows 11) or Acrylic (Windows 10)
                    if let Err(_) = apply_mica(&window, Some(true)) {
                        let _ = apply_acrylic(&window, Some((20, 20, 20, 150)));
                    }
                }
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![toggle_always_on_top])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
