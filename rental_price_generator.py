'''
This module can be used to enter in criteria for
new rental listings and receive recommended pricing
for each listing.
'''

import csv
from rental_pricing_db import *

LISTING_DATA = './challenge_data.csv'

def read_data(csv_file):
	#read rental listing data from provided csv
	csv_data = csv.reader(open(csv_file, 'r'), delimiter = ',')
	
	return csv_data

def csv_to_db(listing):
	#this function should only execute on first run
	if not listing.table_exists():
		csv_data = read_data(LISTING_DATA)
		listing.write_csv_to_db(csv_data)

def rec_price_for_no_match(listing, new_listing):
	#returns listing price based on avg price/bed
	#new_listing[0] = #beds
	all_listings = listing.fetch_all_price_bed_data()
	rec_price = round(listing.calc_avg_price_per_bed(all_listings))
	if new_listing[0] == 0:
		listing_price = rec_price
	else:
		listing_price = rec_price * new_listing[0]

	message = 'No similar listings exist. We recommend using the' \
			' average price per bedroom, %0.2f, for a total listing price' \
			' of %0.2f' % (rec_price, listing_price)
	print message

	return listing_price

def rec_price_for_similar_listing(similar_listings, listing):
	#returns listing price based on avg price of similar listings
	normalized_similar_listings = listing.remove_outliers(similar_listings)
	suggested_price = listing.calc_avg_match_price(normalized_similar_listings)

	return suggested_price

def new_listing_prompt():
	#prompts user for new listing information
	#returns list [beds,baths,sqft,name]
	new_listing = []
	rental_name = raw_input('What title do you want to give this rental listing?:  ')
	beds = raw_input('How many beds?(for studio, enter 0):  ')
	baths = raw_input('How many baths?:  ')
	sqft = raw_input('How many sqft?:  ')
	if len(beds) and len(baths) and len(sqft) and len(rental_name):
		new_listing.extend([round(float(beds)),round(float(baths)),float(sqft),rental_name])
	else:
		print 'Please enter a value for all fields.'
		new_listing = new_listing_prompt()

	return new_listing

def main():
	#open connection to db
	listing = ListingModel('listingdb')
	csv_to_db(listing)

	#new listings dictionary stores rental name and price
	new_listings = {}
	
	while (True):
		#gather new listing requirements from user	
		new_listing = new_listing_prompt()
		title = new_listing.pop()
		similar_listings = listing.get_similar(new_listing)
		if len(similar_listings) == 0:
			#if no similar listings are returned, calc price using avg $/bed
			listing_price = rec_price_for_no_match(listing, new_listing)
			new_listings[title] = listing_price
		elif len(similar_listings) == 1:
			#if only one listing matched, use same price
			new_listings[title] = float(similar_listings[0][1])
		else:
			suggested_price = rec_price_for_similar_listing(similar_listings,listing)
			new_listings[title] = suggested_price

		add_listing = raw_input('Would you like to price another rental listing?(Y/N): ')
		if add_listing.upper() == 'N' or add_listing.upper() == 'NO':
			break

	#close db connection
	listing.close_db()
	print new_listings

if __name__ == '__main__':
	main()