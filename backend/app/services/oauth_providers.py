from urllib.parse import urlencode

import httpx

from app.config import settings


class OAuthNotConfiguredError(RuntimeError):
    pass


def _kakao_configured() -> bool:
    return bool(settings.kakao_rest_api_key and settings.kakao_redirect_uri)


def _naver_configured() -> bool:
    return bool(
        settings.naver_client_id
        and settings.naver_client_secret
        and settings.naver_redirect_uri
    )


def list_enabled_providers() -> list[str]:
    providers: list[str] = []
    if _kakao_configured():
        providers.append("kakao")
    if _naver_configured():
        providers.append("naver")
    return providers


def kakao_authorize_url(state: str) -> str:
    if not _kakao_configured():
        raise OAuthNotConfiguredError("카카오 로그인이 설정되지 않았습니다.")
    params = {
        "client_id": settings.kakao_rest_api_key,
        "redirect_uri": settings.kakao_redirect_uri,
        "response_type": "code",
        "state": state,
    }
    return f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"


async def kakao_exchange_code(code: str) -> dict:
    if not _kakao_configured():
        raise OAuthNotConfiguredError("카카오 로그인이 설정되지 않았습니다.")
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.kakao_rest_api_key,
        "redirect_uri": settings.kakao_redirect_uri,
        "code": code,
    }
    if settings.kakao_client_secret:
        data["client_secret"] = settings.kakao_client_secret
    async with httpx.AsyncClient(timeout=15.0) as client:
        token_res = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")
        if not access_token:
            raise ValueError("카카오 토큰을 받지 못했습니다.")

        profile_res = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_res.raise_for_status()
        profile = profile_res.json()

    kakao_id = str(profile.get("id", ""))
    account = profile.get("kakao_account") or {}
    profile_info = account.get("profile") or {}
    return {
        "provider_user_id": kakao_id,
        "email": account.get("email"),
        "name": profile_info.get("nickname"),
        "avatar_url": profile_info.get("profile_image_url"),
    }


def naver_authorize_url(state: str) -> str:
    if not _naver_configured():
        raise OAuthNotConfiguredError("네이버 로그인이 설정되지 않았습니다.")
    params = {
        "response_type": "code",
        "client_id": settings.naver_client_id,
        "redirect_uri": settings.naver_redirect_uri,
        "state": state,
    }
    return f"https://nid.naver.com/oauth2.0/authorize?{urlencode(params)}"


async def naver_exchange_code(code: str, state: str) -> dict:
    if not _naver_configured():
        raise OAuthNotConfiguredError("네이버 로그인이 설정되지 않았습니다.")
    params = {
        "grant_type": "authorization_code",
        "client_id": settings.naver_client_id,
        "client_secret": settings.naver_client_secret,
        "code": code,
        "state": state,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        token_res = await client.get(
            f"https://nid.naver.com/oauth2.0/token?{urlencode(params)}"
        )
        token_res.raise_for_status()
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("네이버 토큰을 받지 못했습니다.")

        profile_res = await client.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_res.raise_for_status()
        profile = profile_res.json().get("response") or {}

    return {
        "provider_user_id": str(profile.get("id", "")),
        "email": profile.get("email"),
        "name": profile.get("name") or profile.get("nickname"),
        "avatar_url": profile.get("profile_image"),
    }
