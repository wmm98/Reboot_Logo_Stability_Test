import sys
import subprocess
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QThread, Qt, pyqtSignal
from tree_widget import Ui_MainWindow
import os
import shutil
from PyQt5.QtGui import QPixmap
import serial.tools.list_ports
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextImageFormat
import configparser
from Common.config import Config
from Run.run import run_script

# 这是后台脚本要导入的模块
import logging
import cv2
from PIL import Image
import rembg
import binascii
import serial
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights


class ScriptThread(QThread):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        run_script()
        self.finished.emit()


class AllCertCaseValue:
    ROOT_PROTOCON = 0
    ROOT_PROTOCON_STA_CHILD = 1
    ROOT_PROTOCON_STA_TMISCAN_B0 = 2
    ROOT_PROTOCON_STA_TMISCAN_B1 = 3
    ROOT_PROTOCON_STA_TMISCAN_B2 = 4


DictCommandInfo = {

    "A": AllCertCaseValue.ROOT_PROTOCON,
    "适配器开关机": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B0,
    "适配器/电池+电源按键--正常关机（按键开关机-指令代替按键关机）": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B1,
    "适配器/电池+电源按键--异常关机（适配器/电池开路关机-按键开机）": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B2,
}


class UIDisplay(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(UIDisplay, self).__init__()
        self.last_position = 0
        self.last_modify_time = 0
        # 初始化读取内容读取指针在开始位置
        self.setupUi(self)
        self.AllTestCase = None
        self.intiui()
        self.cases_selected_sum = 0

    def intiui(self):
        # 用例数结构
        # 设置列数
        self.treeWidget.setColumnCount(1)
        # 设置树形控件头部的标题
        self.treeWidget.setHeaderLabels(['测试场景'])
        self.treeWidget.setColumnWidth(0, 120)

        # 设置根节点
        self.AllTestCase = QTreeWidgetItem(self.treeWidget)
        self.AllTestCase.setText(0, '测试项')

        for value in DictCommandInfo.keys():
            if DictCommandInfo[value] > AllCertCaseValue.ROOT_PROTOCON_STA_CHILD:
                item_sta_father = QTreeWidgetItem(self.AllTestCase)
                item_sta_father.setText(0, value)
                item_sta_father.setCheckState(0, Qt.Unchecked)
                item_sta_father.setFlags(item_sta_father.flags() | Qt.ItemIsSelectable)

        # 节点全部展开
        self.treeWidget.expandAll()
        # 链槽
        self.select_devices_name()
        self.list_COM()
        self.list_logcat_duration()
        self.is_adapter.clicked.connect(self.adapter_checkbox_change)
        self.is_power_button.clicked.connect(self.power_button_checkbox_change)
        self.is_usb.clicked.connect(self.usb_checkbox_change)
        self.logo_upload_button.clicked.connect(self.upload_reboot_logo)
        self.show_keying_button.clicked.connect(self.show_keying_image)
        self.submit_button.clicked.connect(self.handle_submit)
        self.stop_thread_button.clicked.connect(self.stop_thread)
        # 进程完成
        # self.download_log_button.clicked.connect(self.download_adb_file)
        self.only_boot.clicked.connect(self.only_boot_checkbox_change)

        # 初始化图片cursor
        self.cursor = QTextCursor(self.document)

    def handle_finished(self):
        self.text_edit.insertPlainText("任务已经结束" + "\n")

    # 获取所有节点的状态
    def get_tree_item_status(self, tree_item):
        status = tree_item.checkState(0)
        if status == 2:
            self.cases_selected_sum += 1
        result = {
            "text": tree_item.text(0),
            "status": status,
            "children": []
        }
        # 我添加的
        for i in range(tree_item.childCount()):
            child_item = tree_item.child(i)
            result["children"].append(self.get_tree_item_status(child_item))
        return result

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        try:
            # 先删除原来存在的key图片
            if os.path.exists(Config.camera_key_path):
                os.remove(Config.camera_key_path)
            if os.path.exists(Config.camera2_key_path):
                os.remove(Config.camera2_key_path)
            # 初始化log文件
            with open(Config.debug_log_path, "w") as f:
                f.close()

            if len(self.edit_device_name.currentText()) == 0:
                self.get_message_box("没检测到可用的机器，请检查或者重启界面！！！")
                return
            if len(self.test_COM.currentText()) == 0:
                self.get_message_box("没检测到可用的COM口，请检查或者重启界面！！！")
                return

            if not self.is_adapter.isChecked() and not self.is_power_button.isChecked() and not self.is_usb.isChecked():
                self.get_message_box("请选择接线方式！！！")
                return

            # 继电器路数不能相同
            config_list = []
            if self.adapter_config.isEnabled():
                config_list.append(self.adapter_config.currentText())
            if self.power_button_config.isEnabled():
                config_list.append(self.power_button_config.currentText())
            if self.usb_config.isEnabled():
                config_list.append(self.usb_config.currentText())
            if len(config_list) != len(set(config_list)):
                self.get_message_box("接线配置有相同，请检查！！！")
                return
            # 如果只测开关机，不进行图片比对
            if not self.only_boot.isChecked():
                if len(self.logo_path_edit.text()) == 0:
                    self.get_message_box("请上传开机logo！！！")
                    return

                # # 检查文件是否存在
                reboot_logo_path = self.logo_path_edit.text().strip()
                if not os.path.exists(reboot_logo_path):
                    self.get_message_box("文件路径：%s不存在" % reboot_logo_path)
                    return

                # 检查是否抠图了
                if not os.path.exists(Config.logo_key_path):
                    self.get_message_box("请抠图检查图片是否完整！！！")
                    return

            # 检查用例是否为空
            self.tree_status = []
            for i in range(self.treeWidget.topLevelItemCount()):
                item = self.treeWidget.topLevelItem(i)
                # 2 表示已勾选，0 表示未勾选，1 表示半选中
                self.tree_status.append(self.get_tree_item_status(item))

            # 保存要跑的用例
            self.cases = []
            for slave in self.tree_status[0]["children"]:
                if slave["status"] == 2:
                    if "适配器开关机" in slave["text"]:
                        self.cases.append("1")
                    elif "正常关机" in slave["text"]:
                        self.cases.append("2")
                    else:
                        self.cases.append("3")
            if len(self.cases) == 0:
                self.get_message_box("请勾选用例！！！")
                return

            # 检查完保存配置
            self.save_config(Config.config_file_path)

            # 每次提交先删除失败的照片，避免检错误
            if os.path.exists(Config.failed_image_key_path):
                os.remove(Config.failed_image_key_path)

            # 启动
            self.script_thread = ScriptThread()
            self.script_thread.finished.connect(self.handle_finished)
            self.script_thread.start()

            self.file_timer = QTimer(self)
            self.file_timer.timeout.connect(self.check_image_modification)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_debug_log)

            self.check_interval = 1000  # 定时器间隔，单位毫秒
            self.timer.start(self.check_interval)  # 启动定时器
            self.file_timer.start(self.check_interval)

            self.stop_thread_button.setEnabled(True)
            self.submit_button.setDisabled(True)
            self.submit_button.setText("测试中...")
        except Exception as e:
            print(e)

    def only_boot_checkbox_change(self):
        if self.only_boot.isChecked():
            self.double_screen.setDisabled(True)
            self.logo_upload_button.setDisabled(True)
            self.show_keying_button.setDisabled(True)
        else:
            self.double_screen.setEnabled(True)
            self.logo_upload_button.setEnabled(True)
            self.show_keying_button.setEnabled(True)

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
            # 不显示开机时长
            self.button_boot_time.setDisabled(True)
            self.button_boot_time.clear()
        else:
            self.power_button_config.setEnabled(True)
            for line in self.get_COM_config():
                self.power_button_config.addItem(line)
            # 显示开机时长
            self.button_boot_time.setEnabled(True)
            for duration in [3, 5, 7, 10]:
                self.button_boot_time.addItem(str(duration))

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

        config[section]['cases'] = ",".join(self.cases)
        config[section]['device_name'] = self.edit_device_name.currentText()
        config[section]["COM"] = self.test_COM.currentText()
        config[section]["logcat_duration"] = self.adb_log_duration.currentText()

        # 接线方式
        if self.is_adapter.isChecked():
            config[section]["is_adapter"] = "1"
        else:
            config[section]["is_adapter"] = "0"
        if self.is_power_button.isChecked():
            config[section]["is_power_button"] = "1"
        else:
            config[section]["is_power_button"] = "0"
        if self.is_usb.isChecked():
            config[section]["is_usb"] = "1"
        else:
            config[section]["is_usb"] = "0"

        # 接线配置
        if self.adapter_config.isEnabled():
            if self.adapter_config.currentText() == "1路":
                config[section]["adapter_power_config"] = "relay_1"
            elif self.adapter_config.currentText() == "2路":
                config[section]["adapter_power_config"] = "relay_2"
            elif self.adapter_config.currentText() == "3路":
                config[section]["adapter_power_config"] = "relay_3"
            else:
                config[section]["adapter_power_config"] = "relay_4"

        if self.power_button_config.isEnabled():
            if self.power_button_config.currentText() == "1路":
                config[section]["power_button_config"] = "relay_1"
            elif self.power_button_config.currentText() == "2路":
                config[section]["power_button_config"] = "relay_2"
            elif self.power_button_config.currentText() == "3路":
                config[section]["power_button_config"] = "relay_3"
            else:
                config[section]["power_button_config"] = "relay_4"

        if self.usb_config.isEnabled():
            if self.usb_config.currentText() == "1路":
                config[section]["usb_config"] = "relay_1"
            elif self.usb_config.currentText() == "2路":
                config[section]["usb_config"] = "relay_2"
            elif self.usb_config.currentText() == "3路":
                config[section]["usb_config"] = "relay_3"
            else:
                config[section]["usb_config"] = "relay_4"

        # 其他配置信息
        if self.only_boot.isChecked():
            config[section]["only_boot_config"] = "1"
        else:
            config[section]["only_boot_config"] = "0"

        if self.double_screen.isChecked():
            config[section]["double_screen_config"] = "1"
        else:
            config[section]["double_screen_config"] = "0"

        if self.button_boot_time.isEnabled():
            config[section]["button_boot_time"] = self.button_boot_time.currentText()

        with open(file_name, 'w') as configfile:
            config.write(configfile)

    def get_file_modification_time(self, file_path):
        """获取文件的最后修改时间"""
        file_info = QFileInfo(file_path)
        last_modify = file_info.lastModified()
        return last_modify

    def check_image_modification(self):
        """检查图片文件是否有修改"""
        if os.path.exists(Config.camera_key_path):
            current_mod_time = self.get_file_modification_time(Config.camera_key_path)
            if current_mod_time != self.last_modify_time:
                self.last_modify_time = current_mod_time  # 更新为新的修改时间
                self.add_logo_image()

    def stop_thread(self):
        # 文件位置初始化
        self.force_task_kill()
        self.last_position = 0
        self.stop_thread_button.setDisabled(True)
        self.submit_button.setEnabled(True)
        self.submit_button.setText("开始测试")
        self.timer.stop()
        self.file_timer.stop()

    def force_task_kill(self):
        if hasattr(self, 'thread') and self.script_thread.isRunning():
            self.script_thread.terminate()
            # self.script_thread.quit()
            self.script_thread.wait()
            self.script_thread.deleteLater()
            self.text_edit.insertPlainText("任务已经结束" + "\n")
            
    def closeEvent(self, event):
        self.force_task_kill()
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

    def list_logcat_duration(self):
        duration = [10, 20, 30, 40, 50, 60]
        for dur in duration:
            self.adb_log_duration.addItem(str(dur))
        self.adb_log_duration.setCurrentText("30")

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
        if len(self.logo_path_edit.text()) == 0:
            self.get_message_box("请上传logo！！！")
            return
        self.key_photo()
        pixmap = QPixmap(Config.logo_key_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(439, 230)
            self.exp_image_label.setPixmap(scaled_pixmap)

    def key_photo(self):
        original_path = self.logo_path_edit.text().strip()
        self.save_key_photo(original_path, Config.logo_key_path)

    def save_key_photo(self, orig_path, new_path):
        img = Image.open(orig_path)
        img_bg_remove = rembg.remove(img)
        img_bg_remove.save(new_path)

    def show_failed_image(self):
        pixmap = QPixmap(Config.failed_image_key_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(429, 311)
            self.test_image_label.setPixmap(scaled_pixmap)

    def update_debug_log(self):
        try:
            log_file = Config.debug_log_path
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

        if self.double_screen.isChecked():
            image2_url = QUrl.fromLocalFile(Config.camera2_key_path)
            self.document.addResource(QTextDocument.ImageResource, image2_url, image2_url)
            image_format.setName(image2_url.toString())
            image_format.setWidth(self.image_width)
            image_format.setHeight(self.image_height)
            self.cursor.insertImage(image_format)

        image_url = QUrl.fromLocalFile(Config.camera_key_path)
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
        # self.image_edit.insertPlainText("\n")

    def download_adb_file(self):
        if not self.stop_thread_button.isEnabled():
            # 选择源文件
            source_file = Config.adb_log_path
            if not os.path.exists(source_file):
                self.get_message_box("不存在adb log 文件！！！")
                return

            # 获取源文件的名字
            file_name = os.path.basename(source_file)

            # 选择目标保存位置，默认文件名为源文件名
            target_file, _ = QFileDialog.getSaveFileName(self, 'Save File As', file_name,
                                                         'Text Files (*.txt);;All Files (*)')
            if not target_file:
                return

            self.copy_file(source_file, target_file)
            self.get_message_box("成功下载adb log文件！")
        else:
            self.get_message_box("请等待压测停止再下载adb log！！！")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = UIDisplay()
    myshow.show()
    sys.exit(app.exec_())
