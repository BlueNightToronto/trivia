import discord, csv, datetime, time
from discord.ext import commands
from cogs.utils import checks

from urllib.request import urlopen # Web library
from xml.dom import minidom # Library for parsing XML stuff
import os, asyncio, json, locale, math

locale.setlocale(locale.LC_ALL, 'en_CA.UTF-8')

class njc:
	"""Bot for the NJC server!"""

def setup(bot):
	bot.add_cog(njc(bot))


class njc:
	"""Components for NJC\nRelevant data copyright Toronto Transit Commission 2018."""

	def __init__(self, bot):
		self.bot = bot
		self.channelstatus = 587754803166183424 #bot-console
		self.channelID = 587754803166183424 #bot-console
		self.channelID1 = 587754803166183424 #bot-console
		self.channelID2 = 587754803166183424 #bot-console
		self.channelID3 = 587754803166183424 #bot-console
		self.channelID4 = 587754042340409416 #bot-console-checker
		self.channelID5 = 587754042340409416 #bot-console-checker
		self.backupID = 537718582256336940 #bot-lab
		self.scanInterval = 300
		self.looping = False

	@commands.command()
	async def kirby(self):
		data = discord.Embed(title="Join NJC")
		data.set_image(url="https://i.imgur.com/CRugTWf.png")
		await self.bot.say(embed=data)

	@commands.command()
	async def routeveh(self, rte):
		"""Checks vehicles on a route."""
		data = discord.Embed(title="Vehicles on Route " + rte, description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=8388608))

		url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=ttc&r=" + rte
		mapurl = "https://maps.googleapis.com/maps/api/staticmap?format=png8&zoom=~2&scale=2&size=256x256&maptype=roadmap&format=png&visual_refresh=true&key=AIzaSyBwzgxqLQV91ERZjAlmrJO0yGNd7GxYOlo"
		raw = urlopen(url).read() # Get page and read data
		decoded = raw.decode("utf-8") # Decode from bytes object
		parsed = minidom.parseString(decoded) # Parse with minidom to get XML stuffses
		service = ""
		vehs = int('0')
		vehicles = parsed.getElementsByTagName('vehicle') # Get all tags called 'vehicle'

		for i in vehicles: # For each vehicle found
			veh = i.attributes['id'].value # GETS VEHICLE
			lat = i.attributes['lat'].value # GETS LAT
			lon = i.attributes['lon'].value # GETS LONG
			hea = int(i.attributes['heading'].value) # GETS COMPASS
			service = service + veh + ", " # GETS VEHICLE
			vehs = vehs + int('1')

			if vehs <= int('27'):
				if hea == int('-4'): #label based on compass
					if vehs < int('20'):
						mapurl = mapurl + "&markers=size:mid%7Ccolor:0x000000%7Clabel:O%7C{},{}".format(lat, lon)
				elif hea > int('405'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0x000000%7Clabel:O%7C{},{}".format(lat, lon)
				elif hea > int('315'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0xff0000%7Clabel:N%7C{},{}".format(lat, lon)
				elif hea > int('225'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0xffff00%7Clabel:W%7C{},{}".format(lat, lon)
				elif hea > int('135'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0x0000ff%7Clabel:S%7C{},{}".format(lat, lon)
				elif hea > int('45'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0x00ffff%7Clabel:E%7C{},{}".format(lat, lon)
				else:
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0xff0000%7Clabel:N%7C{},{}".format(lat, lon)

		data.add_field(name="Vehicles", value=service)
		data.set_image(url=mapurl)
		data.set_footer(text="Map only shows up to 27 vehicles at a time. The map is intended to give you an idea of route headways.")


		if service == "":
			await self.bot.say("No vehicles could be found on route {}.".format(rte))
		else:
			try:
				await self.bot.say(embed=data)
			except Exception as errer:
				await self.bot.say("An error occured: `{}`".format(errer))
			return

	@commands.command()
	async def vehicle(self, veh):
		"""Checks information for a selected TTC vehicle."""

#        url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=ttc&t=3000"
		url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocation&a=ttc&v=" + veh
		raw = urlopen(url).read() # Get page and read data
		decoded = raw.decode("utf-8") # Decode from bytes object
		parsed = minidom.parseString(decoded) # Parse with minidom to get XML stuffses
		vehicles = parsed.getElementsByTagName('vehicle') # Get all tags called 'vehicle'
		for i in vehicles: # Loop through these

			service = i.attributes['id'].value # GETS VEHICLE
			if veh == service: # IF MATCHING VEHICLE FOUND
				try:
					dirtag = i.attributes['dirTag'].value # Direction Tag
				except:
					dirtag = str("N/A")
				hea = int(i.attributes['heading'].value) # Compass Direction
				updated = i.attributes['secsSinceReport'].value # Seconds since last updated
				lat = i.attributes['lat'].value #latitude
				lon = i.attributes['lon'].value # lon

				try:
					vision = i.attributes['speedKmHr'].value
				except:
					lon = i.attributes['lon'].value # lon

				try:
					find = i.attributes['routeTag'].value #routetag
					url5 = "http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=ttc"
					raw5 = urlopen(url5).read() # Get page and read data
					decoded5 = raw5.decode("utf-8") # Decode from bytes object
					parsed5 = minidom.parseString(decoded5) # Parse with minidom to get XML stuffses
					route = parsed5.getElementsByTagName('route') # Get all tags called 'vehicle'

					for i in route: # Loop through these
						routag = i.attributes['tag'].value
						if routag == find: # IF MATCHING VEHICLE FOUND
							offroute = i.attributes['title'].value
				except:
					offroute = str("No Route")


				#LOADS FLEET INFO
				try:
					listfleet = open("cogs/njc/fleets/ttc.csv")
					readerfleet = csv.reader(listfleet,delimiter="	")
					linefleet = []
				except:
					await self.bot.say("I couldn't find the file.")
					return

				vehicle = "Test object"
				try:
					for row in readerfleet:
						if str(row[0]) == veh:
							linefleet = row

						# IF OK, THIS IS WHAT IS OUTPUTTED
					listfleet.close()

					data = discord.Embed(title="Vehicle Tracking for TTC {} - {} {}".format(veh,linefleet[2],linefleet[3]), description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=16711680))
				except Exception as errer:
					await self.bot.say("<@&536303913868197898> - Unknown vehicle, add it to the database. `{}`".format(errer))
					data = discord.Embed(title="Vehicle Tracking for TTC {} - UNKNOWN VEHICLE".format(veh), description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=16580352))


				try: # TRIES FETCHING DATA
					taglist = open("cogs/njc/dirTag.csv")
					reader = csv.reader(taglist,delimiter="	")
					line = []
				except Exception as errer:
					await self.bot.say("dirTag.csv not found!\n`" + str(errer) + "`")
					return

				try: # GETS INFO FROM FILE
					for row in reader:
						if str(row[0]) == dirtag:
							line = row

					# IF OK, THIS IS WHAT IS OUTPUTTED
					taglist.close()
					

					if dirtag == str("N/A"):
						try:
							data = discord.Embed(title="Vehicle Tracking for TTC {} - {} {}".format(veh,linefleet[2],linefleet[3]), description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=0))
							data.add_field(name="Off Route", value=offroute)
						except:
							data.add_field(name="Off Route", value="*Not in service?*") 
					else:
						if str(linefleet[4]) not in str(line[6]):
							await self.bot.say(":rotating_light: Branch divisions don't match vehicle division!")
							data = discord.Embed(title="Vehicle Tracking for TTC {} - {} {}".format(veh,linefleet[2],linefleet[3]), description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=5604737))
						data.add_field(name="On Route", value=line[1])  
						data.add_field(name="Currently on Branch", value="`{}`".format(dirtag))  
						data.add_field(name="Starts from", value=line[2])
						data.add_field(name="Ends at", value=line[3])
						data.add_field(name="Sign", value=line[4])
						data.add_field(name="Branch Notes", value=line[5])
						data.add_field(name="Branch Divisions", value=line[6])
		
					try:
						data.add_field(name="Vehicle Division", value=linefleet[4])
						data.add_field(name="Vehicle Status", value=linefleet[6])
					except:
						data.add_field(name="Vehicle Division", value="Unknown")
						data.add_field(name="Vehicle Status", value="Unknown")
				except Exception as errer:
#                    await self.bot.say("dirTag.csv not found!\n`" + str(errer) + "`")
					data.add_field(name="On Route", value="No route")  
					data.add_field(name="Currently on Branch", value="`{}`".format(dirtag))  
					data.add_field(name="Starts from", value="Unknown")
					data.add_field(name="Ends at", value="Unknown")
					data.add_field(name="Sign", value="Unknown")
					data.add_field(name="Branch Notes", value="Unknown")
					await self.bot.say(":question: Unknown branch, add it to the database. `{}`".format(errer))

				data.add_field(name="Compass", value="Facing {} ({}°)".format(*[(["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest", "north", "disabled"][i]) for i, j in enumerate([range(0, 30), range(30, 68), range(68, 113), range(113, 158), range(158, 203), range(203, 248), range(248, 293), range(293, 338), range(338, 360),range(-10, 0)]) if int(hea) in j],hea)) # Obfuscation? Fun, either way
				try:
					vision = vision
					data.add_field(name="VISION Equipped?", value="**Yes!**")
				except:
					data.add_field(name="VISION Equipped?", value="No")

				mapurl = "https://maps.googleapis.com/maps/api/staticmap?format=png8&zoom=15&scale=2&size=256x256&maptype=roadmap&format=png&visual_refresh=true&key=AIzaSyBwzgxqLQV91ERZjAlmrJO0yGNd7GxYOlo"

				if hea == int('-4'): #label based on compass
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0x000000%7Clabel:O%7C{},{}".format(lat, lon)
				elif hea > int('405'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0x000000%7Clabel:O%7C{},{}".format(lat, lon)
				elif hea > int('315'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0xff0000%7Clabel:N%7C{},{}".format(lat, lon)
				elif hea > int('225'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0xffff00%7Clabel:W%7C{},{}".format(lat, lon)
				elif hea > int('135'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0x0000ff%7Clabel:S%7C{},{}".format(lat, lon)
				elif hea > int('45'):
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0x00ffff%7Clabel:E%7C{},{}".format(lat, lon)
				else:
					mapurl = mapurl + "&markers=size:mid%7Ccolor:0xcc00cc%7Clabel:N%7C{},{}".format(lat, lon)
				data.set_image(url=mapurl)
				data.set_footer(text="Last updated {} seconds ago. Division information is from n!fleet".format(updated))

				try:
					await self.bot.say(embed=data)
					return
				except:
					await self.bot.say(":rotating_light: {} is currently on `{}`. Corrupted route data! Please check data for `{}` :rotating_light:".format(veh,dirtag,dirtag))
					return
		await self.bot.say("Vehicle not found! #{}".format(veh))


	@commands.command()
	async def veh(self, veh):
		"""Checks information for a selected TTC vehicle."""

#        url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=ttc&t=3000"
		url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocation&a=ttc&v=" + veh
		raw = urlopen(url).read() # Get page and read data
		decoded = raw.decode("utf-8") # Decode from bytes object
		parsed = minidom.parseString(decoded) # Parse with minidom to get XML stuffses
		vehicles = parsed.getElementsByTagName('vehicle') # Get all tags called 'vehicle'
		for i in vehicles: # Loop through these

			service = i.attributes['id'].value # GETS VEHICLE
			if veh == service: # IF MATCHING VEHICLE FOUND
				try:
					dirtag = i.attributes['dirTag'].value # Direction Tag
				except:
					dirtag = str("N/A")
				hea = int(i.attributes['heading'].value) # Compass Direction
				updated = i.attributes['secsSinceReport'].value # Seconds since last updated
				lat = i.attributes['lat'].value #latitude
				lon = i.attributes['lon'].value # lon

				try:
					vision = i.attributes['speedKmHr'].value
				except:
					lon = i.attributes['lon'].value # lon

				try:
					find = i.attributes['routeTag'].value #routetag
					url5 = "http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=ttc"
					raw5 = urlopen(url5).read() # Get page and read data
					decoded5 = raw5.decode("utf-8") # Decode from bytes object
					parsed5 = minidom.parseString(decoded5) # Parse with minidom to get XML stuffses
					route = parsed5.getElementsByTagName('route') # Get all tags called 'vehicle'

					for i in route: # Loop through these
						routag = i.attributes['tag'].value
						if routag == find: # IF MATCHING VEHICLE FOUND
							offroute = i.attributes['title'].value
				except:
					offroute = str("No Route")


				#LOADS FLEET INFO
				try:
					listfleet = open("cogs/njc/fleets/ttc.csv")
					readerfleet = csv.reader(listfleet,delimiter="	")
					linefleet = []
				except:
					await self.bot.say("I couldn't find the file.")
					return

				vehicle = "Test object"
				try:
					for row in readerfleet:
						if str(row[0]) == veh:
							linefleet = row

						# IF OK, THIS IS WHAT IS OUTPUTTED
					listfleet.close()

					data = discord.Embed(title="Vehicle Tracking for TTC {} - {} {}".format(veh,linefleet[2],linefleet[3]), description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=16711680))
				except Exception as errer:
					await self.bot.say("<@&536303913868197898> - Unknown vehicle, add it to the database. `{}`".format(errer))
					data = discord.Embed(title="Vehicle Tracking for TTC {} - UNKNOWN VEHICLE".format(veh), description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=16580352))


				try: # TRIES FETCHING DATA
					taglist = open("cogs/njc/dirTag.csv")
					reader = csv.reader(taglist,delimiter="	")
					line = []
				except Exception as errer:
					await self.bot.say("dirTag.csv not found!\n`" + str(errer) + "`")
					return

				try: # GETS INFO FROM FILE
					for row in reader:
						if str(row[0]) == dirtag:
							line = row

					# IF OK, THIS IS WHAT IS OUTPUTTED
					taglist.close()
					

					if dirtag == str("N/A"):
						try:
							data = discord.Embed(title="Vehicle Tracking for TTC {} - {} {}".format(veh,linefleet[2],linefleet[3]), description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=0))
							data.add_field(name="Off Route", value=offroute)
						except:
							data.add_field(name="Off Route", value="*Not in service?*") 
					else:
						if str(linefleet[4]) not in str(line[6]):
							await self.bot.say(":rotating_light: Branch divisions don't match vehicle division!")
							data = discord.Embed(title="Vehicle Tracking for TTC {} - {} {}".format(veh,linefleet[2],linefleet[3]), description="<@463799485609541632> TTC tracker.",colour=discord.Colour(value=5604737))
						data.add_field(name="On Route", value=line[1])  
						data.add_field(name="Currently on Branch", value="`{}`".format(dirtag))  
						data.add_field(name="Starts from", value=line[2])
						data.add_field(name="Ends at", value=line[3])
						data.add_field(name="Sign", value=line[4])
						data.add_field(name="Branch Notes", value=line[5])
						data.add_field(name="Branch Divisions", value=line[6])
		
					try:
						data.add_field(name="Vehicle Division", value=linefleet[4])
						data.add_field(name="Vehicle Status", value=linefleet[6])
					except:
						data.add_field(name="Vehicle Division", value="Unknown")
						data.add_field(name="Vehicle Status", value="Unknown")
				except Exception as errer:
#                    await self.bot.say("dirTag.csv not found!\n`" + str(errer) + "`")
					data.add_field(name="On Route", value="No route")  
					data.add_field(name="Currently on Branch", value="`{}`".format(dirtag))  
					data.add_field(name="Starts from", value="Unknown")
					data.add_field(name="Ends at", value="Unknown")
					data.add_field(name="Sign", value="Unknown")
					data.add_field(name="Branch Notes", value="Unknown")
					await self.bot.say(":question: Unknown branch, add it to the database. `{}`".format(errer))

				data.add_field(name="Compass", value="Facing {} ({}°)".format(*[(["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest", "north", "disabled"][i]) for i, j in enumerate([range(0, 30), range(30, 68), range(68, 113), range(113, 158), range(158, 203), range(203, 248), range(248, 293), range(293, 338), range(338, 360),range(-10, 0)]) if int(hea) in j],hea)) # Obfuscation? Fun, either way
				try:
					vision = vision
					data.add_field(name="VISION Equipped?", value="**Yes!**")
				except:
					data.add_field(name="VISION Equipped?", value="No")

				data.set_footer(text="Last updated {} seconds ago. Division information is from n!fleet".format(updated))

				try:
					await self.bot.say(embed=data)
					return
				except:
					await self.bot.say(":rotating_light: {} is currently on `{}`. An error has occured while trying to embed data.".format(veh,dirtag,dirtag))
					return
		await self.bot.say("Vehicle not found! #{}".format(veh))

	#Scans all active vehicles automatically
	async def autoscan(self):
		while True:
			await self.check(discord.Object(id = self.channelID))
			await asyncio.sleep(self.scanInterval)

	async def check(self, channel):
#		await self.bot.send_message(channel, ":mag_right: **Scanning...**\nThis command checks all vehicles in service if the vehicle division matches the branch division. This is useful for finding unknown branches, vehicles on routes out of their division, and updating information. Please don't spam the command.")
		service = ""
		service5 = ""
		url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=ttc&t=0"
		raw = urlopen(url).read() # Get page and read data
		decoded = raw.decode("utf-8") # Decode from bytes object
		parsed = minidom.parseString(decoded) # Parse with minidom to get XML stuffses
		vehicles = parsed.getElementsByTagName('vehicle') # Get all tags called 'vehicle'


		try:
			for i in vehicles: # Loop through these
				veh = i.attributes['id'].value # GETS VEHICLE
				updated = i.attributes['secsSinceReport'].value # Seconds since last updated
				try:
					dirtag = i.attributes['dirTag'].value # Direction Tag
				except:
					dirtag = "N/A"

				if dirtag != "N/A":
					try:
						listfleet = open("cogs/njc/fleets/ttc.csv")
						readerfleet = csv.reader(listfleet,delimiter="	")
						linefleet = []
					except Exception as errer:
						await self.bot.send_message(channel, "fleets/ttc.csv not found!\n`" + str(errer) + "`")

					for row in readerfleet:
						if str(row[0]) == veh:
							linefleet = row

					try: # TRIES FETCHING DATA
						taglist = open("cogs/njc/dirTag.csv")
						reader = csv.reader(taglist,delimiter="	")
						line = []
					except Exception as errer:
						await self.bot.send_message(channel, "dirTag.csv not found!\n`" + str(errer) + "`")

					for row in reader:
						if str(row[0]) == dirtag:
							line = row

					try: #checks if vehicle in service is marked as inactive
						if (str(linefleet[6]) != "Active"):
							if ("TRACK" in str(linefleet[6])):
								service2 = ("`[year-month-day time]`: :white_check_mark: {} is in service on `{}`!".format(veh,dirtag))
								await self.bot.send_message(discord.Object(id = self.channelID4), service2)
							elif ("Retired" in str(linefleet[6])):
								service2 = (":x: :x: :x: :x: <@&566964640114933764> - {} IS MARKED RETIRED BUT IS ON `{}`!".format(veh,dirtag))
								await self.bot.send_message(discord.Object(id = self.channelID3), service2)
							else:
								service2 = ("`[year-month-day time]`: :question: <@&566964640114933764> - {} is not marked active and is on `{}`!".format(veh,dirtag))
								await self.bot.send_message(discord.Object(id = self.channelID3), service2)

							service5 = service5 + service2 + "\n"

						try: #compares fleet division to branch division
							if str(linefleet[4]) not in str(line[6]): #checks if divisions match
								service1 = (":rotating_light: {} is on `{}`, divisions don't match!".format(veh,dirtag))
								await self.bot.send_message(discord.Object(id = self.channelID), service1)
								service = service + service1 + "\n"
							if str("TRACK") in str(line[7]): #Checks if a vehicle is on TRACK branch
								service1 = (":ok_hand: {} is on `{}`!".format(veh,dirtag))
								await self.bot.send_message(discord.Object(id = self.channelID5), service1)
								service = service + service1 + "\n"
						except Exception as errer:
							await self.bot.send_message(discord.Object(id = self.channelID2), ":pencil2: {} is on **UNKNOWN BRANCH `{}`**".format(veh,dirtag,errer))

					except Exception as errer:
						await self.bot.send_message(discord.Object(id = self.channelID1), ":minibus: **UNKNOWN VEHICLE #{}** is on `{}`".format(veh,dirtag,errer))

		except Exception as errer:
			await self.bot.send_message(channel, "**Fatal error occured:**\n**VEHICLE:** `{0}`\n**BRANCH:** `{1}`\n**ERROR:** `{2}`".format(veh,dirtag,errer))

		try: await self.bot.send_message(discord.Object(id = self.channelstatus), "`[year-month-day time]`: :white_check_mark: **Bot service ok. Autoscan currently active.**")
		except: await self.bot.send_message(discord.Object(id = self.channelstatus), "An error may have occured.")
#Groups all messages in one
#		try:
#			if service != "":
#				await self.bot.send_message(channel, service)
#		except Exception as errer:
#			await self.bot.send_message(channel, "**Error,** there may be too many vehicles that don't match: `{}`".format(errer))
#
#		try:
#			if service5 != "":
#				await self.bot.send_message(channel, service5)
#		except Exception as errer:
#			await self.bot.send_message(channel, "**Error 5:** `{}`".format(errer))

#		await self.bot.send_message(channel, "**:white_check_mark: Scan complete. Results listed above.**")

	# COMMAND FOR GETTING NEXT BUS <STOPID>
	@commands.command()
	async def ttcnext(self, stopID):
		"""Obtains next vehicle predictions for TTC bus stop's SMS code. Enter a stopID, 'info', or 'alias'"""

		if stopID == 'info':
			data = discord.Embed(title="Next Vehicle Predictions for Toronto Transit Commission",description="This bot was developed by <@281750712805883904> and <@221493681075650560>. When you submit a valid stop ID, the bot fetches data and displays it here. This information is to let users find departures for a selected bus stop efficiently, without wasting much data.\n\nOne prediction typically looks like this:\n`00:07:07 - #8844 on 25_1_25A*, run 25_52_182`\n\nThis means vehicle `#8844` is coming to the stop in 7 minutes. This can help you find internal branches. `25_1_25A*` means it is on route `25` going `1` outbound on internal branch `25A*`.\n\nWith the run information, you can find interesting run interlines. The run `25_52_82` lets you know if it interlines, and when it services. This is run `8` on route `25`, which operates in the `2` afternoon. The runbox number `52` does not match run `8`. This happens if a route interlines, or if it shares the corridor with another route, to prevent confusion to operators. For possible values of runs, use the command `n!ttcnext runs`\n\nFor daytime routes that fully interline with another route for the whole day, like 130 Middlefield and 132 Milner, the runbox number will not differ from the route run number.\n\nPlease report any bugs to <@221493681075650560>.\n\nThere may currently be more bugs than usual, as the code needs a major rewrite.\n\nAll prediction data is copyright Toronto Transit Commission 2018.", colour=discord.Colour(value=13491480))
			data.set_thumbnail(url="http://ttc.ca/images/ttc-main-logo.gif")
			await self.bot.say(embed=data)
			return
		elif stopID == 'alias':
			data = discord.Embed(title="StopID Alias",description="You can also type these in to get their bus stop.", colour=discord.Colour(value=13491480))

			try:
				fleetlist = open("cogs/njc/ttcalias.csv")
				reader = csv.reader(fleetlist,delimiter=",")
				line = []
			except:
				await self.bot.say("No alias file found... <@221493681075650560>")
				stopID = stopID
			tosay = ""
			for row in reader:
				try:
					if tosay != "":
						tosay=tosay + "; `" + row[0] + "`"
					else:
						tosay = "`" + row[0] + "`"
				except Exception as e:
					stopID = stopID
					await self.bot.say("Error, see console")
					print("Error:", e)
			data.add_field(name='Alias',value=tosay, inline='false') # Alias
			data.set_thumbnail(url="http://ttc.ca/images/ttc-main-logo.gif")
			await self.bot.say(embed=data)
			return
		elif stopID == 'runs':
			data = discord.Embed(title="Runs Information",description="`<route>_<runbox>_<run><time>`, ex. `12_88_20`", colour=discord.Colour(value=13491480))
			data.add_field(name='Values for Routes:',value="The main route for the run. In the example, it is `12`.", inline='false') # Alias
			data.add_field(name='Values for Runbox:',value="Same as run, unless this run goes on more than one route, and/or the route operates very closely to another route. In the example, it is `88`.", inline='false') # Alias
			data.add_field(name='Values for Run:',value="The run number for the particular route. In the example, it is `2`.", inline='false') # Alias
			data.add_field(name='Values for Time:',value="`0` - Run operates all day.\n`1` - Run operates in the morning period only.\n`2` - Run starts to operate in the afternoon period.\nIn the example, it is `0`.", inline='false') # Alias
			data.set_thumbnail(url="http://ttc.ca/images/ttc-main-logo.gif")
			await self.bot.say(embed=data)
			return

		try:
			fleetlist = open("cogs/njc/ttcalias.csv")
			reader = csv.reader(fleetlist,delimiter=",")
			line = []
		except:
			await self.bot.say("No alias file found... <@221493681075650560>")
			stopID = stopID

		try:
			for row in reader:
				if str(row[0]) == stopID:
					line = row
			fleetlist.close()
			stopID=line[1]
		except:
			stopID = stopID

		url = "http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=ttc&stopId=" + stopID
		raw = urlopen(url).read() # Get page and read data
		decoded = raw.decode("utf-8") # Decode from bytes object
		parsed = minidom.parseString(decoded) # Parse with minidom to get XML stuffses

		if len(parsed.getElementsByTagName('Error')) > 0: # Check whether the ID is valid
			data = discord.Embed(title=":x: Invalid Stop ID or Command: " + stopID,description="Type `n!ttcnext info` for help.",colour=discord.Colour(value=16467744))
			await self.bot.say(embed=data)
			return

		msg1 = ["No predictions found for this route."]
		data = discord.Embed(title="Next Vehicle Predictions",description="Stop ID: {}".format(stopID), colour=discord.Colour(value=11250603))
		routes = parsed.getElementsByTagName('predictions') # Get all tags called 'predictions'
		for i in routes: # Loop through these
			stopname = i.attributes['stopTitle'].value # GETS STOP NAME
			routename = i.attributes['routeTitle'].value # GETS ROUTE NAME
			predictions = i.getElementsByTagName('prediction') # Get all sub-tags called 'prediction'
			for i in predictions: # Loop through these
				try: #test
					seconds = int(i.attributes['seconds'].value) # If the seconds value is blank, this will throw an error (dividing by 0) and trigger the exception handler, and this value needs to be an int later anyway
					vehicle = i.attributes['vehicle'].value
					if vehicle >= '1000' and vehicle <= '1149':
						vehicle = vehicle + " VII Hybrid"                    
					elif vehicle >= '1200' and vehicle <= '1423':
						vehicle = vehicle + " VII NG Hybrid"                    
					elif vehicle >= '1500' and vehicle <= '1689':
						vehicle = vehicle + " VII NG Hybrid"                    
					elif vehicle >= '1700' and vehicle <= '1829':
						vehicle = vehicle + " VII NG Hybrid"                    
					elif vehicle >= '3100' and vehicle <= '3369':
						vehicle = vehicle + " LFS VISION"                    
					elif vehicle >= '4000' and vehicle <= '4199':
						vehicle = vehicle + " CLRV"                    
					elif vehicle >= '4200' and vehicle <= '4251':
						vehicle = vehicle + " ALRV"                    
					elif vehicle >= '4400' and vehicle <= '4999':
						vehicle = vehicle + " Flexity"                    
					elif vehicle >= '7500' and vehicle <= '7883':
						vehicle = vehicle + " VII"                    
					elif vehicle >= '7900' and vehicle <= '7979':
						vehicle = vehicle + " VII"                    
					elif vehicle >= '8000' and vehicle <= '8011':
						vehicle = vehicle + " VII-Airport"                    
					elif vehicle >= '8012' and vehicle <= '8099':
						vehicle = vehicle + " VII"                    
					elif vehicle >= '8100' and vehicle <= '8219':
						vehicle = vehicle + " VII NG"         
					elif vehicle >= '8300' and vehicle <= '8396':
						vehicle = vehicle + " VII 3G"         
					elif vehicle >= '8400' and vehicle <= '8504':
						vehicle = vehicle + " LFS"                    
					elif vehicle >= '8510' and vehicle <= '8617':
						vehicle = vehicle + " LFS"                    
					elif vehicle >= '8620' and vehicle <= '8964':
						vehicle = vehicle + " LFS"                    
					elif vehicle >= '9000' and vehicle <= '9152':
						vehicle = vehicle + " LFS-Artic"
					elif vehicle >= '9200' and vehicle <= '9239':
						vehicle = vehicle + " LFS"                    
					else:
						vehicle = vehicle + " UNKNOWN VEHICLE"
					toSay = [vehicle,i.attributes['dirTag'].value,i.attributes['block'].value, str(seconds // 3600).zfill(2), str(seconds // 60 % 60).zfill(2), str(seconds % 60).zfill(2), seconds] # Get the time value, vehicle and route name from the first one

					if msg1[0] == "No predictions found for this route.":
						msg1 = [toSay]
					else:
						msg1.append(toSay)
				except:
					try:
						msg1 = ["No predictions found for this route."]
						continue # And starting the next loop immediately
					except:
						msg1 = "Invalid Data recieved"
						await self.bot.say("Invalid data recieved.") # Dunno how it'll look if there's no data, wrapping it in a try/except should cover all bases

			sortedMessageData = sorted(msg1, key = lambda x:x[6]) # All this bit is hacky as anything, it really needs a rewrite
			cleanMessagesBuffer = ["{3}:{4}:{5} - #{0} on `{1}`, Run `{2}`".format(*i[:-1] if i[6] > 60 else (*i[:-4], "**" + str(i[-4]), str(i[-3]), str(i[-2]) + "**")) for i in sortedMessageData if sortedMessageData[0] != "No predictions found for this route."] # lol if this works first try
			if cleanMessagesBuffer != []:
				cleanMessages = cleanMessagesBuffer
			else:
				cleanMessages = [sortedMessageData[0]] # I didn't realise that if the 'if' statement 4 lines up failed, it would still write to the variable, but it wouldn't actually write any data, so the variable was empty, which caused bad things to happen.
			string = "\n".join(cleanMessages) # I fixed it by checking whether the variable is empty, and replacing it with the no predictions message if it is.
			data.add_field(name=routename,value=string, inline='false') # Say message
			data.set_thumbnail(url="http://ttc.ca/images/ttc-main-logo.gif")
			data.set_footer(text="Use 'n!ttcnext info' for more info about this command.")
			msg1 = ['No predictions found for this route.']

		data.set_author(name=stopname, icon_url="http://ttc.ca/images/ttc-main-logo.gif")
		try:
			await self.bot.say(embed=data)
		except Exception as e:
			await self.bot.say("I need the `Embed links` permission "
			                   "to send this. "
			                   "Check console for error details. "
			                   "(There's a good chance that the error is that the data is too long)")
			print("Error:", e, "\nData:", data.to_dict(), "\nString:", string)

	#Gets info for fleet
	@commands.command()
	async def fleet(self, agency : str, number : int):
		"""Gets information from a fleet. For more info, n!fleet info 0"""
		agencyname = 'null '
		curator = 'null'

		data = discord.Embed(title="Fleet Information",description="Vehicle not found.",colour=discord.Colour(value=12786604))

		url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=ttc"
		raw = urlopen(url).read() # Get page and read data
		decoded = raw.decode("utf-8") # Decode from bytes object
		parsed = minidom.parseString(decoded) # Parse with minidom to get XML stuffses

		if agency == "info":
			data = discord.Embed(title="Sources",description="Most fleet information is from the CPTDB wiki, with data curated by NJC staff.\nhttps://cptdb.ca/wiki/index.php/Main_Page.\n\nNOTE: When a vehicle status is `Inactive`, this means the vehicle is currently not used for revenue service. ",colour=discord.Colour(value=5))
			await self.bot.say(embed=data)
			return


		# AGENCY NAME
		if agency == 'go':
			agencyname = "GO Transit "
		elif agency =='ttc':
			agencyname = "TTC "
		elif agency =='yrt':
			agencyname = "YRT "
		elif agency =='miway':
			agencyname = "MiWay "
		elif agency =='ddot':
			agencyname = "DDOT "
		else:
			agencyname = ""

		try:
			fleetlist = open("cogs/njc/fleets/{}.csv".format(agency))
			reader = csv.reader(fleetlist,delimiter="	")
			line = []
		except Exception as e:
			data = discord.Embed(title="This agency is unsupported or invalid at this time.",description="You can help contribute to the fleet lists. Contact <@300473777047994371>\n\nError: `" + str(e) + "`",colour=discord.Colour(value=5))
			await self.bot.say(embed=data)
			return

		try:
			for row in reader:
				if row[0] != "vehicle" and int(row[0]) == number:
					line = row
			fleetlist.close()
			data = discord.Embed( colour=discord.Colour(value=474494))
			data.add_field(name="Manufacturer", value=line[2])
			data.add_field(name="Model", value=line[3])
			data.add_field(name="Division/Category", value=line[4])
			data.add_field(name="Powertrain/Motor", value=line[5])
			data.add_field(name="Vehicle Group", value=line[1])
			data.add_field(name="Status", value=line[6])
			data.set_footer(text="Last updated " + line[8])


			if number < 1000:
				if agency == 'ttc':
					number = str('W{}'.format(number))
				elif agency == 'miway':
					number = str('0{}'.format(number))
			data.set_author(name="Fleet Information for {}".format(agencyname) + str(number), url=line[7])
			data.set_thumbnail(url=line[7])

		except Exception as e:
			data = discord.Embed(title="Vehicle {} was not found ".format(number) + "for {}".format(agencyname),description="Either you have entered a non-existent vehicle number, or that vehicle has not been added to our database yet! Vehicle groups that have been completely retired are removed from the database!\n\nError: `" + str(e) + "`",colour=discord.Colour(value=16467744))

		await self.bot.say(embed=data)

	# Allows users to edit file
	@commands.command()
	async def fleetedit(self, agency : str, number : int, field: str, newvalue: str):
		"""Allows construction role and higher to edit information about fleet.\n\nAvailable values for field: vehicle, group, manufacturer, model, division, powertrain, status, thumbnail"""    

		try:
			reader = None
			fleetlist = open("cogs/njc/fleets/{}.csv".format(agency))
			reader = csv.reader(fleetlist,delimiter="	")
		except:
			data = discord.Embed(title="This agency is unsupported or invalid at this time.",description="You can help contribute to the fleet lists. Contact <@300473777047994371>",colour=discord.Colour(value=5))
			await self.bot.say(embed=data)
			return


		lineNum = None
		lines = []
		for row in reader:
			if row:
				lines.append(row)
				if len(lines) > 1 and int(row[0]) == number:
					if not lineNum:
						lineNum = len(lines) - 1
					else:
						await self.bot.say("More than one bus :3")
						return
		fleetlist.close()
		if True:
			num = lines[0].index(field)
			if lineNum:
				lines[lineNum][num] = newvalue
				lines[lineNum][-1] = datetime.date.today().strftime("%d %B %Y").lstrip("0")
			else:
				await self.bot.say("Invalid number")
				return
		else:
			await self.bot.say("Invalid field")
			return
		writer = None
		with open("cogs/njc/fleets/{}.csv".format(agency), "w", newline='') as fleetlist:
			writer = csv.writer(fleetlist,delimiter="	")     
			for i in lines:
				writer.writerow(i)
		fleetlist.close()
		data = discord.Embed(title="'{}' has been updated for ".format(field) + agency + " " + str(number),description="New value for {}: ".format(field) + newvalue,colour=discord.Colour(value=34633))
		await self.bot.say(embed=data)

	# Gets schedules
	@commands.command()
	async def schedule(self, agency : str, line : int):
		"""Gets a schedule for selected agency's line. Available agencies: [YRT, GO]"""

		if agency.lower() in ['yrt']:
			data = discord.Embed(colour=discord.Colour(value=2130939))
			data.add_field(name="YRT Route Navigator - Route {}".format(line), value=str("https://www.yrt.ca/en/schedules-and-maps/resources/{}.pdf".format(line)))
		# --- GO TRANSIT ---
		elif agency.lower() in ['go']:
			if line == 18: # REDIRCTS LINE 18 to 01
				line1 = "01"
			elif line == 30 or line == 32 : # REDIRECTS LINES 30 and 32 to 31
				line1 = "31"
			elif line == 40: # REDIRECTS TO ACTUAL TABLE PDF
				line1 = "40-Feb06"
			elif line == 45 or line == 47 or line == 48: # REDIRECTS LINES 45, 47 and 48 to 46
				line1 = "46"
			elif line == 51 or line == 54: # REDIRECTS LINES 51 and 54 to 52
				line1 = "52"
			elif line == 63 or line == 67 or line == 69: # REDIRECTS LINES 63, 67, and 69 to 65
				line1 = "65"
			elif line == 70: # REDIRECTS LINE 70 to LINE 71
				line1 = "71"
			elif line == 90 or line == 91: # REDIRECTS LINE 90 and 91 to 09
				line1 = "09"
			else:
				line1 = line
			data = discord.Embed(colour=discord.Colour(value=2130939))
			data.add_field(name="GO Transit Schedule - Route {}".format(line), value=str("https://www.gotransit.com/static_files/gotransit/assets/pdf/TripPlanning/FullSchedules/Table{}.pdf".format(line1)))

		# --- TORONTO TTC ---
		elif agency.lower() in ['ttc']:
			data = discord.Embed(colour=discord.Colour(value=2130939))
			data.add_field(name="TTC Route Information - Route {}".format(line), value=str("http://ttc.ca/Routes/{}/RouteDescription.jsp".format(line)))
		# --- INVALID AGENCY ---
		else:
			data = discord.Embed(title="This agency is unsupported or invalid at this time.",description="Schedules for this agency could not be fetched.",colour=discord.Colour(value=16467744))
		await self.bot.say(embed=data)

	# Gets map for a route.
	@commands.command(no_pm=False)
	async def map(self, agency : str, line : int):
		"""Gets a map for agency's line. Available agencies: [TTC]"""

		maptitle = [agency , line]
		if agency.lower() in ['ttc']: # TTC
			data = discord.Embed(description="NJC Map Fetcher", title="Toronto Transit Commission - Route {1}".format(*maptitle), colour=discord.Colour(value=2130939))
			if line < 999:
				if line < 10:
					line1 = str("00" + str(line))
				elif line < 100:
					line1 = str("0" + str(line))
				else:
					line1 = line
				data.set_image(url="http://ttc.ca/images/Route_maps/{}map.gif".format(line1))
			else:
				data.add_field(name="Error", value=str("Line too high"))
		else:
			data = discord.Embed(title="This agency is unsupported or invalid at this time.",description="Maps for this agency were not found.",colour=discord.Colour(value=16467744))
		await self.bot.say(embed=data)

	# Gets bylaw
	@commands.command()
	async def bylaw(self, agency : str):
		"""Gets rules for an agency. Available agencies: [TTC, MiWay]"""

		if agency.lower() in ['ttc']: # ttc
			data = discord.Embed(colour=discord.Colour(value=5))
			data.add_field(name="TTC Bylaw No. 1", value=str("https://www.ttc.ca/Riding_the_TTC/TTC_Bylaws/index.jsp"))

		elif agency.lower() in ['miway']: # miway
			data = discord.Embed(colour=discord.Colour(value=5))
			data.add_field(name="THE CORPORATION OF THE CITY OF MISSISSAUGA TRANSIT BY-LAW", value=str("https://www7.mississauga.ca/documents/bylaws/TRANSIT_RULES_UPDATE.pdf"))

		else:
			data = discord.Embed(title="This agency is unsupported or invalid at this time.",description="The bylaw for this agency could not be found.",colour=discord.Colour(value=16467744))
		await self.bot.say(embed=data)

	# Gets profile for TTC route
	@commands.command()
	async def route(self, rte):
		"""Gets information about a TTC route."""

		try:
			list = open("cogs/njc/ttcroute.csv")
			reader = csv.reader(list,delimiter="	")
			line = []
		except:
			await self.bot.say("I couldn't find the route information file.")
			return



		try: # GETS INFO FROM FILE
			for row in reader:
				if str(row[0]) == rte:
					line = row
					data = discord.Embed(title="**{} {}** - **Route Information**".format(rte, line[1]),colour=discord.Colour(value=15801115))


					try:
# BRANCHES
						if line[4] == "":
							data.add_field(name="Internal Branches:", value="undefined",inline='false')
						else:
							data.add_field(name="Internal Branches:", value="`{}`".format(line[4]),inline='false')

# INTERLINES
						if line[3] == "":
							data.add_field(name="Interlined with", value="undefined",inline='false')
						else:
							data.add_field(name="Interlined with", value=line[3],inline='false')

# DIVISIONS
						if line[2] == "":
							data.add_field(name="Divisions", value="undefined",inline='false')
						else:
							data.add_field(name="Divisions", value=line[2],inline='false')

						try:
							url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=ttc&r=" + rte
							raw = urlopen(url).read() # Get page and read data
							decoded = raw.decode("utf-8") # Decode from bytes object
							parsed = minidom.parseString(decoded) # Parse with minidom to get XML stuffses
							service = ""
							vehicles = parsed.getElementsByTagName('vehicle') # Get all tags called 'vehicle'
							for i in vehicles: # For each vehicle found
								veh = i.attributes['id'].value # GETS VEHICLE
								service = service + veh + ", "
							if service == "":
								data.add_field(name="Current Vehicles", value="No vehicles currently on route.",inline='false')
							else:
								data.add_field(name="Current Vehicles", value=service,inline='false')
						except:
							data.add_field(name="Current Vehicles", value="No vehicles currently on route.",inline='false')
						data.set_footer(text="Learn about the branch by doing `n!branch <internal branch>`. Information last updated <future information>")

					except Exception as errer:
						await self.bot.say(errer)
					await self.bot.say(embed=data)

		except Exception as errer:
			await self.bot.say(errer)

	# Gets profile for TTC branch
	@commands.command()
	async def branch(self, branch):
		"""Gets information about a TTC internal branch."""

		try:
			list = open("cogs/njc/dirTag.csv")
			reader = csv.reader(list,delimiter="	")
			line = []
		except:
			await self.bot.say("I couldn't find the branch information file.")
			return

		try: # GETS INFO FROM FILE
			for row in reader:
				if str(row[0]) == branch:
					line = row
					data = discord.Embed(title="Branch Information for `{}`".format(branch),colour=discord.Colour(value=15801115))


					try:
# ROUTE
						if line[1] == "":
							data.add_field(name="Route:", value="undefined",inline='false')
						else:
							data.add_field(name="Route:", value=line[1],inline='false')

# STARTS
						if line[2] == "":
							data.add_field(name="Starts from:", value="undefined",inline='false')
						else:
							data.add_field(name="Starts from:", value=line[2],inline='false')

# ENDS
						if line[3] == "":
							data.add_field(name="Ends at:", value="undefined",inline='false')
						else:
							data.add_field(name="Ends at:", value=line[3],inline='false')

# BRANCHES
						if line[4] == "":
							data.add_field(name="Sign:", value="undefined",inline='false')
						else:
							data.add_field(name="Sign:", value="{}".format(line[4]),inline='false')

# NOTES
						if line[5] == "":
							data.add_field(name="Notes:", value="undefined",inline='false')
						else:
							data.add_field(name="Notes:", value="{}".format(line[5]),inline='false')

# Division
						if line[6] == "":
							data.add_field(name="Branch divisions:", value="undefined",inline='false')
						else:
							data.add_field(name="Branch divisions:", value="{}".format(line[6]),inline='false')

# Long Description
						if line[7] == "":
							data.add_field(name="Long description:", value="Not available.",inline='false')
						else:
							data.add_field(name="Long description:", value="{}".format(line[7]),inline='false')


						data.set_footer(text="Information last updated <future information>")

					except Exception as errer:
						await self.bot.say(errer)
					await self.bot.say(embed=data)

		except Exception as errer:
			await self.bot.say(errer)


	# Gets profile for NJC branch
	@commands.command()
	async def nbranch(self, branch):
		"""Gets information about a NJC internal branch."""

		try:
			list = open("cogs/njc/dirTag-NJC.csv")
			reader = csv.reader(list,delimiter="	")
			line = []
		except:
			await self.bot.say("I couldn't find the branch information file.")
			return

		try: # GETS INFO FROM FILE
			for row in reader:
				if str(row[0]) == branch:
					line = row
					data = discord.Embed(title="Branch Information for `{}`".format(branch),colour=discord.Colour(value=15801115))


					try:
# ROUTE
						if line[1] == "":
							data.add_field(name="Route:", value="undefined",inline='false')
						else:
							data.add_field(name="Route:", value=line[1],inline='false')

# STARTS
						if line[2] == "":
							data.add_field(name="Starts from:", value="undefined",inline='false')
						else:
							data.add_field(name="Starts from:", value=line[2],inline='false')

# ENDS
						if line[3] == "":
							data.add_field(name="Ends at:", value="undefined",inline='false')
						else:
							data.add_field(name="Ends at:", value=line[3],inline='false')

# BRANCHES
						if line[4] == "":
							data.add_field(name="Sign:", value="undefined",inline='false')
						else:
							data.add_field(name="Sign:", value="{}".format(line[4]),inline='false')

# NOTES
						if line[5] == "":
							data.add_field(name="Notes:", value="undefined",inline='false')
						else:
							data.add_field(name="Notes:", value="{}".format(line[5]),inline='false')

# Division
						if line[6] == "":
							data.add_field(name="Branch divisions:", value="undefined",inline='false')
						else:
							data.add_field(name="Branch divisions:", value="{}".format(line[6]),inline='false')

# Long Description
						if line[7] == "":
							data.add_field(name="Long description:", value="Not available.",inline='false')
						else:
							data.add_field(name="Long description:", value="{}".format(line[7]),inline='false')


						data.set_footer(text="Information last updated <future information>")

					except Exception as errer:
						await self.bot.say(errer)
					await self.bot.say(embed=data)

		except Exception as errer:
			await self.bot.say(errer)


	# Gets profile for TTC route
	@commands.command()
	async def route1(self):
		"""Gets information about TTC route"""
		await self.bot.say("**Test command to see how the route command would look!**")
		data = discord.Embed(title="169 HUNTINGWOOD",description="169A DON MILLS STN to SCARBOROUGH CTR via VAN HORNE\n169B DON MILLS STN to SCARBOROUGH CTR",colour=discord.Colour(value=15801115))
		data.add_field(name="Division", value="Wilson, all trips, all days",inline='false')
		data.add_field(name="Operation", value="169A - Except weekday rush and late weekend evening\n169B - During weekday rush",inline='false')
		data.add_field(name="Interlines", value="None",inline='false')
		data.add_field(name="Internal Branches", value="169A - For 169A trips\n169B - For 169B trips\nMCDO - McCowan/Commander to Don Mills Stn, one trip only",inline='false')
		data.add_field(name="Signs", value="169A HUNTINGWOOD TO DON MILLS STN via VAN HORNE\n169A HUNTINGWOOD TO SCARBOROUGH CTR via VAN HORNE\n169B HUNTINGWOOD TO DON MILS STN\n169B HUNTINGWOOD TO SCARBOROUGH CTR",inline='false')
		data.set_footer(text="Page 1 of 2")
		await self.bot.say(embed=data)

	@commands.command()
	async def route2(self):
		"""Gets information about TTC route"""
		await self.bot.say("**Test command to see how the route command would look!**")
		data = discord.Embed(title="119 TORBARRIE",description="119 WILSON STN to CLAYSON and TORBARRIE\n119 WILSON STN to TORBARRIE and CLAYSON",colour=discord.Colour(value=15801115))
		data.add_field(name="Division", value="Arrow Rd, all trips, all days",inline='false')
		data.add_field(name="Operation", value="119 - Rush hours only.",inline='false')
		data.add_field(name="Interlines", value="96 Wilson - one run, one trip.",inline='false')
		data.add_field(name="Internal Branches", value="119a - Morning rush, operates terminus clockwise\n119p - Afternoon rush, operates terminus counterclockwise",inline='false')
		data.add_field(name="Signs", value="119 TORBARRIE TO WILSON STN\n119 TORBARRIE TO TORBARRIE and CLAYSON",inline='false')
		data.set_footer(text="Page 1 of 2")
		await self.bot.say(embed=data)


	# Gets requirements
	@commands.command()
	async def requirements(self):
		"""Sends requirements for downloads on NJC."""
		await self.bot.say("The latest version of New John City requires the following objects:\n\n**Chicago DLC:**\nhttps://store.steampowered.com/app/361290/OMSI_2_Addon_Chicago_Downtown/\n\n**Willshire Objects**\nhttp://www.vtransitcenter.com/index.php?action=downloads;sa=view;down=56\n\n**Simple Streets:**\nhttp://www.omnibussimulator.de/backup/index.php?page=Thread&threadID=2500\n\n**New Flyer Powertrain Mod:**\nhttp://www.vtransitcenter.com/index.php/topic,8.0.html")

	# Sends message you need logfile
	@commands.command()
	async def logfile(self):
		"""Sends requirements for downloads on NJC."""
		await self.bot.say("For further support on your OMSI problem, you must **upload your logfile.txt**.\n\nYou can find **logfile.txt** in the OMSI folder. Upload the file to this channel so we can diagnose for the issue.\n\nhttps://i.imgur.com/DxclO7c.png")

				# Sends message you need logfile
	@commands.command()
	async def logfile2(self):
		"""Sends requirements for downloads on NJC."""
		await self.bot.say("For further support on your openBVE problem, you must **upload your log.txt**.\n\nYou can find **log.txt** in the Userdata/Settings folder. Upload the file to this channel so we can diagnose for the issue.\n\nhttps://i.imgur.com/CPySvL1.png")

	# Fare stuff
	@commands.command()
	async def farecalc(self, start, end, adults = 1, seniors = 0, students = 0, children = 0, returnTrip = False):
		"""Gets fare info for GO or something"""
		await self.bot.say("Getting info for journey {} to {}...".format(start, end))
		url = "https://transitfeeds-data.s3-us-west-1.amazonaws.com/public/feeds/go-transit/32/20180727/original/stops.txt"
		try:
			raw = urlopen(url).readlines()
		except Exception as e:
			await self.bot.say("An error has occured, the servers are most likely not responding.\nPlease try again soon. See console log for error details.")
			print("Error:", e)
			return
		decoded = [i.decode().strip("\ufeff\r\n").split(",") for i in raw[1:]]
		start_id = None
		end_id = None
		for i in decoded:
			if start.upper() in i[1].upper() or i[1].upper() in start.upper() and not start_id:
				start_id = i[0]
				continue
			if end.upper() in i[1].upper() or i[1].upper() in end.upper() and not end_id:
				end_id = i[0]
				continue	
			if start_id and end_id:
				break
		if not start_id or not end_id:
			await self.bot.say("Stop not found: {}".format(start if not start_id else end))
			return
		try:
			returnOrNot = bool(returnTrip)
		except Exception as e:
			await self.bot.say("Invalid option for return-ness: {}\nSee console for error details".format(returnTrip))
			print(e)
			return
		url = "https://api.gotransit.com/Api/farecalculator/cash?FromStop={}&ToStop={}&AdultCount={}&SeniorCount={}&StudentCount={}&ChildCount={}&ReturnTrip=false".format(start_id, end_id, adults, seniors, students, children, returnOrNot)
		raw = urlopen(url)
		try:
			jsonData = json.load(raw)
		except Exception as e:
			await self.bot.say("Error with the URL or something, check logs")
			print("Error:", e, "\nData:", raw.read(), "\nURL:", url)
			return
		cashString = locale.currency(jsonData['TotalCost'])
		await self.bot.say(cashString)  

	# Get stops for GO
	@commands.command()
	async def gostops(self, page = 1):
		"""Get stops for GO"""
		await self.bot.say("Retrieving data...")
		url = "https://transitfeeds-data.s3-us-west-1.amazonaws.com/public/feeds/go-transit/32/20180727/original/stops.txt"
		try:
			raw = urlopen(url).readlines()
		except Exception as e:
			await self.bot.say("An error has occured, the servers are most likely not responding.\nPlease try again soon. See console log for error details.")
			print("Error:", e)
			return
		decoded = [i.decode().strip("\ufeff\r\n").split(",")[1] for i in raw[1:]]
		await self.bot.say("Page {} of {}".format(page, math.ceil(len(decoded) / 10)))
		ordered = sorted(decoded, key = lambda x: x)
		data = ordered[(page - 1) * 10:min(page * 10, len(ordered))]
		await self.bot.say(data)

	# Get GO-specific stops
	@commands.command()
	async def gostn(self):
		"""Get GO-specific stops"""
		await self.bot.say("Retrieving data...")
		url = "https://transitfeeds-data.s3-us-west-1.amazonaws.com/public/feeds/go-transit/32/20180727/original/stops.txt"
		try:
			raw = urlopen(url).readlines()
		except Exception as e:
			await self.bot.say("An error has occured, the servers are most likely not responding.\nPlease try again soon. See console log for error details.")
			print("Error:", e)
			return
		decoded = [i.decode().strip("\ufeff\r\n").split(",") for i in raw[1:]]
		stops = []
		for i in decoded:
			try:
				int(i[0])
				break
			except:
				stops.append(i[1])
		ordered = sorted(stops, key = lambda x: x)
		await self.bot.say(ordered)

	@commands.command()
	async def vehcheck(self):
		if self.looping:
			await self.check(discord.Object(id = self.backupID))
			return
		self.looping = True
		await self.bot.loop.create_task(self.autoscan())

	async def on_ready(self):
		#await self.bot.send_message(discord.Object(id = self.channelID), "Loaded!")
		self.looping = True
		await self.bot.loop.create_task(self.autoscan())
