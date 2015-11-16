# -*- coding: utf-8 -*-
"""QuestionGenerator"""

import requests
import unirest
import tw2.core

class QuestionGenerator(object):
    
    #resources = [tw2.core.CSSLink(link='/css/trivia.css')]
    
    
    def get_question(self):
            #response = requests.get('https://pareshchouhan-trivia-v1.p.mashape.com/v1/getAllQuizQuestions')
            response = unirest.get("https://pareshchouhan-trivia-v1.p.mashape.com/v1/getRandomQuestion",
              headers={
                "X-Mashape-Key": "KZTaiIVbc4mshoHVdYYADSY0Edzvp1C0iH0jsnlvsa5HggKV6u",
                "Accept": "application/json"
              }
            )
            return response.body