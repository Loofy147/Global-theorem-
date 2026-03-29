[app]
# (section) title of your application
title = TGI Mobile

# (section) package name
package.name = tgi_mobile

# (section) package domain (needed for android/ios packaging)
package.domain = org.tgi.intelligence

# (section) source code where the main.py live
source.dir = .

# (section) list of inclusions using pattern matching
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (section) application version
version = 0.1.0

# (section) application requirements
requirements = python3,kivy,numpy,psutil,hashlib,json,requests

# (section) android specific configurations
android.permissions = INTERNET,ACCESS_NETWORK_STATE,BATTERY_STATS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (section) Orientation (landscape, portrait or all)
orientation = portrait

# (section) fullscreen or not
fullscreen = 1

[buildozer]
# (section) log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (section) display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
