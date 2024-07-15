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


class tree(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(tree, self).__init__()
        self.setupUi(self)
        self.intiui()
        self.camera_param = 0
        self.final_report_name = ""
        self.err_flag = 0

    def intiui(self):
        self.standard_group.buttonClicked[int].connect(self.on_check_box_standard_clicked)
        self.group.buttonClicked[int].connect(self.on_check_box_clicked)

        self.folder_upload_button.clicked.connect(self.upload_result_folder)

        self.submit_button.clicked.connect(self.handle_submit)

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        # 文本框非空检查
        if not self.is_quality_device.isChecked() and not self.is_standard_device.isChecked():
            self.get_message_box("请勾选设备为精品或者标准！！！")
            return
        if not self.is_800_camera.isChecked() and not self.is_500_camera.isChecked() and not self.is_200_camera.isChecked() \
                and not self.is_1600_camera.isChecked() and not self.is_1300_camera.isChecked():
            self.get_message_box("请勾选摄像头像素！！！")
            return
        if not self.is_f_test.isChecked() and not self.is_hj_test.isChecked() and not self.is_cwf_test.isChecked() and not self.is_d65_test.isChecked() and not self.is_tl84_test.isChecked():
            self.get_message_box("请勾选测试场景！！！")
            return
        if len(self.camera_product_edit.text()) == 0:
            # 显示错误消息框
            self.get_message_box("摄像头厂家不能为空,请输入！！！")
            return
        if len(self.project_edit.text()) == 0:
            self.get_message_box("项目名称不能为空, 请输入！！！")
            return
        if len(self.folder_path_edit.text()) == 0:
            self.get_message_box("请上传文件夹！！！")
            return

        # 检查文件是否存在
        result_folder_path = self.folder_path_edit.text().strip()
        if not os.path.exists(result_folder_path):
            self.get_message_box("文件夹路径：%s不存在" % self.folder_path_edit.text().strip())
            return
        if self.is_hj_test.isChecked():
            self.HJ_path = os.path.join(result_folder_path, "HJ_summary.csv")
            if not os.path.exists(self.HJ_path):
                self.get_message_box("灰阶数据：%s不存在" % self.HJ_path)
                return
        if self.is_f_test.isChecked():
            self.F_path = os.path.join(result_folder_path, "A_summary.csv")
            if not os.path.exists(self.F_path):
                self.get_message_box("A光数据：%s不存在" % self.F_path)
                return
        if self.is_d65_test.isChecked():
            self.D65_path = os.path.join(result_folder_path, "D65_summary.csv")
            if not os.path.exists(self.D65_path):
                self.get_message_box("D65光数据：%s不存在" % self.D65_path)
                return
        if self.is_tl84_test.isChecked():
            self.TL84_path = os.path.join(result_folder_path, "TL84_summary.csv")
            if not os.path.exists(self.TL84_path):
                self.get_message_box("TL84光数据：%s不存在" % self.TL84_path)
                return
        if self.is_cwf_test.isChecked():
            self.CWF_path = os.path.join(result_folder_path, "CWF_summary.csv")
            if not os.path.exists(self.CWF_path):
                self.get_message_box("CWF光数据：%s不存在" % self.CWF_path)
                return

        # # 检设备名字，检查check box 属性
        self.data["CameraData"]["pixels"] = self.camera_param
        self.data["CameraData"]["project_name"] = self.project_edit.text().strip()
        self.data["CameraData"]["camera_product"] = self.camera_product_edit.text().strip()
        self.data["CameraData"]["is_f_test"] = self.is_f_test.isChecked()
        self.data["CameraData"]["is_d65_test"] = self.is_d65_test.isChecked()
        self.data["CameraData"]["is_tl84_test"] = self.is_tl84_test.isChecked()
        self.data["CameraData"]["is_cwf_test"] = self.is_cwf_test.isChecked()
        self.data["CameraData"]["is_hj_test"] = self.is_hj_test.isChecked()

        # 拷贝csv文件到相应的目录
        if self.is_hj_test.isChecked():
            self.deal_csv_file("HJ", self.HJ_path)

        if self.is_f_test.isChecked():
            self.deal_csv_file("A", self.F_path)

        if self.is_d65_test.isChecked():
            self.deal_csv_file("D65", self.D65_path)

        if self.is_tl84_test.isChecked():
            self.deal_csv_file("TL84", self.TL84_path)

        if self.is_cwf_test.isChecked():
            self.deal_csv_file("CWF", self.CWF_path)

        # 检测报告的生成
        now = datetime.now()
        if now.month < 10:
            month = "0%d" % now.month
        else:
            month = now.month
        if now.day < 10:
            day = "0%d" % now.day
        else:
            day = now.day
        time_info = "%d%s%s" % (now.year, month, day)
        self.final_report_name = "%s-%d万摄像头(%s)-指标测试报告-%s.xlsx" % (
                                                                        self.data["CameraData"]["project_name"],
                                                                        int(self.data["CameraData"]["pixels"]),
                                                                        self.data["CameraData"]["camera_product"], time_info)

        # 已存在的报告,生成新的
        if self.path_is_existed(os.path.join(self.project_path, self.final_report_name)):
            self.err_flag += 1
            self.final_report_name = "%s-%d万摄像头(%s)-指标测试报告-%s(%d).xlsx" % (
                self.data["CameraData"]["project_name"],
                int(self.data["CameraData"]["pixels"]),
                self.data["CameraData"]["camera_product"],
                time_info, self.err_flag)

        self.data["CameraData"]["report_err_flag"] = self.err_flag
        self.data["CameraData"]["report_file_name"] = self.final_report_name
        # 保存修改后的内容回 YAML 文件
        with open(self.yaml_file_path, 'w') as file:
            yaml.safe_dump(self.data, file)

        # 显示报告正在生成中
        self.tips.setText("正在生成报告,请等待.....")
        # 单独线程运行,避免阻塞主线程和 PyQt5 的事件
        thread = threading.Thread(target=self.run_process)
        thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_report)

        self.check_interval = 1000  # 定时器间隔，单位毫秒
        self.timeout_limit = 60 * 1000  # 超时限制，单位毫秒, 10秒超时
        self.elapsed_time = 0  # 已经过的时间

        self.timer.start(self.check_interval)  # 启动定时器

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

    def check_file_extension_name(self, file_name, light):
        if ".csv" != os.path.splitext(file_name)[1].strip():
            self.get_message_box("%s光数据请上传csv格式的数据!!!" % light)
            return False
        return True

    def deal_csv_file(self, light, file_path):
        csv_name = light + "_summary" + os.path.splitext(file_path)[1]
        test_data_path = os.path.join(self.project_path, "TestData")
        des_folder = os.path.join(test_data_path, light)
        des_file = os.path.join(des_folder, csv_name)
        file_copied_path = os.path.join(des_folder, os.path.basename(file_path))
        self.remove_file(des_file)
        self.remove_file(des_file)
        self.copy_file(file_path, des_folder)
        if not self.path_is_existed(des_file):
            self.copy_file(file_path, des_folder)
        self.rename_file(file_copied_path, des_file)

    def on_check_box_clicked(self, id):
        # 处理复选框点击事件
        if id == 1:
            self.camera_param = 800
        elif id == 2:
            self.camera_param = 500
        elif id == 3:
            self.camera_param = 200
        elif id == 4:
            self.camera_param = 1300
        elif id == 5:
            self.camera_param = 1600

    def on_check_box_standard_clicked(self, id):
        if id == 1:
            self.data["CameraData"]["standard"] = False
        else:
            self.data["CameraData"]["standard"] = True

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

    def upload_result_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, '选择文件夹')

        if folder_path:
            self.folder_path_edit.setText(folder_path)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = tree()
    myshow.show()
    sys.exit(app.exec_())
