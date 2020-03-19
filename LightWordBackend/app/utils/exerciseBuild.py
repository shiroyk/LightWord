import sys, re, os, random, json

from flask import current_app
from app.models import VocabData, UserConfig, UserData

class ExerciseBuild(object):
    def __init__(self, user: int, **config):
        self.uid = user
        self.word = None

        if not config:
            config = UserConfig.get_config(self.uid)
        try:
            self.tid = config['vtype']
            self.pron = config['pronounce']
            UserData.forget_time = json.loads(config['timestamp'])
        except (ValueError,KeyError):
            current_app.logger.error('%s: Please check user %s config', __name__, self.uid)
    
    def _random_example(self, define):
        randomex = random.sample(define, 1)[0]
        randomex.update({'examplelist': random.sample(randomex['examplelist'], 1)})
        return randomex
    
    def _pronounce_init(self, pronounce):
        if pronounce:
            if isinstance(pronounce, list):
                if len(pronounce) > 1:
                    if self.pron == 0:
                        return pronounce[0]
                    elif self.pron == 1:
                        return pronounce[1]
                else:
                    return pronounce[0]
            else:
                return pronounce
        else:
            return ''

    def _example_del_word(self, inflection, example):
        #替换例句中的单词
        try:
            for word in inflection:
                match = re.search(word + r'\b', example, re.I)
                if match: match_word = match.group()

            return [re.split(match_word, example),
                    example,
                    match_word
                    ]
        except (UnboundLocalError, ValueError, KeyError):
            current_app.logger.warn('%s: %s of type id %s can\'t replace example', __name__, self.word, self.tid )

    
    def _build_dict(self, words: object, status: str):
        
        for obj in words:
            
            self.word = obj.vocabulary.word
            word_id = obj.vocabulary.id
            word_define = json.loads(obj.vocabulary.localdict)
            random_define = self._random_example(word_define)

            meaning = random_define['meaning']
            pronounce = self._pronounce_init(random_define['pronounce'])
            try:
                part_of_speech = random_define['part of speech']
            except (ValueError, KeyError):
                part_of_speech = None
                current_app.logger.warn('%s: %s of type id %s don\'t have part of speech', __name__, self.word, self.tid )
                continue
            
            inflection = random_define['inflection']

            examplelist = random_define['examplelist'][0]
            example = examplelist['example']
            
            sentence_init = self._example_del_word(inflection, example)
            if sentence_init:
                match_word = sentence_init[2]
                sentence_split = sentence_init[0]
                sentence = sentence_init[1]
            else:
                continue
            translation = examplelist['translation']
            
            yield {
                "status": status,
                "id": word_id,
                "vtype": self.tid,
                "word": self.word,
                "meaning": meaning,
                "pronounce": pronounce,
                "inflection": inflection,
                "additional": part_of_speech,
                "example": {
                        "word": match_word,
                        "split": sentence_split,
                        "sentence": sentence,
                        "translation": translation,
                        },
                }

    def auto_exercise(self, num = 10):
        review_word = UserData.review_word(self.uid, self.tid, num)
        if review_word:
            return list(self._build_dict(review_word, 'Review'))
        else:
            return list(self._build_dict(VocabData.new_word(self.uid, self.tid, num), 'Remember'))

    def new_exercise(self, num = 10):
        return list(self._build_dict(VocabData.new_word(self.uid, self.tid, num), 'Remember'))

