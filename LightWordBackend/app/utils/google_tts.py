import os, web_cache, base64
from google_speech import Speech, SpeechSegment

cachepath = os.path.join('cache')
db_filepath = os.path.join(cachepath, "google_speech-cache.sqlite")
os.makedirs(os.path.dirname(db_filepath), exist_ok=True)
cache_name = "sound_data"
SpeechSegment.BASE_URL = 'https://translate.google.{}/translate_tts'.format(os.environ.get('TLD') or 'com')
SpeechSegment.cache = web_cache.ThreadedWebCache(db_filepath,
                                                   cache_name,
                                                   expiration=60 * 60 * 24 * 365,  # 1 year
                                                   caching_strategy=web_cache.CachingStrategy.LRU)

def get_gspeech(text: str):
    if not text:
        return
    speech = Speech(text, 'en')
    filename = os.path.join(cachepath, "cache.mp3")
    speech.save(filename)
    with open(filename, 'rb') as f:
        base64_audio = base64.b64encode(f.read())
    return base64_audio