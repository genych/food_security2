__author__ = "Kris"
from bs4 import BeautifulSoup
from urllib.request import urlopen
from unicodedata import normalize
from food_security.tofile import CSV_PUT
import json
# google geocode api key :AIzaSyB9Nd9VVUv2AeW-cLegNm17GPlLOzx_A6w
# google maps geocode request: https://maps.googleapis.com/maps/api/geocode/xml?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY
import string
class Data_Miner(object):
    BASELINK = 'http://www.arrondissement.com'

    @staticmethod
    def make_full_link(partial_link):
        """ takes the partial regional link and completes it """
        full_link = Data_Miner.BASELINK + partial_link.replace("'", "")
        return full_link

    @staticmethod
    def get_all_links(complete_link):
        """ uses the completed regional link to find all links to services in that region """
        URL = urlopen(Data_Miner.make_full_link(complete_link))
        soup = BeautifulSoup(URL, "html.parser").find_all('a', class_="title")

        Data_Miner.find_service_addresses(soup)

    @staticmethod
    def find_service_addresses(soup):
        """ creates a list containing only the links to th e services of the chosen region """
        all_links=[]
        serv_number=0
        for item in soup:

            (start, middle, end) = str(item).partition('href="')
            (start2, middle2, end2) = end.partition('" ')
            all_links.append(Data_Miner.BASELINK + start2)

        Data_Miner.parse_address(all_links)

    @staticmethod
    def parse_address(all_links):
        """ Finds the address for each service """
        services =[]
        serv_number = 1
        for link in all_links:
            #print("the service link is ", link)
            URL=urlopen(link)
            soup = BeautifulSoup(URL,"html.parser").find(class_="publication")
            #print("content 0 of that link is", soup.contents[0])
            #print("content 1 of that link is", soup.contents[1])
            #print("content 2 of that link is", soup.contents[2])
            #print("content 3 of that link is", soup.contents[3])
            if isinstance(soup.contents[2], str):
                # if their is an address and an image then the address should be here
                address_location_in_tags = soup.contents[2]
            elif isinstance(soup.contents[1], str):
                # if their is an address but no image, then the address should be here
                address_location_in_tags = soup.contents[1]
            else:
                address_location_in_tags = "No address"


            try:
            # looks for img tag (most services don't have one)
                image_link= Data_Miner.BASELINK + soup.img["src"]
            except:
                image_link="No Image Found"
                pass

            service_geo_coords = Data_Miner.geocode_addresses(address_location_in_tags)
            # returns coords as dictionary
            service_name = soup.find(class_="maintitle").get_text().title()
            # Finds client service name, uppercases the first letters
            service_phone = soup.find(class_="phonefaxline").get_text()
            # finds service phone number (messy)
            (st, md, en) = service_phone.partition(" ")
            en = en[:12]
            service_address = address_location_in_tags
            # returns service address

            services.append([("client{}".format(serv_number)) , (serv_number,
                                                                 service_name,
                                                                 en, service_address,
                                                                 image_link,
                                                                 service_geo_coords['lat'],
                                                                 service_geo_coords['lon'])])
            serv_number += 1
            # appends to a dict containing all client info in the same order as the headers in the csv

            Data_Miner.client_info_printer(service_name,
                                           en,
                                           service_address,
                                           image_link,
                                           service_geo_coords)
            # sends client info to get printed in the console




        CSV_PUT.csv_put_geocords(services)
        # After for-loop sends services dict to csv to get written

    @staticmethod
    def client_info_printer(service_name, en, service_address, image_link, service_geo_coords):
        """ Prints the service info into the console """
        print("----------------------------------------------------------------------------------------------\n"
              "Service name is: {} \n"
              "Service phone number is: {}\n"
              "Service address is: {}\n"
              "Service image_link is {}\n"
              "Longitude is: {}\n"
              "Latitude is: {}\n"
              "-----------------------------------------------------------------------------------------------\n"
              "".format(service_name, en, service_address, image_link, service_geo_coords['lat'], service_geo_coords['lon']))


    @staticmethod
    def geocode_addresses(address_location_in_tags):
        google_link_start = "https://maps.googleapis.com/maps/api/geocode/json?address="
        google_link_end = "key=AIzaSyB9Nd9VVUv2AeW-cLegNm17GPlLOzx_A6w"

        gooch = Data_Miner.accent_remover(address_location_in_tags)
        #print(google_link_start + gooch + google_link_end)
        geocode_request = urlopen(google_link_start + gooch + google_link_end)
        # send to google geocoder api
        soup = BeautifulSoup(geocode_request, "html.parser")
        make_string=str(soup)
        # turns the resulting JSON page into a soup

        if len(make_string) < 200:
            gooch = gooch[gooch.find("Qc"):999]
            geocode_request = urlopen(google_link_start + gooch + google_link_end)
            soup = BeautifulSoup(geocode_request,"html.parser")
            make_string=str(soup)

        lat_start = make_string.find('"lat" : ')
        lat_end = make_string.find(',', lat_start)
        lng_start = make_string.find('"lng" : ')
        lng_end = make_string.find(',', lng_start)


        latitude = make_string[lat_start + 8: lat_end].strip(" ").strip("}")
        longitude = make_string[lng_start + 8: lng_end].strip(" ").strip("}")
        #print(latitude, longitude)
        try:
            float(latitude)
        except:
            latitude = 0

        try:
            float(longitude)
        except:
            longitude = 0

        latitude = float(latitude)
        longitude = float(longitude)
        geo_coords={'lat': latitude, 'lon': longitude}

        return geo_coords
        #print("The lat and long are: ", latitude, ", ", longitude)
        #print("\n------------------------------------------------------------\n")



    @staticmethod
    def accent_remover(address_location_in_tags):
            accent_strip_stage1 = normalize("NFKD", address_location_in_tags)
            accent_strip_stage2 = accent_strip_stage1.encode('ASCII', 'ignore')
            gooch = accent_strip_stage2.decode(errors='ignore').replace(" ", "+")
            gooch = gooch.replace(',', '', 1).replace('boul', 'Boulevard').replace('QC', 'Quebec,+Canada').replace('Nord', 'North')
            (start, middle, end) = gooch.partition("Canada")

            return(start)


    @staticmethod
    def get_phone_numbers(all_links):
        pass

    @staticmethod
    def get_coords(all_links):
        #URL = urlopen(all_links[1])
        #soup = BeautifulSoup(URL,"html.parser")
        #print(soup.prettify())
        """
       for link in all_links:
            print(link)
            URL = link
            soup = BeautifulSoup(URL,"html.parser")
            print(soup)"""

    @staticmethod
    def get_phone_addresses(complete_link):
        pass