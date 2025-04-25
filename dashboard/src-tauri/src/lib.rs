#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      // Configure logging
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      // Log startup information
      log::info!("Coda Dashboard starting up");
      log::info!("Version: {}", env!("CARGO_PKG_VERSION"));

      Ok(())
    })
    // Add custom commands here if needed
    // .invoke_handler(tauri::generate_handler![command1, command2])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
