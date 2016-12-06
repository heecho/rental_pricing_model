'''
This module can be used to read in a set of rental listing data,
write to a local db, and use the data to calculate recommended
prices for new rental listings.
'''
import sqlite3
import operator
import numpy as np

class ListingModel():
	#ListingModel represents a database which has one table 
	#containing historical rental listing data
	
	def __init__(self, db_file):
		self.db_file = db_file
		self.db = self.open_db()

	def open_db(self):
		#open sqlite3 db connection
		return sqlite3.connect(self.db_file)

	def close_db(self):
		#close the connection to sqlite3
		self.db.close()

	def table_exists(self):
		#check db for table, return bool
		cursor = self.db.cursor()
		cursor.execute('''SELECT name FROM sqlite_master WHERE name = ? 
			AND type = ?''', ('listing', 'table'))
		exists = cursor.fetchone()
		if exists:
			return True
		else:
			return False

	def create_table(self):
		#create db table
		cursor = self.db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS listing(listingid INTEGER PRIMARY KEY, 
			price INTEGER, num_bed INTEGER, num_bath INTEGER, sqft INTEGER) ''')
		self.db.commit()

	def create_listing(self, price, num_bed, num_bath, sqft):
		#create new row in db with listing info
		cursor = self.db.cursor()
		cursor.execute('''INSERT INTO listing(price, num_bed, num_bath, sqft) 
			VALUES(?,?,?,?)''', (price, num_bed, num_bath, sqft))
		self.db.commit()

	def write_csv_to_db(self, csv_data):
		#create db entry for each listing in csv 
		if not self.table_exists():
			self.create_table()
			for row in csv_data:
				#row[0], row[1], row[2], row[3] = price, #bed, #bath, sqft
				self.create_listing(row[0], row[1], row[2], row[3])
	
		print "Import Rental Listing Data To DB: Complete"

	def get_similar(self,new_listing):
		#query db for similar listings, return list of matches
		num_bed = new_listing[0]
		num_bath = new_listing[1]
		sqft = new_listing[2]
		cursor = self.db.cursor()
		#find all db entries with matching #bed,#bath,in range of 100sqft of new listing
		cursor.execute('''SELECT * FROM listing WHERE num_bed = ? AND num_bath = ? 
			AND sqft BETWEEN ? AND ?''',(num_bed, num_bath,sqft-50,sqft+50))
		match_listings = cursor.fetchall()
		
		return match_listings
	
	def remove_outliers(self,match_listings):
		#remove min/max values
		match_listings.sort(key = operator.itemgetter(1))
		if len(match_listings) <= 4:
			return match_listings
		else:
			remove_len = round(len(match_listings) * 0.20)
			sorted_match_listings = match_listings[int(remove_len): -int(remove_len)]
			return sorted_match_listings

	def calc_avg_match_price(self,sorted_match_listings):
		#pull prices into sorted list, return average price
		price_sum = 0
		if len(sorted_match_listings):
			for listing in sorted_match_listings:
				price_sum += listing[1]
			average = round(price_sum / (len(sorted_match_listings)))
			
			return average

	def fetch_all_price_bed_data(self):
		#query db for all price & #bed data entries
		#return list containing tuples (price,#bed)
		cursor = self.db.cursor()
		cursor.execute('''SELECT price,num_bed FROM listing''')
		all_listings = cursor.fetchall()

		return all_listings

	def calc_avg_price_per_bed(self,all_listings):
		#return the average price per bed based on all entries in db
		avg_price_per_bed_list = []
		for rental in all_listings[1:]:
			#rental[0] = price
			#rental[1] = #beds
			if rental[1] == 0:
				avg_price_per_bed_list.append(rental[0])
			else:
				price_per_bed = rental[0] / rental[1]
				avg_price_per_bed_list.append(price_per_bed)

		recommended_price_per_bed = np.mean(avg_price_per_bed_list)

		return recommended_price_per_bed

