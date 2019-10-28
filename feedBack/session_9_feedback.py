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
    
    # Answer
    # answer = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

    solution = solution.strip()
    resultList = []
    solved = True
    
    test_pass =[
        " 192.168.10.10 ",
        " 0.0.0.0 ",
        " 255.255.255.255 ",
        " 0.255.49.37 ",
        "(192.168.10.10)"
    ]
    test_not_pass = [
        " 192.18.1 ",
        " 256.1.1.1 ",
        " 192.168.1.256 ",
        " a192.168.10.10 ",
        " 1192.168.10.10 ",
        " 192.168.1.1a ",
        " 192.168.1.1111 "
    ]
    
    def check_test_pass(test_case, expected):
        correct = True
        answer = None
        result = re.search(solution, test_case)
        
        if result != None:
            answer = result.group(0)
            if answer == expected:
                correct = True
            else:
                correct = False
        else:
            correct = False
        
        resultDict_pass = {
            'case_objective': "Test Case: " + test_case + "\nMatch",
            'expected': expected,
            'received': str(answer),
            'correct': correct
        }
        return resultDict_pass
        
    def check_test_not_pass(test_case):
        correct = True
        answer = None
        result = re.search(solution, test_case)
        
        if result != None:
            correct = False
            answer = result.groups()
        
        resultDict_pass = {
            'case_objective': "Test Case: " + test_case + "\nSkip",
            'expected': "None",
            'received': str(answer),
            'correct': correct
        }
        return resultDict_pass
        
    resultDict_pass_1 = check_test_pass(test_pass[0], "192.168.10.10")
    resultList.append(resultDict_pass_1)
    if resultDict_pass_1['correct'] == False:
        solved = False
    resultDict_pass_2 = check_test_pass(test_pass[1], "0.0.0.0")
    resultList.append(resultDict_pass_2)
    if resultDict_pass_2['correct'] == False:
        solved = False
    resultDict_pass_3 = check_test_pass(test_pass[2], "255.255.255.255")
    resultList.append(resultDict_pass_3)
    if resultDict_pass_3['correct'] == False:
        solved = False
    resultDict_pass_4 = check_test_pass(test_pass[3], "0.255.49.37")
    resultList.append(resultDict_pass_4)
    if resultDict_pass_4['correct'] == False:
        solved = False
    resultDict_pass_5 = check_test_pass(test_pass[4], "192.168.10.10")
    resultList.append(resultDict_pass_5)
    if resultDict_pass_5['correct'] == False:
        solved = False
    
    for i in test_not_pass:
        resultDict_not_pass = check_test_not_pass(i)
        resultList.append(resultDict_not_pass.copy())
        if resultDict_not_pass['correct'] == False:
            solved = False

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
    overallResults = """<span class="md-subheading">All tests passed: {0}</span><br/>""".format(
        str(jsonResponseData.get("solved")))
    resultContent = jsonResponseData.get('results')

    if resultContent:
        for i in range(len(resultContent)):
            expectedText = resultContent[i]["expected"]
            receivedText = resultContent[i]["received"]
            correct = resultContent[i]["correct"]
            objective = resultContent[i]["case_objective"]
            if correct:
                textResults = textResults + "\nHurray! You have passed this test case {}.\n".format(expectedText)
                textBackgroundColor = "#b2d8b2"
            else:
                if expectedText == 'skip':
                    textResults = textResults + "\nYou should skip this case: {}".format(expectedText)
                textResults = textResults + "\nThe test case eludes your code so far but try again! You should match {} but received {}.\n".format(
                    expectedText, receivedText)
                textBackgroundColor = "#ff9999"
            tableContents = tableContents + """
                    <tr bgcolor={4}>
                        <td>{0}</td>
                        <td>{1}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                    </tr>
                    """.format(objective, expectedText, receivedText, str(correct), textBackgroundColor)
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
                            <span class="md-subheading tableTitle">Tests</span>
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
                    br {{
                        display:block;
                        content:"";
                        margin:1rem
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
