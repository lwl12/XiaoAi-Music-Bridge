from xiaoai import *
import json
import requests


def outputJson(toSpeakText, is_session_end, openMic=True):
    xiaoAIResponse = XiaoAIResponse(to_speak=XiaoAIToSpeak(
        type_=0, text=toSpeakText), open_mic=openMic)
    response = xiaoai_response(XiaoAIOpenResponse(version="1.0",
                                                  is_session_end=is_session_end,
                                                  response=xiaoAIResponse))
    return response


def main(event):
    req = xiaoai_request(event)
    if req.request.type == 0:
        return outputJson("欢迎来到云村，你想听什么歌呢？", False)
    elif req.request.type == 1:
        if ((not hasattr(req.request, "slot_info")) or (not hasattr(req.request.slot_info, "intent_name"))):
            return outputJson("你想听什么歌呢？", False)
        else:
            if req.request.slot_info.intent_name == 'Search':
                slotsList = req.request.slot_info.slots
                musicName = [
                    item for item in slotsList if item['name'] == 'Music'][0]['value']
                try:
                    searchResult = requests.get('https://api.lwl12.com/music/netease/search?keyword=' +
                                                musicName, headers={'User-Agent': 'miai-LapiBridge/1.0.0'})
                    searchResult = json.loads(searchResult.text)

                    if (len(searchResult) < 1 or not searchResult[0] or not searchResult[0]["url_id"] or not searchResult[0]["url_id"]):
                        return outputJson("抱歉，未能找到相关歌曲", False)
                    musicURL = requests.get('https://api.lwl12.com/music/netease/song?id=' + str(
                        searchResult[0]["url_id"]), headers={'User-Agent': 'miai-LapiBridge/1.0.0'})
                    musicURL = json.loads(musicURL.text)
                    if (not musicURL or not musicURL["result"] or not musicURL["result"]["url"]):
                        return outputJson("抱歉，未能找到相关歌曲", False)
                    gap = "，"

                    infoTTS = XiaoAIDirective(type_="tts", tts_item=XiaoAITTSItem(
                        type_="0", text='好的，马上为您播放' + gap.join(searchResult[0]["artist"]) + '的' + searchResult[0]["name"]))
                    infoAudio = XiaoAIDirective(type_="audio", audio_item=XiaoAIAudioItem(stream=XiaoAIStream(
                        url="https://api.lwl12.com/music/netease/song?id=" + str(searchResult[0]["url_id"]))))
                    xiaoAIResponse = XiaoAIResponse(
                        directives=[infoTTS, infoAudio], open_mic=False)
                    response = xiaoai_response(XiaoAIOpenResponse(
                        version="1.0", is_session_end=True, response=xiaoAIResponse))
                except Exception as e:
                    #return outputJson(str(e), False)
                    return outputJson("抱歉，出现未知错误，我们会尽快修复", True, False)
                return response

            else:
                return outputJson("欢迎来到云村，你可以说：来首 Are you OK", False)
    else:
        return outputJson("感谢使用云村，下次再见", True, False)