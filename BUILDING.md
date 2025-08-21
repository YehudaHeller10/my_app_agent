# Building Android App Generator

## Build and Run from Source

```bash
pip install -r requirements.txt
python main.py
```

## Package as a Single EXE (Windows)

```bash
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed \
  --name AndroidAppGenerator \
  --add-data "templates:templates" \
  --add-data "core:core" \
  --add-data "gui:gui" \
  main.py
```

Output: `dist/AndroidAppGenerator.exe`.

Notes:
- On first run, the app may download models into `models/` and Android tools into `tools/` next to the EXE.
- On Linux/macOS use the same command (omit `.exe`) or run from source.

## End-to-End APK Build

After project generation, the app will:
- Check/install JDK, Android SDK command-line tools, and Gradle locally (under `tools/`)
- Accept SDK licenses and install `platforms;android-34`, `build-tools;34.0.0`, `platform-tools`
- Run Gradle sync and `assembleDebug`

The final APK is located under `app/build/outputs/apk/debug/` in the generated project. The UI shows the APK path.

