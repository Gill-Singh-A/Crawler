#!/usr/bin/env python3

import requests, pickle
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

internal_urls, external_urls, all_urls, interested_url = [], [], [], []
total_visited = 0
done = []
crawl_external = False

def is_valid_url(url):
	parsed = urlparse(url)
	return bool(parsed.netloc) and bool(parsed.scheme)
def get_all_urls(url):
	domain_name = urlparse(url).netloc
	try:
		response = requests.get(url, headers=headers)
	except KeyboardInterrupt:
		display(' ', f"Keyboard Interrupt Detected...Quiting!", start='\n')
		return -2
	except:
		display(':', f"Error while Crawling URL {Back.MAGENTA}{url}{Back.RESET}")
		return -1
	try:
		soup = BeautifulSoup(response.content, "html.parser")
	except:
		display(' ', f"Error while Parsing {Back.MAGENTA}{url}{Back.RESET}")
		return -1
	for a_tag in soup.findAll("a"):
		href = a_tag.attrs.get("href")
		if href == "" or href is None:
			continue
		href = urljoin(url, href)
		parsed_href = urlparse(href)
		href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
		if parsed_href.query != '':
			href += f"?{parsed_href.query}"
		if not is_valid_url(href):
			continue
		if href in internal_urls:
			continue
		if domain_name not in href:
			if href not in external_urls:
				display(':', f"External Link => {Back.MAGENTA}{href}{Back.RESET}")
				external_urls.append(href)
				all_urls.append(href)
			continue
		display('+', f"Internal Link => {Back.MAGENTA}{href}{Back.RESET}")
		internal_urls.append(href)
		all_urls.append(href)
	return response.text
def crawl(url, interests, external):
	global total_visited
	total_visited += 1
	try:
		i = 1
		while True:
			display('*', f"Crawling => {Back.MAGENTA}{url}{Back.RESET}")
			response = get_all_urls(url)
			done.append(url)
			if response == -2:
				return len(internal_urls) + len(external_urls)
			if response != -1:
				for interest in interests:
					if interest not in response and interest.upper() not in response and interest.lower() not in response:
						break
				else:
					interested_url.append(url)
					display('-', f"Interested URL => {Back.MAGENTA}{url}{Back.RESET}")
			if external == False:
				if i < len(internal_urls)-1:
					while internal_urls[i] in done and i < len(internal_urls)-1:
						i += 1
					url = internal_urls[i]
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
		return len(internal_urls) + len(external_urls)
	return len(internal_urls) + len(external_urls)

if __name__ == "__main__":
	data = get_arguments(('-u', "--url", "url", "URL to start Crawling from"),
                         ('-t', "--in-text", "intext", "Words to find in text (seperated by ',')"),
                         ('-s', "--session-id", "session_id", "Session ID (Cookie) for the Request Header (Optional)"),
                         ('-w', "--write", "write", "Name of the File for the data to be dumped (default=current data and time)"),
						 ('-e', "--external", "external", f"Crawl on External URLs (True/False, default={crawl_external})"))
	if not data.url:
		display('-', "Please specify a URL!")
		exit(0)
	if not data.intext:
		display('-', "Please specify Words to find")
		exit(0)
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
	crawl(data.url, data.intext, data.external)
	print(f"Internal URLs = {len(internal_urls)}")
	print(f"External URLs = {len(external_urls)}")
	print(f"\nTotal URLs Extracted = {len(internal_urls) + len(external_urls)}")
	final = '\n'.join(interested_url)
	print(f"\n{Fore.GREEN}Interested URLs = {len(interested_url)}\n{Fore.CYAN}{Style.BRIGHT}{final}{Style.RESET_ALL}")
	display(':', f"Dumping Data to file {Back.MAGENTA}{data.write}{Back.RESET}", start='\n')
	with open(f"{data.write}", 'wb') as file:
		pickle.dump([internal_urls, external_urls, interested_url, data.intext], file)
	display('+', f"Dumped Data to file {Back.MAGENTA}{data.write}{Back.RESET}")
