from __future__ import absolute_import
import re
import scrapy

# from simpleraceday import items
from datetime import date, time, datetime, timedelta
# from racedaylive.utilities import *
from dateutil.parser import parse
import pprint
from collections import *
import logging
from fractions import Fraction
from dateutil import tz
import operator
import math
from operator import methodcaller, is_not
from functools import partial
import unicodedata
import sys
from simpleraceday import items
from scrapy.settings import Settings
from itertools import izip, chain
from simpleraceday import hkjc_utilities
# import numpy as np
from decimal import *
import os
getcontext().prec = 2



logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger()

def to_int(s):
    if s is None:
        return None
    if s.isdigit():
        return int(s)
    else:
        return None

def dict_factory():
    return defaultdict(dict_factory)

def distancetonorp(d):
    d = int(d)
    lookup = {
    "1650": 4,
    "1800": 5,
    "1600": 4,
    "1400": 4,
    "2000": 5,
    "1200": 3,
    "1000": 3,
    "2200": 5,
    "2400": 5
    }
    return lookup.get(d, 0)

def get_horsewt(wt):
    if wt == u'--' or wt is None or wt == u'':
        return 0
    else:
        int(wt)

##rewrite - for all but 1st
def get_lbw(value):
    value= value.strip()
    value = cleanstring(value)
    if value.isdigit():
        return try_float(value)
    else:
        if value is None or '---' in value:
            return None
        if "-" in value and len(value) > 1 and "/" not in value:
            #10-3/4 
            return float(Fraction(value.split('-')[0]) + Fraction(value.split('-')[1]))
        if '/' in value:
            return float(Fraction(value)) 
        return None

def horselengthprocessor(value):
    value = cleanstring(value)
    #covers '' and '-'
    if value is None:
        return None
    if '---' in value:
        return None
    elif value == '-' or u'':
        #winner
        return 0.0
    elif "-" in value and len(value) > 1:
        return float(Fraction(value.split('-')[0]) + Fraction(value.split('-')[1]))
    elif value == u'N':
        return 0.3
    elif value == u'SH':
        return 0.1
    elif value == u'HD':
        return 0.2
    elif value == u'SN':
        return 0.25  
    #nose?           
    elif value == 'NOSE':
        return 0.05
    elif '/' in value:
         return float(Fraction(value))        
    elif value.isdigit():
        if len(value) ==1:
            return value
        else:
            return try_float(value)
    else:
        return None


'''
use cases: u'\r\n2\r\n\t\t\t\t\t'
also remove '\xa0'
'''
def cleanstring(s):
    s = unicode(s)
    r = unicodedata.normalize('NFD', s)
    r = r.encode('ascii', 'ignore').decode('ascii')
    r = cleanescapes(r)
    r = r.replace(u'\xa0',u'')
    pattern = re.compile(r'\s+')
    return re.sub(pattern, u' ',r)

def try_float(value):
    try:
        return float(value)
    except:
        return 0.0

def try_int(value):
    try:
        return int(value)
    except:
        return 0

'''
distance string to int
removes m returns int
'''
def get_distance(d):
    if 'M' in d or 'm' in d:
        d = d.replace('m').replace('M')
    return int(d)

def get_priority(value):
    return unicode.strip(value)

def get_rating(ratingstr):
    return try_int(ratingstr)

def getdateobject(date_str):
    #two variants on retired its %Y, on old its %y which is '15, on newform its '15 too
    if len(date_str) ==10:
        return datetime.strptime(date_str, '%d/%m/%Y')
    elif len(date_str) == 8:
        return datetime.strptime(date_str, '%d/%m/%y')
    else:
        raise ValueError

def get_racecoursecode(longname):
    if longname == 'Sha Tin':
        return 'ST'
    if longname == 'Happy Valley':
        return 'HV'
    else:
        return None


def removeunicode(value):
    return value.encode('ascii', 'ignore')

def get_hkjc_ftime(ftime, myformat=None):
    '''
    strftime('%s')
    expected format:1:40.7 m.ss.n
    if format =='s' return no of seconds else datetiem obj
    '''
    if ftime is None:
        return None
    dt1_obj = datetime.strptime(ftime, "%M.%S.%f")
    if dt1_obj is not None:
        totalsecs = (dt1_obj.minute*60.0) + dt1_obj.second + (dt1_obj.microsecond/1000.0)
    if myformat == u's':
        return totalsecs
    else:
        return dt1_obj

def get_scmp_ftime(ftime, myformat=None):
    '''
    strftime('%s')
    expected format:1:40.7 m:ss.n
    if format =='s' return no of seconds else datetiem obj
    '''
    if ftime is None:
        return None
    dt1_obj = datetime.strptime(ftime, "%M:%S.%f")
    if dt1_obj is not None:
        totalsecs = (dt1_obj.minute*60.0) + dt1_obj.second + (dt1_obj.microsecond/1000.0)
    if myformat == u's':
        return totalsecs
    else:
        return dt1_obj

def get_sec(s):
    # 1.40.68
    if isinstance(s, list):
        s = s[0]
    if s == '--' or s == '---':
        return None
    try:
        l = s.split('.') #array min, secs, milli - we want seconds
    # l[0]*60 + l[1] + l[2]/60.0
        if len(l) == 3:
            return float(l[0])*60 + float(l[1]) + (float(l[2])*0.01)
    except ValueError:
        return s

def get_odds(odds):
    if odds is None or odds == 99:
        return None
    else:
        return try_float(odds)



def cleanescapes(s):
    s = s.replace(u'\r', u'')
    s = s.replace(u'\t', u'')
    s = s.replace(u'\n', u'')
    s = s.replace(u' ', u'')
    return s

def removeunicode(value):
    return value.encode('ascii', 'ignore')

def cleanpm(prizemoney):
    return float(''.join(re.findall("[-+]?\d+[\.]?\d*", prizemoney)))/1000.0

def get_placing(place):
    place99 = ['DISQ', 'DNF', 'FE', 'PU', 'TNP', 'UR', 'VOID', 'WD', 'WR', 'WV', 'WV-A', 'WX', 'WX-A']
    if place is None:
        return None
    elif place in place99:
        return 99
# r_dh = r'.*[0-9].*DH$'
    else:
        return try_int(place)

def dodivide(x,y, f=True):
    if x == u'--' or y == u'--':
        return None
    if x is None or x== '' or y is None or y== '':
        return None
    if f:
        try:
            round(x/float(y),2)
        except ZeroDivisionError:
            return None
    else:
        return try_int(x/y)

def min_max_mean(lis):
    if lis is None or len(lis) ==0 or lis == []:
        return None,None, None
    lis = [x for x in lis if isinstance(x, float) or isinstance(x, int)]
    mean = dodivide(sum(lis), len(lis))
    return min(lis), max(lis), mean


def isscratched(pos):
    return int(pos) ==99 

def islowdraw(dr):
    return dr in [1,2,3]

def accumu(lis):
    total = 0
    for x in lis:
        total += x
        yield total

# def _dict_factory():
#    return defaultdict(dict_factory)

class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

##preferred
def generatestandardtimes2():
    import csv
    newdict = Vividict()
    with open("/home/vmac/PY/simpleraceday/simpleraceday/spiders/standardtimes.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            finish, sec1, sec2, sec3, sec4, sec5, sec6 = row['finish'],row['sec1'],\
            row['sec2'],row['sec3'],row['sec4'],row['sec5'],row['sec6'] 
            racedate, racecoursecode, racedistance ,raceclass = row['racedate'], row['racecoursecode'],row['racedistance'], row['raceclass']
            t = [ finish, sec1, sec2, sec3, sec4, sec5, sec6 ]
            newdict[racedate][racecoursecode][racedistance][raceclass] = t
    return newdict 

# def generatestandardtimes():
#     import csv
#     newdict = _dict_factory()
#     print os.getcwdu()
#     with open("/home/vmac/PY/simpleraceday/simpleraceday/spiders/standardtimes.csv") as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             finish, sec1, sec2, sec3, sec4, sec5, sec6 = row['finish'],row['sec1'],\
#             row['sec2'],row['sec3'],row['sec4'],row['sec5'],row['sec6'] 
#             racedate, racecoursecode, racedistance ,raceclass = row['racedate'], row['racecoursecode'],row['racedistance'], row['raceclass']
#             t = [ finish, sec1, sec2, sec3, sec4, sec5, sec6 ]
#             newdict[racedate][racecoursecode][racedistance][raceclass] = t
#     return newdict 


'''
expect format datetime object + time 1:45 12 hour clock
convert to UTC time object -8
need to explicity state timezone in datetime object?
'''
def local2utc(todaysdate, basictime):
    h = int(basictime.split(':')[0])
    h = h+12 if h < 12 else h
    m = int(basictime.split(':')[1])
    hk_t = time(h,m)
    hk_d = datetime.combine(todaysdate, hk_t) ##todaysdate is a date object
    return hk_d - timedelta(hours=8) 

class RaceSpider(scrapy.Spider):

    name = 'simpleraceday'
    allowed_domains = ['racing.scmp.com', 'hkjc.com']
    count_all_horse_requests = 0
    count_unique_horse_request = 0
    todaysdate = datetime.today().date()
    historical = 0
    pastraces = defaultdict(list)# racedate_raceindex: horsecodes
    code_set = set()
    runners_list = defaultdict(list)
    tips_url = 'http://racing.scmp.com/Tips/tips.asp'
    
    def __init__(self, racedate, racecoursecode, *args, **kwargs):
        assert racecoursecode in ['ST', 'HV']
        assert len(racedate) == 8 and racedate[:2] == '20'
        super(RaceSpider, self).__init__(*args, **kwargs) #makes sure parent is init'd
        
        self.hkjc_domain = 'racing.hkjc.com'
        self.domain = 'hkjc.com'
        self.racedate = racedate
        self.racedateo = datetime.strptime(self.racedate, '%Y%m%d').date()
        self.racecoursecode = racecoursecode
        self.todaysdate = datetime.today().date()
        self.inputdate = datetime.strptime(racedate, "%Y%m%d").date()
        _isit = (self.inputdate - self.todaysdate).days > 3
        self.historical = _isit
        self.tips_url = 'http://racing.scmp.com/Tips/tips.asp'
        self.hkjcraces_url = 'http://{domain}/racing/Info/Meeting/RaceCard'\
            '/English/Local/{racedate}/{coursecode}/1'.format(
                domain=self.hkjc_domain,
                racedate=racedate, 
                coursecode=racecoursecode,
        )
        self.racecardpro_url = 'http://racing.scmp.com/racecardpro/racecardpro.asp'
        self.start_urls = [
            'http://racing.scmp.com/login.asp'
        ]
    #
    def parse(self, response):
        if (self.inputdate - self.todaysdate).days > 3:
            self.historical = 1
            # return scrapy.Request(self.hkjcraces_url, callback=self.parse_hkjc_races)
        else:
            return scrapy.http.FormRequest.from_response(
            response,
            formdata={'Login': 'luckyvince', 'Password': 'invader'},
            callback=self.after_login,
        )

    def after_login(self, response):
        if "authentication failed" in response.body:
            self.logger.error("Login failed")
            return
        else:
            return scrapy.Request(self.racecardpro_url, callback=self.parse_racecardpro_url)

    def parse_racecardpro_url(self, response):

        logging.debug("racecard url {}".format(response.url))

        #LOGGED IN http://racing.scmp.com/racecardpro/racecardpro.asp
        # _thedate = response.xpath('//tr/td/font/b[contains(text(),"Sunday")'
        #     'or contains(text(),"Wednesday") or contains(text(),"Saturday") or contains(text(),"Tuesday")'
        #     ' or contains(text(),"Thursday")]/text()').extract()[0]
        # print _thedate

        _noraces = map(try_int, map(cleanstring, response.xpath('//select/option/@value').extract()) )
        logging.debug("no of races today {}".format(max(_noraces)))
        # _notips=  response.xpath('//select/option/.[contains(text(),"No Current Tips")]/text()').extract()
        #are tips available??
        # print boolean(_notips), max(_noraces)
        # print response.xpath(u"//select/option").extract()
        return scrapy.Request(self.hkjcraces_url, callback=self.parse_hkjc_races)
        # _tips = response.xpath('//font/select/option/text()').extract()
        # if _tips:
        #     if "No Current Tips" in cleanstring(_tips[0]):
        #         return scrapy.Request(self.hkjcraces_url, callback=self.parse_hkjc_races)
        #         ##go to HKJC
        #         return
        # else:
        #     print "get tips and then comments"

    def parse_hkjc_races(self, response):
        #HKJC racecard
        race_paths = response.xpath('//td[@nowrap="nowrap" and @width="24px"]'
            '/a/@href').extract()
        card_urls = ['http://{domain}{path}'.format(
                domain=self.hkjc_domain,
                path=path,
            ) for path in race_paths
        ] + [response.url]
        # result_urls = [_url.replace('RaceCard', 'Results') for _url in card_urls]
        for card_url in card_urls:
        #     if int(card_url.split('/')[-1]) > 9:
        #         racenumber = '{}'.format(card_url.split('/')[-1])
        #     else:
        #         racenumber = '0{}'.format(card_url.split('/')[-1])
            request = scrapy.Request(card_url, callback=self.parse_hkjc_racecard)
            request.meta.update(response.meta)
            # request.meta['racenumber'] = racenumber
            request.meta['card_url'] = card_url
            yield request

    def parse_hkjc_racecard(self, response):
        print "the url {}- hist? {}".format(response.url, RaceSpider.historical)
        # racename_ = response.xpath('//table[@class="font13 lineH20 tdAlignL"]//span[@class="bold"]/text()').extract()
        # if racename_ is None:
        #     racename = racename_[0]
        # racename = re.match(r'^Race \d+.{3}(?P<name>.+)$', racename_
        #     ).groupdict()['name']
        card_url = response.url
        if int(card_url.split('/')[-1]) > 9:
            _racenumber = '{}'.format(card_url.split('/')[-1])
        else:
            _racenumber = '0{}'.format(card_url.split('/')[-1])
        racenumber = try_int(_racenumber)
        # data only avail from sectionals if historical
        _marginsbehindleader = None
        _placing = None
        _finishtime = None
        _positions = None
        _timelist = None
        date_racecourse_localtime= None
        if self.historical:
            sec_time_data = response.meta['sectional_time_data'][(horsecode, response.meta['racenumber'])]
            _marginsbehindleader = map(horselengthprocessor, sec_time_data['marginsbehindleader'])
            _placing = get_placing(sec_time_data['placing'])
            _finishtime = get_sec(sec_time_data['finish_time'])
            _positions = map(try_int, sec_time_data['positions'])
            _timelist = sec_time_data['timelist']
        raceinfo_ = response.xpath('//table[@class="font13 lineH20 tdAlignL"]//descendant::text()[ancestor::td and normalize-space(.) != ""][position()>=2]').extract()
        if raceinfo_:
            date_racecourse_localtime = cleanstring(raceinfo_[0])
            surface_distance = raceinfo_[1].encode('utf-8').strip()
            print "surface_distance--> {}".format(surface_distance)
            prize_rating_class = cleanstring(raceinfo_[2])
        
        localtime= None
        if date_racecourse_localtime: 
            # racecourse = unicode.strip(unicode.split(date_racecourse_localtime, u',')[-2])
            localtime = unicode.strip(unicode.split(date_racecourse_localtime, u',')[-1])
        distance = None
        surface = None
        _surface = None 
        _trackvariant= None 
        _distance= None 
        going = None
        if surface_distance:
            ##Turf, "A+3" Course, 1800M, Good
            try:
                _surface, _trackvariant, _distance, _going = surface_distance.split(u',')
                _trackvariant = _trackvariant.replace('\"', '').strip()
                _distance = _distance.replace('M','').replace('m', '')
                going = hkjc_utilities.get_goingabb(_going,_surface)
                surface = _trackvariant.replace(u'Course', u'').strip()
            except ValueError:
                _surface, _trackvariant, _distance = surface_distance.split(u',')
            
            if _surface != "All Weather Track":
                surface = _trackvariant.replace(u'Course', u'').strip()
            else:
                surface = _surface
        racerating = None
        raceclass = None
        if prize_rating_class:
            racerating = unicode.strip( unicode.split(prize_rating_class, u',')[-2].replace(u'Rating:', ''))
            _raceclass = prize_rating_class.split(u',')[-1] 
            raceclass = hkjc_utilities.get_raceclass(_raceclass)

        '''

        Race 2 - CHONGQING HANDICAP
        Thursday, October 01, 2015, Sha Tin, 13:30
        Turf, "A+3" Course, 1800M, Good
        Prize Money: $1,165,000, Rating:80-60, Class 3 

        '''

        # print "RACE DATA: racenumber {}, surface{}, going {}, class {}, rating {}".format(racenumber,surface, going, raceclass, racerating)

        ##RaceType racecourse numberofrunners surface distance going

        # Turf, "A" Course
        # surface = re.match(r'^[^,](?P<surface>.+),.*', raceinfo_).groupdict()['surface']

        # pprint.pprint(surface_distance)
        # pprint.pprint(prize_rating_class)
        # racerating = re.match(r'^Rating:\d{2-3}-\d{2-3}(?P<rating>.+).*', raceinfo_).groupdict()['rating']

        ### RaceCategory RACETIME SURFACE DISTANCE GOING 
        ### PM RATING CLASS  
        ##season_stakes and priority
        for tr in response.xpath('(//table[@class="draggable hiddenable"]//tr)'
                '[position() > 1]'):

            horsenumber = tr.xpath('td[1]/text()').extract()[0]
            horsename = tr.xpath('td[4]/a/text()').extract()[0]
            horse_path = tr.xpath('td[4]/a/@href').extract()[0]
            # http://www.hkjc.com/english/racing/horse.asp?HorseNo=S142&Option=1#htop
          
            # horse_url = horse_url
            horsecode_ = tr.xpath('td[4]/a/@href').extract()[0]
            horsecode = re.match(r"^[^\?]+\?horseno=(?P<code>\w+)'.*$",
                horsecode_).groupdict()['code']
            horse_url = 'http://www.hkjc.com/english/racing/horse.asp?HorseNo={}&Option=1#htop'.format(horsecode)
            self.code_set.add(horsecode)
            self.runners_list[_racenumber].append(horsecode)
            logger.warning('-------------------------------------------------')
            logger.warning('horse code set')
            logger.warning(str(len(self.code_set)))

            jockeyname_ = tr.xpath('td[7]/a/text()').extract()[0]
            jockeycode_ = tr.xpath('td[7]/a/@href').extract()[0]
            jockeycode = re.match(r"^[^\?]+\?jockeycode=(?P<code>\w+)'.*",
                jockeycode_).groupdict()['code']
            
            ##TRAINER CODE
            trainername_ = tr.xpath('td[10]/a/text()').extract()[0]
            trainercode_ = tr.xpath('td[10]/a/@href').extract()[0]
            trainercode = re.match(r"^[^\?]+\?trainercode=(?P<code>\w+)'.*",
                trainercode_).groupdict()['code']

            todaysrating_ = tr.xpath('td[11]/text()').extract()[0]
            owner_ = tr.xpath('td[22]/text()').extract()[0]
            gear_ = tr.xpath('td[21]/text()').extract()[0]

            seasonstakes_ = tr.xpath('td[18]/text()').extract()[0]
            priority_ = tr.xpath('td[20]/text()').extract()[0]
            draw_ = tr.xpath('td[9]//text()[normalize-space()]').extract()[0]
            # draw_ = tr.xpath('td[8]/text()[normalize-space()]').extract()[0]
            draw_ = draw_.replace(u'\xa0', u'')
            # print("todays draw {}- {}").format(draw_, try_int(draw_))

            # request = scrapy.Request('http://www.hkjc.com/english/racing/horse.'
            #     'asp?horseno={}'.format(horsecode), callback=self.parse_horse)

            ##or get all races
           

            request = scrapy.Request('http://www.hkjc.com/english/racing/horse.asp?HorseNo={}&Option=1#htop'.format(horsecode), callback=self.parse_horse)
            request.meta.update(response.meta)
            request.meta.update(
                localtime=localtime,
                utcracetime = local2utc(self.racedateo, localtime),
                racecoursecode=self.racecoursecode,
                racesurface=surface,
                racenumber=racenumber,
                racegoing= going,
                racedistance=_distance,
                raceclass=raceclass,
                racerating= try_int(racerating),
                racedate = self.racedateo,
                horsenumber=try_int(horsenumber),
                horsename=horsename,
                horsecode=horsecode,
                horse_url= horse_url,
                jockeycode=jockeycode,
                # jockeyname=re.sub(r'\([^)]*\)', '', jockeyname_),
                trainercode=trainercode,
                # trainername = trainername_,
                todaysrating=try_int(todaysrating_),
                ownername=owner_,
                gear=removeunicode(gear_),
                draw= draw_,
           
                seasonstakes = try_int(seasonstakes_),
                priority = get_priority(priority_)
            )
            yield request

    '''
    C-D-T SPECIFIC
    TIMES
    CAREER
    reg (old) http://www.hkjc.com/english/racing/horse.asp?horseno=S142
    http://www.hkjc.com/english/racing/horse.asp?HorseNo=S142&Option=1#htop
    '''
    def parse_horse(self, response):
        print response.meta["horsecode"]
        _horsename = response.meta["horsename"]
        # print response.meta
        RaceSpider.count_unique_horse_request += 1
        logger.warning('RaceSpider.count_unique_horse_request')
        logger.warning(str(RaceSpider.count_unique_horse_request))

        ##today

        today_rc = response.meta["racecoursecode"]
        todays_d = response.meta["racedistance"].lstrip()
        today_cl = unicode(response.meta["raceclass"]).strip()
        todays_cl_fullname = hkjc_utilities.getfullraceclassname(today_cl)

        logger.debug("todays cl fullname {}".format(todays_cl_fullname))

        today_dr =  response.meta["draw"]
        today_surf = response.meta["racesurface"]
        logger.debug("RC {}, D {}, CL {}, DR {} SURF {}".format(today_rc, todays_d, today_cl, today_dr,today_surf))
        logger.debug("today_rc {}, todays_d {},todays_cl_fullname {}".format(today_rc,todays_d,todays_cl_fullname))
        # today_dr = response.meta["draw"])
        standardspeeds = Vividict()
        standardspeeds= generatestandardtimes2()
        # pprint.pprint(standardspeeds)
        
        racestandardfinish = standardspeeds['20150906'][today_rc][str(todays_d)][todays_cl_fullname][0]
        logger.info("standard finish time: {}".format(racestandardfinish))
        

        # print "todays draw{} and surface {}".format(today_dr, today_surf)

        # print "draw: {}".format(today_dr)
        
        

        

        ## GET SEASON STAKES INSTEAD
        totalstakes = response.xpath('//td[preceding-sibling::td[1]/font['
            'text() = "Total Stakes*"]]/font/text()').extract()[0]
        careerstakes_hkabroad= cleanpm(totalstakes)

        # #DD - previousruns: Place, Date, Rating
        prev_rc_track_course = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=4]/text()[normalize-space()]").extract()
        prev_rc_track_course = map(cleanstring, prev_rc_track_course)
        prev_rc_track_course= [ unicode.split(x.strip(),u'/')[0] for x in prev_rc_track_course]
        prev_rcs  = [ str(x) for i,x in enumerate(prev_rc_track_course) if i%2 ==0]
        prev_surfaces  = [ x for i,x in enumerate(prev_rc_track_course) if i%2 ==1]
        prev_surfaces = [ x.replace(u'"', u'') for x in prev_surfaces if x not in [u' ', u'', u'--']]
        prev_places = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=2]//font/text()[normalize-space()]").extract()
        prev_raceclasses = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=7]//text()[normalize-space()]").extract()
        prev_draws = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=8]//text()").extract()
        
        # prev_rps = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=15]//font/text()[normalize-space()]").extract()
        rps = OrderedDict()
        rps_d = OrderedDict()
        
        

        for rprow in response.xpath("//table[@class='bigborder']//tr[position()>1]"):
            #skip seasons
            _rd = rprow.xpath(".//td[3]/text()").extract()
            _d = rprow.xpath(".//td[5]/text()").extract()
            if _rd:
                _prevdate = datetime.strptime(_rd[0], '%d/%m/%y').date() #29/03/15
                _prevdist = _d[0]
                _rp = map(hkjc_utilities.removeunicode, rprow.xpath("./td[15]//font/text()").extract()) #this is a list
                if _prevdate is not None and _prevdate < self.inputdate:
                    # print "racedate, racep {}, {}".format(_rd[0], _rp)
                    rps[_prevdate] = _rp
                    if _prevdist == todays_d:
                        rps_d[_prevdate] = _rp
        # print "rps::::{}".format(rps)
        #sort rps and return values()
        rps_ordered = OrderedDict(sorted(rps.items(), key=lambda t: t[0]))
        rps_d_ordered = OrderedDict(sorted(rps_d.items(), key=lambda t: t[0]))
        previous_rps = rps_ordered.values()  #zip with prev_draws
        previous_rps_d = rps_d_ordered.values() #zip prev_draws
        #previous_rps_d after we have all as ordered dict
        


        prev_ftimes = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=16]//text()[normalize-space()]").extract()
        

        prev_raceindexes = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=1]/a//text()[normalize-space()]").extract()
        prev_actualwts = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=14]//text()[normalize-space()]").extract()
        prev_horsewts = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=17]//text()[normalize-space()]").extract()

        prev_winodds = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=13]//text()[normalize-space()]").extract()
        prev_lbws = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=12]//text()[normalize-space()]").extract()
        logger.debug("Raceno {} : Horsecode {}- name {} - careerstakes_hkabroad $ {}".format(\
            response.meta["racenumber"], response.meta["horsecode"],_horsename, careerstakes_hkabroad))

        

        
        prev_raceclasses = map(cleanstring, prev_raceclasses)
        prev_raceclasses = [ unicode.strip(x) for x in prev_raceclasses]
        prev_draws = map(cleanstring, prev_draws)
        prev_draws = [ int(x) for x in prev_draws if x not in [u' ', u'', u'--', None]]
        
        prev_actualwts = map(try_int, prev_actualwts)
        prev_horsewts = map(to_int, prev_horsewts)
        # prev_horsewts = map(cleanstring, prev_horsewts)
        # prev_horsewts = map(get_horsewt, prev_horsewts)
        
        

        prev_dates = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=3]//text()[normalize-space()]").extract()
        prev_ratings = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=9]/text()").extract()
        prev_distances = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=5]/text()").extract()
        prev_places = map(get_placing, prev_places)
        # print("prev lbws1: {}".format(prev_lbws))
        # print("prev ds1: {}".format(prev_distances))
        ##make sure only valud ones
        prev_dates = map(cleanstring, prev_dates)
        prev_dates = [datetime.strptime(x, '%d/%m/%y').date() for x in prev_dates]
        valid_indexes = [i for i, x in enumerate(prev_dates) if x < self.racedateo ]
        nonoverseas_races_indexes =[i for i,x in enumerate(prev_raceindexes) if x != u'Overseas'] 
        
        ##### validate
        valid_indexes = list(set(valid_indexes).intersection(nonoverseas_races_indexes))
        prev_dates = [x for i,x in enumerate(prev_dates) if i in valid_indexes]
        prev_actualwts = [x for i,x in enumerate(prev_actualwts) if i in valid_indexes]
        prev_horsewts = [x for i,x in enumerate(prev_horsewts) if i in valid_indexes]
        prev_ratings = [x for i,x in enumerate(prev_ratings) if i in valid_indexes]
        prev_raceindexs = [x for i,x in enumerate(prev_raceindexes) if i in valid_indexes]
        prev_raceclasses = [x for i,x in enumerate(prev_raceclasses) if i in valid_indexes]
        prev_distances = [x for i,x in enumerate(prev_distances) if i in valid_indexes]
        prev_draws = [x for i,x in enumerate(prev_draws) if i in valid_indexes]

        # prev_rps = [x for i,x in enumerate(prev_rps) if i in valid_indexes]
        previous_rps_draws = OrderedDict(zip(prev_draws, rps_ordered.values()))
        previous_rps_d_draws = OrderedDict(zip(prev_draws, rps_d_ordered.values()))
        # LATER DO rc_indexes
        # OrderedDict(k, v for k, v in previous_rps_d_draws.values())
        # prev_rps = map(hkjc_utilities.removeunicode, prev_rps)
        # prev_rps = [x for x in prev_rps if x not in [u' ', u'', u'--', None, u'\xa0\xa010']]
        # print("previous rps draws: {}----{}").format(previous_rps_draws,previous_rps_d)
        ## u'\xa0\xa05'
        # print("todays raceclass {} ---> prev raceclasses: {}".format(today_cl, prev_raceclasses))
        # print("Todays surface {} - and previous surfaces {}").format(today_surf,prev_surfaces==today_surf)
        # print("Todays draw {} - is low draw {} - and previous draws {}").format(today_dr,islowdraw(today_dr), prev_draws)

        prev_ftimes = [ get_sec(f) for f in prev_ftimes ]
        #compare with the standard times based on class distance and racecourse! 

        ##GET RPS per RACE as DICT ENTRY RACEDATE_RACEINDEX RP OR ARRAY
        # print("New previous rps {}".format(prev_rps))

        
        # _tmp = prev_rps

        ###used to split rps from long list of ints to ints per race
        # prev_rpnos = map(distancetonorp, prev_distances)
        # accum_prev_rpnos = list(accumu(prev_rpnos))
        # accum_prev_rpnos.insert(0,0)
        # previous_rp_aggs = list()
        # print("prev rps {} - length {}").format(prev_rps, len(prev_rps))
        # print("accum {} sum of prevrpnos {}".format(accum_prev_rpnos, sum(prev_rps) ))
        # for x, y in zip(accum_prev_rpnos, accum_prev_rpnos[1:]):
        #     _tmp = prev_rps[x:y]
        # if _tmp != []:
        #     print "Previous rps {}  ismadeall {}, islostlead {}, pasthorsessecl1 {}, isonpace {}, isbackmarker{}".format(\
        #     _tmp,hkjc_utilities.ismadeall(_tmp), hkjc_utilities.islostlead(_tmp), 
        #     hkjc_utilities.pasthorsessecl1(_tmp), hkjc_utilities.isonpace(_tmp),  hkjc_utilities.isbackmarker(_tmp) )
        #     previous_rp_aggs.append( [_tmp,hkjc_utilities.ismadeall(_tmp), hkjc_utilities.islostlead(_tmp), 
        #     hkjc_utilities.pasthorsessecl1(_tmp), hkjc_utilities.isonpace(_tmp),  hkjc_utilities.isbackmarker(_tmp)] )
        #slice prev_rps at these indexes

        prev_distances = map(get_distance, prev_distances)
        # prev_rps = map(cleanstring, prev_rps) 
        # prev_rps = map(get_placing, prev_rps)
        prev_winodds = map(get_odds, prev_winodds)
        # prev_lbws = map(get_lbw, prev_lbws)
        # print("prev lbws: {}".format(prev_lbws))
        # print("prev ds: {}".format(prev_distances))
        # print("prev ftimes: {}".format(prev_ftimes))
        avg_spds = [float(x)/float(y) for x, y in zip(prev_distances, prev_ftimes) if y != 0 and y is not None]

        #take finish time of previous races winner 

        # avg_spds = ["%.4f" % x if isinstance(x, float) else x for x in avg_spds]
        # avg_spds = ["%.4f" % x for x in avgspds if isinstance(x, float)]
        meanwinodds = l3odds = None
        if len(prev_winodds) >0:
            meanwinodds = float(sum(prev_winodds))/float(len(prev_winodds))
            meanwinodds = round(meanwinodds,2)
            l3odds = prev_winodds[:3]
        avg_spds_nonones = filter(partial(is_not, None), avg_spds)
        seq = sorted(avg_spds,reverse=True)
        ranked_avgspds = [seq.index(v)+1 for v in avg_spds_nonones]
        # print "CAREER avg speeds".format(avg_spds)
        # print "ranked avg speeds {} : mean odds {}, L3 odds{}, ".format(ranked_avgspds,meanwinodds,l3odds)
        

        #career
        winning_indexes = [i for i, x in enumerate(prev_places) if x == 1]
        placed_indexes = [i for i, x in enumerate(prev_places) if x in [2,3]]
        f4_indexes = [i for i, x in enumerate(prev_places) if x in [1,2,3,4]]
        rc_indexes = [i for i, x in enumerate(prev_rcs) if x == today_rc]
        scratched_indexes = [i for i, x in enumerate(prev_places) if x == 99]
        winning_ratings_dates = [ x for i,x in enumerate(zip(prev_ratings,prev_dates)) if i in winning_indexes]
        lastwonat = None
        lastwonago = None
        lastwonracesago = None
        if len(winning_ratings_dates) >0:
            lastwondate = winning_ratings_dates[0][1]
            lastwonat = winning_ratings_dates[0][0]
            lastwonracesago = prev_dates.index(lastwondate) + 1
            lastwonago =  abs( (lastwondate -self.inputdate).days)
        # print "Previous winning ratings and dates {}".format(winning_ratings_dates)
        # print "lastwonat {} last won ago {} and runs ago {}".format(lastwonat, lastwonago,  lastwonracesago)
        # lastwonat and lastwonago (dff days)
        dayssincelastrun_h = [ abs((t - s).days) for s, t in zip(prev_dates, prev_dates[1:])]
        dayssincelastrun = None
        if len(prev_dates) >0:
            dayssincelastrun = ( datetime.today().date()-prev_dates[0]).days 

        startseason_1516 =  datetime.strptime('20150901', '%Y%m%d').date()
        startseason_1415 =  datetime.strptime('20140901', '%Y%m%d').date()
        startseason_1314 =  datetime.strptime('20130901', '%Y%m%d').date()
        startseason_1213 =  datetime.strptime('20120901', '%Y%m%d').date()
        startseason_1112 =  datetime.strptime('20110901', '%Y%m%d').date()
        startseason_1011 =  datetime.strptime('20100901', '%Y%m%d').date()

         #20150527
        # print("Prev wts {} --> horse wts {}".format(prev_actualwts,prev_horsewts))
        # print "prev {}- {}".format(pastraces_keys,weights_performances)

        # jtohweights_h = [x/y for x,y in zip(prev_actualwts, prev_horsewts) if y not in [0, None, u''] and x not in [0, None, u''] ]
        # jtohweights_h = [s for s in jtohweights_h if s not in [u' ', u'', u'--', None]]
        # jtohweights_h = [round(i*100,3) for i in jtohweights_h]
        # print("jtohweights_h: {}".format(jtohweights_h ))
        _horsecode =  response.meta['horsecode']
        # print "tuple stats date, index, wts, places {}>{}>{}>{}".format(prev_dates,prev_raceindexes,prev_jtohweights,prev_places)
        pastraces_keys = [datetime.strftime(x, '%Y%m%d') +"_" + str(y) for x,y in zip(prev_dates,prev_raceindexes) ]
        weights_performances = [ x for x in zip(prev_actualwts,prev_places) ]
        h_pastraces = defaultdict(list)
        for k, p in zip(pastraces_keys, weights_performances):
            self.pastraces[k].append( (_horsecode,p ))  #master dictionary to get an idea of key races
            h_pastraces[k] = p
            # self.pastraces.merge(h_pastraces) #how to merges
        # print "past races {}- {}".format(pastraces_keys,weights_performances)

        

        seasonindexes_1516 = [i for i, x in enumerate(prev_dates) if x > startseason_1516 and i in valid_indexes ]
        prev_ftimes = [i for i, x in enumerate(prev_ftimes) if i in valid_indexes ]
        d_ind = [i for i, x in enumerate(prev_distances) if x ==int(todays_d) and i in valid_indexes]
        cl_ind = [i for i, x in enumerate(prev_raceclasses) if x ==today_cl and i in valid_indexes]

        surf_ind = [i for i, x in enumerate(prev_surfaces) if x ==str(today_surf) and i in valid_indexes]
        # rps_d = [x for i, x in enumerate(prev_rps) if i in d_ind ]
        wins_d_ind = [i for i in d_ind if i in winning_indexes]
        wins_cl_ind = [i for i in cl_ind if i in winning_indexes]
        wins_surf_ind = [i for i in surf_ind if i in winning_indexes]

        total_winodds = sum([x for i,x in enumerate(prev_winodds) if i in winning_indexes])
        total_runs = len(valid_indexes)
        roi = None
        if total_runs > 0:
            roi = ((total_winodds- total_runs)/float(total_runs))*100.0 

        f4_indexes_d = [i for i, x in enumerate(prev_places) if x in [1,2,3,4] and i in d_ind]
        f4_indexes_cl = [i for i, x in enumerate(prev_places) if x in [1,2,3,4] and i in cl_ind]
        f4_indexes_surf = [i for i, x in enumerate(prev_places) if x in [1,2,3,4] and i in surf_ind]


        placed_indexes_d = [i for i, x in enumerate(prev_places) if x in [2,3] and i in d_ind]
        placed_indexes_cl = [i for i, x in enumerate(prev_places) if x in [2,3] and i in cl_ind]
        placed_indexes_surf = [i for i, x in enumerate(prev_places) if x in [2,3] and i in surf_ind]


        prev_distances = [i for i, x in enumerate(prev_distances) if i in valid_indexes]
        # prev_avg_spds = [float(x)/float(y) for x, y in zip(prev_distances, prev_ftimes) if y != 0 and y is not None]
        prev_avg_spds_d = [ x for i,x in enumerate(avg_spds) if i in d_ind]
        prev_avg_spds_cl = [ x for i,x in enumerate(avg_spds) if i in cl_ind]
        prev_avg_spds_surf = [ x for i,x in enumerate(avg_spds) if i in surf_ind]
        
        if today_dr:
            #do low-medium-high
            dr_ind = [i for i, x in enumerate(prev_draws) if x ==today_dr and i in valid_indexes]
        if today_cl:
            cl_ind = [i for i, x in enumerate(prev_raceclasses) if x ==str(today_cl) and i in valid_indexes]
            
            # surf_ind = [i for i, x in enumerate(prev_surfaces) if x ==today_surf ]
        

        ##intersperse with days between
        # print "prev places {} and dayssincelastrun_h {}".format(prev_places, dayssincelastrun_h)
        # places_daysoff =  [x for x in chain.from_iterable(zip(prev_places,dayssincelastrun_h )) if x]
        places_daysoff =  [str(x) + " after" + str(y) + "d)" for x,y in zip(prev_places,dayssincelastrun_h ) if x]
        all_runs = "<".join(map(str,prev_places))
        all_runs_winloss = hkjc_utilities.get_winlossstring(all_runs)

        # print "todays dayssincelastrun {} days".format(dayssincelastrun)
        # print "todays lastwinago {} days".format(lastwonago)
        # print places_daysoff


        min_d, max_d, mean_d = min_max_mean(prev_avg_spds_d)
        min_car, max_car, mean_car = min_max_mean(avg_spds)
        min_cl, max_cl, mean_cl = min_max_mean(prev_avg_spds_cl)
        min_surf, max_surf, mean_surf = min_max_mean(prev_avg_spds_surf)
        # print "prev races breakdown:{}".format("".join(h_pastraces.values())) 
        # print "{} days since L1 - Days between previous runs: {}".format(dayssincelastrun,dayssincelastrun_h)
        print "CAREER number of previous races:{} - wins {}, placed {}, f4 {} scratches {}, max {}, min{}, mean {}, roi {}".format(\
            len(valid_indexes), len(winning_indexes), len(placed_indexes), len(f4_indexes),\
             len(scratched_indexes), min_car, max_car, mean_car, roi) 
        print ("No of races per season: {}, races this rc{}, this dist{}, this class {}".format(\
            len(seasonindexes_1516), len(rc_indexes), len(d_ind), len(cl_ind)))
        print ("DISTANCE: {}, wins {}, places: {}, f4s: {}, avgftimes {} max {}, min{}, mean {}".format(len(d_ind),\
         len(wins_d_ind),len(placed_indexes_d), len(f4_indexes_d),prev_avg_spds_d, min_d, max_d, mean_d) )
        print ("CLASS: {}, wins {}, places:{}, f4s:{}, avgftimes {} max {}, min{}, mean {}".format(\
            len(cl_ind), len(wins_cl_ind), len(placed_indexes_cl),len(f4_indexes_cl), prev_avg_spds_cl, 
            min_cl, max_cl, mean_cl) )
        print ("SURFACE: {}, wins {}, places: {}, f4s:{}, avgftimes {} max {}, min{}, mean {}".format(len(surf_ind)\
            , len(wins_surf_ind), len(placed_indexes_surf),len(f4_indexes_surf), prev_avg_spds_surf,
            min_surf, max_surf, mean_surf))
        if len(dayssincelastrun_h) >0:
            print("max-min {} ={}, avg {} days between runs".format( min(dayssincelastrun_h), max(dayssincelastrun_h), sum(dayssincelastrun_h) /len(dayssincelastrun_h) ))
        # print("avgspeeds {}".format(prev_avg_spds))
                # localtime=localtime,
                # utcracetime = local2utc(self.racedateo, localtime),
                # # racename=racename,
                # racecoursecode=get_racecoursecode(racecourse),
                # racesurface=get_surface(surface),
                # racenumber=racenumber,
                # racegoing= going,
                # racedistance=get_distance(distance),
                # raceclass=raceclass,
                # racerating= try_int(racerating),
                # racedate = self.racedateo,
                # horsenumber=try_int(horsenumber),
                # horsename=horsename,
                # horsecode=horsecode,
                # horse_url= horse_url,
                # jockeycode=jockeycode,
                # # jockeyname=re.sub(r'\([^)]*\)', '', jockeyname_),
                # trainercode=trainercode,
                # # trainername = trainername_,
                # todaysrating=try_int(todaysrating_),
                # owner=owner_,
                # gear=removeunicode(gear_),
                # draw= draw_,

           
                # seasonstakes = try_int(seasonstakes_),
                # priority = get_priority(priority_)





        # print np.mean(np.array(date_diffs))
        # prev_ratings = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=9]/text()").extract()

        # prev_distances = response.xpath("//table[@class='bigborder']//tr[position()>1]//td[position()=5]/text()").extract()
        
        # # pprint.pprint(prev_places)
        # # pprint.pprint(prev_dates)
        # #todays rc track course racecoursecode\s/\s #ST / "Turf" / "A+3 "    ST / "AWT" / "-" 
        # # todaysrc_track_course = getrc_track_course(response.meta['racecourse'], response.meta['racesurface'])
        # # pprint.pprint(todaysrc_track_course) 
        # ##DD isMdn
        # # datetime.strptime(response.meta['racedate'], '%Y%m%d')
        
        # valid_from_index = None
        # win_indices = [i for i, x in enumerate(prev_places) if x == "01"]
        # if len(invalid_dates) >0:
        #     valid_from_index = max(invalid_dates) 
        #     win_indices = win_indices[valid_from_index:]

        # is_maiden = False

        # if len(win_indices) ==0:
        #     is_maiden= True

        # min_index = None
        # last_won_at = None
        # if len(win_indices) >0: 
        #     min_index = min(win_indices)
        #     last_won_at = prev_ratings[min_index]


        # ##EarlyPacePoints need secs + lbw_post  
        # ##what are qualifying races?


        # ## utcracetime = local2utc(response.meta['racedate'],response.meta['localtime']),
        # ##TODO internalhorseindex - need racecourse

        ## random horse quiz
        ## matrix of each horse's runline parameters
        ## 
        ## Avg, min, max days between runs, lastwonat, isMaiden, classWINSR, classPlaces, classF4s, dist/surface
        ## avgspds, season, previousruns (list)
        ## 
        yield items.SimpleracedayItem(
            racedate=response.meta['racedate'],
            utcracetime = local2utc(response.meta['racedate'],response.meta['localtime']),
            racecoursecode=response.meta['racecoursecode'],
            raceclass=try_int(response.meta['raceclass']),
            racedistance=todays_d,
            racegoing=response.meta['racegoing'],
            racesurface=response.meta['racesurface'],
            racerating=response.meta['racerating'],
            racestandardfinish=float(racestandardfinish),
            # racename=unicode.strip(response.meta['racename']),
            racenumber=try_int(response.meta['racenumber']),
            horsenumber=try_int(response.meta['horsenumber']),
            horsename=unicode.strip(response.meta['horsename']),
            horsecode=response.meta['horsecode'],
            jockeycode=response.meta['jockeycode'],
            # jockeyname=response.meta['jockeyname'],
            trainercode=response.meta['trainercode'],
            # trainername=response.meta['trainername'],
            ownername=response.meta['ownername'],
            # totalstakes=cleanpm(unicode.strip(totalstakes)),
            # todaysrating=response.meta['todaysrating'],
            gear= response.meta['gear'],
            # lastwonat = get_rating(last_won_at),
            # isMaiden = is_maiden,
            # placing=try_int(response.meta['placing']),
            # finish_time=response.meta['finish_time'],
            # marginsbehindleader=response.meta['marginsbehindleader'],
            # positions=response.meta['positions'],
            # timelist=response.meta['timelist'],
            priority=removeunicode(response.meta['priority']),
            seasonstakes=response.meta['seasonstakes'],
            lastwonago=lastwonago,
            lastwonat=lastwonat,
            lastwonracesago=lastwonracesago,
            dayssincelastrun = dayssincelastrun,
            dayssincelastrun_h = dayssincelastrun_h,
            previousruns_car = len(valid_indexes),
            previouswins_car = len(winning_indexes),
            previousruns_d =  len(d_ind),
            previouswins_d= len(wins_d_ind),

            avg_spds = avg_spds,
            ranked_avgspds= ranked_avgspds,
            prev_avg_spds_d =prev_avg_spds_d,
            prev_avg_spds_cl =  prev_avg_spds_cl,
            # jtohweights_h=jtohweights_h,
            h_pastraces=h_pastraces.items(),
            l3odds = l3odds,

            all_runs=all_runs,
            previous_rps=previous_rps_draws,
            previous_rps_d=previous_rps_d_draws,
            places_daysoff=places_daysoff,
            career_roi= roi,
            previousruns_cl =  len(cl_ind),
            previouswins_cl= len(wins_cl_ind),
            previousruns_surf =  len(surf_ind),
            previouswins_surf= len(wins_surf_ind),
            min_d=min_d, 
            max_d=max_d,
            mean_d=mean_d,
            min_car=min_car, 
            max_car=max_car,
            mean_car=mean_car,
            min_cl=min_cl, 
            max_cl=max_cl,
            mean_cl=mean_cl,
            min_surf=min_surf, 
            max_surf=max_surf,
            mean_surf=mean_surf,
            # previous_rp_aggs=previous_rp_aggs,


            # runners_list=self.runners_list,
        )
