from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit
from PyQt6.QtCore import QThreadPool, pyqtSlot
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

        # d = api.get_emote_set("https://7tv.app/emote-sets/01JDQ3YGV7TS0814C326PZFK9C")
        # for emote in d:
        #     self.emotesList.addEmote(emote.url)



    @pyqtSlot(SevenTvEmote, bytes)
    def addEmoteToDisplay(self, emote_data, image_data):
        self.emotesList.addEmoteToDisplay(Emote(emote_data, image_data))


def main() -> None:
    app = QApplication(sys.argv)
    emo = Emo()
    emo.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()