# Camera_Stability_Test
开关机压测卡logo测试


# 打包指令
nuitka --standalone --onefile --windows-console-mode=disable --include-package=Common --include-package=Run --include-data-dir=./UI=UI  --include-package=PyQt5 --output-dir=dist --enable-plugin=pyqt5 --enable-plugin=upx UI/logo.py


nuitka --standalone --onefile --include-package=Common --include-package=Run --include-data-dir=./UI=UI --include-package=PyQt5 --output-dir=dist --enable-plugin=pyqt5 --enable-plugin=upx UI/logo.py