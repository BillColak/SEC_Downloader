import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

DEBUG = False


def make_url(base_for_url, comp):
    url = base_for_url
    for r in comp:
        url = '{}/{}'.format(url, r)
    return url


def check_ele_exists(html_soup):
    """Returns bs4 object or returns False"""
    try:
        if len(html_soup.findAll("td", {"class": "small"})) > 0:
            td = html_soup.findAll("td", {"class": "small"})
            return td
        elif html_soup.find("h1").text != None:
            print(html_soup.find("h1").text)

    except: print("No statements available, check parameters.")


def get_sec_file(parameter_dict):
    parameter_dict["CIK"] = parameter_dict["CIK"].replace(".", "-")
    base_url = r"https://www.sec.gov"
    endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"

    response = requests.get(url=endpoint, params=parameter_dict)
    if DEBUG: print(parameter_dict["CIK"], response.url)

    link_content = requests.get(response.url).content
    soup = BeautifulSoup(link_content, 'html.parser')
    td = check_ele_exists(soup)

    Acc_list = []

    if td:  # don't ask for permission, ask for forgiveness.
        for table_soup in td:
            filings = table_soup.parent.findAll("td", {"nowrap": "nowrap"})

            filing_name = filings[0].text
            filing_link = filings[1].a.get("href")
            link_list = (filing_link.split("/")[1:-1])

            if filing_name == parameter_dict['type']:
                Acc_list.append(link_list)

        filing_number = Acc_list[0]  # gets the latest 10-k
        documents_url_json = make_url(base_url, [*filing_number, "index.json"])
        content = requests.get(documents_url_json).json()

        content_url = None
        xml_summary = None

        for file in content['directory']['item']:
            if file['name'] == 'FilingSummary.xml':
                xml_summary = base_url + content['directory']['name'] + "/" + file['name']
                if DEBUG: print(parameter_dict['CIK'], ": ", xml_summary)
                content_url = requests.get(xml_summary).content

        xml_base_url = xml_summary.replace('FilingSummary.xml', '')
        soup = BeautifulSoup(content_url, 'html.parser')
        reports = soup.find('myreports')

        master_reports = []
        for report in reports.find_all('report')[:-1]:
            report_dict = dict()
            report_dict['name_short'] = report.shortname.text
            report_dict['name_long'] = report.longname.text
            report_dict['position'] = report.position.text
            report_dict['category'] = report.menucategory.text
            report_dict['reporttype'] = report.reporttype.text
            report_dict['url'] = xml_base_url + report.htmlfilename.text

            master_reports.append(report_dict)

        BS = ["balance sheet", "financial position", "financial condition", "statements of condition",
              "statement of condition"]
        IS = ["income statement", "earnings", "operations", "statement of income", "statements of income"]
        CF = ["cash flow"]
        EQ = ["equity", "statement of shareholder"]
        CI = ["comprehensive income", "comprehensive loss", "comprehensive income (loss)",
              "comprehensive operation", "comprehensive earnings"]

        statements_dict = {}

        for report_dict in master_reports:

            name_short = report_dict["name_short"].lower()
            reporttype = report_dict["reporttype"].lower()

            if reporttype == "sheet" and name_short.find("parenthetical") < 0:

                for i in BS:
                    if len(re.findall(i, name_short)) != 0:
                        if not statements_dict.get("BS"):
                            if DEBUG:
                                print(name_short, ",", i)
                                print("BS =", report_dict['url'])
                            statements_dict["BS"] = report_dict["url"]

                for i in IS:  # How do you reduces the conditions (make the matches less specific if no match) in a pythonic way.
                    if len(re.findall(i, name_short)) != 0 and len(re.findall("comprehensive", name_short)) == 0:
                        if not statements_dict.get("IS"):
                            if DEBUG:
                                print(name_short, ",", i)
                                print("IS =", report_dict['url'])
                            statements_dict["IS"] = report_dict["url"]

                    elif len(re.findall(i, name_short)) != 0:
                        if not statements_dict.get("IS"):
                            if DEBUG:
                                print(name_short, ",", i)
                                print("IS =", report_dict['url'])
                            statements_dict["IS"] = report_dict["url"]

                for i in CF:
                    if len(re.findall(i, name_short)) != 0:
                        if not statements_dict.get("CF"):
                            if DEBUG:
                                print(name_short, ",", i)
                                print("CF =", report_dict['url'])
                            statements_dict["CF"] = report_dict["url"]

                for i in EQ:
                    if len(re.findall(i, name_short)) != 0:
                        if not statements_dict.get("EQ"):
                            if DEBUG:
                                print(name_short, ",", i)
                                print("EQ =", report_dict['url'])
                            statements_dict["EQ"] = report_dict["url"]

                for i in CI:
                    if len(re.findall(i, name_short)) != 0:
                        if not statements_dict.get("CI"):
                            if DEBUG:
                                print(name_short, ",", i)
                                print("CI =", report_dict['url'])
                            statements_dict["CI"] = report_dict["url"]

        return statements_dict


def parse_sec_file(file_url):
    statement_data = dict()
    statement_data['headers'] = ["Taxonomy", "Category"]
    statement_data['data'] = []
    statement_data['periods'] = []

    resp = requests.get(file_url).content
    report_soup = BeautifulSoup(resp, 'html.parser')

    has_colspan = False
    for row in report_soup.table.find_all('tr'):
        table_header = row.find_all("th", {"class": "th"})
        for i in table_header:
            if i.attrs.get("colspan") and re.search("^[0-9]", i.text):
                has_colspan = True
                colspan = i.attrs.get("colspan")
                statement_data['periods'].append([i.text, int(colspan)])
            else:
                statement_data['periods'].append(i.text)

        for ele in table_header:
            if not ele.sup:
                ele = ele.text.strip()
                if not re.search("^[0-9]", ele):
                    statement_data['headers'].append(ele)

        row_value = row.find_all(["a", "td"], ["num", "nump", "a", "text"])  # nump for shop is not working
        row_tox = re.findall("defref_\w+.\w+", str(row.find("a")))

        if row_value:
            val = [ele.text.strip() for ele in row_value]
            if row_tox:
                val.insert(0, *row_tox)
            statement_data['data'].append(val)

    income_df = pd.DataFrame(statement_data['data'])

    income_df = income_df.replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True) \
        .replace('', 'NaN', regex=True)

    income_df.columns = statement_data["headers"]
    income_df.iloc[:, 2:] = income_df.iloc[:, 2:].astype(float, errors="ignore")

    if has_colspan:
        period_break = statement_data['periods'][0][1] + 2
        if len(statement_data['periods']) > 1:
            income_df.loc[-1, 2:period_break] = statement_data['periods'][0][0]
            income_df.loc[-1, period_break:] = statement_data['periods'][1][0]
            income_df.index = income_df.index + 1
            income_df.sort_index(inplace=True)
        else:
            income_df.loc[-1, 2:period_break] = statement_data['periods'][0][0]
            income_df.index = income_df.index + 1
            income_df.sort_index(inplace=True)
    else:
        if DEBUG:
            print("Period length not provided")

    return income_df


ticker = "AAPL"
file_type = '10-K'
date_prior = '20200710'

param_dict = {'action': 'getcompany',
              'CIK': ticker,
              'type': file_type,
              'dateb': date_prior,
              'owner': 'exclude',
              'start': '',
              'output': '',
              'count': '10'}

statements_dict = get_sec_file(param_dict)
with pd.ExcelWriter(ticker + '_' + file_type + '.xlsx') as writer:
    for k, v in statements_dict.items():
        filings_df = parse_sec_file(v)
        filings_df.to_excel(writer, sheet_name=k)
