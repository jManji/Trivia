# -*- coding: utf-8 -*-
"""QuestionGenerator"""

import requests
import unirest
import tw2.core

from HTMLParser import HTMLParser
from email.generator import DecodedGenerator

class QuestionGenerator(object):
    
    #resources = [tw2.core.CSSLink(link='/css/trivia.css')]
    html_parser = HTMLParser()
    
    def get_question(self):

        #response = requests.get('https://pareshchouhan-trivia-v1.p.mashape.com/v1/getAllQuizQuestions')
        response = unirest.get("https://pareshchouhan-trivia-v1.p.mashape.com/v1/getRandomQuestion",
          headers={
            "X-Mashape-Key": "KZTaiIVbc4mshoHVdYYADSY0Edzvp1C0iH0jsnlvsa5HggKV6u",
            "Accept": "application/json"
          }
        )
        
        print '******* RESPONSE: ', self.html_parser.unescape(response.body['q_text'])

        return {'id': response.body['id'],
                'question': self.html_parser.unescape(response.body['q_text']),
                'option_1': self.html_parser.unescape(response.body)['q_options_1'],
                'option_2': self.html_parser.unescape(response.body)['q_options_2'],
                'option_3': self.html_parser.unescape(response.body)['q_options_3'],
                'option_4': self.html_parser.unescape(response.body)['q_options_4'],
                'correct_option': response.body['q_correct_option']
                }