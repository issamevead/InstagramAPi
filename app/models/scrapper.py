from dataclasses import dataclass
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional

import requests
from requests import Response, get
from tenacity import RetryError, retry, stop_after_attempt
from pydantic import BaseModel
from log.logger import Logs

class GetInfoUser(BaseModel):
    username:str

class GetUserByPOst(BaseModel):
    username:str
    number_of_posts:int

@dataclass
class BaseInfo:
    timeout: int
    proxies: dict
    verify: bool = False


class ScrapperBase(ABC):
    def __init__(self, base: BaseInfo) -> None:
        self.timeout = base.timeout
        self.proxies = base.proxies
        self.verify = base.verify

    @abstractmethod
    def process(self):
        pass

    def get_hash_based_bin(self, bin) -> str:
        return hashlib.sha256(str(bin).encode()).hexdigest()

    @retry(stop=stop_after_attempt(2))
    def request_template(self, url: str, headers: dict) -> Optional[Response]:
        """Make an HTTP request using custom headers
        request header
        Args:
            url (str): URL for the request
            timeout (int, optional): How many seconds to wait for the server to send data
            before giving up. Defaults to 10.
        Returns:
            requests.Response: Response object
        """
        try:
            url = url.encode().decode("utf-8")
            response = get(
                url,
                headers=headers,
                proxies=self.proxies,
                allow_redirects=True,
                verify=self.verify,
                timeout=self.timeout,
            )
            return response
        except requests.exceptions.Timeout as e_1:
            Logs().warn(e_1)
            return None
        except requests.exceptions.HTTPError as e_2:
            Logs().error(e_2)
            raise e_2
        except requests.exceptions.ConnectionError as e_3:
            Logs().error(e_3)
            return None
        except requests.exceptions.MissingSchema as e_4:
            Logs().error(e_4)
            raise e_4
        except requests.exceptions.InvalidSchema as e_5:
            Logs().error(e_5)
            raise e_5

    def get(
        self,
        url: str,
        headers: Optional[dict] = None,
    ) -> Optional[Response]:
        """get function"""
        try:
            response = self.request_template(url, headers)
            return response
        except RetryError as err:
            Logs().error(f"Max retries exceeded: {err}")
            return None
