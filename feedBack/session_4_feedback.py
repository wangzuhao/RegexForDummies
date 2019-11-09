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
    test_cases = OrderedDict([('task is successful', 'match'),
                              ('task is unsuccessful', 'match'),
                              ('ask successfully completed', 'skip')
                              ]
                             )

    resultList = []
    solved = True
    for case in test_cases:
        objective = test_cases[case]
        match_result = re.search(solution, case)
        if match_result:
            got = match_result.group()
            if objective == 'match' and got == case:
                correct = True
            else:
                correct = solved = False
        else:
            got = 'skipped'
            if objective == 'skip':
                correct = True
            else:
                correct = solved = False

        resultDict = {'case_objective': objective, 'expected': case, 'received': got, 'correct': correct}
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
                textResults = textResults + "\nGreat! You have passed this test case {}.\n".format(expectedText)
                textBackgroundColor = "#b2d8b2"
            else:
                if expectedText == 'skip':
                    textResults = textResults + "\nYou should skip this case: {}".format(expectedText)
                textResults = textResults + "\nMaybe you should try again for this case. You should match {} but received {}.\n".format(
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

    if not jsonResponseData.get("solved", False):
        if "$" not in solution:
            textResults += "\nHint: you may try using $ at the end of a word to match a string with the word in the end"
        elif "?" not in solution and "\\b" not in solution:
            textResults += "\nHint: you may try ? and/or \\b to match both 'successful' and 'unsuccessful'."

    solvedStatusText = str(jsonResponseData.get("solved")) or "error"
    textResults = """All tests passed: {0}\n""".format(solvedStatusText) + textResults
    if not resultContent:
        textResults = "Your test is passing but something is incorrect..."

    if timeout or jsonResponseData.get("errors"):
        textResults = "There is an error happening in the backend, please check again your input"
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

