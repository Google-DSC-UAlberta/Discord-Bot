# import module
import requests
from bs4 import BeautifulSoup
import pandas as pd
from Database import Database

db = Database()

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

# return job titles from indeed
def job_title(soup, page):
    # find all tags with job titles
    parent = soup.find("div", class_ = "mosaic-zone", id  = "mosaic-zone-jobcards")
    titles = parent.findChildren("h2", class_ = ["jobTitle", "jobTitle jobTitle-newJob"])

    # get the text from each job title tag
    for i in range(len(titles)):
        titles[i] = titles[i].text
    
    return titles

# return company names from indeed
def company_names(soup,page):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    names = parent.findChildren("span", class_=["companyName"])

    for i in range(len(names)):
        names[i] = names[i].text
        
    return names

# return company locations from indeed
def company_locations(soup,page):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    locations = parent.findChildren("div", class_="companyLocation")

    for i in range(len(locations)):
        locations[i] = locations[i].text
        
    return locations

# return company urls from indeed
def company_urls(soup,page):
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
    tags = parent.findChildren("a", class_ = "base-card__full-link", href = True)

    for link in tags:
        urls.append(link["href"])
    
    return urls

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
    
    # INDEED JOBS
    while True:
        # change 'start' every iteration to go to next page
        url = "https://ca.indeed.com/jobs?q=" + job + "&l=" + location + "&start=" + str(page)       
        # get html string 
        soup = html_code(url)

        # get information on jobs and companies
        jobtitles += job_title(soup, page)
        names_company += company_names(soup,page)
        locations_company += company_locations(soup,page)
        job_urls += company_urls(soup,page)
        
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
    
    # creating a dataframe with all the information 
    df = pd.DataFrame()
    df['Title'] = jobtitles
    df['Company'] = names_company
    df['Location'] = locations_company
    df['URL'] = job_urls

    print(df)

    for index, row in df.iterrows():
        db.add_job(row['Title'], row['Company'], row['Location'], row['URL'])
