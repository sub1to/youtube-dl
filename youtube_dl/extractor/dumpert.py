# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import (
    int_or_none,
    qualities,
)


class DumpertIE(InfoExtractor):
    _VALID_URL = r'(?P<protocol>https?)://(?:(?:www|legacy)\.)?dumpert\.nl/(?:mediabase/|embed/|item/|(?:toppers|latest)?\?selectedId=)(?P<id>[0-9]+[/_][0-9a-zA-Z]+)'
    _TESTS = [{
        'url': 'https://www.dumpert.nl/toppers?selectedId=100047162_9197be8a',
        'md5': 'f45fd6919d887c9c72f61e1cc5ae0257',
        'info_dict': {
            'id': '100047162/9197be8a',
            'ext': 'm3u8',
            'title': 'Engelse humor',
            'description': '<p>Hebben het wel </p>',
            'thumbnail': r're:^https?://.*\.(?:jpg|png)$',
        }
    }, {
        'url': 'https://www.dumpert.nl/item/100047162_9197be8a',
        'only_matching': True,
    }, {
        'url': 'https://www.dumpert.nl/embed/100047162/9197be8a',
        'only_matching': True,
    }, {
        'url': 'http://legacy.dumpert.nl/mediabase/100047162/9197be8a',
        'only_matching': True,
    }, {
        'url': 'http://legacy.dumpert.nl/embed/100047162/9197be8a',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url).replace('_', '/')
        item = self._download_json(
            'http://api-live.dumpert.nl/mobile_api/json/info/' + video_id.replace('/', '_'),
            video_id)['items'][0]
        title = item['title']
        media = next(m for m in item['media'] if m.get('mediatype') == 'VIDEO')

        quality = qualities(['flv', 'mobile', 'tablet', '720p', 'stream'])
        formats = []
        for variant in media.get('variants', []):
            uri = variant.get('uri')
            if not uri:
                continue
            version = variant.get('version')
            formats.append({
                'url': uri,
                'format_id': version,
                'quality': quality(version),
            })
        self._sort_formats(formats)

        thumbnails = []
        stills = item.get('stills') or {}
        for t in ('thumb', 'still'):
            for s in ('', '-medium', '-large'):
                still_id = t + s
                still_url = stills.get(still_id)
                if not still_url:
                    continue
                thumbnails.append({
                    'id': still_id,
                    'url': still_url,
                })

        stats = item.get('stats') or {}

        return {
            'id': video_id,
            'title': title,
            'description': item.get('description'),
            'thumbnails': thumbnails,
            'formats': formats,
            'duration': int_or_none(media.get('duration')),
            'like_count': int_or_none(stats.get('kudos_total')),
            'view_count': int_or_none(stats.get('views_total')),
        }
