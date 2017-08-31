#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developer: Andrew Kirfman & Cuong Do                                         #
# Project: Dividend Stripper Application                                       #
#                                                                              #
# File ./dividend_stripper.py                                                  #
# ---------------------------------------------------------------------------- #

import sys
import requests
import calendar
import time

# BeautifulSoup HTML parsing library
from bs4 import BeautifulSoup, SoupStrainer

# yahoo-finance package
from yahoo_finance import Share

# Proxy generator
sys.path.append("./request_proxy/")
from http.requests.proxy.requestProxy import RequestProxy

# Contain all data in a MySQL database
import MySQLdb

# Database login information.  Change this to fit your own parameters
DB_HOST="127.0.0.1"
DB_USER="root"
DB_PASSWD="drew11"
DB_STOCK_DATABASE="primary_stocks"

# The current year.  I promise that this define makes sense
CURRENT_YEAR = 2017

# Month conversions
MONTHS = {'jan' : '1',
          'feb' : '2',
          'mar' : '3',
          'apr' : '4',
          'may' : '5',
          'jun' : '6',
          'jul' : '7',
          'aug' : '8',
          'sep' : '9',
          'oct' : '10',
          'nov' : '11',
          'dec' : '12'
         }

# Number of days in each month
days_per_month = {'1' : '31',
                  '2' : '28',
                  '3' : '31',
                  '4' : '30',
                  '5' : '31',
                  '6' : '30',
                  '7' : '31',
                  '8' : '31',
                  '9' : '30',
                  '10' : '31',
                  '11' : '30',
                  '12' : '31'
                  }

# The name to give the upcoming Ex-dividend dates file
UPCOMING_EX_DATES = "./upcoming_ex_dates.txt"

# Function to account for leap years
def get_days_per_month(month, year):
    if month != '2' or (month == '2' and not calendar.isleap(int(year))):
        return days_per_month[month]
    else:
        return '29'

# This is kind of a stupid function.  It's just supposed to subtract one day
# from a date string.
def subtract_one_day(date_string):
    date = date_string.split('-')
    year = date[0]
    month = date[1]
    day = date[2]

    # If the day is greater than 1, no problem.  Just subtract one
    if int(day) > 1:
        day = str(int(day) - 1)
    # If the day is 1, the day I set it to depends on the month
    elif (int(day) == 1):
        pass
        month = str(int(month) - 1)
        day = get_days_per_month(month, year)

    return "%s-%s-%s" % (year, month, day)


def update_ex_div_dates(req_proxy):
    save_stdout = sys.stdout
    dev_null = open("/dev/null", "w")
    sys.stdout = dev_null

    upcoming_ex_data = None
    while upcoming_ex_data is None:
        upcoming_ex_data = req_proxy.generate_proxied_request("http://dividata.com/dividates")

    dev_null.close()
    sys.stdout = save_stdout

    # Parse result from requests.get()

    upcoming_ex_soup = BeautifulSoup(upcoming_ex_data.text, 'html5lib')

    # The day titles are stored in thead sections.  All of the odd titles are useless.
    # Filter them out
    ex_dates = []
    iterator = 0
    for date in upcoming_ex_soup.find_all('thead'):
        # Is the index even?  If it is, save the date
        if iterator % 2 == 0:
            ex_dates.append(date.text)

        iterator = iterator + 1

    ex_data_per_date = []

    for set_of_stocks in upcoming_ex_soup.find_all('tbody'):
        ex_data_per_date.append([(stock.find_all('td')[0].text, stock.find_all('td')[1].text, stock.find_all('td')[2].text,\
            stock.find_all('td')[3].text, stock.find_all('td')[4].text, stock.find_all('td')[5].text)\
            for stock in set_of_stocks.find_all('tr')])

    # Open the file to write the dividend data to
    dividend_file = open(UPCOMING_EX_DATES, "w+")

    iterator = 0
    for day in ex_data_per_date:
        dividend_file.write("Date: " + ex_dates[iterator] + "\n")

        for stock in day:
            dividend_file.write("%s, %s, %s, %s, %s, %s\n" % (stock[0], stock[1], stock[2], stock[3], stock[4], stock[5]))

        iterator = iterator + 1

    dividend_file.close()

class stock_database:
    def __init__(self):
        self.database_object = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWD)

        # Attempt to use the existing stock database
        if self.issue_db_command("USE %s;" % DB_STOCK_DATABASE) is False:
            result = self.issue_db_command("CREATE DATABASE %s;" % DB_STOCK_DATABASE)

            # Need to handle an error here.  Right now, if the database fails,
            # just terminate the program with an error
            if result is False:
                print "[ERROR]: Could not use the correct database."
                sys.exit(1)

            result = self.issue_db_command("USE %s;" % DB_STOCK_DATABASE)

            if result is False:
                print "[ERROR]: Could not use the correct database.  Create command failed."
                sys.exit(1)


    def issue_db_command(self, cmd):
        """
        Issue a generic command denoted by cmd to the database.  Performs basic error checking
        and loggs the result.  Returns the result of the command or False if it failed.

        """

        current_pointer = self.database_object.cursor()

        try:
            # Execute the command
            result = current_pointer.execute(cmd)

            self.database_object.commit()

            return current_pointer.fetchall()
        except Exception as e:
            # Replace this with a logger call
            print "[ERROR]: Could not execute command: " + "\n"\
                + "  - Message " + str(e[1]) + "\n"\
                + "  - Command: " + str(cmd)

            return False

class dividend_stripper:
    def __init__(self):
        self.stock_database = stock_database()

    def update_ex_div_dates(req_proxy):
        save_stdout = sys.stdout
        dev_null = open("/dev/null", "w")
        sys.stdout = dev_null

        upcoming_ex_data = None
        while upcoming_ex_data is None:
            upcoming_ex_data = req_proxy.generate_proxied_request("http://dividata.com/dividates")

        dev_null.close()
        sys.stdout = save_stdout

        # Parse result from requests.get()
        upcoming_ex_soup = BeautifulSoup(upcoming_ex_data.text, 'html5lib')

        # The day titles are stored in thead sections.  All of the odd titles are useless.
        # Filter them out
        ex_dates = []
        iterator = 0
        for date in upcoming_ex_soup.find_all('thead'):
            # Is the index even?  If it is, save the date
            if iterator % 2 == 0:
                ex_dates.append(date.text)

            iterator = iterator + 1

        ex_data_per_date = []

        for set_of_stocks in upcoming_ex_soup.find_all('tbody'):
            ex_data_per_date.append([(stock.find_all('td')[0].text, stock.find_all('td')[1].text, stock.find_all('td')[2].text,\
                stock.find_all('td')[3].text, stock.find_all('td')[4].text, stock.find_all('td')[5].text)\
                for stock in set_of_stocks.find_all('tr')])

        # Open the file to write the dividend data to
        dividend_file = open(UPCOMING_EX_DATES, "w+")

        iterator = 0
        for day in ex_data_per_date:
            dividend_file.write("Date: " + ex_dates[iterator] + "\n")

            for stock in day:
                dividend_file.write("%s, %s, %s, %s, %s, %s\n" % (stock[0], stock[1], stock[2], stock[3], stock[4], stock[5]))

            iterator = iterator + 1

        dividend_file.close()

class stock_database:
    def __init__(self):
        pass



def main(argc, argv):
    pass
    

def strip_dividends(ticker, req_proxy):

    return_html = "<table class=\"table\">"\
                    + "<thead>"\
                    +     "<tr>"\
                    +     "<th>Ex Dividend Date</th>"\
                    +     "<th>Previous Day Close</th>"\
                    +     "<th>Ex Dividend Day Close</th>"\
                    +     "<th>Ex Dividend Day High</th>"\
                    +     "<th>Dividend Payout</th>"\
                    +   "</tr>"\
                    + "</thead>"\
                    + "<tbody>"
                    
    # Template for dividend requests: 
    # http://dividata.com/stock/XOM/dividend

    ex_dividend_data = None

    # The requests proxy library sometimes throws some weird exceptions.  If that happens, break out of
    # the loop and don't do anything.
    skip = False
    while ex_dividend_data is None:
        try:
            ex_dividend_data = None

            if req_proxy is not None:
                ex_dividend_data = req_proxy.generate_proxied_request("http://dividata.com/stock/%s/dividend" % ticker)
            else:
                ex_dividend_data = requests.get("http://dividata.com/stock/%s/dividend" % ticker)

            if ex_dividend_data is not None:
                if ex_dividend_data.status_code == 404:
                    raise
                
                if ex_dividend_data.status_code != 200:
                    ex_dividend_data = None
        
        except Exception as e:
            return return_html + "</tbody></table>"
            skip = True
            break

    # If something went wrong collecting data, just go on to the next ticker
    if skip is True:
        return return_html + "</tbody></table>"

    # Parse it using BeautifulSoup
    ex_dividend_soup = BeautifulSoup(ex_dividend_data.text, 'html5lib');

    # Extract the dates and dividend amounts for each stock.
    ex_dividend_history = []
    ex_dividend_soup = ex_dividend_soup.find_all("tr")

    # The first element in the list is useless, get rid of it
    # Figure out a better way to deal with this
    first = True

    # Make a nice data structure containing the dates
    for ex_div in ex_dividend_soup:
        if first == True:
            first = False
            continue

        div_element = ex_div.find_all('td')

        date = div_element[0].text.replace(",", "")
        date = date.lower().split(" ")

        # If the year is greater than 5 years ago, break.  Yahoo finance
        # doesn't have history going back that far
        if (CURRENT_YEAR - 5) > int(date[2]):
            break

        date = "%s-%s-%s" % (date[2], MONTHS[date[0]], date[1])

        amount = float(div_element[1].text.replace("$", ""))

        ex_dividend_history.append((date, amount))

    # Get share data for each ex-dividend date.  Get the price on that day
    # and the price the day before.
    ticker_share = Share(ticker)

    ex_dividend_stock_prices = []

    for ex_div in ex_dividend_history:

        try:
            ex_dividend_stock_prices.append((ticker_share.get_historical(subtract_one_day(ex_div[0]),
                ex_div[0]), ex_div[1]))
        except Exception as e:
            import code; code.interact(local=locals())

        time.sleep(0.1)

    # Now, see if the stock price actually recovered the day after the dividend got paid out
    for dividend_event in ex_dividend_stock_prices:

        # Some of the dividend_events have a length of only 1.  Figure out why this is later on
        if len(dividend_event[0]) != 2:
            continue

        try:
            dividend_payout = float(dividend_event[1])
            pre_dividend_close = float(dividend_event[0][1]['Close'])
            post_dividend_open = float(dividend_event[0][1]['Open'])
            post_dividend_h = float(dividend_event[0][0]['High'])
            post_dividend_high = float(dividend_event[0][0]['Close'])
            ex_div_day = dividend_event[0][1]['Date']
            
            if post_dividend_open == post_dividend_h:
                post_dividend_h = post_dividend_high

        except Exception as e:
            print "What went wrong: " + str(e)
            
            return return_html + "</tbody></table>"

        # Make sure that we would make at least 10 cents per share
        if((pre_dividend_close + 0.10) < (post_dividend_high + dividend_payout)):
            return_html = return_html + "<tr class=\"table-success\" style=\"background-color: #dff0d8;\">"\
                        +   "<td>" + str(ex_div_day) + "</td>"\
                        +   "<td>" + "%.2f" % float(pre_dividend_close) + "</td>"\
                        +   "<td>" + "%.2f" % float(post_dividend_high) + "</td>"\
                        +   "<td>" + "%.2f" % float(post_dividend_h) + "</td>"\
                        +   "<td>" + "%.2f" % float(dividend_payout) + "</td>"\
                        + "</tr>"
        else:
            return_html = return_html + "<tr class=\"table-danger\" style=\"background-color: #F2DEDE;\">"\
                        +   "<td>" + str(ex_div_day) + "</td>"\
                        +   "<td>" + "%.2f" % float(pre_dividend_close) + "</td>"\
                        +   "<td>" + "%.2f" % float(post_dividend_high) + "</td>"\
                        +   "<td>" + "%.2f" % float(post_dividend_h) + "</td>"\
                        +   "<td>" + "%.2f" % float(dividend_payout) + "</td>"\
                        + "</tr>"            
    
    # Finally, return the result html
    return str(return_html)



if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
