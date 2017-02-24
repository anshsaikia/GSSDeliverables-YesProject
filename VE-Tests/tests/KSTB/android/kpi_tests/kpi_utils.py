__author__ = 'oceane'


def kpi_to_csv(reportName, kpiData=[]):
    """
    function: store kpiData list as csv line (separator ";") in csv file named from reportName argument
    :param reportName : test name used for report name
    :param kpiData : KPI data to be stored
    :return:
    """
    # format
    csvLine = ';'.join(kpiData) + "\n"

    # open report file (path = test execution path)
    csvReport = open(reportName + "_report.csv", mode="a")

    # write lines in file
    csvReport.write(csvLine)

    # close report file
    csvReport.close()
