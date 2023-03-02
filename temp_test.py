import requests
import os
video_url = 'https://rr2---sn-npoe7nsr.googlevideo.com/videoplayback?expire=1669010508&ei=7L96Y9XpEMH74-EPoKm0yA4&ip=43.156.63.82&id=o-AGn_elVJCdpk3ODMjgXnMgW8sBNvgrS2FK6heWCAtaa6&itag=299&aitags=133%2C134%2C135%2C136%2C160%2C242%2C243%2C244%2C247%2C278%2C298%2C299%2C302%2C303&source=youtube&requiressl=yes&mh=sC&mm=31%2C26&mn=sn-npoe7nsr%2Csn-30a7rned&ms=au%2Conr&mv=m&mvi=2&pl=18&initcwndbps=1030000&vprv=1&mime=video%2Fmp4&ns=CEZIXEFwXPymE7ZUqRu2O_EJ&gir=yes&clen=353166036&dur=484.166&lmt=1668946135924559&mt=1668988618&fvip=1&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=6319224&n=pK6vD8P-gp9mmDVBC&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRQIhAJReRRMYuafKzwB9SCkeNK1bNjzEE_fmPv_83w1Ks-iAAiBhuyrCTnxRJCDZe8f4CtOnBCfl1mNtF3-Sqhz_QQq_sw%3D%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRgIhAPD2uHIXuhhDjyosCFJ20Mip53yblGJUHPN3OPJzfzGhAiEAiKB-WvmaYIR-_Pe7OD6JG3ls_9LB9pLP9n2WcKApm50%3D'

audio_url = 'https://rr2---sn-npoe7ns7.googlevideo.com/videoplayback?expire=1669010485&ei=1b96Y-L0K4SB4-EP8MuyiAY&ip=43.156.63.82&id=o-AMfqWlJjWGui1rLgHJ6qV3OzRMqqSa3XGdH4zr7AwWe4&itag=251&source=youtube&requiressl=yes&mh=8T&mm=31%2C29&mn=sn-npoe7ns7%2Csn-npoeens7&ms=au%2Crdu&mv=m&mvi=2&pl=18&initcwndbps=583750&vprv=1&mime=audio%2Fwebm&ns=MxDHt9C3jqx4Dz_J4RRkmhMJ&gir=yes&clen=2468825&otfp=1&dur=185.181&lmt=1668979481605107&mt=1668988618&fvip=4&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=6211224&n=cUqFi-PGsQ9j2pP8s&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cotfp%2Cdur%2Clmt&sig=AOq0QJ8wRgIhAM7wVppyj-aDdEYta0XB3GUk0V0VXM0XpExX3jhuICPHAiEAhArb6cAYxVfaCRxF1P4ebRIeDu4-kDt1jKz82Z-ilKs%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRAIgJcob8LK6XoL6kb0QcMKNjG8f_xc6IcJydnmB6cNJt0oCIAeTgJWs4jVIt181WeJgfd29bOs-uYEbdz-Vvinn4kjd'
audio = requests.get(audio_url)
with open(f'test.mp3', mode='wb') as f:
    print('下载音频')
    f.write(audio.content)
video = requests.get(video_url)
with open(f'test.mp4', mode='wb') as f:
    print('下载视频')
    f.write(video.content)


def merge():
    print(f'开始合并')
    ffmpeg = r'/home/ubuntu/ffmpeg/bin/ffmpeg -i ' + 'test.mp4 -i ' + 'test.mp3 -acodec copy -vcodec copy ' + 'out.mp4'
    os.popen(ffmpeg)
merge()

