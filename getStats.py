from selenium import webdriver
from bs4 import BeautifulSoup
import re
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.firefox.options import Options
import time

#setup the required functions
def scrollTo(driver,obj):
    """
    Used to bring object into view before clicking
    """
    driver.execute_script("return arguments[0].scrollIntoView();", obj)
    driver.execute_script("window.scrollBy(0, -150);")

    return None

def clickWait(obj,sleeping=20):
    """
    Used to click on an object and then wait for a delay
    """
    obj.click()
    time.sleep(sleeping)
    return None

def clickCheckbox(driver,var):
    """
    Used to click check boxes, when searching by id. This is necessary because
    we may need to uncheck/check boxes for specific variables
    """
    check_box = driver.find_element_by_id(var)
    if check_box.is_displayed():
        check_box.click()
    return None

def duplicateByColspan(souped):
    """
    Used to duplicate text if colspan exists. Otherwise it will return 1
    """
    if souped.attrs.__contains__('colspan'):
        return int(souped.attrs['colspan'])
    else:
        return 1

def getTextOrTitle(souped):
    """
    Used to create better headers. Sometimes a more descriptive text is imbedded
    in the title tag of the header ('th') we will try to extract it for the
    scenario that it actually exists.

    if name == 'td' then the normal text will be used
    if name == 'th' then we will use the title tag
    otherwise we will use the normal text
    """
    if souped.name == 'td':
        text = " %s," % (souped.getText())
    elif (souped.name == 'th' and souped.attrs.__contains__('title')):
        text = " %s," % (souped.attrs['title'])
    else:
        text = " %s," % (souped.getText())
    return text

def getTable(it,season,rnd,driver):
    """
    Used to get the raw table from HTML then write it to a csv file.
    """
    soup = BeautifulSoup(driver.page_source, "html.parser")
    getTable=soup.findAll(lambda tag: tag.name=='table' and
                            tag.has_attr("id") and
                            tag['id']=="team-stats")

    file_open = open('D:/AFL/Model/Data/CSVs/Team Stats by Round/%s_%s_%s.csv' % (season,rnd,it),'w')
    table_string=''

    for table in getTable:
        rows = table.findAll('tr')
        for tr in rows:
            cols = tr.findAll(['td','th'])
            table_raw ="".join([getTextOrTitle(it)*duplicateByColspan(it)
                                    for it in cols])
            table_clean = re.sub(r'(\n )+',r'\n',table_raw)
            table_string+='%s \n' % (table_clean.encode('utf-8').strip('\n'))

    file_open.write(table_string)
    file_open.close()
    return None

def clickAdvOpt(driver):
    """
    Used to find and click the advanced options tab
    """
    #xpath for advanced options - couldn't find another way to identify
    xpath_search = "//*[@id='stats-team-stats']/div[1]/div[1]/div[4]/a/span[2]"
    advopt = driver.find_element_by_xpath(xpath_search)
    while True:
        try:
            scrollTo(driver,advopt)
            clickWait(advopt,2)
            break
        except Exception as e:
            print 'advanced options not loaded'
            continue
    return None

def xpCSVs(season,rnd):
    """
    Used outside of this module to scrape the data displayed at http://www.afl.com.au/stats.
    Row by row comments are provided for educational purposes.
    """
    print '\nCollect team stats from http://www.afl.com.au/stats:'
    #setup bot-browser
    options = Options()
    #headless should render faster
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options)
    driver.get('http://www.afl.com.au/stats')

    #make use of the user defined function
    clickAdvOpt(driver)

    #identify the javascript checkboxes and turn them into a dictionary to be used later
    soup = BeautifulSoup(driver.page_source, "html.parser")
    get_checkboxes = soup.findAll('input', attrs={'type' : "checkbox"})
    default_checkbox_id = [checkbox.attrs['id'] for checkbox in list(set(get_checkboxes)) if driver.find_element_by_id(checkbox.attrs['id']).is_selected()]
    checkbox_id         = [checkbox.attrs['id'] for checkbox in list(set(get_checkboxes)) if driver.find_element_by_id(checkbox.attrs['id']).is_displayed()]
    checkbox_id_dict = {'vl1':checkbox_id[0:4],
                        'vl2':checkbox_id[4:8],
                        'vl3':checkbox_id[8:12],
                        'vl4':checkbox_id[12:16],
                        'vl5':checkbox_id[16:20],
                        'vl6':checkbox_id[20:24],
                        'vl7':checkbox_id[24:]}


    #run loop for all var in it (checkboxes on)
    for it in checkbox_id_dict:
        #this refreshes the page, which helps the javascript to display the correct information
        driver.get('http://www.afl.com.au/stats')
        driver_year = driver.find_element_by_name('year')
        for sy in driver_year.find_elements_by_tag_name('option'):
            #select the correct year
            if sy.text != str(season): continue
            clickWait(sy)
            #click the advanced option button
            clickAdvOpt(driver)
            #uncheck all default boxes
            for var in default_checkbox_id:
                clickCheckbox(driver,var)
            #check all checkboxes for vars in it
            for var in checkbox_id_dict[it]:
                clickCheckbox(driver,var)
            #select the required round
            sel_rnd = driver.find_element_by_name('round')
            for sr in sel_rnd.find_elements_by_tag_name('option'):
                    if sr.text != rnd: continue
                    clickWait(sr)
                    #scrape the data into a CSV
                    getTable(it,season,rnd,driver)
                    #send some shit to the log (for fun)
                    print '  > ' + ','.join(map(str,[i[1:] for i in checkbox_id_dict[it]])) + ' sent to CSV'

    driver.quit()

    return None