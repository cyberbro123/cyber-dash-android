# Cyber Dash — Android cloud-build project

This project packages the existing Pygame game as an Android app through SDL2 and a local `pygame-ce` python-for-android recipe.

## What is included

- `cyber_dash.py` — Android-adjusted copy of the current game.
- `main.py` — Android app entry point.
- `buildozer.spec` — Android package configuration.
- `p4a-recipes/pygame-ce/` — local Android build recipe for Pygame-CE.
- `.github/workflows/android.yml` — cloud workflow that builds and uploads a debug APK.

The original Windows game file is not changed by this Android project.

## Build without changing Windows

This project is set up for GitHub-hosted Ubuntu runners. You do not need to install Linux, WSL, Android Studio, or the Android SDK on your Windows PC.

1. Sign in to GitHub and create a new repository named `cyber-dash-android`.
2. Extract this ZIP on Windows.
3. Upload the extracted project files and folders to the repository. Include the hidden `.github` folder; in File Explorer, enable **View → Show → Hidden items** if needed.
4. Commit the upload to the `main` branch. The workflow starts automatically. You can also open the repository's **Actions** tab and run **Build Cyber Dash APK** manually.
5. When the workflow finishes successfully, open its run, find **Artifacts**, and download `Cyber-Dash-APK`. Extract that downloaded ZIP to get the `.apk` file.
6. Transfer the APK to your Android phone and open it to install. Android may ask you to allow installation from the app you used to open the file.

## Notes

- This cloud project has not been compiled in this workspace. The build runs on GitHub's hosted Android build environment, so the first run downloads the Android SDK/NDK and compiles Pygame-CE.
- The Pygame-CE Android recipe is based on the Pygame-CE recipe proposed in python-for-android PR #2971. It is supplied locally because that recipe is not part of the standard p4a recipe set referenced by the current docs. Pygame-CE Android support may still need build fixes depending on upstream changes.
- The game uses touch taps for menu selections and jumping. The developer secret field asks Android to show the software keyboard.
- Save data is directed to Android's app-private folder when `ANDROID_PRIVATE` is provided by the runtime; desktop saves continue to use the script folder.
- This is a debug APK for testing, not a Play Store release. Publishing requires a separately signed release build and store setup.

## Build locally (optional)

If you later decide to use a Linux/macOS build machine, install Buildozer's documented prerequisites, then run:

```bash
buildozer -v android debug
```

See the current Buildozer and python-for-android documentation for supported toolchain versions.
