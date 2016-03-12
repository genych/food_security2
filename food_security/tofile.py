__author__ = "Kris"

import csv

class CSV_PUT(object):

    @staticmethod
    def csv_put_geocords(var):
        print("Sending info to CSV")
        with open('food_security.csv', 'r+', newline='') as csvfile:
            csvfile.truncate()
            infowriter = csv.writer(csvfile, delimiter=',')
            infowriter.writerow(("","Name" , "Phone Number", "Address", "Img_link", "latitude", "longitude"))
            for k, v in var:
                print(v,'\n')
                infowriter.writerow(v)
                print(v,'\n')



