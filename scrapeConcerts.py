from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

#מחלקת הסורק.
class scraper_concerts:
    def __init__(self):
         None
    #פעולה שמקבלת מדינה, שהיא בעצם טאפל שכולל את שם המדינה,הדרך בה מופיעה בדפדפן, ומספר העמודים לסריקה,
    #ומחזיר 8 רשימות:שם המדינה,שנת האירוע,יום האירוע,חודש האירוע,שם האירוע,אומנים משתתפים,מקום האירוע,כתובת האירוע.כל index הוא אירוע מסוים.
    def getP1Show(self,state):
        pages=state[2]
        page=1
        years_list=[]
        states_list = []
        days_list = []
        months_list = []
        events_list = []
        artists_list = []
        venues_list = []
        addresses_list = []
        while page<=pages:
            link="https://www.songkick.com/festivals/countries/"+state[1]+"?page="+str(page)
            path = 'C:\Program Files (x86)\chromedriver.exe'
            option = webdriver.ChromeOptions()
            option.add_argument('headless')
            driver = webdriver.Chrome(path, options=option)
            driver.get(link)
            wait = WebDriverWait(driver, 30)
            page_source = driver.page_source
            driver.close()
            soup = BeautifulSoup(page_source, 'html.parser')
            all_date_and_time_tags=soup.find_all(class_="with-date")
            all_date_and_time=[]
            for date_and_time_tag in all_date_and_time_tags:
                all_date_and_time.append(date_and_time_tag.find("time").get_text())
            all_titles=[]
            for date_and_time in all_date_and_time:
                all_titles.append(soup.find(title=date_and_time))
                words=date_and_time.split()
                day=words[1]
                month=words[2]
                year=words[3]
                days_list.append(day)
                months_list.append(month)
                years_list.append(year)
            for title in all_titles:
                artists_summery=title.find(class_="artists summary")
                name_of_event=artists_summery.find("strong").get_text()
                artists=artists_summery.find("span").get_text()
                location=title.find("p",class_="location")
                venue_name=location.find("a")
                venue="not found."
                address_name=""
                if venue_name!=None:
                    venue=venue_name.get_text()
                    address_name=location.find_all("span")[1]
                else:
                    address_name=location.find("span")
                address=address_name.find("span").get_text()
                events_list.append(name_of_event)
                artists_list.append(artists)
                venues_list.append(venue)
                addresses_list.append(address)
                states_list.append(state[0])
            page=page+1
        return states_list,days_list,months_list,years_list,events_list,artists_list ,venues_list ,addresses_list
    # פעולה שמחזירה רשימות של פרטי אירועים לפי index במדינות שנבחרו בה.
    def ret_events(self):
        states_list = []
        days_list = []
        months_list = []
        years_list=[]
        events_list = []
        artists_list = []
        venues_list = []
        addresses_list = []
        states=[('United States','us',40),('United Kindom','uk',40),('Germany','de',36),('Spain','es',13),('France','fr',12),('Italy','it',5)]
        for state in states:
            current_states_list, current_days_list,current_months_list,current_years_list,current_events_list,current_artists_list,current_venues_list,current_addresses_list=self.getP1Show(state)
            states_list=states_list+current_states_list
            days_list=days_list+current_days_list
            months_list=months_list+current_months_list
            years_list=years_list+current_years_list
            events_list=events_list+current_events_list
            artists_list=artists_list+current_artists_list
            venues_list=venues_list+current_venues_list
            addresses_list=addresses_list+current_addresses_list
        return states_list,days_list,months_list,years_list,events_list,artists_list ,venues_list ,addresses_list

def main():
    h1=scraper_concerts()
    h=h1.ret_events()
    print(h[0])
    print (h[1])
    print (h[2])
    print (h[3])
    print (h[4])
    print (h[5])
    print (h[6])
if __name__ == '__main__':
     main()