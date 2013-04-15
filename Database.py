import sqlite3 as lite


class Database:

	def __init__(self):
		self.conn = lite.connect("panorama.db")
	
	def addPropertyLabel( self, property, label ):
		query = "INSERT INTO properties VALUES ('"+ property +"', '"+label+"' )"
		cursor = self.conn.cursor()
		cursor.execute(query)
		self.conn.commit()

	def addResourceLabel( self, resource, label ):
		query = "INSERT INTO resources VALUES ('"+ resource +"', '"+label+"' )"
		cursor = self.conn.cursor()
		cursor.execute( query )
		self.conn.commit()
	
	def getResourceLabel( self, resource ):
		query = "SELECT label FROM resources WHERE resource = '" + resource +"'"
		cursor = self.conn.cursor()
		cursor.execute( query )
		row = cursor.fetchone()

		if row == None:
			return None
		else:
			return row[0]
	
	def getPropertyLabel( self, property ):
		query = "SELECT label FROM properties WHERE property = '" + property +"'"
		cursor = self.conn.cursor()
		cursor.execute( query )
		row = cursor.fetchone()
		
		if row == None:
			return None
		else:
			return row[0]

	def __del__( self ):
		self.conn.close()
