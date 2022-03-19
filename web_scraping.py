# import module
import requests
from bs4 import BeautifulSoup
import pandas as pd
from Database import Database
from urllib.parse import quote
import datetime

db = Database()

headers = {
    'cache-control': 'max-age=0',
    'rtt': '300',
    'downlink': '1.35',
    'ect': '3g',
    'sec-ch-ua': '"Google Chrome"; v="83"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
}

print("headers: ", headers)

# user define function
# Scrape the data
# and get in string
def getdata(url):
    r = requests.get(url, headers=headers)
    return r.text

# Get Html code using parse
def html_code(url):
    # pass the url
    # into getdata function
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')

    # return html code
    return (soup)

# return job titles from indeed
def job_title_indeed(soup):
    # find all tags with job titles
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    titles = parent.findChildren("h2", class_=["jobTitle", "jobTitle jobTitle-newJob"])

    # get the text from each job title tag
    for i in range(len(titles)):
        titles[i] = titles[i].text

    return titles


# return company names from indeed
def company_names_indeed(soup):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    names = parent.findChildren("span", class_=["companyName"])

    for i in range(len(names)):
        names[i] = names[i].text

    return names


# return company locations from indeed
def company_locations_indeed(soup):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    locations = parent.findChildren("div", class_=["companyLocation"])

    for i in range(len(locations)):
        locations[i] = locations[i].text

    return locations


# return company urls from indeed
def company_urls_indeed(soup):
    urls = []
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    tags = parent.findChildren("a", href=True, id=True)

    for link in tags:
        urls.append("https://ca.indeed.com" + link["href"])

    return urls


# return dates of job postings for indeed
def date_data_indeed(soup):
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    children = parent.findChildren("span", class_=["date"])
    cur_date = datetime.date.today()

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
        subtract_time = datetime.timedelta(days=int(children[i]))
        children[i] = (cur_date - subtract_time).strftime("%Y %m %d")

    return children

# return job titles from linkedin
def job_title_linkedin(soup):
    parent = soup.find("ul", class_ = "jobs-search__results-list")
    titles = parent.findChildren("h3", class_= "base-search-card__title")

    # get the text from each job title tag
    for i in range(len(titles)):
        titles[i] = titles[i].text.strip()
    
    return titles

# return company names from linkedin
def company_names_linkedin(soup):
    parent = soup.find("ul", class_ = "jobs-search__results-list")
    names = parent.findChildren("h4", class_ = "base-search-card__subtitle")

    for i in range(len(names)):
        names[i] = names[i].text.strip()

    return names

# return company locations from linkedin
def company_locations_linkedin(soup):
    parent = soup.find("ul", class_ = "jobs-search__results-list")
    locations = parent.findChildren("span", class_ = "job-search-card__location")

    for i in range(len(locations)):
        locations[i] = locations[i].text.strip()

    return locations
    
# return company urls from linkedin
def company_urls_linkedin(soup):
    urls = []
    parent = soup.find("ul", class_ = "jobs-search__results-list")
    tags = parent.findChildren("a", attrs={"data-tracking-control-name":"public_jobs_jserp-result_search-card"}, href = True)

    for link in tags:
        urls.append(link["href"])
    
    return urls

def post_dates_linkedin(soup):
    parent = soup.find("ul", class_ = "jobs-search__results-list")
    tags = parent.findChildren("time", class_ = "job-search-card__listdate")

    dates = []
    for date in tags:
        dates.append(date["datetime"])

    return dates
    
def date_data(soup, page):
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    children = parent.findChildren("span", class_=["date"])

    # get the text from each job title tag
    for i in range(len(children)):
        children[i] = str(page) + " " + children[i].text

    return children

def fetch_new_jobs(job_keywords, locations):
    """
    Fetch jobs in locations with job_keywords 
    Args:
        A list of job keywords and a list of locations
    """

    # Replace whitespaces with '%20' in job_keywords and locations 
    job_keywords = list(map(quote, job_keywords))
    locations = list(map(quote, locations))

    jobtitles = []
    names_company = []
    locations_company = []
    job_urls = []
    post_dates = []

    for location in locations:
        for job in job_keywords:
            
            # INDEED JOBS
            for page in range(0, 50, 10):
                # change 'start' every iteration to go to next page
                url = "https://ca.indeed.com/jobs?q=" + job + "&l=" + location + "&start=" + str(page)       
                # get html string 
                soup = html_code(url)

                # get information on jobs and companies
                jobtitles += job_title_indeed(soup)
                names_company += company_names_indeed(soup)
                locations_company += company_locations_indeed(soup)
                job_urls += company_urls_indeed(soup)
                post_dates += date_data_indeed(soup)
            
            # LINKEDIN JOBS
            url = "https://www.linkedin.com/jobs/search?keywords=" + job + "&location=" + location
            soup = html_code(url)

            jobtitles += job_title_linkedin(soup)
            names_company += company_names_linkedin(soup)
            locations_company += company_locations_linkedin(soup)
            job_urls += company_urls_linkedin(soup)
            post_dates += post_dates_linkedin(soup)

            #print(post_dates)
            
            # creating a dataframe with all the information 
            df = pd.DataFrame()
            df['Title'] = jobtitles
            df['Company'] = names_company
            df['Location'] = locations_company
            df['URL'] = job_urls
            df['Date'] = pd.Series(post_dates)

    print(df)

    for index, row in df.iterrows():
        db.add_job(row['Title'], row['Company'], row['Location'], row['URL'], row['Date'])

# driver nodes/main function
if __name__ == "__main__":

    # Data for URL
    job = "software%20developer"
    location = "edmonton"
    page = 0    

    jobtitles = []
    names_company = []
    locations_company = []
    job_urls = []
    post_dates = []
    
    # INDEED JOBS
    while True:
        # change 'start' every iteration to go to next page
        url = "https://ca.indeed.com/jobs?q=" + job + "&l=" + location + "&start=" + str(page)       
        # get html string 
        soup = html_code(url)

        # get information on jobs and companies
        jobtitles += job_title_indeed(soup)
        names_company += company_names_indeed(soup)
        locations_company += company_locations_indeed(soup)
        job_urls += company_urls_indeed(soup)
        post_dates += date_data_indeed(soup)
        
        page = page + 10
        # get info from the first 5 pages
        if page == 50:
            break  
    
    # LINKEDIN JOBS
    url = "https://www.linkedin.com/jobs/search?keywords=" + job + "&location=" + location
    soup = html_code(url)

    jobtitles += job_title_linkedin(soup)
    names_company += company_names_linkedin(soup)
    locations_company += company_locations_linkedin(soup)
    job_urls += company_urls_linkedin(soup)
    post_dates += post_dates_linkedin(soup)

    #print(post_dates)
    
    # creating a dataframe with all the information 
    df = pd.DataFrame()
    df['Title'] = jobtitles
    df['Company'] = names_company
    df['Location'] = locations_company
    df['URL'] = job_urls
    df['Date'] = pd.Series(post_dates)

    print(df)

    for index, row in df.iterrows():
        db.add_job(row['Title'], row['Company'], row['Location'], row['URL'], row['Date'])