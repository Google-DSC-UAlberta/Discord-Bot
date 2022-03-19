# import module
import requests
from bs4 import BeautifulSoup
import pandas as pd
from Database import Database
from urllib.parse import quote

db = Database()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}

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
def job_title(soup):
    # find all tags with job titles
    parent = soup.find("div", class_ = "mosaic-zone", id  = "mosaic-zone-jobcards")
    titles = parent.findChildren("h2", class_ = ["jobTitle", "jobTitle jobTitle-newJob"])

    # get the text from each job title tag
    for i in range(len(titles)):
        title = titles[i].text
        if title[0:3] != 'new':
            titles[i] = title
        else:
            titles[i] = title[3:]
    
    return titles

# return company names from indeed
def company_names(soup):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    names = parent.findChildren("span", class_=["companyName"])

    for i in range(len(names)):
        names[i] = names[i].text
        
    return names

# return company locations from indeed
def company_locations(soup):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    locations = parent.findChildren("div", class_="companyLocation")

    for i in range(len(locations)):
        locations[i] = locations[i].text
        
    return locations

# return company urls from indeed
def company_urls(soup):
    urls = []
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    tags = parent.findChildren("a", href = True, id = True)
    
    for link in tags:
        urls.append("https://ca.indeed.com" + link["href"])

    return urls

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
                jobtitles += job_title(soup)
                names_company += company_names(soup)
                locations_company += company_locations(soup)
                job_urls += company_urls(soup)
                post_dates += date_data(soup, page)
            
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
        jobtitles += job_title(soup)
        names_company += company_names(soup)
        locations_company += company_locations(soup)
        job_urls += company_urls(soup)
        post_dates += date_data(soup, page)
        
        page = page + 10
        # get info from the first 5 pages
        if page == 50:
            break  
    
    # LINKEDIN JOBS
    url = "https://www.linkedin.com/jobs/search?keywords=" + job + "&location=" + location
    soup = html_code(url)

    # jobtitles += job_title_linkedin(soup)
    # names_company += company_names_linkedin(soup)
    # locations_company += company_locations_linkedin(soup)
    # job_urls += company_urls_linkedin(soup)
    # post_dates += post_dates_linkedin(soup)

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