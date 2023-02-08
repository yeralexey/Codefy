from json import JSONDecodeError
from typing import Union, Optional

import aiohttp


class attrdict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, name):
        return self[name]


class Error(Exception):
    pass
class UnknownError(Error):
    pass
class HostDownError(Error):
    pass
class TooFastError(Error):
    pass


class NekoFy:
    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.__dict__}>"

    def __repr__(self) -> str:
        return self.__str__()



class Neko(NekoFy):
    def __init__(
        self,
        ok: bool,
        result: dict,
        **kwargs
    ):
        self.success = ok
        self.key = result["key"]
        self.url = "https://nekobin.com/" + result["key"]
        self.raw = "https://nekobin.com/raw/" + result["key"]
        self.title = result["title"]
        self.author = result["author"]
        self.date = result["date"]  # time is being generated fine!
        # self.views = result["views"] # Has no attribure "view"
        self.length = result["length"]
        self.content = result["content"]


class NekoBin:
    def __init__(
        self,
        *,
        host: str = "https://nekobin.com",
        path: str = "/api/documents"
    ) -> None:
        self._host = host
        self._path = path

    async def do_request(
        self,
        data: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
    ):
        async with aiohttp.ClientSession() as ses:
            request = await ses.post(
                f"{self._host}{self._path}",
                json={
                    'content': data,
                    'title': title,
                    'author': author,
                },
                timeout=3
            )
        try:
            return await request.json(), request
        except JSONDecodeError:
            return await request.text(), request

    async def nekofy(
        self,
        content: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
    ) -> Union[Neko, bool]:
        try:
            data, _ = await self.do_request(
                content,
                title,
                author
            )
            try:
                if data["error"] == 'TOO_FAST':
                    # raise TooFastError("Too many requests")
                    data = {"ok": False, "result": {"error": "TOO_FAST", "key": "None", "title": "None", "author": "None", "content": "None", "date": "None", "length": "None"}}
                    return Neko(**data)

            except:
                return Neko(**data)
        except UnknownError:
            return False
        except aiohttp.ClientConnectorError:
            raise HostDownError("Client cannot reach Host at the moment")
