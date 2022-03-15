# import module
import requests
from bs4 import BeautifulSoup
import datetime

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

# get job title
def job_title(soup, page):
    # find all tags with job titles
    parent = soup.find("div", class_ = "mosaic-zone", id  = "mosaic-zone-jobcards")
    children = parent.findChildren("h2", class_ = ["jobTitle", "jobTitle jobTitle-newJob"])

    # get the text from each job title tag
    for i in range(len(children)):
        children[i] = str(page) + " " + children[i].text
    
    # return list of all job titles in a page
    return children


# filter company_data using
# find_all function


def company_data(soup,page):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    children = parent.findChildren("div", class_=["company_location", "company_Info"])

    # get the text from each job title tag
    for i in range(len(children)):
        children[i] = str(page) + " " + children[i].text


    return children


def date_data(soup):
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    children = parent.findChildren("span", class_=["date"])
    cur_date =  datetime.date.today()

    # get the text from each job title tag
    for i in range(len(children)):
        if "PostedToday" in children[i].text:
            children[i] = "0"
        elif "PostedJust posted" in children[i].text:
            children[i] = "0"
        elif "EmployerActive " in children[i].text:
            children[i] = str(children[i].text[15]) + str(children[i].text[16])
        else:
            children[i] = str(children[i].text[6]) + str(children[i].text[7])
        subtract_time = datetime.timedelta(days = int(children[i]))
        children[i] = (cur_date - subtract_time).strftime("%Y %m %d")
    #     print(children[i])
    #     for j in range(len(children[i])):
    #         if children[i][j].isdigit() == True:
    #             children[i] = str(children[i][j]) + str(children[i][j])
    # for i in range(len(children)):
    #     children[i] =" " + children[i].text

    return children

# driver nodes/main function
if __name__ == "__main__":

    # Data for URL
    job = "software%20developer"
    location = "edmonton"
    page = 0    


    jobs_list = []
    company_list = []
    date_list = []
    while True:
        # change 'start' every iteration to go to next page
        url = "https://ca.indeed.com/jobs?q=" + job + "&l=" + location + "&start=" + str(page)
        # get html string 
        soup = html_code(url)
        # append list of jobs per page to jobs_list
        jobs_list.append(job_title(soup, page))
        company_list.append(company_data(soup,page))
        date_list.append(date_data(soup))
        page = page + 10


        # get info from the first 5 pages
        if page == 50:
            break
    remove_char = ["P","o","s","t","e","d"]
    # print(jobs_list)
    # print(company_list)
    print(date_list)

    # call job and company data
    # and store into it var

#    com_res = company_data(soup)

    # Traverse the both data
    # temp = 0
    # for i in range(1, len(job_res)):
    #     j = temp
    #     for j in range(temp, 2 + temp):
    #         print("Company Name and Address : " + com_res[j])

    #     temp = j
    #     print("Job : " + job_res[i])
    #     print("-----------------------------")
