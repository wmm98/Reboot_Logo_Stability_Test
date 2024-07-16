# -*- coding: utf-8 -*-
import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QRunnable, QThreadPool
from tree_widget import Ui_MainWindow
import yaml
import os
import shutil
import threading
from datetime import datetime
from PyQt5.QtGui import QPixmap
from Common.device_check import Shell
import serial.tools.list_ports

shell = Shell()


class UIDisplay(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(UIDisplay, self).__init__()
        self.setupUi(self)
        self.intiui()
        self.camera_param = 0
        self.final_report_name = ""
        self.err_flag = 0

    def intiui(self):
        self.select_devices_name()
        self.group.buttonClicked[int].connect(self.on_check_box_clicked)
        self.logo_upload_button.clicked.connect(self.upload_reboot_logo)
        self.show_keying_button.clicked.connect(self.show_keying_image)
        self.submit_button.clicked.connect(self.handle_submit)

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        # 文本框非空检查
        if len(self.logo_path_edit.text()) == 0:
            self.get_message_box("请上传开机logo！！！")
            return

        # 检查文件是否存在
        reboot_logo_path = self.logo_path_edit.text().strip()
        if not os.path.exists(reboot_logo_path):
            self.get_message_box("文件夹路径：%s不存在" % reboot_logo_path)
            return

        # 显示报告正在生成中
        # self.tips.setText("正在生成报告,请等待.....")
        # 单独线程运行,避免阻塞主线程和 PyQt5 的事件
        # thread = threading.Thread(target=self.run_process)
        # thread.start()
        #
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.check_report)
        #
        # self.check_interval = 1000  # 定时器间隔，单位毫秒
        # self.timeout_limit = 60 * 1000  # 超时限制，单位毫秒, 10秒超时
        # self.elapsed_time = 0  # 已经过的时间
        #
        # self.timer.start(self.check_interval)  # 启动定时器

    def check_report(self):
        path = os.path.join(self.project_path, self.final_report_name)  # 要检查的路径
        if os.path.exists(path):
            self.tips.setText("报告已经生成:  %s" % self.final_report_name)
            self.timer.stop()  # 如果报告存在，停止定时器
        else:
            self.elapsed_time += self.check_interval
            if self.elapsed_time >= self.timeout_limit:
                self.tips.setText("生成报告失败,请再次生成")
                self.timer.stop()  # 如果超时，停止定时器

    def closeEvent(self, event):
        self.timer.stop()  # 在窗口关闭时停止定时器
        event.accept()

    def run_process(self):
        subprocess.run([os.path.join(self.project_path, "Run", "bat_run.bat")])

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

    def onSerialCheckboxStateChanged(self, state):
        if state == 2:  # 选中状态
            self.COM_name.setEnabled(True)
            self.edit_device_name_COM.setEnabled(True)
            self.edit_device_name.setDisabled(True)
            ports = self.serial.get_current_COM()
            for port in ports:
                self.COM_name.addItem(port)
            if len(ports) == 0:
                self.err_COM_Tips.setText("没有可用的COM口, 请检查！！！")
                self.err_COM_Tips.setVisible(True)
                self.COM_name.setEnabled(True)
            elif len(ports) == 1:
                pass
            else:
                self.err_COM_Tips.setText("当前多个COM可用, 请选择需测试COM口！！！")
                self.err_COM_Tips.setVisible(True)
        else:
            self.edit_device_name_COM.setDisabled(True)
            self.edit_device_name.setEnabled(True)
            self.err_COM_Tips.setVisible(False)
            self.COM_name.setDisabled(True)

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
        devices_info = shell.invoke("adb devices").split("\r\n")[1:-2]
        devices = [device_str.split("\t")[0] for device_str in devices_info if device_str.split("\t")[1] == "device"]
        for device in devices:
            self.edit_device_name.addItem(str(device))

    def show_keying_image(self):
        print(self.logo_path_edit.text())
        pixmap = QPixmap(self.logo_path_edit.text())
        print(pixmap)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(439, 311)
            self.exp_image_label.setPixmap(scaled_pixmap)
        else:
            print("无法加载照片")

        # self.show_failed_image()

    def show_failed_image(self):
        print(self.logo_path_edit.text())
        pixmap = QPixmap(self.logo_path_edit.text())
        print(pixmap)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(429, 311)
            self.test_image_label.setPixmap(scaled_pixmap)
        else:
            print("无法加载照片")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = UIDisplay()
    myshow.show()
    sys.exit(app.exec_())
