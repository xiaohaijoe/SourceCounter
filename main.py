
from index import Ui_IndexWindow
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json
import os
import _thread
import time

class mywindow(QtWidgets.QMainWindow, Ui_IndexWindow):
    is_file = True
    configTypes = None
    codeNum = 0
    commentNum = 0
    emptyNum = 0
    totalNum = 0
    table_model = None
    tableDataSignal = QtCore.pyqtSignal(str, int, int, int, int)           # 列表更新信号量

    def __init__(self):
        super(mywindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("代码行数统计工具V1.0")
        self.setFixedSize(self.width(), self.height());

        self.button_file.clicked.connect(self.open_file)    # 打开文件
        self.button_dir.clicked.connect(self.open_dir)      # 打开目录
        self.button_start.clicked.connect(self.start)       # 开始统计

        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.table_model = QStandardItemModel();
        self.table_model.setHorizontalHeaderLabels(['文件名', '代码数', '注释数', '空行数', '总行数'])
        self.tableView.setModel(self.table_model)
        self.tableView.setColumnWidth(0, 270)
        self.tableView.setColumnWidth(1, 70)
        self.tableView.setColumnWidth(2, 70)
        self.tableView.setColumnWidth(3, 70)
        self.tableView.setColumnWidth(4, 70)

        self.tableDataSignal.connect(self.model_setItem)

        self.configTypes = self.open_accordant_config()
        for item in self.configTypes:
            self.selector_language.addItem(item["name"])

    def open_accordant_config(self):
        '''
        调用配置文件
        '''
        config_file = "./config.json"
        fo = open(config_file, 'r', encoding='utf-8')
        return json.load(fo)["types"]

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "请选择要统计的文件", "./")
        self.label_address.setText(filename)
        self.is_file = True

    def open_dir(self):
        filename = QFileDialog.getExistingDirectory(self, "请选择要统计的文件夹", './')
        self.label_address.setText(filename)
        self.is_file = False

    def start(self):
        self.codeNum = 0
        self.commentNum = 0
        self.emptyNum = 0
        self.totalNum = 0
        self.table_model.removeRows(0,self.table_model.rowCount())
        filename = self.label_address.text()
        # 要解析的语言
        index = self.selector_language.currentIndex()
        type = self.configTypes[index]
        _thread.start_new_thread(self.analyze_files, (filename, type))


    def analyze_files(self, filename, currentType):
        if self.is_file:
            # 如果是上传文件
            type = self.get_file_config_type(filename,currentType)
            if type != None:
                self.analyze_content(filename, type)
        else:
            # 如果是上传文件夹
            for root, dirs, files in os.walk(filename):
                for name in files:
                    type = self.get_file_config_type(name, currentType)
                    if type != None:
                        self.analyze_content(root + "/" + name, type)

    def get_file_config_type(self, filename, currentType):
        suffix = os.path.splitext(filename)
        # 如果指定统计某格式文件
        if len(currentType["suffix"]) != 0:
            if suffix[1] == currentType["suffix"]:
                return currentType
            else:
                return None

        for type in self.configTypes:
            if type["suffix"] == suffix[1]:
                return type
        return None

    def analyze_content(self, filename, type):
        try:
            file = open(filename, 'r', encoding='utf-8')
            lines = file.readlines()
        except:
            file.close()
            return

        codeNum = 0         # 代码数
        emptyNum = 0        # 空行数
        commentNum = 0      # 注释数
        totalNum = 0        # 总行数

        comments = []
        for item in type["comment"]:
            if item.rfind("single") > 0:
                # 单行注释
                comments.append(item.split("single"))
                # comments[len(comments) - 1].append("single")
            elif item.rfind("multi") > 0:
                # 多行注释
                comments.append(item.split("multi"))
                comments[len(comments) - 1].append("multi")
            else:
                # 单行注释
                comments.append([item])

        # print(comments)
        multiCommentHeader = None  # 如果是多行注释，则该值为注释开头字符，否则为None
        index = 0
        for line in lines:
            index = index + 1
            # print(index,line)
            newLine = line.replace(" ", "").replace("\t", "").strip()
            if multiCommentHeader != None:
                # 如果是多行注释，则判断是否多行注释结束符
                # print(multiCommentHeader,newLine)
                for comment in comments:
                    if multiCommentHeader == comment[0]:
                        commentNum = commentNum + 1
                        if newLine.endswith(comment[1]):
                            multiCommentHeader = None
            else:
                if newLine == "":
                    # 空白行
                    emptyNum = emptyNum + 1
                else:
                    # 判断是否注释行
                    isComment = False
                    for comment in comments:
                        if len(comment) > 2:
                            # 多行注释
                            if newLine.startswith(comment[0]):
                                multiCommentHeader = comment[0]
                                commentNum = commentNum + 1
                                isComment = True
                            if newLine != comment[0] and newLine.endswith(comment[1]):
                                multiCommentHeader = None
                        else:
                            # 单行注释
                            if newLine.startswith(comment[0]):
                                commentNum = commentNum + 1
                                isComment = True
                    if isComment == False:
                        codeNum = codeNum + 1
            totalNum = totalNum + 1

        self.codeNum = self.codeNum + codeNum
        self.commentNum = self.commentNum + commentNum
        self.emptyNum = self.emptyNum + emptyNum
        self.totalNum = self.totalNum + totalNum

        self.label_code_num.setText(str(self.codeNum))
        self.label_comment_num.setText(str(self.commentNum))
        self.label_empty_num.setText(str(self.emptyNum))
        self.label_total_num.setText(str(self.totalNum))
        self.tableDataSignal.emit(filename, codeNum, emptyNum, commentNum, totalNum)
        file.close()

    def model_setItem(self, filename, codeNum, emptyNum, commentNum, totalNum):
        # print(1)
        # self.table_model.insertRow(1)
        # print(2)
        row = self.table_model.rowCount();
        # print("行数", row,filename,codeNum,emptyNum,commentNum,totalNum)
        self.table_model.setItem(row, 0, QStandardItem(filename))
        self.table_model.setItem(row, 1, QStandardItem(str(codeNum)))
        self.table_model.setItem(row, 2, QStandardItem(str(commentNum)))
        self.table_model.setItem(row, 3, QStandardItem(str(emptyNum)))
        self.table_model.setItem(row, 4, QStandardItem(str(totalNum)))


if __name__=="__main__":
    import sys
    app=QtWidgets.QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())

