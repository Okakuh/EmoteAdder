import httpx
import httpx
import json


class SevenTvEmote:
    url_image_prefix = 'https://cdn.7tv.app/emote/'

    def __init__(self, name: str, animated: bool, resolution: list, emote_id: str):
        self.name = name
        self.url = "https://7tv.app/emotes/" + emote_id
        # self.author = author
        self.animated = animated
        self.resolution = resolution
        self.emote_id = emote_id

        resolution = list(
            map(lambda x: x if ".gif" in x["name"] or ".png" in x["name"] else {"height": 0, "width": 0}, resolution))
        self.better_res = max(resolution, key=lambda x: x['width'] and x['height'])

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"

    def if_animated(self) -> bool:
        return self.animated

    def emote_name(self) -> str:
        return self.name

    def get_better_res(self):
        return self.better_res

    def get_image_url(self):
        return SevenTvEmote.url_image_prefix + self.emote_id + "/" +self.get_better_res()["name"]
    
    
class SevenTvApi:
    api = 'https://7tv.io/v3/'

    def __init__(self):
        pass

    def return_json(self, url: str):
        emote_id = url[16:]
        result = httpx.get(self.api + emote_id).json()
        return result

    def get_emote(self, url: str) -> object:
        """
        Получает ссылку и обращается по id эмоута к 7tv api
        После создаёт объект класса `SevenTvEmote()` и возвращает его пользователю
        :param url: str
        :return: SevenTvEmote()
        """
        emote_id = url[16:]
        
        # result = httpx.get(self.api + emote_id).json()
        result = httpx.get(self.api + emote_id).json()
        name = result["name"]
        animated = result["animated"]
        resolution = result["host"]["files"]

        return SevenTvEmote(name, animated, resolution, emote_id[7:])

    def get_emote_set(self, url: str) -> list:
        """
        Получает ссылку и обращается к сету эмотов по id
        Возращает список создержащий объекты эмоутов `SevenTvEmotes()`
        :param url: str
        :return: [SevenTvEmotes()...]
        """
        set_id = url[16:]
        result = httpx.get(self.api + set_id).json()

        emote_list = list()

        for emote in result["emotes"]:
            name = emote["name"]
            animated = emote["data"]["animated"]
            resolution = emote["data"]["host"]["files"]
            emote_id = emote["data"]["id"]
            emote_list.append(SevenTvEmote(name, animated, resolution, emote_id))

        return emote_list
