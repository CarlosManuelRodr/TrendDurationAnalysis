import pandas as pd
import time
from datetime import datetime

try:
    from requests_html import HTMLSession
except Exception:
    pass


# Set-up user agent rotator
try:
    from random_user_agent.user_agent import UserAgent
    from random_user_agent.params import SoftwareName, OperatingSystem

    software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value]
    operating_systems = [OperatingSystem.LINUX.value, OperatingSystem.WINDOWS.value, OperatingSystem.MAC.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
except ImportError:
    print("""Warning - User agent rotator is not available.

             If needed, install using: 
             pip install random_user_agent""")
    UserAgent = None
    SoftwareName = None
    OperatingSystem = None
    user_agent_rotator = None

def print_log(log):
    timeStamp = "[Options module " + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + "] "
    print(timeStamp + log)

def build_options_url(ticker, date = None):
    
    """Constructs the URL pointing to options chain"""
       
    url = "https://finance.yahoo.com/quote/" + ticker + "/options?p=" + ticker

    if date is not None:
        url = url + "&date=" + str(int(pd.Timestamp(date).timestamp()))

    if user_agent_rotator is not None:
        headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
    else:
        headers = {}

    return url, headers

def get_options_chain(ticker, date = None, safemode = False):
    
    """Extracts call / put option tables for input ticker and expiration date.  If
       no date is input, the default result will be the earliest expiring
       option chain from the current date.
    
       @param: ticker
       @param: date"""

    trialsLeft = 5
    validRequest = False
    session = HTMLSession()

    while not validRequest and trialsLeft != 0:
        try:
            site, headers = build_options_url(ticker, date)
            resp = session.get(site, headers=headers, timeout=(10.0, 10.0))
            html = resp.html.raw_html.decode()
            tables = pd.read_html(html)
            validRequest = True
        except:
            if not safemode:
                print_log("Failed to fetch option chain. Trials left: " + str(trialsLeft))
                trialsLeft -= 1
            else:
                print_log("Failed to fetch option chain. Trying again in 5 seconds.")
            time.sleep(5)

    session.close()
    
    if validRequest:
        if trialsLeft != 5:
            print_log("Succeeded at trial " + str(trialsLeft))

        calls = tables[0].copy()
        puts = tables[1].copy()
        return {"calls": calls, "puts":puts}
    else:
        print_log("Could not fetch option chain. Skipping")
        return {"calls": [], "puts": []}

def get_calls(ticker, date = None):

    """Extracts call option table for input ticker and expiration date
    
       @param: ticker
       @param: date"""
       
    options_chain = get_options_chain(ticker, date)
    
    return options_chain["calls"]
    
    

def get_puts(ticker, date = None):

    """Extracts put option table for input ticker and expiration date
    
       @param: ticker
       @param: date"""
    
    options_chain = get_options_chain(ticker, date)
    
    return options_chain["puts"]

    
def get_expiration_dates(ticker, safemode = False):

    """Scrapes the expiration dates from each option chain for input ticker
    
       @param: ticker"""

    validRequest = False
    session = HTMLSession()
    trialsLeft = 5

    while not validRequest and trialsLeft != 0:
        site, headers = build_options_url(ticker)
        resp = session.get(site, headers=headers, timeout=(10.0, 10.0))
        html = resp.html.raw_html.decode()
        splits = html.split("</option>")
        if len(splits) > 1:
            validRequest = True
        else:
            if not safemode:
                print_log("Failed to fetch expiration dates. Trials left: " + str(trialsLeft))
                trialsLeft -= 1
            else:
                print_log("Failed to fetch expiration dates. Trying again in 5 seconds")
            time.sleep(5)

    session.close()

    if validRequest:
        if trialsLeft != 5:
            print_log("Succeeded at trial " + str(trialsLeft))

        print_log("Fetched " + str(len(splits) - 1) + " expiration dates")
        dates = [elt[elt.rfind(">"):].strip(">") for elt in splits]
        dates = [elt for elt in dates if elt != '']
        return dates
    else:
        print_log("Could not fetch expiration dates. Skipping")
        return []