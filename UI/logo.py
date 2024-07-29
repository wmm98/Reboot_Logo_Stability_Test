import subprocess
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QProcess, Qt
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
        self.is_adapter.clicked.connect(self.adapter_checkbox_change)
        # self.is_battery.clicked.connect(self.battery_checkbox_change)
        self.is_power_button.clicked.connect(self.power_button_checkbox_change)
        self.is_usb.clicked.connect(self.usb_checkbox_change)
        self.logo_upload_button.clicked.connect(self.upload_reboot_logo)
        self.show_keying_button.clicked.connect(self.show_keying_image)
        self.submit_button.clicked.connect(self.handle_submit)
        self.stop_process_button.clicked.connect(self.stop_process)

        # 初始化图片cursor
        self.cursor = QTextCursor(self.document)

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

        # 先删除原来存在的key图片
        if os.path.exists(self.camera_key_path):
            os.remove(self.camera_key_path)
        # 初始化log文件
        with open(self.debug_log_path, "w") as f:
            f.close()

        if len(self.edit_device_name.currentText()) == 0:
            self.get_message_box("没检测到可用的机器，请检查或者重启界面！！！")
            return
        if len(self.test_COM.currentText()) == 0:
            self.get_message_box("没检测到可用的机器，请检查或者重启界面！！！")
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

        if len(self.logo_path_edit.text()) == 0:
            self.get_message_box("请上传开机logo！！！")
            return

        # # 检查文件是否存在
        reboot_logo_path = self.logo_path_edit.text().strip()
        if not os.path.exists(reboot_logo_path):
            self.get_message_box("文件路径：%s不存在" % reboot_logo_path)
            return

        # 检查是否抠图了
        if not os.path.exists(self.logo_key_path):
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
        self.save_config(self.config_file_path)

        # 每次提交先删除失败的照片，避免检错误
        if os.path.exists(self.failed_image_key_path):
            os.remove(self.failed_image_key_path)
        # 启动
        self.start_qt_process(self.run_bat_path)

        self.file_timer = QTimer(self)
        self.file_timer.timeout.connect(self.check_image_modification)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_debug_log)

        self.check_interval = 1000  # 定时器间隔，单位毫秒
        self.timer.start(self.check_interval)  # 启动定时器
        self.file_timer.start(self.check_interval)

        self.stop_process_button.setEnabled(True)
        self.submit_button.setDisabled(True)
        self.submit_button.setText("测试中...")

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
            current_mod_time = self.get_file_modification_time(self.camera_key_path)
            if current_mod_time != self.last_modify_time:
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
        if len(self.logo_path_edit.text()) == 0:
            self.get_message_box("请上传logo！！！")
            return
        self.key_photo()
        pixmap = QPixmap(self.logo_key_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(439, 250)
            self.exp_image_label.setPixmap(scaled_pixmap)

    def key_photo(self):
        original_path = self.logo_path_edit.text().strip()
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
