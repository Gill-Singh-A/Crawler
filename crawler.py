#!/usr/bin/env python3

from sys import argv
import requests
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

def get_time():
	return strftime("%H:%M:%S", localtime())
def display(status, data):
	print(f"{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {get_time()}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}")

def get_arguments(*args):
	parser = OptionParser()
	for arg in args:
		parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
	return parser.parse_args()[0]

internal_urls, external_urls, interested_url = [], [], []
total_visited = 0
done = []

def is_valid_url(url):
	parsed = urlparse(url)
	return bool(parsed.netloc) and bool(parsed.scheme)
def get_all_urls(url):
	domain_name = urlparse(url).netloc
	response = requests.get(url)
	soup = BeautifulSoup(response.content, "html.parser")
	for a_tag in soup.findAll("a"):
		href = a_tag.attrs.get("href")
		if href == "" or href is None:
			continue
		href = urljoin(url, href)
		parsed_href = urlparse(href)
		href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
		if not is_valid_url(href):
			continue
		if href in internal_urls:
			continue
		if domain_name not in href:
			if href not in external_urls:
				display(':', f"External Link => {Back.MAGENTA}{href}{Back.RESET}")
				external_urls.append(href)
			continue
		display('+', f"Internal Link => {Back.MAGENTA}{href}{Back.RESET}")
		internal_urls.append(href)
	return response.text
def crawl(url, interests):
	global total_visited
	total_visited += 1
	display('*', f"Crawling => {Back.MAGENTA}{url}{Back.RESET}")
	try:
		i = 1
		while True:
			response = get_all_urls(url)
			done.append(url)
			for interest in interests:
				if interest not in response and interest.upper() not in response and interest.lower() not in response:
					break
			else:
				interested_url.append(url)
				display('-', f"Interested URL => {Back.MAGENTA}{url}{Back.RESET}")
			if i < len(internal_urls)-1:
				while internal_urls[i] in done:
					i += 1
				url = internal_urls[i]
			else:
				break
	except KeyboardInterrupt:
		return len(interested_url) + len(external_urls)

if __name__ == "__main__":
	print(f"\nTotal URLs Extracted = {crawl(argv[1], argv[2:])}")
	print(f"Internal URLs = {len(internal_urls)}")
	print(f"External URLs = {len(external_urls)}")
	final = '\n'.join(interested_url)
	print(f"\n{Fore.GREEN}Interested URLs = {len(interested_url)}\n{Fore.CYAN}{Style.BRIGHT}{final}{Style.RESET_ALL}")