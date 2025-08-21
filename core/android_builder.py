import os
import sys
import shutil
import subprocess
import platform
import tarfile
import zipfile
import time
from typing import Optional, Dict

import requests


class AndroidBuilder:
    """
    Ensures Android build toolchain (JDK, Android SDK, Gradle) is available
    and builds an APK from a generated Android Studio project.

    - Works sequentially and saves state to disk (under tools/ directory)
    - Avoids parallel operations to keep memory/CPU low on modest machines
    - Does not modify system installations; installs locally under project dir
    """

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tools_dir = os.path.join(self.base_dir, "tools")
        self.jdk_dir = os.path.join(self.tools_dir, "jdk")
        self.android_dir = os.path.join(self.tools_dir, "android")
        self.gradle_dir = os.path.join(self.tools_dir, "gradle")
        self.logs_dir = os.path.join(self.base_dir, "logs")

        os.makedirs(self.tools_dir, exist_ok=True)
        os.makedirs(self.jdk_dir, exist_ok=True)
        os.makedirs(self.android_dir, exist_ok=True)
        os.makedirs(self.gradle_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        self.log_file = os.path.join(self.logs_dir, "builder.log")

    def ensure_tools(self):
        """Ensure JDK, Android SDK, and Gradle are available locally."""
        self._log("Ensuring build tools are available...")
        self._ensure_jdk()
        self._ensure_android_sdk()
        self._ensure_gradle()

    def gradle_sync(self, project_path: str):
        """Trigger a Gradle sync (dependency resolution)."""
        self._log("Running Gradle sync...")
        self._run_gradle(project_path, ["--no-daemon", "help"])  # lightweight target to force resolution

    def assemble_debug(self, project_path: str) -> str:
        """Build a debug APK and return the APK path."""
        self._log("Assembling debug APK...")
        self._run_gradle(project_path, ["--no-daemon", "assembleDebug"])

        # Find the resulting APK
        apk_dir = os.path.join(project_path, "app", "build", "outputs", "apk", "debug")
        candidates = []
        if os.path.isdir(apk_dir):
            for name in os.listdir(apk_dir):
                if name.endswith(".apk"):
                    candidates.append(os.path.join(apk_dir, name))

        if not candidates:
            raise RuntimeError("APK not found after build. Check logs/builder.log for details.")

        # Return the newest APK
        apk_path = max(candidates, key=lambda p: os.path.getmtime(p))
        self._log(f"APK built: {apk_path}")
        return apk_path

    # Internal helpers

    def _ensure_jdk(self):
        if shutil.which("java"):
            self._log("System JDK detected; using system java.")
            return

        # If local JDK already installed, set JAVA_HOME
        local_java = self._find_local_java()
        if local_java:
            self._log("Local JDK detected; configuring JAVA_HOME.")
            return

        self._log("No JDK detected. Downloading a local JDK (Temurin 17)...")
        urls = self._temurin_urls()
        url = urls.get(self._os_key())
        if not url:
            raise RuntimeError("Automatic JDK install not supported for this OS/arch. Please install JDK 17.")

        archive_path = os.path.join(self.jdk_dir, os.path.basename(url))
        self._download(url, archive_path)
        self._extract_archive(archive_path, self.jdk_dir)

        # Set JAVA_HOME by locating the extracted jdk directory
        self._find_local_java(required=True)

    def _ensure_android_sdk(self):
        sdk_root = self._get_android_sdk_root()
        cmdline_bin = os.path.join(sdk_root, "cmdline-tools", "latest", "bin", "sdkmanager")
        if os.path.isfile(cmdline_bin) or os.path.isfile(cmdline_bin + ".bat"):
            self._log("Android command-line tools present.")
        else:
            self._log("Android command-line tools missing. Downloading...")
            os_key = self._os_key()
            osmap = {
                "windows": "win",
                "linux": "linux",
                "darwin": "mac",
            }
            sdk_zip_url = f"https://dl.google.com/android/repository/commandlinetools-{osmap.get(os_key, 'linux')}-11076708_latest.zip"
            archive_path = os.path.join(self.android_dir, os.path.basename(sdk_zip_url))
            self._download(sdk_zip_url, archive_path)
            # Extract under cmdline-tools/latest
            target = os.path.join(sdk_root, "cmdline-tools", "latest")
            os.makedirs(target, exist_ok=True)
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(os.path.join(sdk_root, "cmdline-tools", "tmp"))
            # Move contents
            src = os.path.join(sdk_root, "cmdline-tools", "tmp", "cmdline-tools")
            self._move_all(src, target)
            shutil.rmtree(os.path.join(sdk_root, "cmdline-tools", "tmp"), ignore_errors=True)

        # Install required packages (platforms, build-tools, platform-tools)
        self._log("Installing Android SDK components (platforms;android-34, build-tools;34.0.0, platform-tools)...")
        packages = [
            "platform-tools",
            "platforms;android-34",
            "build-tools;34.0.0",
        ]
        self._run_sdkmanager(packages)
        self._accept_licenses()

    def _ensure_gradle(self):
        # Prefer system Gradle
        if shutil.which("gradle"):
            self._log("System Gradle detected; will use it if wrapper is unavailable.")
            return

        # Install local gradle
        gradle_bin = os.path.join(self.gradle_dir, "gradle-8.5", "bin", "gradle")
        if os.path.isfile(gradle_bin) or os.path.isfile(gradle_bin + ".bat"):
            self._log("Local Gradle present.")
            return

        self._log("Gradle not found. Downloading Gradle 8.5...")
        url = "https://services.gradle.org/distributions/gradle-8.5-bin.zip"
        archive_path = os.path.join(self.gradle_dir, os.path.basename(url))
        self._download(url, archive_path)
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(self.gradle_dir)

    def _run_gradle(self, project_path: str, args: list):
        env = self._build_env()
        is_windows = self._os_key() == "windows"

        tried = []

        def run_cmd(cmd):
            self._log(f"Executing: {' '.join(cmd)}")
            with open(self.log_file, "a", encoding="utf-8") as lf:
                return subprocess.run(
                    cmd,
                    cwd=project_path,
                    env=env,
                    stdout=lf,
                    stderr=lf,
                    text=True,
                )

        # Prefer system/local gradle first
        gradle = shutil.which("gradle")
        if not gradle:
            local_gradle = os.path.join(self.gradle_dir, "gradle-8.5", "bin", "gradle")
            if is_windows:
                local_gradle += ".bat"
            if os.path.isfile(local_gradle):
                gradle = local_gradle
        if gradle:
            tried.append("gradle")
            proc = run_cmd([gradle, "-p", project_path] + args)
            if proc.returncode == 0:
                return

        # Fallback to project wrapper
        wrapper = os.path.join(project_path, "gradlew")
        if is_windows:
            wrapper += ".bat"
        if os.path.isfile(wrapper):
            tried.append("gradlew")
            proc = run_cmd([wrapper] + args)
            if proc.returncode == 0:
                return

        raise RuntimeError(f"Gradle command failed using: {', '.join(tried)}. See logs/builder.log")

    def _run_sdkmanager(self, packages: list):
        env = self._build_env()
        sdk_root = self._get_android_sdk_root()
        bin_path = os.path.join(sdk_root, "cmdline-tools", "latest", "bin")
        sdkmanager = os.path.join(bin_path, "sdkmanager")
        if self._os_key() == "windows":
            sdkmanager += ".bat"
        cmd = [sdkmanager, "--sdk_root=" + sdk_root] + packages
        self._log(f"Executing: {' '.join(cmd)}")
        with open(self.log_file, "a", encoding="utf-8") as lf:
            proc = subprocess.run(cmd, env=env, stdout=lf, stderr=lf, text=True, input="y\n" * 50)
        if proc.returncode != 0:
            raise RuntimeError("sdkmanager failed. See logs/builder.log")

    def _accept_licenses(self):
        env = self._build_env()
        sdk_root = self._get_android_sdk_root()
        bin_path = os.path.join(sdk_root, "cmdline-tools", "latest", "bin")
        sdkmanager = os.path.join(bin_path, "sdkmanager")
        if self._os_key() == "windows":
            sdkmanager += ".bat"
        cmd = [sdkmanager, "--licenses", "--sdk_root=" + sdk_root]
        self._log("Accepting Android SDK licenses...")
        with open(self.log_file, "a", encoding="utf-8") as lf:
            proc = subprocess.run(cmd, env=env, stdout=lf, stderr=lf, text=True, input="y\n" * 50)
        if proc.returncode != 0:
            raise RuntimeError("Accepting licenses failed. See logs/builder.log")

    def _build_env(self) -> Dict[str, str]:
        env = os.environ.copy()

        # JAVA_HOME
        java_home = env.get("JAVA_HOME")
        if not java_home:
            local_jdk = self._detect_local_jdk_root()
            if local_jdk:
                env["JAVA_HOME"] = local_jdk
                env["PATH"] = os.path.join(local_jdk, "bin") + os.pathsep + env.get("PATH", "")

        # ANDROID_SDK_ROOT
        sdk_root = self._get_android_sdk_root()
        env["ANDROID_SDK_ROOT"] = sdk_root
        env["ANDROID_HOME"] = sdk_root
        # Add SDK tools + platform-tools to PATH
        sdk_bins = [
            os.path.join(sdk_root, "cmdline-tools", "latest", "bin"),
            os.path.join(sdk_root, "platform-tools"),
            os.path.join(sdk_root, "tools", "bin"),
        ]
        for p in sdk_bins:
            env["PATH"] = p + os.pathsep + env.get("PATH", "")

        # GRADLE
        local_gradle = os.path.join(self.gradle_dir, "gradle-8.5", "bin")
        if os.path.isdir(local_gradle):
            env["PATH"] = local_gradle + os.pathsep + env.get("PATH", "")

        return env

    def _get_android_sdk_root(self) -> str:
        # Prefer existing env, else use local tools path
        sdk_root = os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME")
        if sdk_root:
            return sdk_root
        local = os.path.join(self.android_dir, "sdk")
        os.makedirs(local, exist_ok=True)
        return local

    def _find_local_java(self, required: bool = False) -> Optional[str]:
        # Detect extracted JDK root and set JAVA_HOME if found
        jdk_root = self._detect_local_jdk_root()
        if jdk_root:
            os.environ["JAVA_HOME"] = jdk_root
            os.environ["PATH"] = os.path.join(jdk_root, "bin") + os.pathsep + os.environ.get("PATH", "")
            return os.path.join(jdk_root, "bin", "java")
        if required:
            raise RuntimeError("Failed to locate local JDK after extraction.")
        return None

    def _detect_local_jdk_root(self) -> Optional[str]:
        if not os.path.isdir(self.jdk_dir):
            return None
        for name in os.listdir(self.jdk_dir):
            p = os.path.join(self.jdk_dir, name)
            if os.path.isdir(p) and (name.startswith("jdk") or name.startswith("jre") or "temurin" in name.lower()):
                # Ensure it has a bin/java
                java_bin = os.path.join(p, "bin", "java.exe" if self._os_key() == "windows" else "java")
                if os.path.isfile(java_bin):
                    return p
        return None

    def _temurin_urls(self) -> Dict[str, str]:
        # Latest URLs may change; these use the "latest" alias from Adoptium where possible
        # Fall back to commonly used filenames if needed.
        return {
            "windows": "https://github.com/adoptium/temurin17-binaries/releases/latest/download/OpenJDK17U-jdk_x64_windows_hotspot.zip",
            "linux": "https://github.com/adoptium/temurin17-binaries/releases/latest/download/OpenJDK17U-jdk_x64_linux_hotspot.tar.gz",
            "darwin": "https://github.com/adoptium/temurin17-binaries/releases/latest/download/OpenJDK17U-jdk_x64_mac_hotspot.tar.gz",
        }

    def _os_key(self) -> str:
        sysname = platform.system().lower()
        if "windows" in sysname:
            return "windows"
        if "darwin" in sysname or "mac" in sysname:
            return "darwin"
        return "linux"

    def _download(self, url: str, dest: str):
        if os.path.isfile(dest):
            self._log(f"Already downloaded: {dest}")
            return
        self._log(f"Downloading {url} -> {dest}")
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0) or 0)
            downloaded = 0
            chunk = 1024 * 1024
            with open(dest, 'wb') as f:
                for part in r.iter_content(chunk_size=chunk):
                    if part:
                        f.write(part)
                        downloaded += len(part)
                        if total:
                            pct = int(downloaded * 100 / total)
                            self._log(f"Downloading... {pct}%")

    def _extract_archive(self, archive_path: str, target_dir: str):
        self._log(f"Extracting {archive_path} -> {target_dir}")
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(target_dir)
        elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
            with tarfile.open(archive_path, 'r:gz') as tf:
                tf.extractall(target_dir)
        else:
            raise RuntimeError(f"Unsupported archive format: {archive_path}")

    def _move_all(self, src_dir: str, dst_dir: str):
        for name in os.listdir(src_dir):
            src = os.path.join(src_dir, name)
            dst = os.path.join(dst_dir, name)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            shutil.move(src, dst)

    def _log(self, msg: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} {msg}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass
