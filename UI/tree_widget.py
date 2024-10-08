import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter,  QTextEdit
from PyQt5.QtCore import pyqtSlot


class Ui_MainWindow(object):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly
    project_path = path_dir = str(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    config_file_path = os.path.join(project_path, "UI", "config.ini")
    logo_take_path = os.path.join(project_path, "Photo", "Logo", "Logo", "Logo.png")
    logo_key_path = os.path.join(project_path, "Photo", "Logo", "Key", "Key.png")
    camera_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Key.png")
    camera2_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Key2.png")
    debug_log_path = os.path.join(project_path, "Log", "Debug", "debug_log.txt")
    # failed_logcat.txt
    adb_log_path = os.path.join(project_path, "Log", "Logcat", "failed_logcat.txt")
    run_bat_path = os.path.join(project_path, "Run", "bat_run.bat")
    failed_image_key_path = os.path.join(project_path, "Photo", "CameraPhoto", "Key", "Failed.png")
    # 测试前先清除
    if os.path.exists(debug_log_path):
        os.remove(debug_log_path)
    if os.path.exists(adb_log_path):
        os.remove(adb_log_path)
    if os.path.exists(logo_key_path):
        os.remove(logo_key_path)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 850)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # 创建水平布局
        self.main_layout = QHBoxLayout(self.centralwidget)

        # 创建 QSplitter 控件，分割两个子窗口
        splitter = QSplitter()
        self.main_layout.addWidget(splitter)

        # 左侧所有部件
        left_widget = QWidget()
        self.verticalLayout_left = QtWidgets.QVBoxLayout(left_widget)

        layout_device_info = QHBoxLayout()
        self.label_device_name = QtWidgets.QLabel("设备名称:")
        self.edit_device_name = QComboBox()
        # 测试COM
        self.COM_tips = QtWidgets.QLabel("测试COM口:")
        self.test_COM = QComboBox()
        # adb log 时长
        self.adb_log_lable = QtWidgets.QLabel("Logcat时长(min):")
        self.adb_log_duration = QComboBox()

        layout_device_info.addWidget(self.label_device_name)
        layout_device_info.addWidget(self.edit_device_name)
        layout_device_info.addWidget(self.COM_tips)
        layout_device_info.addWidget(self.test_COM)
        layout_device_info.addWidget(self.adb_log_lable)
        layout_device_info.addWidget(self.adb_log_duration)
        layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_device_info)
        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        layout_device_control = QHBoxLayout()
        self.boot_way = QtWidgets.QLabel("接线方式:")
        self.is_adapter = QCheckBox("适配器/电池")
        self.is_power_button = QCheckBox("电源按键")
        self.is_usb = QCheckBox("Type-c/mico-usb")
        self.usb_tips = QtWidgets.QLabel("usb接继电器仅限900P")
        self.usb_tips.setStyleSheet("color: blue;")

        layout_device_control.addWidget(self.boot_way)
        layout_device_control.addWidget(self.is_adapter)
        layout_device_control.addWidget(self.is_power_button)
        layout_device_control.addWidget(self.is_usb)
        layout_device_control.addWidget(self.usb_tips)
        layout_device_control.addStretch(1)
        # 将水平布局放入垂直布局
        self.verticalLayout_left.addLayout(layout_device_control)
        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        layout_COM_config = QHBoxLayout()
        self.config_label = QtWidgets.QLabel("接线配置:")
        self.adapter_label = QtWidgets.QLabel("适配器/电池:")
        self.adapter_config = QComboBox()
        self.adapter_config.setDisabled(True)
        layout_COM_config.addWidget(self.config_label)
        layout_COM_config.addWidget(self.adapter_label)
        layout_COM_config.addWidget(self.adapter_config)

        self.power_button_label = QtWidgets.QLabel("电源按键:")
        self.power_button_config = QComboBox()
        self.power_button_config.setDisabled(True)
        layout_COM_config.addWidget(self.power_button_label)
        layout_COM_config.addWidget(self.power_button_config)

        self.usb_label = QtWidgets.QLabel("USB:")
        self.usb_config = QComboBox()
        self.usb_config.setDisabled(True)
        self.config_tips = QtWidgets.QLabel("接线提示:电源按键接常开端(COM,N0）,其他接常闭端(COM,NC)")
        self.config_tips.setStyleSheet("color: blue;")
        layout_COM_config.addWidget(self.usb_label)
        layout_COM_config.addWidget(self.usb_config)
        layout_COM_config.addStretch(1)
        self.verticalLayout_left.addLayout(layout_COM_config)
        self.verticalLayout_left.addWidget(self.config_tips)
        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

        other_layout_device_info = QHBoxLayout()
        self.other_device_info = QtWidgets.QLabel("其他配置:")
        # 只测开关机，不拍照
        self.only_boot = QCheckBox("只开关机")

        self.double_screen = QCheckBox("双屏")
        # 按键开机时长
        self.button_boot_lable = QtWidgets.QLabel("按键开机时长(sec):")
        self.button_boot_time = QComboBox()
        self.button_boot_time.setDisabled(True)
        other_layout_device_info.addWidget(self.other_device_info)
        other_layout_device_info.addWidget(self.only_boot)
        other_layout_device_info.addWidget(self.double_screen)
        other_layout_device_info.addWidget(self.button_boot_lable)
        other_layout_device_info.addWidget(self.button_boot_time)
        other_layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(other_layout_device_info)
        self.button_boot_tips = QtWidgets.QLabel("提示：“只测开关机”不进行图片拍照对比，只查看adb是否起来")
        self.button_boot_tips.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(self.button_boot_tips)

        # 间隔
        self.verticalLayout_left.addWidget(QtWidgets.QLabel())

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

        self.test_image_label = QtWidgets.QLabel()
        self.test_image_label.setScaledContents(True)
        self.verticalLayout_left.addWidget(self.test_image_label)
        self.verticalLayout_left.setSpacing(10)

        # 用例树
        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)  # 设置多选模式
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.verticalLayout_left.addWidget(self.treeWidget)

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("开始压测")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.stop_process_button = QtWidgets.QPushButton("停止压测")
        self.stop_process_button.setDisabled(True)
        self.verticalLayout_left.addWidget(self.stop_process_button)

        # 下载adb log文件
        # log_layout = QHBoxLayout()
        self.download_log_button = QtWidgets.QPushButton("下载ADB Log")
        self.verticalLayout_left.addWidget(self.download_log_button)
        # adb log tips
        self.download_log_tips = QtWidgets.QLabel()
        self.download_log_tips.setStyleSheet("color: red;")

        # 添加左边部分
        # 右侧部件
        right_widget = QWidget()
        self.verticalLayout_right = QtWidgets.QVBoxLayout(right_widget)
        self.verticalLayout_right.addWidget(QtWidgets.QLabel("实时log打印:"))
        # 展示log
        self.text_edit = ScrollablePlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.verticalLayout_right.addWidget(self.text_edit)
        # 展示图片
        self.verticalLayout_right.addWidget(QtWidgets.QLabel("每次重启后的捉拍:"))
        self.image_edit = ScrollablePlainTextEdit()
        width = self.image_edit.viewport().width()
        height = self.image_edit.viewport().height()
        self.image_width = width / 2
        self.image_height = height / 3
        self.document = self.image_edit.document()
        self.verticalLayout_right.addWidget(self.image_edit)

        self.verticalLayout_left.addStretch(1)
        self.verticalLayout_left.setSpacing(10)  # 设置左侧垂直布局的间距为10像素
        self.verticalLayout_right.setSpacing(10)  # 设置右侧垂直布局的间距为10像素

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


class ScrollablePlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 连接 rangeChanged 信号到 slot_scroll_to_bottom 槽
        self.verticalScrollBar().rangeChanged.connect(self.slot_scroll_to_bottom)

    @pyqtSlot(int, int)
    def slot_scroll_to_bottom(self, min, max):
        # 设置滚动条到底部
        self.verticalScrollBar().setValue(max)
