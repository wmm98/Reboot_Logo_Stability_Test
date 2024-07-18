import subprocess
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QProcess
from tree_widget import Ui_MainWindow
import os
import shutil
import threading
from datetime import datetime
from PyQt5.QtGui import QPixmap
import serial.tools.list_ports
import msvcrt
from PIL import Image
import rembg


class UIDisplay(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(UIDisplay, self).__init__()
        self.last_position = 0
        # 初始化读取内容读取指针在开始位置
        self.setupUi(self)
        self.qt_process = QProcess(self)
        self.intiui()

    def intiui(self):
        self.select_devices_name()
        self.group.buttonClicked[int].connect(self.on_check_box_clicked)
        self.logo_upload_button.clicked.connect(self.upload_reboot_logo)
        self.show_keying_button.clicked.connect(self.show_keying_image)
        self.stop_process_button.clicked.connect(self.stop_process)
        self.submit_button.clicked.connect(self.handle_submit)

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        self.stop_process_button.setEnabled(True)
        self.submit_button.setDisabled(True)
        self.submit_button.setText("测试中...")
        # 文本框非空检查
        # if len(self.logo_path_edit.text()) == 0:
        #     self.get_message_box("请上传开机logo！！！")
        #     return
        #
        # # 检查文件是否存在
        # reboot_logo_path = self.logo_path_edit.text().strip()
        # if not os.path.exists(reboot_logo_path):
        #     self.get_message_box("文件夹路径：%s不存在" % reboot_logo_path)
        #     return

        # 开始测试、停止测试的文本切换
        # if self.submit_button.text().strip() == "开始测试":
        #     self.submit_button.setText("停止测试")
        # else:
        #     self.submit_button.setText("开始测试")

        # 每次提交先删除失败的照片，避免检错误
        failed_image_path = os.path.join(self.project_path, "Photo", "CameraPhoto", "Key", "Failed.png")
        if os.path.exists(failed_image_path):
            os.remove(failed_image_path)

        # self.start_qt_process(os.path.join(self.project_path, "Run", "bat_run.bat"))

        # 启动 外部 脚本
        self.qt_process.start(os.path.join(self.project_path, "Run", "bat_run.bat"))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_debug_log)

        self.check_interval = 1000  # 定时器间隔，单位毫秒
        self.timer.start(self.check_interval)  # 启动定时器

    def stop_process(self):
        self.log_edit.clear()
        self.qt_process.kill()
        import time
        time.sleep(3)
        self.stop_process_button.setDisabled(True)
        self.submit_button.setEnabled(True)
        self.submit_button.setText("开始测试")

    def start_qt_process(self, file):
        self.qt_process = QProcess(self)
        # 启动 外部 脚本
        self.qt_process.start(file)

    def closeEvent(self, event):
        # 在窗口关闭时停止定时器,关闭任务运行
        # 停止 QProcess 进程
        self.qt_process.kill()
        event.accept()

    def copy_file(self, origin, des):
        shutil.copy(origin, des)

    def rename_file(self, origin, des):
        shutil.move(origin, des)

    def remove_file(self, path):
        if os.path.isfile(path):
            os.remove(path)

    def path_is_existed(self, path):
        if os.path.exists(path):
            return True
        else:
            return False

    def upload_reboot_logo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 'Images (*.png *.jpg *.jpeg)')
        if file_name:
            self.logo_path_edit.setText(file_name)

    def on_check_box_clicked(self, id):
        # 处理复选框点击事件
        if id == 1:
            self.COM1_name.setEnabled(True)
            self.COM2_name.setEnabled(True)
            self.COM3_name.setDisabled(True)
            self.COM3_name.clear()
        elif id == 2:
            self.COM2_name.setEnabled(True)
            self.COM1_name.setDisabled(True)
            self.COM3_name.setDisabled(True)
            self.COM1_name.clear()
            self.COM3_name.clear()
        elif id == 3:
            self.COM1_name.setEnabled(True)
            self.COM2_name.setDisabled(True)
            self.COM3_name.setDisabled(True)
            self.COM2_name.clear()
            self.COM3_name.clear()
        elif id == 4:
            self.COM3_name.setEnabled(True)
            self.COM1_name.setEnabled(True)
            self.COM2_name.setDisabled(True)
            self.COM2_name.clear()
        # 显示COMs
        self.list_COM()

    def list_COM(self):
        ports = self.get_current_COM()
        for port in ports:
            if self.COM1_name.isEnabled():
                self.COM1_name.addItem(port)
            if self.COM2_name.isEnabled():
                self.COM2_name.addItem(port)
            if self.COM3_name.isEnabled():
                self.COM3_name.addItem(port)

    def get_current_COM(self):
        serial_list = []
        ports = list(serial.tools.list_ports.comports())
        if len(ports) != 0:
            for port in ports:
                if 'SERIAL' in port.description:
                    COM_name = port.device.replace("\n", "").replace(" ", "").replace("\r", "")
                    serial_list.append(COM_name)
            return serial_list
        else:
            return []

    def select_devices_name(self):
        devices_info = self.invoke("adb devices").split("\r\n")[1:-2]
        devices = [device_str.split("\t")[0] for device_str in devices_info if device_str.split("\t")[1] == "device"]
        for device in devices:
            self.edit_device_name.addItem(str(device))

    def invoke(self, cmd, runtime=120):
        try:
            output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE).communicate(
                timeout=runtime)
            o = output.decode("utf-8")
            return o
        except subprocess.TimeoutExpired as e:
            print(str(e))

    def show_keying_image(self):
        self.key_photo()
        pixmap = QPixmap(os.path.join(self.logo_key_path, "Failed.png"))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(439, 311)
            self.exp_image_label.setPixmap(scaled_pixmap)

    def key_photo(self):
        original_path = self.logo_path_edit.text().strip()
        if len(original_path) == 0:
            self.get_message_box("请上传图片再抠图")
            return
        new_path = os.path.join(self.logo_key_path, "Failed.png")
        self.save_key_photo(original_path, new_path)

    def save_key_photo(self, orig_path, new_path):
        img = Image.open(orig_path)
        img_bg_remove = rembg.remove(img)
        img_bg_remove.save(new_path)

    def show_failed_image(self):
        pixmap = QPixmap(os.path.join(self.logo_key_path, "Failed.png"))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(429, 311)
            self.test_image_label.setPixmap(scaled_pixmap)

    def update_debug_log(self):
        try:
            log_file = self.debug_log_path
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as file:
                    msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, os.path.getsize(log_file))  #
                    file.seek(self.last_position)
                    new_content = file.read()
                    self.log_edit.insertPlainText(new_content + "\n")
                    self.last_position = file.tell()
                    msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, os.path.getsize(log_file))  # 解锁
        except Exception as e:
            pass
        #     print(f"读取日志文件时出错: {e}")

    def write_to_log(self, text):
        try:
            log_file = self.debug_log_path
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as file:
                    msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, os.path.getsize(log_file))  #
                    file.seek(self.last_position)
                    new_content = file.read()
                    print(new_content)
                    cursor = self.log_edit.textCursor()

                    cursor.movePosition(cursor.End)
                    print("============")
                    cursor.insertText(text + '\n')
                    print("============")
                    self.log_edit.setTextCursor(cursor)
                    print("============")
                    self.log_edit.ensureCursorVisible()
                    print("============")
                    self.last_position = file.tell()
                    msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, os.path.getsize(log_file))  # 解锁
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = UIDisplay()
    myshow.show()
    sys.exit(app.exec_())
