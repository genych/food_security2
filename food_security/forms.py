__author__ = "Kris"


from wtforms import SelectField

from flask_wtf import Form
from bs4 import BeautifulSoup
from urllib.request import urlopen

def get_region():
    """ now unused, replaced by links_and_regions """
    URL = urlopen("http://www.arrondissement.com/plateau_mont_royal/s1-alimentation/")
    soup = BeautifulSoup(URL, "html.parser")

    #All_Links={}
    All_Regions = {}
    divisions = soup.select("ul[name=divisions_form] ul > li")
    # Selects li tags which are directly below ul tags which have the name divisions_forms
    for division in divisions:
        All_Regions[division.a.get_text(strip=True)] = [
            subitem.a.get_text(strip=True) for subitem in division.select(".divisionDDM > li")
        ]

    return All_Regions

def link_and_region_raw():
    """ gets all the links associated with places on the site using beautiful soup """
    URL = urlopen("http://www.arrondissement.com/plateau_mont_royal/s1-alimentation/")
    soup = BeautifulSoup(URL, "html.parser")

    all_links = {}
    # sets an empty dictionary
    divisions = soup.select("ul[name=divisions_form] ul > li")
    # Selects li tags which are directly below ul tags which have the name divisions_forms
    for division in divisions:
        all_links[division.a.get('href')] = [
            subitem.a for subitem in division.select(".divisionDDM > li")
        ]
    return all_links

def link_and_region_cleaner():
    """ converts the raw tag/text data from link_and_region_raw into a list containing pairs region:link """
    names_and_links=[]
    #sets an empty dictionary
    all = link_and_region_raw()
    # all is a list of partial urls like this:  >  /pointe_claire/s1-alimentation/  <
    for key in all:
        (start, middle, end) = key[1:len(key)].partition('/')
        # grabs the links from within the url using / delimeter. The first / is ignored by setting key[1]
        place_name = start.replace("_", " ")
        # strips underscores from the place names
        names_and_links.append((key, place_name))
        # adds the partial url (key) and the place name to a list
    return names_and_links


def place_name_maker(link):
    print("link is", link)
    """ extracts and normalizes a placename from within a link """
    (st, md, en) = link[1:len(link)].partition('/')
    print("key is ", link)
    place_name = st.replace("_", " ")
    return place_name


class Select_Field_Form(Form):
    """ creates a form """
    selectfield = SelectField(default="None", choices=sorted(link_and_region_cleaner()))



