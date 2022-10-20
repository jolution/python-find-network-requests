#!/usr/bin/python
#
# Network Requests search Python Script v0.0.2 by jolution
# Description: If you enter a sitemap (without another sitemap below it), each of the pages will be searched for non-domain accesses. Theoretically, you can see on which Wordpress subpage Google Fonts are used remotely. Attention, this is only a test script which is not intended for production use. I do not guarantee that you can find out everything with it. Use at your own risk. Alpha version.
# I am happy if you want to develop the script further.
# For more information, see:
# https://github.com/jolution/python-find-network-requests/
# run from cmd with "python networkrequests.py https://example.de/page-sitemap.xml"
import sys
import emoji
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

sitemap = ''
url = ''

# Attention: Do not enter a sitemap url which has other XML sitemaps inside. This is not programmed yet ;-)
if sys.argv[1].endswith("xml", 3):
	sitemap = sys.argv[1]
else:
	url = sys.argv[1]

# Domain e.g. example.com without https or trailing slashes
domain = urlparse(sys.argv[1]).netloc

test_list__googleFonts = ['fonts.googleapis.com', 'fonts.gstatic.com']
test_list__googleCaptcha = ['www.google.com/recaptcha/', 'www.gstatic.com/recaptcha/']
test_list__googleMaps = ['maps.gstatic.com']
test_list__youtube = ['youtube.com', 'googlevideo.com', 'youtube-nocookie.com', 'yt3.ggpht.com', 'i.ytimg.com']
test_list__vimeo = ['vimeocdn.com', 'vimeo.com']
test_list__facebook = ['connect.facebook.net', 'www.facebook.com/tr']

def urlsFromSitemap(sitemap):
    sitemap = requests.get(sitemap)
    soup = BeautifulSoup(sitemap.content, "xml")

    elements = soup.findAll("url")
    urls = [elem.find("loc").string for elem in elements]

    for url in urls:
        goToUrl(url)

def checkIfExternal(data, page, prefix):
    if domain not in data.url:
        if any(e in data.url for e in test_list__googleFonts):
            print (prefix, emoji.emojize(':collision:'),'Google Fonts find on', page.url, ':', data.url)
        elif 'googleapis.com' in data.url:
            print (prefix, emoji.emojize(':collision:'),'Google Apis find on', page.url, ':', data.url)
        elif 'paypalobjects.com' in data.url:
            print (prefix, emoji.emojize(':collision:'),'PayPal Connection find on', page.url, ':', data.url)
        elif 'google-analytics.com' in data.url:
            print (prefix, emoji.emojize(':collision:'),'Google Analytics find on', page.url, ':', data.url)
        elif 's.w.org' in data.url:
            print (prefix, emoji.emojize(':thumbs_down:'),'wp emoji find on', page.url, ':', data.url)
        elif 'consentmanager.net' in data.url:
            print (prefix, emoji.emojize(':cookie:'),'consentmanager find on', page.url, ':', data.url)
        elif 'fontawesome.com' in data.url:
            print (prefix, emoji.emojize(':collision:'),'Fontawesome CDN find on', page.url, ':', data.url)
        elif any(e in data.url for e in test_list__googleCaptcha):
            print (prefix, emoji.emojize(':collision:'),'Google Recaptcha find on', page.url, ':', data.url)
        elif any(e in data.url for e in test_list__googleMaps):
            print (prefix, emoji.emojize(':collision:'),'Google Maps find on', page.url, ':', data.url)
        elif 'gravatar.com' in data.url:
            print (prefix, emoji.emojize(':collision:'),'Gravatar find on', page.url, ':', data.url)
        elif 'hcaptcha.com' in data.url:
            print (prefix, emoji.emojize(':collision:'),'Hcaptcha find on', page.url, ':', data.url)
        elif any(e in data.url for e in test_list__facebook):
            print (prefix, emoji.emojize(':clinking_glasses:'),'Facebook Pixel find on', page.url, ':', data.url)
        elif any(e in data.url for e in test_list__youtube):
            print (prefix, emoji.emojize(':collision:'),'Google YouTube find on', page.url, ':', data.url)
        elif any(e in data.url for e in test_list__vimeo):
            print (prefix, emoji.emojize(':collision:'),'Google YouTube find on', page.url, ':', data.url)
        elif 'google.com' in data.url:
            print (prefix, emoji.emojize(':collision:'),'Google Connection find on', page.url, ':', data.url)
        else:
            print (prefix, emoji.emojize(':thinking_face:'), 'Unkown', page.url, data.url)
    #else:
        #print(prefix, data.url)

def checkDNSPrefetch(page):
    find_results = page.locator('//link[@rel="dns-prefetch"]')
    # get the number of elements/tags
    count = find_results.count()
    # loop through all elements/tags
    for i in range(count):
        # get the element/tag
        element = find_results.nth(i)
        # get the text of the element/tag
        #text = element.inner_text()
        text = element.get_attribute('href')
        # print the text
        if (text == "//s.w.org"):
            print (emoji.emojize(':collision:'),'s.w.org Prefetch find on', page.url)
        elif (text == "//fonts.googleapis.com"):
            print (emoji.emojize(':collision:'),'GoogleApis Prefetch find on', page.url)
        else:
            print(text)

def checkCookies(context):
    cookies = context.cookies()
    cookies_no_consent = [{
        "name" : cookie["name"],
        "domain" : cookie["domain"],
        "expires" : cookie["expires"]
    } for cookie in cookies]
    if cookies_no_consent:
        print ("--", emoji.emojize(':cookie:'),'cookies found', cookies_no_consent)

def goToUrl(url):
    chromium = playwright.chromium
    browser = chromium.launch()
    context = browser.new_context(viewport={'width': 1920,'height': 1080})
    page = context.new_page()
    print(url,page.title())
    page.on('request', lambda request: checkIfExternal(request, page,"->"))
    page.on('response', lambda response: checkIfExternal(response, page,"<-"))
    page.goto(url, wait_until="networkidle")
    checkDNSPrefetch(page)
    checkCookies(context)
    browser.close()

def run(playwright):
    if sitemap != "":
        urlsFromSitemap(sitemap)
    elif url != "":
        goToUrl(url)

with sync_playwright() as playwright:
    run(playwright)
