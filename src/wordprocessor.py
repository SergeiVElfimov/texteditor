import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QActionGroup, QFont, QIcon, QImage, QKeySequence, QTextDocument
from PyQt6.QtPrintSupport import QPrintDialog
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFontComboBox,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .utils import hexuuid, splitext

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
IMAGE_EXTENSIONS = [".jpg", ".png", ".bmp"]
TEXT_EXTENSIONS = [".txt"]


class TextEdit(QTextEdit):
    def canInsertFromMimeData(self, source):

        if source.hasImage():
            return True
        else:
            return super(TextEdit, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source):

        cursor = self.textCursor()
        document = self.document()

        if source.hasUrls():

            for u in source.urls():
                file_ext = splitext(str(u.toLocalFile()))
                if u.isLocalFile() and file_ext in IMAGE_EXTENSIONS:
                    image = QImage(u.toLocalFile())
                    document.addResource(QTextDocument.ImageResource, u, image)
                    cursor.insertImage(u.toLocalFile())
                else:
                    break

            else:
                return

        elif source.hasImage():
            image = source.imageData()
            uuid = hexuuid()
            document.addResource(QTextDocument.ImageResource, uuid, image)
            cursor.insertImage(uuid)
            return

        super(TextEdit, self).insertFromMimeData(source)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.editor = TextEdit()
        self.editor.setAutoFormatting(QTextEdit.AutoFormatting.AutoAll)
        self.editor.selectionChanged.connect(self.update_format)
        font = QFont("Times", 12)
        self.editor.setFont(font)
        self.editor.setFontPointSize(12)

        self.path = None

        layout.addWidget(self.editor)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        file_toolbar = QToolBar("File")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(
            QIcon(os.path.join("images", "blue-folder-open-document.png")),
            "Open file...",
            self,
        )
        open_file_action.setStatusTip("Open file")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        save_file_action = QAction(
            QIcon(os.path.join("images", "disk.png")), "Save", self
        )
        save_file_action.setStatusTip("Save current page")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        save_as_file_action = QAction(
            QIcon(os.path.join("images", "disk--pencil.png")), "Save As...", self
        )
        save_as_file_action.setStatusTip("Save current page to specified file")
        save_as_file_action.triggered.connect(self.file_save_as)
        file_menu.addAction(save_as_file_action)
        file_toolbar.addAction(save_as_file_action)

        print_action = QAction(
            QIcon(os.path.join("images", "printer.png")), "Print...", self
        )
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Edit")

        undo_action = QAction(
            QIcon(os.path.join("images", "arrow-curve-180-left.png")), "Undo", self
        )
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(
            QIcon(os.path.join("images", "arrow-curve.png")), "Redo", self
        )
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join("images", "scissors.png")), "Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(
            QIcon(os.path.join("images", "document-copy.png")), "Copy", self
        )
        copy_action.setStatusTip("Copy selected text")
        cut_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(
            QIcon(os.path.join("images", "clipboard-paste-document-text.png")),
            "Paste",
            self,
        )
        paste_action.setStatusTip("Paste from clipboard")
        cut_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(
            QIcon(os.path.join("images", "selection-input.png")), "Select all", self
        )
        select_action.setStatusTip("Select all text")
        cut_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        wrap_action = QAction(
            QIcon(os.path.join("images", "arrow-continue.png")),
            "Wrap text to window",
            self,
        )
        wrap_action.setStatusTip("Toggle wrap text to window")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

        format_toolbar = QToolBar("Format")
        format_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(format_toolbar)
        format_menu = self.menuBar().addMenu("&Format")

        self.fonts = QFontComboBox()
        self.fonts.currentFontChanged.connect(self.editor.setCurrentFont)
        format_toolbar.addWidget(self.fonts)

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in FONT_SIZES])

        self.fontsize.currentTextChanged[str].connect(
            lambda s: self.editor.setFontPointSize(float(s))
        )
        format_toolbar.addWidget(self.fontsize)

        self.bold_action = QAction(
            QIcon(os.path.join("images", "edit-bold.png")), "Bold", self
        )
        self.bold_action.setStatusTip("Bold")
        self.bold_action.setShortcut(QKeySequence.StandardKey.Bold)
        self.bold_action.setCheckable(True)
        self.bold_action.toggled.connect(
            lambda x: self.editor.setFontWeight(
                QFont.Weight.Bold if x else QFont.Weight.Normal
            )
        )
        format_toolbar.addAction(self.bold_action)
        format_menu.addAction(self.bold_action)

        self.italic_action = QAction(
            QIcon(os.path.join("images", "edit-italic.png")), "Italic", self
        )
        self.italic_action.setStatusTip("Italic")
        self.italic_action.setShortcut(QKeySequence.StandardKey.Italic)
        self.italic_action.setCheckable(True)
        self.italic_action.toggled.connect(self.editor.setFontItalic)
        format_toolbar.addAction(self.italic_action)
        format_menu.addAction(self.italic_action)

        self.underline_action = QAction(
            QIcon(os.path.join("images", "edit-underline.png")), "Underline", self
        )
        self.underline_action.setStatusTip("Underline")
        self.underline_action.setShortcut(QKeySequence.StandardKey.Underline)
        self.underline_action.setCheckable(True)
        self.underline_action.toggled.connect(self.editor.setFontUnderline)
        format_toolbar.addAction(self.underline_action)
        format_menu.addAction(self.underline_action)

        format_menu.addSeparator()

        self.align_left_action = QAction(
            QIcon(os.path.join("images", "edit-alignment.png")), "Align left", self
        )
        self.align_left_action.setStatusTip("Align text left")
        self.align_left_action.setCheckable(True)
        self.align_left_action.triggered.connect(
            lambda: self.editor.setAlignment(Qt.Alignment.AlignLeft)
        )
        format_toolbar.addAction(self.align_left_action)
        format_menu.addAction(self.align_left_action)

        self.align_center_action = QAction(
            QIcon(os.path.join("images", "edit-alignment-center.png")),
            "Align center",
            self,
        )
        self.align_center_action.setStatusTip("Align text center")
        self.align_center_action.setCheckable(True)
        self.align_center_action.triggered.connect(
            lambda: self.editor.setAlignment(Qt.Alignment.AlignCenter)
        )
        format_toolbar.addAction(self.align_center_action)
        format_menu.addAction(self.align_center_action)

        self.align_right_action = QAction(
            QIcon(os.path.join("images", "edit-alignment-right.png")),
            "Align right",
            self,
        )
        self.align_right_action.setStatusTip("Align text right")
        self.align_right_action.setCheckable(True)
        self.align_right_action.triggered.connect(
            lambda: self.editor.setAlignment(Qt.Alignment.AlignRight)
        )
        format_toolbar.addAction(self.align_right_action)
        format_menu.addAction(self.align_right_action)

        self.align_justify_action = QAction(
            QIcon(os.path.join("images", "edit-alignment-justify.png")), "Justify", self
        )
        self.align_justify_action.setStatusTip("Justify text")
        self.align_justify_action.setCheckable(True)
        self.align_justify_action.triggered.connect(
            lambda: self.editor.setAlignment(Qt.Alignment.AlignJustify)
        )
        format_toolbar.addAction(self.align_justify_action)
        format_menu.addAction(self.align_justify_action)

        format_group = QActionGroup(self)
        format_group.setExclusive(True)
        format_group.addAction(self.align_left_action)
        format_group.addAction(self.align_center_action)
        format_group.addAction(self.align_right_action)
        format_group.addAction(self.align_justify_action)

        format_menu.addSeparator()

        self._format_actions = [
            self.fonts,
            self.fontsize,
            self.bold_action,
            self.italic_action,
            self.underline_action,
        ]

        self.update_format()
        self.update_title()
        self.show()

    def block_signals(self, objects, b):
        for o in objects:
            o.blockSignals(b)

    def update_format(self):
        """
        Update the font format toolbar/actions when a new text selection is made. This is necessary to keep
        toolbars/etc. in sync with the current edit state.
        :return:
        """

        self.block_signals(self._format_actions, True)
        self.fonts.setCurrentFont(self.editor.currentFont())
        self.fontsize.setCurrentText(str(int(self.editor.fontPointSize())))
        self.italic_action.setChecked(self.editor.fontItalic())
        self.underline_action.setChecked(self.editor.fontUnderline())
        self.bold_action.setChecked(self.editor.fontWeight() == QFont.bold)
        self.align_left_action.setChecked(
            self.editor.alignment() == Qt.Alignment.AlignLeft
        )
        self.align_center_action.setChecked(
            self.editor.alignment() == Qt.Alignment.AlignCenter
        )
        self.align_right_action.setChecked(
            self.editor.alignment() == Qt.Alignment.AlignRight
        )
        self.align_justify_action.setChecked(
            self.editor.alignment() == Qt.Alignment.AlignJustify
        )

        self.block_signals(self._format_actions, False)

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "Text documents (*.txt);;All files (*.*)",
        )

        try:
            with open(path, "rU") as f:
                text = f.read()

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.editor.setText(text)
            self.update_title()

    def file_save(self):
        if self.path is None:
            return self.file_save_as()

        text = (
            self.editor.toHtml()
            if splitext(self.path) in TEXT_EXTENSIONS
            else self.editor.toPlainText()
        )

        try:
            with open(self.path, "w") as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

    def file_save_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save file",
            "",
            "Text documents (*.txt);;All files (*.*)",
        )

        if not path:
            return

        text = (
            self.editor.toHtml()
            if splitext(path) in TEXT_EXTENSIONS
            else self.editor.toPlainText()
        )

        try:
            with open(path, "w") as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())

    def update_title(self):
        self.setWindowTitle(
            "%s - Megasolid Idiom"
            % (os.path.basename(self.path) if self.path else "Untitled")
        )

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)
