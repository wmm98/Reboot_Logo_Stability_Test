import os
import yaml
from PyQt5 import QtCore, QtWidgets, Qt
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QLineEdit, QCompleter, QComboBox, QButtonGroup, QWidget, QSplitter, \
    QSizePolicy


class Ui_MainWindow(object):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly
    project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    print(project_path)

    # yaml_file_path = os.path.join(project_path, "Conf", "test_data.yaml")
    # # 加载 YAML 文件
    # with open(yaml_file_path, 'r', encoding="utf-8") as file:
    #     data = yaml.safe_load(file)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # 创建水平布局
        self.main_layout = QHBoxLayout(self.centralwidget)

        # 创建 QSplitter 控件
        splitter = QSplitter()
        self.main_layout.addWidget(splitter)

        # 左侧所有部件
        left_widget = QWidget()
        self.verticalLayout_left = QtWidgets.QVBoxLayout(left_widget)

        self.boot_way = QtWidgets.QLabel("开关机方式:")
        layout_device_control = QHBoxLayout()
        self.is_power_button_boot = QCheckBox("适配器+按键")
        self.is_power_boot = QCheckBox("适配器")
        self.is_button_boot = QCheckBox("电池按键")
        self.is_900_boot = QCheckBox("900P")
        layout_device_control.addWidget(self.boot_way)
        layout_device_control.addWidget(self.is_power_button_boot)
        layout_device_control.addWidget(self.is_power_boot)
        layout_device_control.addWidget(self.is_button_boot)
        layout_device_control.addWidget(self.is_900_boot)
        layout_device_control.addStretch(1)
        # 将水平布局放入垂直布局

        # 创建按钮组并将复选框添加到按钮组中
        self.group = QButtonGroup()
        self.group.addButton(self.is_power_button_boot, id=1)
        self.group.addButton(self.is_power_boot, id=2)
        self.group.addButton(self.is_button_boot, id=3)
        self.group.addButton(self.is_900_boot, id=4)
        self.verticalLayout_left.addLayout(layout_device_control)

        layout_device_info = QHBoxLayout()
        self.label_device_name = QtWidgets.QLabel("设备名称:")
        self.edit_device_name = QComboBox(self)
        layout_device_info.addWidget(self.label_device_name, 1)
        layout_device_info.addWidget(self.edit_device_name, 2)

        layout_com = QHBoxLayout()
        self.COM1_label = QtWidgets.QLabel("按键COM:")
        self.COM1_name = QComboBox(self)
        # self.COM1_name.setDisabled(True)
        layout_com.addWidget(self.COM1_label, 1)
        layout_com.addWidget(self.COM1_name, 1)

        self.COM2_label = QtWidgets.QLabel("适配器COM:")
        self.COM2_name = QComboBox(self)
        # self.COM1_name.setDisabled(True)
        layout_com.addWidget(self.COM2_label, 1)
        layout_com.addWidget(self.COM2_name, 1)

        self.COM3_label = QtWidgets.QLabel("USB COM:")
        self.COM3_name = QComboBox(self)
        # self.COM1_name.setDisabled(True)
        layout_com.addWidget(self.COM3_label, 1)
        layout_com.addWidget(self.COM3_name, 1)
        layout_com.addStretch(1)
        # 装饰的label
        # layout_device_info.addWidget(QtWidgets.QLabel(), 1)

        self.verticalLayout_left.addLayout(layout_device_info)

        # 上传图片
        self.reboot_logo_info = QtWidgets.QLabel("上传开机logo照片：")
        self.verticalLayout_left.addWidget(self.reboot_logo_info)
        layout_upload_logo = QHBoxLayout()
        self.logo_path_edit = QtWidgets.QLineEdit()
        layout_upload_logo.addWidget(self.logo_path_edit)
        self.logo_upload_button = QtWidgets.QPushButton("点击上传")
        layout_upload_logo.addWidget(self.logo_upload_button)
        self.verticalLayout_left.addLayout(layout_upload_logo)

        # 创建 QLabel 用于显示照片
        # 显示图片
        self.show_keying_button = QtWidgets.QPushButton("显示抠图")
        self.verticalLayout_left.addWidget(self.show_keying_button)

        self.exp_image_label = QtWidgets.QLabel()
        self.exp_image_label.setScaledContents(True)
        self.verticalLayout_left.addWidget(self.exp_image_label)

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("开始压测")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.test_image_label = QtWidgets.QLabel()
        self.test_image_label.setScaledContents(True)
        self.verticalLayout_left.addWidget(self.test_image_label)
        self.verticalLayout_left.setSpacing(10)
        # self.main_layout.setSpacing(2)

        # 添加左边部分
        # 右侧部件
        right_widget = QWidget()
        self.verticalLayout_right = QtWidgets.QVBoxLayout(right_widget)
        self.verticalLayout_right.addWidget(QCheckBox("控件3"))  # 右侧列的控件1
        self.verticalLayout_right.addWidget(QCheckBox("控件4"))  # 右侧列的控件2
        self.verticalLayout_right.addWidget(QCheckBox("控件5"))  # 右侧列的控件2
        self.verticalLayout_right.addWidget(QCheckBox("控件6"))  # 右侧列的控件2
        self.edit = QLineEdit()
        self.verticalLayout_right.addWidget(self.edit)  # 右侧列的控件2
        self.verticalLayout_left.addStretch(1)
        # self.verticalLayout_left.setSpacing(10)  # 设置左侧垂直布局的间距为10像素
        # self.verticalLayout_right.setSpacing(10)  # 设置右侧垂直布局的间距为10像素

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStyleSheet("""
                                    QSplitter::handle {
                                        background: #f0f0f0;  /* 分割条的颜色为最浅的灰色 */
                                        width: 1px;           /* 分割条的最细宽度 */
                                        border: 1px solid #CCCCCC; /* 分割条的边框颜色为灰白色 */
                                    }
                                    QSplitter::handle:horizontal {
                                        height: 100%;  /* 垂直分割条的高度 */
                                    }
                                    QSplitter::handle:vertical {
                                        width: 100%;   /* 水平分割条的宽度 */
                                    }
                                """)

        # 设置伸展因子确保两侧距离一致
        splitter.setStretchFactor(0, 1)  # 左侧部件的伸展因子
        splitter.setStretchFactor(1, 3)  # 右侧部件的伸展因子

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

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
