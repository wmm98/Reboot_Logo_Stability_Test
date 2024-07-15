import os
import yaml
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QLineEdit, QCompleter, QComboBox, QButtonGroup


class Ui_MainWindow(object):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly
    project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    print(project_path)

    yaml_file_path = os.path.join(project_path, "Conf", "test_data.yaml")
    # 加载 YAML 文件
    with open(yaml_file_path, 'r', encoding="utf-8") as file:
        data = yaml.safe_load(file)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 300)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.device_info = QtWidgets.QLabel("摄像头信息：")
        self.verticalLayout.addWidget(self.device_info)

        # 将标签添加到水平布局中
        # 添加checkbox
        standard_layout = QHBoxLayout()
        self.test_standard = QtWidgets.QLabel("指标：")
        self.is_standard_device = QCheckBox("标准")
        self.is_quality_device = QCheckBox("精品")
        standard_layout.addWidget(self.test_standard)
        standard_layout.addWidget(self.is_standard_device)
        standard_layout.addWidget(self.is_quality_device)
        standard_layout.addStretch(1)
        self.standard_group = QButtonGroup()
        self.standard_group.addButton(self.is_standard_device, id=1)
        self.standard_group.addButton(self.is_quality_device, id=2)
        # 设置按钮组中只能有一个选中
        self.standard_group.setExclusive(True)
        self.verticalLayout.addLayout(standard_layout)

        layout = QHBoxLayout()
        self.camera_pixels = QtWidgets.QLabel("像素：")
        self.is_800_camera = QCheckBox("800万")
        self.is_500_camera = QCheckBox("500万")
        self.is_200_camera = QCheckBox("200万")
        self.is_1300_camera = QCheckBox("1300万")
        self.is_1600_camera = QCheckBox("1600万")

        layout.addWidget(self.camera_pixels)
        layout.addWidget(self.is_800_camera)
        layout.addWidget(self.is_500_camera)
        layout.addWidget(self.is_200_camera)
        layout.addWidget(self.is_1300_camera)
        layout.addWidget(self.is_1600_camera)
        # 添加一个拉伸因子以将水平布局放在窗口底部
        layout.addStretch(1)
        # 将水平布局放入垂直布局

        # 创建按钮组并将复选框添加到按钮组中
        self.group = QButtonGroup()
        self.group.addButton(self.is_800_camera, id=1)
        self.group.addButton(self.is_500_camera, id=2)
        self.group.addButton(self.is_200_camera, id=3)
        self.group.addButton(self.is_1300_camera, id=4)
        self.group.addButton(self.is_1600_camera, id=5)

        # 设置按钮组中只能有一个选中
        self.group.setExclusive(True)
        self.verticalLayout.addLayout(layout)

        light_layout = QHBoxLayout()
        self.test_section = QtWidgets.QLabel("场景：")
        self.is_hj_test = QCheckBox("HJ(灰阶)")
        self.is_f_test = QCheckBox("A")
        self.is_d65_test = QCheckBox("D65")
        self.is_cwf_test = QCheckBox("CWF")
        self.is_tl84_test = QCheckBox("TL84")

        light_layout.addWidget(self.test_section)
        light_layout.addWidget(self.is_hj_test)
        light_layout.addWidget(self.is_f_test)
        light_layout.addWidget(self.is_d65_test)
        light_layout.addWidget(self.is_cwf_test)
        light_layout.addWidget(self.is_tl84_test)
        # 添加一个拉伸因子以将水平布局放在窗口底部
        light_layout.addStretch(1)
        self.verticalLayout.addLayout(light_layout)
        # csv命名提示
        csv_name_tips = QtWidgets.QLabel("csv命名提示：请以 HJ_summary.csv， A_summary.csv， TL84_summary.csv， D65_summary.csv， CWF_summary.csv 命名")
        csv_name_tips.setStyleSheet("color: blue;")
        self.verticalLayout.addWidget(csv_name_tips)

        layout_product = QHBoxLayout()
        self.camera_product_name = QtWidgets.QLabel("厂家：")
        self.camera_product_edit = QtWidgets.QLineEdit()
        self.project_name = QtWidgets.QLabel("项目名称：")
        self.project_edit = QtWidgets.QLineEdit()
        layout_product.addWidget(self.camera_product_name)
        layout_product.addWidget(self.camera_product_edit)
        layout_product.addWidget(self.project_name)
        layout_product.addWidget(self.project_edit)
        self.verticalLayout.addLayout(layout_product)

        self.result_folder_info = QtWidgets.QLabel("上传Imatest生成的result文件夹：")
        self.verticalLayout.addWidget(self.result_folder_info)
        layout_upload_folder = QHBoxLayout()
        self.folder_path_edit = QtWidgets.QLineEdit()
        layout_upload_folder.addWidget(self.folder_path_edit)
        self.folder_upload_button = QtWidgets.QPushButton("点击上传")
        layout_upload_folder.addWidget(self.folder_upload_button)
        self.verticalLayout.addLayout(layout_upload_folder)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("开始生成报告")
        self.verticalLayout.addWidget(self.submit_button)

        self.tips = QtWidgets.QLabel()
        self.tips.setStyleSheet("color: red;")
        self.tips.setText("未开始生成报告...")
        # self.tips.setVisible(False)
        self.verticalLayout.addWidget(self.tips)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
