import mysql.connector
# https://www.youtube.com/watch?v=-YU36D7oTLA

mydb = mysql.connector.connect(user='test',
	password='test',
	database="mylbinv",
	host='127.0.0.1',
	auth_plugin='mysql_native_password')

print(mydb)
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE parts (partID VARCHAR(256), qtyOnHand INTEGER(6), rev VARCHAR(4), dimXmm INTEGER (4), dimYmm INTEGER(4))")
# for tb in mycursor:
	# print tb
