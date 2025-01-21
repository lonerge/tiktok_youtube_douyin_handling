# -*- coding: utf-8 -*-
# @Author  : dongdonglongbbb@gmail.com
# @Time    : 2024/5/20 15:58
# @Desc    :
import re
import subprocess


def get_ab(target_url, user_agent, cookie_str):
    for index in range(2):
        try:
            p = subprocess.Popen(['node', './douyin_a_bogus.js', target_url, user_agent, cookie_str], stdout=subprocess.PIPE)
            result = p.stdout.read().strip().decode('utf-8')
            a_bogus = re.search(r'a_bogus: (.+)', result).group(1)
            return a_bogus
        except:
            pass

    return False


if __name__ == '__main__':
    url = 'device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=7366231405833063719&update_version_code=170400&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=124.0.0.0&browser_online=true&engine_name=Blink&engine_version=124.0.0.0&os_name=Mac+OS&os_version=10.15.7&cpu_core_num=8&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid=7319780293514495522&verifyFp=verify_lw66uj9x_y69HTWBr_NOK0_4O0k_As0k_vZiOREH3U5SC&fp=verify_lw66uj9x_y69HTWBr_NOK0_4O0k_As0k_vZiOREH3U5SC&msToken=yU6YuJRXkpxHbKfBk21OZvRCCT7IaC3T-rQDXilk_D3Xfm9vMEHr4sJmGuz5WREz4PjAyf3fs8DZXvQBYFRd4j-NdHvQavb4t-kMpfHxsjb0meScI2D1nPztQm7muZY%3D'

    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

    cookie = 'csrf_session_id=d7ee7cb6dd02be8dcbc16a59d8622bed; __live_version__=%221.1.1.7793%22; webcast_local_quality=null; live_use_vvc=%22false%22; bd_ticket_guard_client_web_domain=2; store-region=cn-gd; store-region-src=uid; ttwid=1%7Cew2pGD0-_59z9Q2hDGpEGZla0DwYQpmz-CRd8r7I8qo%7C1709894493%7C4384e326b20a95134bf9ed9eb679aa6d2f8d19bb079b12865e16e05b89e0b2ff; douyin.com; device_web_cpu_core=8; device_web_memory_size=8; xgplayer_device_id=75207733943; xgplayer_user_id=779808914697; xg_device_score=7.568284552297575; dy_swidth=1440; dy_sheight=900; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; passport_csrf_token=d2493f8362f4c7d54bf28282c2b563bf; passport_csrf_token_default=d2493f8362f4c7d54bf28282c2b563bf; s_v_web_id=verify_lw66uj9x_y69HTWBr_NOK0_4O0k_As0k_vZiOREH3U5SC; odin_tt=c30f2f3f8ce5a3d66818390cc2ce531dc578acc581b43601e97b9cd9d737b1b5642d163d93173928f0c69279cd5a3a2a978e9d059378f7711cc3707b169224739e58938a491b6d6b1972cc898c2bd370; download_guide=%223%2F20240514%2F0%22; pwa2=%220%7C0%7C3%7C0%22; strategyABtestKey=%221716191929.837%22; volume_info=%7B%22isUserMute%22'

    print(f'res: {get_ab(target_url=url, user_agent=agent, cookie_str=cookie)}')