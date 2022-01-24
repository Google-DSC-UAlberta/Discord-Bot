# import module
import requests
from bs4 import BeautifulSoup


# user define function
# Scrape the data
# and get in string
def getdata(url):
    r = requests.get(url)
    return r.text


# Get Html code using parse
def html_code(url):
    # pass the url
    # into getdata function
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')

    # return html code
    return (soup)


# filter job data using
# find_all function
def job_data(soup):
    # find the Html tag
    # with find()
    # and convert into string
    data_str = ""
    for item in soup.find_all("span", class_="jobtitle turnstileLink"):
        data_str = data_str + item.get_text()
    result_1 = data_str.split("\n")
    return (result_1)


# filter company_data using
# find_all function


def company_data(soup):
    # find the Html tag
    # with find()
    # and convert into string
    data_str = ""
    result = ""
    for item in soup.find_all("div", class_="sjcl"):
        data_str = data_str + item.get_text()
    result_1 = data_str.split("\n")

    res = []
    for i in range(1, len(result_1)):
        if len(result_1[i]) > 1:
            res.append(result_1[i])
    return (res)


# driver nodes/main function
if __name__ == "__main__":

    # Data for URL
    job = "software%20engineer%20intern"
    Location = "Canada&vjk="
    url = "https://ca.indeed.com/jobs?q=" + job + "&l=" + Location

    # Pass this URL into the soup
    # which will return
    # html string
    soup = html_code(url)

    # call job and company data
    # and store into it var
    job_res = job_data(soup)
    com_res = company_data(soup)

    # Traverse the both data
    temp = 0
    for i in range(1, len(job_res)):
        j = temp
        for j in range(temp, 2 + temp):
            print("Company Name and Address : " + com_res[j])

        temp = j
        print("Job : " + job_res[i])
        print("-----------------------------")
