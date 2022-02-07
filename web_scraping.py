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

# return job titles
def job_title(soup, page):
    # find all tags with job titles
    parent = soup.find("div", class_ = "mosaic-zone", id  = "mosaic-zone-jobcards")
    titles = parent.findChildren("h2", class_ = ["jobTitle", "jobTitle jobTitle-newJob"])

    # get the text from each job title tag
    for i in range(len(titles)):
        titles[i] = "page " + str(page),i, " " + titles[i].text
    
    return titles

# return company names
def company_names(soup,page):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    names = parent.findChildren("span", class_=["companyName"])

    for i in range(len(names)):
        names[i] = "page " + str(page),i, " " + names[i].text
        
    return names

# return company locations
def company_locations(soup,page):
    # find the Html tag
    # with find()
    # and convert into string
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    locations = parent.findChildren("div", class_="companyLocation")

    for i in range(len(locations)):
        locations[i] = "page " + str(page), i, locations[i].text
        
    return locations

# return company urls  
def company_urls(soup,page):
    parent = soup.find("div", class_="mosaic-zone", id="mosaic-zone-jobcards")
    tags = parent.findChildren("a", href = True, id = True)
    
    for link in tags:
        urls.append("https://ca.indeed.com" + link["href"])

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
    urls = []
    
    while True:
        # change 'start' every iteration to go to next page
        url = "https://ca.indeed.com/jobs?q=" + job + "&l=" + location + "&start=" + str(page)       
        # get html string 
        soup = html_code(url)

        # get information on jobs and companies
        jobtitles.append(job_title(soup, page))
        names_company.append(company_names(soup,page))
        locations_company.append(company_locations(soup,page))
        urls.append(company_urls(soup,page))
        
        page = page + 10
        # get info from the first 5 pages
        if page == 50:
            break  
        
    print(jobtitles)
    print("\n" * 2)
    print(names_company)
    print("\n" * 2)
    print(locations_company)
    print("\n" * 2)
    print(urls)
