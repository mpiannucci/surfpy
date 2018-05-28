import math
import datetime
from .location import Location
import logging

class Sun:  
    """  
    Calculate sunrise and sunset based on equations from NOAA 
    http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html 
 
    typical use, calculating the sunrise at the present day: 
  
    import datetime 
    import sunrise 
    s = sun(lat=49,long=3) 
    print('sunrise at ',s.sunrise(when=datetime.datetime.now()) 
    """  
    def __init__(self, location): # default Amsterdam  
        self.location = location
    
    def sunrise(self,when=None):  
        """ 
        return the time of sunrise as a datetime.time object 
        when is a datetime.datetime object. If none is given 
        a local time zone is assumed (including daylight saving 
        if present) 
        """  
        if when is None: 
            when = datetime.datetime.now()  
        self.__preptime(when)  
        self.__calc()  
        return Sun.__timefromdecimalday(self.sunrise_t)
    
    def sunset(self,when=None):  
        if when is None: 
            when = datetime.datetime.now()  
        self.__preptime(when)  
        self.__calc()  
        return Sun.__timefromdecimalday(self.sunset_t)
    
    def solarnoon(self,when=None):  
        if when is None: 
            when = datetime.datetime.now()  
        self.__preptime(when)  
        self.__calc()  
        return Sun.__timefromdecimalday(self.solarnoon_t)  
   
    @staticmethod  
    def __timefromdecimalday(day):  
        """ 
        returns a datetime.time object. 
   
        day is a decimal day between 0.0 and 1.0, e.g. noon = 0.5 
        """  
        hours = 24.0*day  
        h = int(hours)
        minutes = (hours-h)*60  
        m = int(minutes)  
        seconds = (minutes-m)*60  
        s = int(seconds)
        if h > 23:
            h = 0
        return datetime.time(hour=h,minute=m,second=s)  
  
    def __preptime(self,when):  
        """ 
        Extract information in a suitable format from when,  
        a datetime.datetime object. 
        """  
        # datetime days are numbered in the Gregorian calendar  
        # while the calculations from NOAA are distibuted as  
        # OpenOffice spreadsheets with days numbered from  
        # 1/1/1900. The difference are those numbers taken for   
         # 18/12/2010  
        self.day = when.toordinal()-(734124-40529)  
        t=when.time()  
        self.time= (t.hour + t.minute/60.0 + t.second/3600.0)/24.0  
    
        self.timezone=0  
        offset=when.utcoffset()  
        if not offset is None:  
            self.timezone=offset.seconds/3600.0  
    
    def __calc(self):  
        """ 
        Perform the actual calculations for sunrise, sunset and 
        a number of related quantities. 
   
        The results are stored in the instance variables 
        sunrise_t, sunset_t and solarnoon_t 
        """  
        timezone = self.timezone # in hours, east is positive  
        longitude = self.location.adjusted_longitude     # in decimal degrees, east is positive  
        latitude = self.location.adjusted_latitude     # in decimal degrees, north is positive  
  
        time = self.time  # percentage past midnight, i.e. noon  is 0.5  
        day = self.day     # daynumber 1=1/1/1900  
   
        Jday = day+2415018.5+time-timezone/24 # Julian day  
        Jcent = (Jday-2451545)/36525    # Julian century  
  
        Manom    = 357.52911+Jcent*(35999.05029-0.0001537*Jcent)  
        Mlong    = 280.46646+Jcent*(36000.76983+Jcent*0.0003032)%360  
        Eccent   = 0.016708634-Jcent*(0.000042037+0.0001537*Jcent)  
        Mobliq   = 23+(26+((21.448-Jcent*(46.815+Jcent*(0.00059-Jcent*0.001813))))/60)/60  
        obliq    = Mobliq+0.00256*math.cos(math.radians(125.04-1934.136*Jcent))  
        vary     = math.tan(math.radians(obliq/2))*math.tan(math.radians(obliq/2))  
        Seqcent  = math.sin(math.radians(Manom))*(1.914602-Jcent*(0.004817+0.000014*Jcent))+math.sin(math.radians(2*Manom))*(0.019993-0.000101*Jcent)+math.sin(math.radians(3*Manom))*0.000289  
        Struelong= Mlong+Seqcent  
        Sapplong = Struelong-0.00569-0.00478*math.sin(math.radians(125.04-1934.136*Jcent))  
        declination = math.degrees(math.asin(math.sin(math.radians(obliq))*math.sin(math.radians(Sapplong))))  
    
        eqtime   = 4*math.degrees(vary*math.sin(2*math.radians(Mlong))-2*Eccent*math.sin(math.radians(Manom))+4*Eccent*vary*math.sin(math.radians(Manom))*math.cos(2*math.radians(Mlong))-0.5*vary*vary*math.sin(4*math.radians(Mlong))-1.25*Eccent*Eccent*math.sin(2*math.radians(Manom)))  
  
        hourangle= math.degrees(math.acos(math.cos(math.radians(90.833))/(math.cos(math.radians(latitude))*math.cos(math.radians(declination)))-math.tan(math.radians(latitude))*math.tan(math.radians(declination))))  
  
        self.solarnoon_t=(720-4*longitude-eqtime+timezone*60)/1440  
        self.sunrise_t =self.solarnoon_t-hourangle*4/1440  
        self.sunset_t =self.solarnoon_t+hourangle*4/1440  