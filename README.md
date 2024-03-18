# Crawler
A Program that crawls on web starting from a given web page and looking for keywords through other internal links that are found.

## Requirements
Langauge Used = Python3<br />
Modules/Packages used:
* requests
* pickle
* bs4
* datetime
* optparse
* colorama
* time
<!-- -->
Install the dependencies:
```bash
pip install -r requirements.txt
```
## Input
 * '-u', "--url" : URL to start Crawling from
 * '-t', "--in-text" : Words to find in text (seperated by ',')
 * '-s', "--session-id" : Session ID (Cookie) for the Request Header (Optional)
 * '-w', "--write" : Name of the File for the data to be dumped (default=current data and time)
 * '-e', "--external" : Crawl on External URLs (True/False, default=False)
 * '-T', "--timeout" : Request Timeout
## Output
It will stop when it has crawled all the internal links of the given URL or if the user presses CTRL+C.<br />
It then display Information about total URLs extracted, Internal URLs extracted and external URLs extracted.<br />
And finally gives a list or URLs in which the keywords we've interested in were found.
