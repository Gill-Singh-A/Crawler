#!/usr/bin/env python3

import requests, pickle
from multiprocessing import cpu_count, Pool, Lock
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from time import strftime, localtime, time

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE,
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36",
    "Connection": "close",
    "DNT": "1"
}

def get_time():
    return strftime("%H:%M:%S", localtime())
def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

lock = Lock()
thread_count = cpu_count()
crawl_external = False

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
def get_all_urls(thread_name, url, internal_urls, external_urls, all_urls, timeout, ignore_extensions):
    domain_name = urlparse(url).netloc
    try:
        if timeout == -1:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
    except KeyboardInterrupt:
        with lock:
            display(' ', f"{Back.BLUE}{thread_name}{Back.RESET} : Keyboard Interrupt Detected...Quiting!", start='\n')
        return internal_urls, external_urls, all_urls, -2
    except requests.Timeout:
        display('-', f"{Back.BLUE}{thread_name}{Back.RESET} : Request Timed Out while Crawling URL {Back.MAGENTA}{url}{Back.RESET}")
        return internal_urls, external_urls, all_urls, -3
    except:
        with lock:
            display(':', f"{Back.BLUE}{thread_name}{Back.RESET} : Error while Crawling URL {Back.MAGENTA}{url}{Back.RESET}")
        return internal_urls, external_urls, all_urls, -1
    try:
        soup = BeautifulSoup(response.content, "html.parser")
    except:
        with lock:
            display(' ', f"{Back.BLUE}{thread_name}{Back.RESET} : Error while Parsing {Back.MAGENTA}{url}{Back.RESET}")
        return internal_urls, external_urls, all_urls, -1
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if parsed_href.query != '':
            href += f"?{parsed_href.query}"
        if href.split('.')[-1].lower() in ignore_extensions:
            continue
        if not is_valid_url(href):
            continue
        if href in internal_urls:
            continue
        if domain_name not in href:
            if href not in external_urls:
                with lock:
                    display(':', f"{Back.BLUE}{thread_name}{Back.RESET} : External Link => {Back.MAGENTA}{href}{Back.RESET}")
                external_urls.append(href)
                all_urls.append(href)
            continue
        with lock:
            display('+', f"{Back.BLUE}{thread_name}{Back.RESET} : Internal Link => {Back.MAGENTA}{href}{Back.RESET}")
        internal_urls.append(href)
        all_urls.append(href)
    return internal_urls, external_urls, all_urls, response.text
def crawl(thread_name, urls, interests, external, timeout, ignore_extensions):
    crawl_data = {}
    try:
        for url in urls:
            start_url = url
            crawl_data[start_url] = {"internal_urls": [], "external_urls": [], "interested_urls": []}
            all_urls, done = [], []
            i = 1
            while True:
                crawl_data[start_url]["internal_urls"], crawl_data[start_url]["external_urls"], all_urls, response = get_all_urls(thread_name, url, crawl_data[start_url]["internal_urls"], crawl_data[start_url]["external_urls"], all_urls, timeout, ignore_extensions)
                with lock:
                    display('*', f"{Back.BLUE}{thread_name}{Back.RESET} : Crawling => {Back.MAGENTA}{url}{Back.RESET}")
                done.append(url)
                if response == -2:
                    return crawl_data
                if response == -3:
                    break
                if response != -1:
                    for interest in interests:
                        if interest in response or interest.upper() in response or interest.lower() in response:
                            crawl_data[start_url]["interested_urls"].append(url)
                            with lock:
                                display('-', f"{Back.BLUE}{thread_name}{Back.RESET} : Interested URL => {Back.MAGENTA}{url}{Back.RESET}")
                            break
                if external == False:
                    if i < len(crawl_data[start_url]["internal_urls"])-1:
                        while crawl_data[start_url]["internal_urls"][i] in done and i < len(crawl_data[start_url]["internal_urls"])-1:
                            i += 1
                        url = crawl_data[start_url]["internal_urls"][i]
                    else:
                        break
                else:
                    if i < len(all_urls)-1:
                        while all_urls[i] in done and i < len(all_urls)-1:
                            i += 1
                        url = all_urls[i]
                    else:
                        break
    except KeyboardInterrupt:
        display('*', f"{Back.BLUE}{thread_name}{Back.RESET} : DONE")
        return crawl_data
    display('*', f"{Back.BLUE}{thread_name}{Back.RESET} : DONE")
    return crawl_data

if __name__ == "__main__":
    data = get_arguments(('-u', "--url", "url", "URLs to start Crawling from (seperated by ',') or Path of File containing list of URLs"),
                         ('-t', "--in-text", "intext", "Words to find in text (seperated by ',')"),
                         ('-s', "--session-id", "session_id", "Session ID (Cookie) for the Request Header (Optional)"),
                         ('-w', "--write", "write", "Name of the File for the data to be dumped (default=current data and time)"),
                         ('-e', "--external", "external", f"Crawl on External URLs (True/False, default={crawl_external})"),
                         ('-T', "--timeout", "timeout", "Request Timeout"),
                         ('-i', "--ignore-extensions", "ignore_extensions", "Extensions to Ignore (seperated by ',')"))
    if not data.url:
        display('-', "Please specify a URL!")
        exit(0)
    else:
        try:
            with open(data.url, 'r') as file:
                data.url = [url for url in file.read().split('\n') if url != '']
        except FileNotFoundError:
            data.url = data.url.split(',')
        except:
            display('-', f"Error while Loading URLs from File {Back.YELLOW}{data.url}{Back.RESET}")
            exit(0)
    if not data.intext:
        data.intext = []
    else:
        data.intext = data.intext.split(',')
    if data.external == "True":
        data.external = True
        display('*', "Crawling on External URLs set to True")
    else:
        data.external = crawl_external
    if data.session_id:
        headers["Cookie"] = data.session_id
    if not data.write:
        data.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}"
    if data.timeout:
        data.timeout = float(data.timeout)
    else:
        data.timeout = -1
    if data.ignore_extensions:
        data.ignore_extensions = data.ignore_extensions.split(',')
    else:
        data.ignore_extensions = []
    total_urls = len(data.url)
    if total_urls < thread_count:
        thread_count = total_urls
    display(':', f"Starting {Back.MAGENTA}{thread_count}{Back.RESET} Crawling Threads")
    pool = Pool(thread_count)
    url_divisions = [data.url[group*total_urls//thread_count: (group+1)*total_urls//thread_count] for group in range(thread_count)]
    threads = []
    crawl_data = {}
    for index, url_division in enumerate(url_divisions):
        threads.append(pool.apply_async(crawl, (f"Thread {index+1}", url_division, data.intext, data.external, data.timeout, data.ignore_extensions)))
    for thread in threads:
        crawl_data.update(thread.get())
    pool.close()
    pool.join()
    for url, url_crawl_data in crawl_data.items():
        display('+', f"URL => {Back.MAGENTA}{url}{Back.RESET}")
        display(':', f"\tInternal URLs   = {Back.MAGENTA}{len(url_crawl_data['internal_urls'])}{Back.RESET}")
        display(':', f"\tExternal URLs   = {Back.MAGENTA}{len(url_crawl_data['external_urls'])}{Back.RESET}")
        display(':', f"\tInterested URLs = {Back.MAGENTA}{len(url_crawl_data['interested_urls'])}{Back.RESET}")
        print()
        print(f"{Fore.BLUE}")
        print('\n'.join(url_crawl_data['interested_urls']))
        print(f"{Fore.RESET}")
        print('\n')
    display(':', f"Dumping Data to file {Back.MAGENTA}{data.write}{Back.RESET}", start='\n')
    with open(f"{data.write}", 'wb') as file:
        pickle.dump(crawl_data, file)
    display('+', f"Dumped Data to file {Back.MAGENTA}{data.write}{Back.RESET}")