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

    cookie = cookie_str

    print(f'res: {get_ab(target_url=url, user_agent=agent, cookie_str=cookie)}')