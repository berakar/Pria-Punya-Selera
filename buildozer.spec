[app]
title = BPJS Automation
package.name = bpjsautomation
package.domain = com.bpjs
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt
version = 1.0.0
requirements = python3,kivy==2.1.0,selenium,beautifulsoup4,pandas,openpyxl,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 23
android.ndk = 23b
p4a.branch = master
android.arch = armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1