import itertools
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import quote

from pydantic import BaseModel
from utils.util import go_sleep, json_extract

from models.scrapper import ScrapperBase

QUERY_HASH = "69cba40317214236af40e7efa697781d"


class UserInfos(BaseModel):
    username: str
    user_id: str
    user_full_name: str
    user_followers: int
    user_following: int
    number_of_posts: Optional[int]
    biography: str


@dataclass
class PostInstagram:
    images: List[str]
    media_caption: str
    media_likes_number: int
    media_comments_number: int


@dataclass
class InstagramRequest:
    username: str
    user_id: int = None
    follow: int = None
    followed_by: int = None
    biography: str = None
    number_of_posts: int = None
    full_name: int = None
    number_of_images: int = None
    data: List[PostInstagram] = field(default_factory=list)


class InstagramImageScrapper(ScrapperBase):
    def __init__(self, base, user: InstagramRequest, max_iterations=20):
        ScrapperBase.__init__(self, base)
        self.user = user
        self.max_iterations = max_iterations
        self.post_per_call = 12
        self.cursors: List[str] = []
        self.initiate()

    def initiate(self):
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={self.user.username}"
        headers = {
            "authority": "i.instagram.com",
            "accept": "*/*",
            "accept-language": "fr-FR,fr;q=0.9",
            "cookie": "_js_ig_did=4743D1B2-888A-4199-BD97-63849C03070B; _js_datr=3VEGYwDc4o1YXpvN---R3dcB; csrftoken=5EaeghvFnfZdJ2FhuX9rH6CnFwU6Idaa; ig_did=456545FC-015E-4F1F-9432-CC858F153006; ig_nrcb=1; mid=YwZVowALAAF9NbINoRJlwldd6o7w",
            "origin": "https://www.instagram.com",
            "referer": "https://www.instagram.com/",
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "x-asbd-id": "198387",
            "x-ig-app-id": "936619743392459",
            "x-ig-www-claim": "0",
        }
        for _ in range(3):
            response = self.get(url, headers=headers)
            if response is not None and response.status_code == 200:
                response = response.json()
                # go_sleep(10)
                self.user.user_id = response["data"]["user"]["id"]
                self.cursors.append(
                    response["data"]["user"]["edge_owner_to_timeline_media"][
                        "page_info"
                    ]["end_cursor"]
                )
                self.user.followed_by = response["data"]["user"]["edge_followed_by"][
                    "count"
                ]
                self.user.follow = response["data"]["user"]["edge_follow"]["count"]
                self.user.biography = response["data"]["user"]["biography"]
                self.user.full_name = response["data"]["user"]["full_name"]
                self.user.number_of_posts = response["data"]["user"][
                    "edge_owner_to_timeline_media"
                ]["count"]
                break

    def formulate_variables(self) -> str:
        """Formulate variables for the query."""
        variables = {
            "id": self.user.user_id,
            "first": self.post_per_call,
            "after": self.cursors[-1],
        }
        return variables

    def instagram_call(self, query_hash):
        var = self.formulate_variables()
        a = quote(str(var).replace(" ", "").replace("'", '"'))
        url = f"https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables={a}"
        headers = {
            "authority": "www.instagram.com",
            "accept": "*/*",
            "accept-language": "fr-FR,fr;q=0.9",
            "cookie": "ig_nrcb=1; csrftoken=hf5MXNY4XWrWJSRqG9NUdTkf6GRl6dfu; mid=YwZR3gALAAFeLOglEDRYh02J7tJF; ig_did=B90D69C8-27AF-45D1-A023-FEAD2DE9E41A; datr=tjUHY1_GtwW19NgjLFIw5rTC; csrftoken=5EaeghvFnfZdJ2FhuX9rH6CnFwU6Idaa; ig_did=456545FC-015E-4F1F-9432-CC858F153006; ig_nrcb=1; mid=YwZVowALAAF9NbINoRJlwldd6o7w",
            "referer": f"https://www.instagram.com/{self.user.username}/",
            "sec-ch-prefers-color-scheme": "light",
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "viewport-width": "612",
            "x-asbd-id": "198387",
            "x-csrftoken": "hf5MXNY4XWrWJSRqG9NUdTkf6GRl6dfu",
            "x-ig-app-id": "936619743392459",
            "x-ig-www-claim": "0",
            "x-requested-with": "XMLHttpRequest",
        }
        for _ in range(3):
            response = self.get(url, headers=headers)
            if response is not None and response.status_code == 200:
                return response.json()
        return {"status": "error"}

    @staticmethod
    def instagram_parser(response_json):
        if response_json["status"] == "ok":
            edges = response_json["data"]["user"]["edge_owner_to_timeline_media"][
                "edges"
            ]
            cursor_info = response_json["data"]["user"]["edge_owner_to_timeline_media"][
                "page_info"
            ]
            posts = []
            for edge in edges:
                edge = edge["node"]
                images = json_extract(edge, "display_url")

                likes = json_extract(edge["edge_media_preview_like"], "count")
                n_likes = likes[0] if likes else 0

                n_comments = json_extract(edge["edge_media_to_comment"], "count")
                n_comments = n_comments[0] if n_comments else 0

                captions = json_extract(edge["edge_media_to_caption"], "text")
                posts.append(PostInstagram(images, captions, n_likes, n_comments))
            return posts, cursor_info["has_next_page"], cursor_info["end_cursor"]
        return [], False, ""

    def get_posts(self, number_of_posts: int) -> list:
        self.post_per_call = number_of_posts
        call = self.instagram_call(QUERY_HASH)
        posts, _, _ = self.instagram_parser(call)
        return posts

    def process(self):
        images = []
        for _ in range(self.max_iterations):
            call = self.instagram_call(QUERY_HASH)
            posts, _, end_cursor = self.instagram_parser(call)
            self.cursors.append(end_cursor)
            self.user.data.extend(posts)
            images.extend([e.images for e in posts])
            go_sleep(20)

        self.user.number_of_images = len(images)
        images = list(itertools.chain.from_iterable(images))
        return self.user
