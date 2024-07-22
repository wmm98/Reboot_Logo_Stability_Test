import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTabWidget Example")
        self.tabWidget = QTabWidget()

        # 创建第一页
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1_layout.addWidget(QPushButton("Button 1 on Tab 1"))
        self.tab1.setLayout(self.tab1_layout)

        # 创建第二页
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2_layout.addWidget(QPushButton("Button 2 on Tab 2"))
        self.tab2.setLayout(self.tab2_layout)

        # 添加标签到 QTabWidget
        self.tabWidget.addTab(self.tab1, "Tab 1")
        self.tabWidget.addTab(self.tab2, "Tab 2")

        # 设置中心部件为 QTabWidget
        self.setCentralWidget(self.tabWidget)


def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()