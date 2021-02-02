# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'connect_me.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
#导入程序运行必须模块
import sys
import time
#PyQt5中使用的基本控件都在PyQt5.QtWidgets模块中
from PyQt5 import QtWidgets
from PyQt5.QtCore import QBasicTimer, Qt, pyqtSignal
from PyQt5.Qt import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QProgressDialog
#导入designer工具生成的界面代码
from ui import Ui_Form
#业务代码
from extract import extract_file, remove_compressed_file, get_compressed_filesize

class Thread_Extract(QThread):  # 解压线程
    _signal = pyqtSignal(dict)

    def __init__(self, folderPath, fileType, password):
        super().__init__()
        self.folderPath = folderPath
        self.fileType = fileType
        self.password = password

    def run(self):
        result = extract_file(self.folderPath, self.fileType, self.password)
        self._signal.emit(result)   # 发射信号，回调解压结果


class MyMainForm(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit_select_folder.setReadOnly(True)   # 选择文件夹文本框不可编辑只能选择
        self.step = 1   # 进度条步长
        self.toolButton_select_un7z_folder.clicked.connect(self.select_folder)
        self.PushButton_uncompress.clicked.connect(self.extract_show)
        # self.PushButton_uncompress.clicked.connect(self.one_cilck_extract)
        # self.PushButton_delete.clicked.connect(self.ProgressDialog)
        self.PushButton_delete.clicked.connect(self.delete_compressed_package)
        self.pushButton_cancel.clicked.connect(self.close)
    # 选择待解压文件夹
    def select_folder(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", "")  # 通过按钮获取文件夹路径
        print("starting at:",directory)
        '''
        self.lineEdit_select_folder.clear() # 清除上一次选择的路径
        self.lineEdit_select_folder.insert(directory) # 文件夹路径显示在文本框上
        '''
        self.lineEdit_select_folder.setText(directory) # 文件夹路径显示在文本框上
    # 删除压缩包
    def delete_compressed_package(self):
        folderPath = self.lineEdit_select_folder.text()
        if not folderPath or folderPath == "":
            msg = "文件路径无效"
            QMessageBox.warning(self, "解压失败", msg, QMessageBox.Close)
            return
        result = remove_compressed_file(folderPath)
        if result:
            QMessageBox.information(self, "删除结果", "成功", QMessageBox.Close)
        else:
            QMessageBox.warning(self, "删除结果", "失败", QMessageBox.Close)

    # 解压和显示进度条
    def extract_show(self):
        # 获取解压必需的参数
        folderPath = self.lineEdit_select_folder.text()
        if not folderPath or folderPath == "":
            msg = "文件路径无效"
            QMessageBox.warning(self, "解压失败", msg, QMessageBox.Close)
            return
        password = self.lineEdit_input_password.text()
        fileType = self.comboBox.currentText()

        self.timer = QBasicTimer()  # 初始化一个时钟
        self.progressDialog = QProgressDialog(self)  # 初始化进度条
        self.progressDialog.setWindowTitle("请稍等")
        self.progressDialog.setLabelText("正在解压...")
        self.progressDialog.setCancelButtonText("取消")   # 其实取消按钮应该能够停止解压操作
        # self.progressDialog.setWindowModality(Qt.WindowModal)
        self.progressDialog.setMinimumDuration(1000)
        self.progressDialog.setRange(0,100)
        self.progressDialog.setValue(0)

        begin = time.time()
        filesize = get_compressed_filesize(folderPath, fileType)

        self.PushButton_uncompress.setEnabled(False)  # 设置button暂时不可用
        x = filesize//(1024*1024*100)
        y = x**2/100+x*25
        print("x = %d, y = %d" %(x,y))
        self.timer.start(y, self) # 通过文件大小来估算进度条时间
        self.thread_extract = Thread_Extract(folderPath, fileType, password)
        # self.thread_extract._signal.connect(self.set_btn)  # 此线程执行完毕后需要恢复button
        self.thread_extract._signal.connect(self.extract_callback)  # 执行回调函数
        self.thread_extract.start()

        show_size, file_byte = filesize, 0
        while show_size > 1024:
            show_size = show_size/1024
            file_byte += 1
        if file_byte == 0:
            print("filesize = {} Byte".format(show_size))
        elif file_byte == 1:
            print("filesize = %.3f KB" %(show_size))
        elif file_byte == 2:
            print("filesize = %.3f MB" %(show_size))
        elif file_byte == 3:
            print("filesize = %.3f GB" %(show_size))
        else:
            print("filesize = %.3f TB" %(show_size))

        end = time.time()
        time_cost = end-begin
        if time_cost>1:
            print("get filesize cost {}s".format(time_cost))
        elif time_cost*1000>1:
            print("get filesize cost {}us".format(time_cost*1000))
        elif time_cost*1000000>1:
            print("get filesize cost {}ms".format(time_cost*1000000))
        # 主线程弹窗
        # if filesize > 0:
            # self.ProgressDialog((filesize // 100))

    # def set_btn(self):
        # self.PushButton_uncompress.setEnabled(True)

    def extract_callback(self, result):  # 解压结果回调函数
        self.step = -1
        self.progressDialog.setValue(100)
        print("result = ", result)
        if result['code'] == 0:
            # QMessageBox.information(self, "解压结果", "成功", QMessageBox.Yes | QMessageBox.No)
            msg = str(result['success_times']) + "个文件解压成功，" + str(result['failed_times']) + "个文件解压失败，" + str(
                result['unknown_times']) + "个文件无需解压或类型不支持"
            print(msg)
            QMessageBox.information(self, "解压完毕", msg, QMessageBox.Close)
        elif result['code'] == 2:
            msg = "文件类型错误"
            QMessageBox.critical(self, "解压失败", msg, QMessageBox.Close)
        self.PushButton_uncompress.setEnabled(True)
        # self.progressDialog.setValue(0)

    # 一键解压
    def one_cilck_extract(self):
        folderPath = self.lineEdit_select_folder.text()
        if not folderPath or folderPath == "":
            msg = "文件路径无效"
            QMessageBox.warning(self, "解压失败", msg, QMessageBox.Close)
            return
        password = self.lineEdit_input_password.text()
        fileType = self.comboBox.currentText()
        result = extract_file(folderPath, fileType, password)
        print("result = ",result)
        if result['code'] == 0:
            # QMessageBox.information(self, "解压结果", "成功", QMessageBox.Yes | QMessageBox.No)
            msg = str(result['success_times'])+"个文件解压成功，"+str(result['failed_times'])+"个文件解压失败，"+str(result['unknown_times'])+"个文件无需解压或类型不支持"
            print(msg)
            QMessageBox.information(self, "解压完毕", msg, QMessageBox.Close)
        elif result['code'] == 2:
            msg = "文件类型错误"
            QMessageBox.critical(self, "解压失败", msg, QMessageBox.Close)
    # 进度条弹窗
    def ProgressDialog(self, num = 100000):
        print("num = ",num)
        progress = QProgressDialog(self)
        progress.setWindowTitle("请稍等")
        progress.setLabelText("正在操作...")
        progress.setCancelButtonText("取消")
        progress.setMinimumDuration(1000)
        progress.setWindowModality(Qt.WindowModal)
        progress.setRange(0, num)
        for i in range(num + 1):
            progress.setValue(i)
            if progress.wasCanceled():
                # QMessageBox.warning(self, "提示", "操作失败")
                break
        else:
            pass
            # progress.setValue(num)
            # QMessageBox.information(self, "提示", "操作成功")

    def timerEvent(self, *args, **kwargs):  # QBasicTimer的事件回调函数
        if self.step != -1:
            # 把step每次重置的值赋给进度条
            self.progressDialog.setValue(self.step)
        else:
            # 解压完毕后停止时钟
            self.timer.stop()
            return

        if self.step >= 100:
            # 停止进度条
            self.timer.stop()
            self.step = 1
            return
        # 把进度条卡在99，等处理好了再到100
        elif self.step < 99 and self.step > 0:
            self.step += 1

if __name__ == "__main__":
    #固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    #初始化
    myWin = MyMainForm()
    #将窗口控件显示在屏幕上
    myWin.show()
    #程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())