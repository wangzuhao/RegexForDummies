# This module run test cases and generate feedbacks for a session

import re
import json
import signal
import io
from collections import OrderedDict


def run_test_case_session(solution):
    """
    run test cases here
    :param solution: user submit solution
    :return: a tuple of (result, is_solved)
    """
    
    resultList = []
    solved = False
    objective = 'Keep Lyrics Only'
    expectation = "TEARS IN HEAVEN \n Would you know my name,\n If I saw you in heaven?\n Would it be the same,\n If I saw you in heaven?\n I must be strong,\n and carry on,\n 'Cause I know I don't belong,\n Here in heaven."
    
    # 检测用户提交的regex语法是否正确
    try:
        answer = re.compile(solution)
        
    except re.error:
        resultDict = {'case_objective': objective, 'expected': expectation, 'received': "Check your Regex syntax.\nDid you miss a ')' or something?", 'correct': solved}
        resultList.append(resultDict)
        
        return resultList, solved

    original = ["TEARS IN HEAVEN \n", 
                "(A         E      F#m  A/E)\n", 
                " Would you know my name,\n", 
                "(D/F#    A/E          E)\n", 
                " If I saw you in heaven?\n", 
                "(A      E       F#m A/E)\n", 
                " Would it be the same,\n", 
                "(D/F#    A/E         E)\n", 
                " If I saw you in heaven?\n", 
                "[Verse]\n", 
                "(F#m          C#/E#)\n", 
                " I must be strong,\n", 
                "(A7/E         F#7)\n", 
                " and carry on,\n", 
                "(         Bm            Bm7/E)\n", 
                " 'Cause I know I don't belong,\n", 
                "(      A        )\n", 
                " Here in heaven."]

    lyrics = ""                         

    for line in original:
        isMatched = answer.search(line)
        
        if not isMatched:
            lyrics = lyrics + line
    
    if lyrics == expectation:
        correct = solved = True
    else:
        correct = solved = False

    resultDict = {'case_objective': objective, 'expected': expectation, 'received': lyrics, 'correct': correct}
    resultList.append(resultDict)

    return resultList, solved
    
    

def generate_feedback(solution):
    """
    take in user submit solution and run test cases to generate feedback
    :param solution: user submit solution
    :return: a dict of feedback
    """
    output = io.StringIO()

    timeout = False

    # handler function that tell the signal module to execute
    # our own function when SIGALRM signal received.
    def timeout_handler(num, stack):
        print("Received SIGALRM")
        raise Exception("processTooLong")

    # register this with the SIGALRM signal
    signal.signal(signal.SIGALRM, timeout_handler)

    # signal.alarm(10) tells the OS to send a SIGALRM after 10 seconds from this point onwards.
    signal.alarm(10)

    # After setting the alarm clock we invoke the long running function.
    try:
        result, solved = run_test_case_session(solution)
        printed = output.getvalue()
        responseDict = {"solved": solved, "results": result, "printed": printed}
    except Exception as ex:
        if "processTooLong" in ex:
            timeout = True
            print("processTooLong triggered")
    # set the alarm to 0 seconds after all is done
    finally:
        signal.alarm(0)

    jsonResponseData = responseDict

    textResults = tableContents = ""
    overallResults = """<span class="md-subheading">All tests passed: {0}</span><br/>""".format(str(jsonResponseData.get("solved")))
    resultContent = jsonResponseData.get('results')

    if resultContent:
        for i in range(len(resultContent)):
            expectedText = resultContent[i]["expected"]
            receivedText = resultContent[i]["received"]
            correct = resultContent[i]["correct"]
            objective = resultContent[i]["case_objective"]
            if correct:
                textResults = textResults + "\nHurray! You have passed this test case \n{}".format(expectedText)
                textBackgroundColor = "#b2d8b2"
            else:
                if expectedText == 'skip':
                    textResults = textResults + "\nYou should skip this case: {}".format(expectedText)
                textResults = textResults + "\nThe test case eludes your code so far but try again! You should match: \n\n{} \n\nbut received:\n\n{}\n".format(expectedText, receivedText)
                textBackgroundColor = "#ff9999"
            tableContents = tableContents + """
                    <tr bgcolor={4}>
                        <td>{0}</td>
                        <td>{1}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                    </tr>
                    """.format(objective, expectedText.replace('\n', '<br />'), receivedText.replace('\n', '<br />'), str(correct), textBackgroundColor)
    solvedStatusText = str(jsonResponseData.get("solved")) or "error"
    textResults = """All tests passed: {0}\n""".format(solvedStatusText) + textResults
    if not resultContent:
        textResults = "Your test is passing but something is incorrect..."

    if timeout or jsonResponseData.get("errors"):
        textResults = "An error - probably related to code syntax - has occured. Do look through the JSON results to understand the cause."
        tableContents = """
                    <tr>
                        <td></td>
                        <td></td>
                        <td>error</td>
                        <td></td>
                    </tr>
                    """
    htmlResults = """
                <html>
                    <head>
                        <meta charset="utf-8">
                        <meta content="width=device-width,initial-scale=1,minimal-ui" name="viewport">
                    </head>
                    <body>
                        <div>
                            {0}
                            <table>
                                 <thead>
                                    <tr>
                                        <th>Objective</th>
                                        <th>Case</th>
                                        <th>Received</th>
                                        <th>Correct</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {1}
                                </tbody>
                            </table>
                        </div>
                    </body>
                    <style>
                        br {{ /*
                            display:block;
                            content:"";
                            margin:1rem; */
                            line-height:10px
                            
                        }}
                        table{{
                            text-align:center
                        }}
                        .tableTitle{{
                            text-decoration:underline
                        }}
                    </style>
                </html>
                """.format(overallResults, tableContents)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "isComplete": jsonResponseData.get("solved"),
            "jsonFeedback": jsonResponseData,
            "htmlFeedback": htmlResults,
            "textFeedback": textResults
        })
    }