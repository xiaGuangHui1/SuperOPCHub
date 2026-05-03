"""Supabase Auth 中间件 —— JWT 验证与用户身份提取"""

from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError

from config import config


def get_current_user(authorization: str = Header(None)) -> str:
    """
    从 Authorization header 验证 Supabase JWT，返回 user_id。

    用法：在路由函数中添加 Depends(get_current_user)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    # 提取 Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="认证格式错误，应为 Bearer <token>")

    token = parts[1]

    try:
        payload = jwt.decode(
            token,
            config.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},  # Supabase JWT 的 aud 可能不同
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="令牌中缺少用户标识")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")


# 可选认证：有 token 就验证，没有也能访问
def get_optional_user(authorization: str = Header(None)) -> str | None:
    if not authorization:
        return None
    try:
        return get_current_user(authorization)
    except HTTPException:
        return None
