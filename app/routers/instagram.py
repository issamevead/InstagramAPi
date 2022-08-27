from fastapi import APIRouter, HTTPException
from log.logger import Logs
from models.instagram_model import InstagramImageScrapper, InstagramRequest
from models.scrapper import BaseInfo
from utils.util import get_random_proxy, get_proxy
from models.scrapper import GetInfoUser, GetUserByPOst

router = APIRouter(prefix="/instagram", tags=["instagram"])


@router.get("/userInfos")
def get_user_infos(username: str):
    try:
        proxy = get_proxy()
        base = BaseInfo(10, proxy, True)
        Logs().info(f"request on proxy | {proxy}")
        account = InstagramImageScrapper(base, InstagramRequest(username))
        return {
            "username": account.user.username,
            "user_id": account.user.user_id,
            "full_name": account.user.full_name,
            "follow": account.user.follow,
            "followed_by": account.user.followed_by,
            "number_of_posts": account.user.number_of_posts,
            "biography": account.user.biography,
        }
    except ValueError as e:
        raise HTTPException(status_code=406, detail=str(e)) from e


@router.get("/userMedia")
def get_user_infos_by_posts(username: str, number_of_posts: int):
    try:
        base = BaseInfo(10, get_proxy(), True)
        account = InstagramImageScrapper(base, InstagramRequest(username))
        posts = account.get_posts(number_of_posts)
        return {index: post for index, post in enumerate(posts)}
    except ValueError as e:
        raise HTTPException(status_code=406, detail=str(e)) from e
