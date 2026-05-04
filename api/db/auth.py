"""Supabase Auth 中间件 —— JWT 验证与用户身份提取"""

from fastapi import Header, HTTPException
import httpx
from jose import jwt, JWTError
from jose.constants import Algorithms

from config import config

# Supabase 新项目使用 ECC (ES256) 签名，通过 JWKS 获取公钥验证
_JWKS_URL = f"{config.SUPABASE_URL}/auth/v1/.well-known/jwks.json"


def _get_signing_key(token: str):
    """从 Supabase JWKS 获取匹配的签名密钥"""
    try:
        response = httpx.get(_JWKS_URL, timeout=10)
        jwks = response.json()
    except Exception:
        # 网络问题降级到 HS256
        return config.SUPABASE_JWT_SECRET

    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

    # 无匹配 key 降级到 HS256
    return config.SUPABASE_JWT_SECRET


def get_current_user(authorization: str = Header(None)) -> str:
    """
    从 Authorization header 验证 Supabase JWT，返回 user_id。

    用法：在路由函数中添加 Depends(get_current_user)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="认证格式错误，应为 Bearer <token>")

    token = parts[1]

    try:
        key = _get_signing_key(token)
        payload = jwt.decode(
            token,
            key,
            algorithms=[Algorithms.ES256, Algorithms.HS256],
            options={"verify_aud": False},
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="令牌中缺少用户标识")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")


def get_optional_user(authorization: str = Header(None)) -> str | None:
    if not authorization:
        return None
    try:
        return get_current_user(authorization)
    except HTTPException:
        return None
