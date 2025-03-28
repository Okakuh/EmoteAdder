from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QScrollArea, QPushButton, QDialog, QGridLayout, QLineEdit
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, QRunnable, Q_ARG
import requests
from PIL import Image, ImageSequence
from io import BytesIO
from Scripts.seventv import SevenTvApi, SevenTvEmote
from time import sleep

api = SevenTvApi()

def kids(layout: QHBoxLayout) -> list:
    result = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget():
            result.append(item.widget())
            continue
        result.append(item)
    return result



class Emote(QPushButton):
    border = 2
    style_unselected = "border: 1px solid gray"
    style_selected = "border: 3px solid orange"
    emote_height = 50

    def __init__(self, emote_data, image_data: bytes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__emote_data: SevenTvEmote = emote_data

        self.sevenTvName = self.__emote_data.emote_name()
        
        self.minecraft_name = "name"
        self.minecraft_file = "file"
        self.minecraft_chars = "chars"
        self.minecraft_height = "height"
        self.minecraft_ascent = "ascent"

        self.sevenTvUrl = self.__emote_data.url
        self.image_data = image_data
        self.setStyleSheet(Emote.style_unselected)

        pixmap = QPixmap()
        pixmap.loadFromData(self.image_data)
        self.set_icon(pixmap)

        self.mousePressEvent = self.button_mouse_press_event
        self.iconWidth = self.size().width()

    def emote_slected(self):
        self.select()

    def __str__(self):
        return f"Class Emote: {self.sevenTvUrl}"

    def __repr__(self):
        return f"Class Emote: {self.sevenTvUrl}"

    def parse_gif(self, response) -> list[QPixmap]:
        gif = Image.open(BytesIO(response))
        frames = []
        for frame in ImageSequence.Iterator(gif):
            byte_array = BytesIO()
            frame.save(byte_array, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array.getvalue())
            frames.append(pixmap)
        return frames

    def set_icon(self, icon: QPixmap):
        icon = icon.scaledToHeight(Emote.emote_height)
        self.setFixedSize(QSize(icon.size().width() + Emote.border * 2, Emote.emote_height + Emote.border * 2))
        self.setIconSize(self.size())
        self.setIcon(QIcon(icon))

    def button_mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.open_frame_selector()
            self.click()
        super().mousePressEvent(event)

    def open_frame_selector(self):
        window_width = 850
        self.selector_dialog = QDialog(self.parent())
        self.selector_dialog.setWindowTitle("Select Frame")
        self.selector_dialog.setGeometry(200, 200, window_width, 600)

        dialog_layout = QVBoxLayout(self.selector_dialog)
        scroll_area = QScrollArea(self.selector_dialog)
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)

        row = 0
        col = 0
        self.gif_frames = self.parse_gif(self.image_data)
        for index, frame in enumerate(self.gif_frames):
            frame_button = QPushButton()
            frame = frame.scaledToHeight(Emote.emote_height)
            frame_button.setFixedSize(frame.size())
            frame_button.setIconSize(self.size())
            frame_button.setIcon(QIcon(frame))
            frame_button.mousePressEvent = lambda event, idx=index: self.select_frame(idx)
            
            scroll_layout.addWidget(frame_button, row, col)
            col += 1
            if (col+1) * frame.size().width() + col * 7 > window_width - 30:
                col = 0
                row += 1

        scroll_area.setWidget(scroll_widget)
        dialog_layout.addWidget(scroll_area)
        self.selector_dialog.exec()

    def select_frame(self, frame_index):
        self.set_icon(self.gif_frames[frame_index])
        self.selector_dialog.close()

    def select(self):
        self.setStyleSheet(Emote.style_selected)

    def unselect(self):
        self.setStyleSheet(Emote.style_unselected)
    


class Worker(QRunnable):
    def __init__(self, url, main_window):
        super().__init__()
        self.url = url
        self.main_window = main_window

    def run(self):
        emote_data = api.get_emote(self.url)
        # image_url = emote_data.get_image_url()
        response = requests.get(emote_data.get_image_url())
        if response.status_code == 200:
            self.main_window.metaObject().invokeMethod(
                self.main_window,
                "__road",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(SevenTvEmote, emote_data),
                Q_ARG(bytes, response.content),
            )
        else:
            print(f"Failed to load {self.url}")


class EmotesDisplay:
    def __init__(self, mainWindow, widget: QWidget):
        self.mainWindow = mainWindow
        self.widget = widget
        self.displayWidth = self.widget.size().width() - 40

        first_vlayout = QVBoxLayout(self.widget)
        self.emotes_rows = QVBoxLayout()
        first_vlayout.addLayout(self.emotes_rows)
        first_vlayout.addSpacerItem(QSpacerItem(1, 300))
        self.widget.setLayout(first_vlayout)
        self.selectedEmote: Emote = None

    def addEmoteToDisplay(self, emoteToAdd: Emote):
        def place(self, emoteToAdd: Emote):
            spacing = 5
            if not kids(self.emotes_rows):
                self.addNewRow()

            rows = kids(self.emotes_rows)
            for indx, layout in enumerate(rows):
                emotes = kids(layout)
                total_widget_lenth = len(emotes) * spacing
                for emote in emotes:
                    total_widget_lenth += emote.iconWidth
                    
                if total_widget_lenth + emoteToAdd.iconWidth < self.displayWidth:
                    return rows[indx]
                else:
                    if indx + 1 == len(rows):
                        self.addNewRow()
                        return kids(self.emotes_rows)[-1]
            

        emoteToAdd.clicked.connect(lambda: self.select(emoteToAdd))
        place(self, emoteToAdd).addWidget(emoteToAdd)

    def addNewRow(self):
        self.emotes_rows.addLayout(QHBoxLayout())

    def emotes(self) -> list[Emote]:
        result = []
        for row in kids(self.emotes_rows):
            for emote in kids(row):
                result.append(emote)
        return result

    def select(self, selectedEmote: Emote) -> None:
        for emote in self.emotes():
            if emote != selectedEmote:
                emote.unselect()
            else:
                emote.select()
                self.selectedEmote: Emote = selectedEmote
        self.mainWindow.selectedEmote.setFixedSize(selectedEmote.size())
        self.mainWindow.selectedEmote.setIconSize(selectedEmote.size())
        self.mainWindow.selectedEmote.setIcon(selectedEmote.icon())
        
        self.mainWindow.emoteSvnTvName.setText(self.selectedEmote.sevenTvName)
        self.mainWindow.emoteName.setText(self.selectedEmote.minecraft_name)
        self.mainWindow.emoteFile.setText(self.selectedEmote.minecraft_file)
        self.mainWindow.emoteHeight.setText(self.selectedEmote.minecraft_height)
        self.mainWindow.emoteChars.setText(self.selectedEmote.minecraft_chars)
        self.mainWindow.emoteAscent.setText(self.selectedEmote.minecraft_ascent)


    def addEmote(self, url: str):
        worker = Worker(url, self.mainWindow)
        self.mainWindow.thread_pool.start(worker)
        sleep(0.1)


