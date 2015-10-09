from subprocess import Popen
import time
'''
get owner t j record from DB


'''

## get dates from DB
def runSpider():
	# scrapy crawl simpleraceday -a racecoursecode=HV -a racedate=20151007
    p = Popen(["scrapy", "crawl", "simpleraceday", "-a", "racecoursecode=HV", "-a", "racedate=20151007"], 
        cwd="/home/vmac/PY/simpleraceday")
    stdout, stderr = p.communicate()
    time.sleep(15)

runSpider()