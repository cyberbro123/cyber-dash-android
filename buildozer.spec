[app]
# App identity
title = Cyber Dash
package.name = cyberdash
package.domain = com.cyberdash.arcade
source.dir = .
source.include_exts = py,json
source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__
version = 2.1.0

# Pygame-CE runs on Android through the SDL2 backend.
requirements = python3,pygame-ce
orientation = landscape
fullscreen = 1

# Android targets
android.api = 35
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.debug_artifact = apk

# Pygame-CE recipe is supplied locally with this project.
p4a.bootstrap = sdl2
p4a.branch = develop
p4a.local_recipes = ./p4a-recipes

[buildozer]
log_level = 2
warn_on_root = 1
