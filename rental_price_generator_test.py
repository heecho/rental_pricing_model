import unittest
from rental_pricing_db import *
from rental_price_generator import *

class TestRentalDB(unittest.TestCase):
	def test_table_exists(self):
		listing = ListingModel('listingdb')
		result = listing.table_exists()
		listing.close_db()
		self.assertEqual(type(result), bool)

	def test_get_similar(self):
		listing = ListingModel('listingdb')
		new_listing = [2,2,1250]
		result = listing.get_similar(new_listing)
		listing.close_db()
		self.assertTrue(len(result) > 0)

	def test_get_similar_no_match(self):
		listing = ListingModel('listingdb')
		new_listing = [12,2,125]
		result = listing.get_similar(new_listing)
		listing.close_db()
		self.assertEqual(result, [])

	def test_remove_outliers(self):
		listing = ListingModel('listingdb')
		match_listings = [(1200,0,1,600), (2850,2,2,1250)]
		result = listing.remove_outliers(match_listings)
		listing.close_db()
		self.assertEqual(len(result), len(match_listings))

	def test_calc_avg_match_price(self):
		listing = ListingModel('listingdb')
		similar_listings = [(1,900,0,1,600), (2,1600,2,2,1250), (3,500,0,1,450)]
		result = listing.calc_avg_match_price(similar_listings)
		listing.close_db()
		self.assertEqual(result, 1000)

class TestRentalPriceGen(unittest.TestCase):
	def test_read_data(self):
		result = read_data(LISTING_DATA)
		self.assertTrue(type(result), list)

	def test_rec_price_for_no_match(self):
		listing = ListingModel('listingdb')
		result = rec_price_for_no_match(listing, [0,12,450])
		listing.close_db()
		self.assertEqual(result, 1447.0)

	def test_rec_price_for_similar_listing(self):
		listing = ListingModel('listingdb')
		result = rec_price_for_similar_listing([(1,1875,0,1,801), 
			(2,2200,0,1,720)], listing)
		listing.close_db()
		self.assertEqual(result, 2037)

if __name__ == '__main__':
    unittest.main()