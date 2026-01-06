import re
import json
from src.downloaders.base_downloader import BaseDownloader
from configs.logging_config import logger


class XiaohongshuDownloader(BaseDownloader):
    def __init__(self, real_url):
        super().__init__(real_url)
        self.headers = {
            "content-type": "application/json; charset=UTF-8",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            'referer': 'https://www.xiaohongshu.com/'
        }
        self.data = self.fetch_html_data()

    def fetch_html_data(self):
        self.html_content = self.fetch_html_content()
        pattern = re.compile(r'window\.__INITIAL_STATE__\s*=\s*(\{.*\})', re.DOTALL)
        json_data = BaseDownloader.parse_html_data(self.html_content, pattern)
        return json_data

    def get_real_video_url(self):
        try:
            data_dict = json.loads(self.data)
            first_note_id = data_dict['note']['firstNoteId']
            note_detail = data_dict['note']['noteDetailMap'][first_note_id]['note']
            
            # 新的视频地址路径
            if 'video' in note_detail and 'media' in note_detail['video']:
                # 获取最高质量的视频流
                h264_streams = note_detail['video']['media']['stream']['h264']
                if h264_streams:
                    # 选择第一个流（通常是最高质量的）
                    video_url = h264_streams[0]['masterUrl']
                    return video_url.replace("\\u002F", "/")
            
            raise Exception("无法找到视频地址")
        except Exception as e:
            logger.error(f"解析视频URL失败: {e}")
            logger.debug(f"完整note_detail数据: {json.dumps(note_detail, indent=2, ensure_ascii=False)}")
            raise
        
    def get_title_content(self):
        try:
            data_dict = json.loads(self.data)
            first_note_id = data_dict['note']['firstNoteId']
            title_content = data_dict['note']['noteDetailMap'][first_note_id]['note']['title']
            desc_content = data_dict['note']['noteDetailMap'][first_note_id]['note']['desc']
            return title_content + desc_content
        except (KeyError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse title content: {e}")

    def get_cover_photo_url(self):
        try:
            data_dict = json.loads(self.data)
            first_note_id = data_dict['note']['firstNoteId']
            note_detail = data_dict['note']['noteDetailMap'][first_note_id]['note']
            
            # 新的封面图片路径
            if 'imageList' in note_detail and note_detail['imageList']:
                return note_detail['imageList'][0]['urlDefault']
            
            # 或者从video信息中获取
            if 'video' in note_detail and 'image' in note_detail['video']:
                # 这里可以根据需要构造封面URL
                pass
                
            raise Exception("无法找到封面图片地址")
        except Exception as e:
            logger.warning(f"解析封面URL失败: {e}")
            return None


if __name__ == '__main__':
    real_url = 'https://www.xiaohongshu.com/explore/66265ead000000000d030c3f?xsec_token=ABClLfS3dCR8EaYcL9WW7xzrqPoYH4oOildl5Xg1vGjMo=&xsec_source=pc_search'
    xhs_dl = XiaohongshuDownloader(real_url)
    print(xhs_dl.get_title_content())
    print(xhs_dl.get_cover_photo_url())
    print(xhs_dl.get_real_video_url())
