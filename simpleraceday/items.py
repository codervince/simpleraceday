# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SimpleracedayItem(scrapy.Item):
    ### to rd_race
    racedate = scrapy.Field() 
    racecoursecode = scrapy.Field()
    raceclass = scrapy.Field()
    racestandardfinish = scrapy.Field()
    racerating = scrapy.Field()
    runners_list = scrapy.Field()
    racegoing = scrapy.Field()
    racesurface = scrapy.Field()
    trackvariant= scrapy.Field()
    racedistance=scrapy.Field()
    racenumber = scrapy.Field()
    racename = scrapy.Field()
    localracetime = scrapy.Field()
    utcracetime = scrapy.Field()
    #####
    ### to rd_runner
    horsename = scrapy.Field() #to rdhorse and id to rd_runner
    horsenumber = scrapy.Field() #to rdhorse
    horsecode = scrapy.Field() #to rdhorse
    horse_url= scrapy.Field()
    jockeycode = scrapy.Field()
    jockeyname = scrapy.Field()
    trainercode = scrapy.Field()
    trainername = scrapy.Field()
    seasonstakes = scrapy.Field()
    todaysrating = scrapy.Field()
    lastwonat = scrapy.Field()
    isMaiden = scrapy.Field()
    ownername = scrapy.Field()
    gear = scrapy.Field()
    placing = scrapy.Field()
    finish_time = scrapy.Field()
    marginsbehindleader = scrapy.Field()
    positions = scrapy.Field()
    timelist = scrapy.Field()
    priority = scrapy.Field()
    raceday_id = scrapy.Field()
    owner_id = scrapy.Field()
    jockey_id = scrapy.Field()
    trainer_id = scrapy.Field()
    horse_id = scrapy.Field()
    race_id = scrapy.Field()
    dayssincelastrun_h= scrapy.Field()
    previousruns_car= scrapy.Field()
    previouswins_car= scrapy.Field()
    previousruns_d= scrapy.Field()
    previouswins_d= scrapy.Field()
    ranked_avgspds= scrapy.Field()
    avg_spds = scrapy.Field()
    prev_avg_spds_d= scrapy.Field()
    prev_avg_spds_cl= scrapy.Field()
    jtohweights_h= scrapy.Field()
    h_pastraces = scrapy.Field()
    l3odds= scrapy.Field()
    dayssincelastrun= scrapy.Field()
    all_runs= scrapy.Field()
    places_daysoff = scrapy.Field()
    career_roi = scrapy.Field()
    previousruns_cl = scrapy.Field()
    previouswins_cl = scrapy.Field()
    previousruns_surf = scrapy.Field()
    previouswins_surf = scrapy.Field()
    min_d = scrapy.Field()
    max_d = scrapy.Field()
    mean_d= scrapy.Field()
    min_car= scrapy.Field()
    max_car= scrapy.Field()
    mean_car= scrapy.Field()
    min_cl= scrapy.Field()
    max_cl= scrapy.Field()
    mean_cl= scrapy.Field()
    min_surf= scrapy.Field()
    max_surf= scrapy.Field()
    mean_surf= scrapy.Field()
    previous_rps= scrapy.Field()
    previous_rps_d = scrapy.Field()
    lastwonat = scrapy.Field()
    lastwonago = scrapy.Field()
    lastwonracesago = scrapy.Field()


#SECOND
class RaceItem(scrapy.Item):
    #to rd_Race
    racedate = scrapy.Field() #rd_raceid
    racenumber = scrapy.Field()
    racecoursecode = scrapy.Field()
   
    horsename = scrapy.Field() #rd_horse_id
    tips = scrapy.Field()
    naps = scrapy.Field() 
    scmp_runner_comment = scrapy.Field()
    totaljump = scrapy.Field()
    totalcanter = scrapy.Field()
    totalbarrier = scrapy.Field()
    barriertimes = scrapy.Field()
    jumptimes = scrapy.Field()
    totalswim = scrapy.Field()






   
