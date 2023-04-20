# Crawler
A Program that crawls on web starting from a given web page and looking for keywords through other internal links that are found.

## Requirements
Langauge Used = Python3<br />
Modules/Packages used:
* sys
* requests
* bs4
* datetime
* optparse
* colorama
* time
## Input
It takes input from the command that is used to run the python program.<br />It takes 2 types of arguments:
1. URL to start crawling from
2. Keywords to search
<!-- -->
For Example:
```bash
python crawler.py url keyword_1 keyword_2 ...
```
## Output
It will stop when it has crawled all the internal links of the given URL or if the user presses CTRL+C.<br />
It then display Information about total URLs extracted, Internal URLs extracted and external URLs extracted.<br />
And finally gives a list or URLs in which the keywords we've interested in were found.