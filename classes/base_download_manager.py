import abc
import io
import zipfile
from pathlib import Path
from threading import Thread
from typing import Final, Optional

import httpx


class BaseDownloadManager(abc.ABC):
    def __thread_work(self):
        """Function of another thread for downloading and unzipping something"""
        with httpx.Client(http2=True, http1=False) as client:
            with client.stream("GET",
                               self.url,
                               follow_redirects=True) as stream:
                self._content_length = int(stream.headers["Content-Length"])
                self._content_bytes_downloaded = 0
                data = io.BytesIO()
                for chunk in stream.iter_bytes():
                    data.write(chunk)
                    self._content_bytes_downloaded += len(chunk)
                with zipfile.ZipFile(data) as zip_file:
                    zip_file.extractall(self.path)
        self._thread_done = True

    @property
    @abc.abstractmethod
    def path(self) -> Path:
        """The path where something will be stored. For example `sprites/` or `sounds/`"""
        ...

    @property
    @abc.abstractmethod
    def url(self) -> str:
        """Direct-Link to the zip-archive that will be unzipped to the :attr:`~BaseDownloadManager.path`"""
        ...

    @property
    def content_length(self) -> Optional[int]:
        return self._content_length

    @property
    def content_bytes_downloaded(self) -> Optional[int]:
        return self._content_bytes_downloaded

    @property
    def thread_done(self) -> bool:
        return self._thread_done

    def __init__(self):
        self.thread: Final[Thread] = Thread(target=self.__thread_work, daemon=True)
        self._content_length: Optional[int] = None
        self._content_bytes_downloaded: Optional[int] = None
        self._thread_done: bool = False

    def start_download(self):
        """Start a download"""
        if not self.path.exists() or not set(self.path.glob("*")):
            self.path.mkdir(exist_ok=True)
            self.thread.start()
        else:
            self._thread_done = True
