from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import QThreadPool, pyqtSlot, QMimeData
from PyQt6.QtGui import QClipboard
import sys
from os import getcwd
from Scripts.seventv import SevenTvApi, SevenTvEmote
from Scripts.uiclass import Emote, EmotesDisplay

api = SevenTvApi()
this_folder = getcwd()


class Emo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(f"{this_folder}/emotes.ui", self)
        
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(5)

        self.emotesList = EmotesDisplay(self, self.emotesDisplay)

        d = api.get_emote_set("https://7tv.app/emote-sets/01JDQ3YGV7TS0814C326PZFK9C")
        for emote in d:
            print(emote.url)
            # self.emotesList.addEmote(emote.url)
 
        self.butAddEmotes: QPushButton = self.butAddEmotes
        self.butAddEmotes.clicked.connect(self.clickedAddEmotes)

    @pyqtSlot(SevenTvEmote, bytes)
    def __road(self, emote_data, image_data):
        self.emotesList.addEmoteToDisplay(Emote(emote_data, image_data))

    def clickedAddEmotes(self):
        mime_data: QMimeData = QApplication.clipboard().mimeData()

        if mime_data.hasText():
            text = mime_data.text()
            print("Содержимое буфера обмена:", text)
            if text.startswith("https://7tv.app/emote-sets/"):
                for emote in api.get_emote_set(text):
                    self.emotesList.addEmote(emote.url)
            elif text.startswith("https://7tv.app/emotes/"):
                self.emotesList.addEmote(api.get_emote(text).url)

def main() -> None:
    app = QApplication(sys.argv)
    emo = Emo()
    emo.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()