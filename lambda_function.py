# This is the main function that defines lambda_handler
# This activity requires Python 3.7 runtime
# -*- coding: utf-8 -*-
import json
import os
from feedBack import *


def lambda_handler(event, context):
    method = event.get('httpMethod', {})

    # load the main webpage
    with open('./webContent/index.html', 'r', encoding='utf8') as f:
        indexPage = f.read()

    # load each question
    for i in range(1, 11):
        with open(os.path.join('./webContent/', 'session_{}.txt'.format(i)), 'r', encoding='utf8') as f:
            indexPage = indexPage.replace('%question_{}_content'.format(i), f.read())

    if method == 'GET':
        return {
            "statusCode": 200,
            "headers": {
                'Content-Type': 'text/html',
            },
            "body": indexPage
        }

    if method == 'POST':
        bodyContent = event.get('body', {})
        parsedBodyContent = json.loads(bodyContent)
        session_index = parsedBodyContent["sessionIndex"]["0"]

        if session_index == "10":
            test_cases = parsedBodyContent["testCase"]["0"]
            solution = parsedBodyContent["solution"]["0"]
            output = globals()['session_{}_feedback'.format(session_index)].generate_feedback(test_cases, solution)
        else:
            solution = parsedBodyContent["editable"]["0"]
            output = globals()['session_{}_feedback'.format(session_index)].generate_feedback(solution)

        return output