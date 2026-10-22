import json
import os
from pathlib import Path


def _environment_value(name):
    value = os.environ.get(name)
    return value.strip() if value else None


def _read_local_secret(file_path, label):
    try:
        value = Path(file_path).read_text(encoding='utf-8').strip()
    except OSError as exc:
        raise RuntimeError(f'{label} is not configured. Set its environment variable or create {file_path}.') from exc

    if not value or value.startswith('#'):
        raise RuntimeError(f'{label} is not configured. Set its environment variable or add a value to {file_path}.')
    return value


def get_required_env(name):
    value = _environment_value(name)
    if value:
        return value
    raise RuntimeError(f'{name} must be set in the environment.')


def add_optional_cookie_header(headers, env_name):
    value = _environment_value(env_name)
    if value:
        headers['cookie'] = value
    return headers


def load_douyin_cookie(file_path='douyin_cookies.txt'):
    value = _environment_value('DOUYIN_COOKIE')
    if value:
        return value

    file_path = os.environ.get('DOUYIN_COOKIES_FILE', file_path)
    return _read_local_secret(file_path, 'Douyin cookie')


def load_tiktok_cookie_header(file_path='tiktok_cookies.json'):
    value = _environment_value('TIKTOK_COOKIE')
    if value:
        return value

    file_path = os.environ.get('TIKTOK_COOKIES_FILE', file_path)
    try:
        cookies = json.loads(_read_local_secret(file_path, 'TikTok cookie'))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'TikTok cookie file {file_path} must contain a JSON object.') from exc

    if not isinstance(cookies, dict) or not cookies:
        raise RuntimeError(f'TikTok cookie file {file_path} must contain a non-empty JSON object.')

    return '; '.join(f'{name}={value}' for name, value in cookies.items())
