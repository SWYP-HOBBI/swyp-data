import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 절대 경로로 수정
from database import Base
from models.user import User
from models.post import Post
from models.post_comment import PostComment
from models.post_like import PostLike
from models.post_like_count import PostLikeCount
from models.post_comment_count import PostCommentCount
from models.post_image import PostImage
from models.post_hobby_tag import PostHobbyTag
from models.hobby_tag import HobbyTag
from models.user_hobby_tag import UserHobbyTag
from models.notification import Notification
from models.deleted_user import DeletedUser

# 순환 참조 문제를 막기 위한 관계 초기화용 메서드 / 필수 x
def get_related_models():
    # 실제 실행 시점에서 import 하여 순환 import 회피
    from models import (
        user,
        post,
        post_comment,
        post_like,
        post_like_count,
        post_comment_count,
        post_image,
        post_hobby_tag,
        hobby_tag,
        user_hobby_tag,
        notification,
        deleted_user,
    )
    return (
        user,
        post,
        post_comment,
        post_like,
        post_like_count,
        post_comment_count,
        post_image,
        post_hobby_tag,
        hobby_tag,
        user_hobby_tag,
        notification,
        deleted_user,
    )
