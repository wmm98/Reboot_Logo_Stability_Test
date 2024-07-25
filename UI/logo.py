import subprocess
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QProcess
from tree_widget import Ui_MainWindow
import os
import shutil
from PyQt5.QtGui import QPixmap
import serial.tools.list_ports
from PIL import Image
import rembg
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextImageFormat
import configparser


class UIDisplay(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(UIDisplay, self).__init__()
        self.last_position = 0
        self.last_modify_time = 0
        # 初始化读取内容读取指针在开始位置
        self.setupUi(self)
        self.intiui()

    def intiui(self):
        self.select_devices_name()
        self.list_COM()
        self.is_adapter.clicked.connect(self.adapter_checkbox_change)
        self.is_battery.clicked.connect(self.battery_checkbox_change)
        self.is_power_button.clicked.connect(self.power_button_checkbox_change)
        self.is_usb.clicked.connect(self.usb_checkbox_change)
        self.logo_upload_button.clicked.connect(self.upload_reboot_logo)
        self.show_keying_button.clicked.connect(self.show_keying_image)
        self.submit_button.clicked.connect(self.handle_submit)
        self.stop_process_button.clicked.connect(self.stop_process)

        # 初始化图片cursor
        # self.add_logo_image()
        # self.get_file_modification_time()
        self.cursor = QTextCursor(self.document)

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        # 先删除原来存在的key图片
        if os.path.exists(self.camera_key_path):
            os.remove(self.camera_key_path)
        # 初始化log文件
        with open(self.debug_log_path, "w") as f:
            f.close()
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

        # 检查完保存配置
        self.save_config(self.config_file_path)

        # 每次提交先删除失败的照片，避免检错误
        if os.path.exists(self.failed_image_key_path):
            os.remove(self.failed_image_key_path)

        self.start_qt_process(self.run_bat_path)

        self.file_timer = QTimer(self)
        self.file_timer.timeout.connect(self.check_image_modification)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_debug_log)

        self.check_interval = 1000  # 定时器间隔，单位毫秒
        self.timer.start(self.check_interval)  # 启动定时器
        self.file_timer.start(self.check_interval)

    def adapter_checkbox_change(self):
        if self.adapter_config.isEnabled():
            self.adapter_config.setDisabled(True)
            self.adapter_config.clear()
        else:
            self.adapter_config.setEnabled(True)
            for line in self.get_COM_config():
                self.adapter_config.addItem(line)

    def power_button_checkbox_change(self):
        if self.power_button_config.isEnabled():
            self.power_button_config.setDisabled(True)
            self.power_button_config.clear()
        else:
            self.power_button_config.setEnabled(True)
            for line in self.get_COM_config():
                self.power_button_config.addItem(line)

    def battery_checkbox_change(self):
        if self.battery_config.isEnabled():
            self.battery_config.setDisabled(True)
            self.battery_config.clear()
        else:
            self.battery_config.setEnabled(True)
            for line in self.get_COM_config():
                self.battery_config.addItem(line)

    def usb_checkbox_change(self):
        if self.usb_config.isEnabled():
            self.usb_config.setDisabled(True)
            self.usb_config.clear()
        else:
            self.usb_config.setEnabled(True)
            for line in self.get_COM_config():
                self.usb_config.addItem(line)

    def get_COM_config(self):
        return ["1路", "2路", "3路", "4路"]

    def save_config(self, file_name):
        config = configparser.ConfigParser()
        section = "Config"
        config.add_section(section)
        config[section]['test'] = "1"
        with open(file_name, 'w') as configfile:
            config.write(configfile)

    def get_file_modification_time(self, file_path):
        """获取文件的最后修改时间"""
        file_info = QFileInfo(file_path)
        last_modify = file_info.lastModified()
        return last_modify

    def check_image_modification(self):
        """检查图片文件是否有修改"""
        if os.path.exists(self.camera_key_path):
            print(self.camera_key_path)
            current_mod_time = self.get_file_modification_time(self.camera_key_path)
            print(current_mod_time)
            if current_mod_time != self.last_modify_time:
                # self.text_edit.insertPlainText("图片时间已经修改" + current_mod_time.toString(Qt.TextDate))
                # print(f"图片文件已更改: {current_mod_time.toString()}")
                self.last_modify_time = current_mod_time  # 更新为新的修改时间
                self.add_logo_image()

    def stop_process(self):
        # 文件位置初始化
        self.force_task_kill()
        self.last_position = 0
        self.stop_process_button.setDisabled(True)
        self.submit_button.setEnabled(True)
        self.submit_button.setText("开始测试")
        self.timer.stop()
        self.file_timer.stop()

    def start_qt_process(self, file):
        self.qt_process = QProcess()
        # 启动 外部 脚本
        self.qt_process.start(file)

    def force_task_kill(self):
        res = self.qt_process.startDetached("taskkill /PID %s /F /T" % str(self.qt_process.processId()))
        if res:
            self.text_edit.insertPlainText("任务已经结束" + "\n")
        else:
            self.text_edit.insertPlainText("任务还没结束" + "\n")

    def closeEvent(self, event):
        # 在窗口关闭时停止定时器,关闭任务运行
        # 停止 QProcess 进程
        self.invoke("taskkill /PID %s /F /T" % str(self.qt_process.processId()))
        self.timer.stop()
        self.file_timer.stop()
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

    def list_COM(self):
        ports = self.get_current_COM()
        for port in ports:
            self.test_COM.addItem(port)

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
        pixmap = QPixmap(self.logo_key_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(439, 311)
            self.exp_image_label.setPixmap(scaled_pixmap)

    def key_photo(self):
        original_path = self.logo_path_edit.text().strip()
        if len(original_path) == 0:
            self.get_message_box("请上传图片再抠图")
            return
        self.save_key_photo(original_path, self.logo_key_path)

    def save_key_photo(self, orig_path, new_path):
        img = Image.open(orig_path)
        img_bg_remove = rembg.remove(img)
        img_bg_remove.save(new_path)

    def show_failed_image(self):
        pixmap = QPixmap(self.failed_image_key_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(429, 311)
            self.test_image_label.setPixmap(scaled_pixmap)

    def update_debug_log(self):
        try:
            log_file = self.debug_log_path
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as file:
                    file.seek(self.last_position)
                    new_content = file.read()
                    if new_content:
                        self.text_edit.insertPlainText(new_content + "\n")
                        self.last_position = file.tell()
        except Exception as e:
            self.log_edit.insertPlainText(str(e) + "\n")

    def add_logo_image(self):
        # self.cursor = QTextCursor(self.document)
        # 将图片路径转为 QUrl
        # 创建 QTextImageFormat 对象
        self.image_edit.clear()
        image_format = QTextImageFormat()
        image_url = QUrl.fromLocalFile(self.camera_key_path)
        # 添加图片资源到 QTextDocument
        self.document.addResource(QTextDocument.ImageResource, image_url, image_url)
        # 设置图片格式的 ID
        image_format.setName(image_url.toString())
        # 设置图片的大小
        image_format.setWidth(self.image_width)
        image_format.setHeight(self.image_height)

        # 插入图片到 QTextDocument
        self.image_edit.insertPlainText("\n")
        self.cursor.insertImage(image_format)
        self.image_edit.insertPlainText("\n")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = UIDisplay()
    myshow.show()
    sys.exit(app.exec_())
