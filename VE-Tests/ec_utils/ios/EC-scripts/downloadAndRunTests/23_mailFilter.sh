#!/usr/bin/env bash
#!/usr/bin/env python
import os
try:
    import xmltodict
except ImportError:
    # try to install xmltodict on machine
    os.system('pip install xmltodict --user')
    import xmltodict
os.system('ectool getJobStepDetails "$(ectool getProperty "/myJob/jobSteps/jobStepId"")" > job_step.xml')

with open('job_step.xml') as f:
    data = xmltodict.parse(f)

def get_projects_test(data):
    return [(project['stepName'], get_tests(project['calledProcedure']['jobStep']))
            for project in sorted(data, key=lambda t: t['stepName'])
            if 'calledProcedure' in project and project['stepName'] != "set_job_parameters"]

def discover_step(test, step):
    """
    This function discovers the Run_Test_Script step
    Return: status of the step (success, error, skip)
            description of the step:
            - in case of error - pytest statistics, not including 'xfail' and 'xpass'
            - in case of skip - description of why this step was skipped
    """
    status = None
    description = None

    if step['outcome'] == 'error':
        if 'errorCode' in step:
            error_code = step['errorCode']
            print("    errorCode: {}".format(error_code))
            if error_code == 'CANCELED':
                status = 'skip'
                if 'errorMessage' in test:
                    description = test['errorMessage'][22:]#Cut 'Step error [Aborted]: '
            elif error_code == 'TIMEOUT':
                status = 'error'
                description = 'timeout'
            elif error_code == 'ABORTED':
                status = 'skip'
                if 'errorMessage' in step:
                    description = step['errorMessage'][22:]#Cut 'Step error [Aborted]: '
    try:
        properties = step['propertySheet']['property']
        for property in properties:
            try:
                if property['propertyName'] == 'summary':
                    description = property['value'].replace('\n', ' ')
                    #description = '   '.join([':'.join(reversed(param_list))
                    #        for param_list in [param_str.split()
                    #            for param_str in property['value'].split('\n')]
                            #if param_list[1] not in ['xfail', 'xpass']])
                    #        if param_list[1]
                    break
            except:
                pass
    except:
        print("    No propertySheet found for step")

    return status, description

def discover_test(test):
    print("Processing test '{}'".format(test['stepName']))
    test_1down = test['calledProcedure']['jobStep']
    for step in test_1down:
        step_name = ''
        try:
            step_name = step['stepName']
            print("Processing step '{}'".format(step_name))
        except Exception, e:
            print("##############################################")
            print("WARNING: Failed to parse step.")
            print(e.message)
            print("step content: \n{}".format(step))
            print("##############################################")
        if step_name == 'Run_Test_Script' or step_name == 'Run_Script':
            outcome, description = discover_step(test, step)
            #if outcome is not None:
            #    return outcome, description
            return outcome, description

        if step_name == 'Run_Post_Script':
            outcome, description = discover_step(test, step)
            if outcome is not None:
                return outcome, description

    return None, None

job_step_url = r'https://spvss-ec.cisco.com/commander/link/jobStepDetails/jobSteps/{}?jobId={}'

def get_test(test):
    sub_test = test['calledProcedure']['jobStep']
    if 'calledProcedure' in sub_test:
        outcome, description = discover_test(sub_test)
        url = job_step_url.format(sub_test['jobStepId'], test['jobId'])
    else:
        outcome, description = discover_test(test)
        url = job_step_url.format(test['jobStepId'], test['jobId'])

    if outcome is None:
        outcome = test['outcome']
    if description is None:
        description = outcome

    return test['stepName'], outcome, description, url


def get_tests(data):
    if ('stepName' not in data):
        return list()
    stepName = data['stepName'];
    subproject = data['subproject'];
    subprocedure = data['subprocedure'];
    print("Getting data for: {} ({}:{})".format(stepName, subproject, subprocedure))
    if ('calledProcedure' not in data or 'jobStep' not in data['calledProcedure']):
        print("    WARNING: Could not find any called procedure for this step.")
        tests_data = list()
    else:
        tests_data = data['calledProcedure']['jobStep']

    if not isinstance(tests_data, list):
        # handle one test for scrum team
        tests_data = [tests_data]

    return [get_test(test)
            for test in sorted(tests_data, key=lambda t: t['stepName'])
            if test['outcome'] != 'skipped' and 'calledProcedure' in test ]

def print_report(summary):
    html = ''
    html += '''
<!doctype html>
<html>
<head><title>Summary: $(ectool getProperty "jobId")</title>
<style>
a:link    {color:#000000; background-color:transparent; text-decoration:none}
a:visited {color:#000000; background-color:transparent; text-decoration:none}
a:hover   {color:#ff0000; background-color:transparent; text-decoration:underline}
a:active  {color:#ff0000; background-color:transparent; text-decoration:underline}
table, th, td {border: 1px solid black; border-collapse: collapse; font-family: "Lucida Console", Monaco, monospace;}
tr {background: #b8d1f3;}
tr:nth-child(odd) {background: #b8d1f3;}
tr:nth-child(even) {background: #dae5f4;}
.skip {background: #a1a1a1;}
.error {background: #d16a51;}
.success {background: #66c266;}
</style>
</head>
<body>
<h3>EC Job Summary - job-CI_Full_E2E_Deployment_And_Regression-$(ectool getProperty "jobId")</h3>
<a style='color:#0000ff; text-decoration:underline;' href='https://spvss-ec.cisco.com/commander/link/jobDetails/jobs/$(ectool getProperty "jobId")'>job-CI_Full_E2E_Deployment_And_Regression-$(ectool getProperty "jobId]</a><br/>
<a style='color:#0000ff; text-decoration:underline;' href='http://engci-maven-master.cisco.com/artifactory/spvss-cloud-ci-yum-dev/VGW/HE_DEPLOYMENTS/$(ectool getProperty "$(ectool getProperty "/myJob/workflowProps")/he_version_tag")'>HE Snapshot version: $(ectool getProperty "$(ectool getProperty "/myJob/workflowProps]/he_version_tag]</a><br/>
<a style='color:#0000ff; text-decoration:underline;' href='https://spvss-ec.cisco.com$(ectool getProperty "/myJob/report-urls/ PyTest Report - all_tests")'>Full PyTest Report</a><br/><br/>
RDK Version: $(ectool getProperty "/myJob/artifactSummary")<br/>
RDK Commit SHA1: $(ectool getProperty "/artifactVersions/$(ectool getProperty "/myJob/artifactSummary")/commit_sha1")<br/><br/>

<table style='border: 1px solid black;'>
<tr><th width="100">Scrum Team</th><th width="500">Test Name</th><th width="700">Description</th>
'''
    for scrum, tests in summary:
        if tests is None:
            html += '<tr><td>{0}</td><td colspan="2">There are no tests for {0}</td></tr>\n'.format(scrum)
            html += '<tr><td style="height: 0.2em;" colspan="3"></td></tr>'
            continue

        try:
            scrum_pytest_url = 'https://spvss-ec.cisco.com'
            resp = os.popen("ectool getProperty '/myJob/report-urls/ PyTest Report - {}'".format(scrum)).read()
            if resp == '':
                print("No pytest URL report was found for {}.".format(scrum))
                raise
            scrum_pytest_url += resp
            scrum_element = "<a href='{}'>{}</a>".format(scrum_pytest_url, scrum)
        except:
            scrum_element = scrum
            pass;

        html += '<tr><td rowspan="{}">{}</td>\n'.format(len(tests), scrum_element)
        first = True
        #    return test['stepName'], outcome, description, url
        for name, status, description, url in tests:
            if not first:
                html += '<tr>'
            first = False
            html += '<td class="{1}"><a href="{3}">{0}</a></td><td class="{1}">{2}</td></tr>\n'.format(name, status, description, url)
        html += '<tr><td style="height: 0.2em;" colspan="3"></td></tr>'
    html += '</table></body></html>\n'
    try:
        os.mkdir('artifacts')
    except OSError:
        pass
    finally:
        with open('artifacts/summary.html', 'w') as f:
            f.write(html)
        print(html)
        # os.system('ectool setProperty "/myJob/report-urls/  Job Summary" "https://spvss-ec.cisco.com/commander/jobSteps/$(ectool getProperty "/myJobStep/jobStepId")/summary.html"')
        # os.system('ectool setProperty "/myJob/regressionSummary" --value "$(cat artifacts/summary.html)"')

print_report(get_projects_test(data['response']['jobStep']['calledProcedure']['jobStep']))