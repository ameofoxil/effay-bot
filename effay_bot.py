#  decorate a def with @client.event and async def if it uses a discord.py funcion that is a coroutine 
#  all discord.py coroutines need to be prefixed with await
#  use await asyncio.sleep(<seconds>) for waiting

import discord
import asyncio
import datetime


class EffayBot():
	"""
	Methods and functionality for a fashion discord bot
	Functions:
		Log on and off
		Delete messages from a specified user posted in the last x time
		Post a welcome message when a new user joins
		Post a help message displaying commands
		TODO :: Post fashion inspo pictures scrubbed from reddit
		Prune members who haven't been active

		TODO :: Make a separate voting class
		TODO :: Extend functionality to all channels
	"""


	client = discord.Client()
	channel = None
	server = None
	channel_id = ""
	server_id = ""
	token = ""
	flag_name = ""


	def __init__(self, t, s, c):
		"""
		<t> token to log the bot in
		<s> the id of the server
		<c> channel id the bot should post in - usually the general channel"""
		EffayBot.token = t
		EffayBot.server_id = s
		EffayBot.channel_id = c

	@client.event
	async def on_ready():
		EffayBot.server = EffayBot.client.get_server(EffayBot.server_id)
		EffayBot.channel = EffayBot.client.get_channel(EffayBot.channel_id)
		print("ready")

	def start(self):
		"""Starts the bot, connects to the server, and prints to the console to show progress"""
		EffayBot.client.run(EffayBot.token)

	@client.event
	async def log_off(message):
		"""Closes the connection to discord"""
		admin = False
		for i in message.author.roles:
			if(i.name == "administration"):
				admin = True
				break
		if(admin is True):
			await EffayBot.client.logout()
		else:
			await EffayBot.client.send_message(EffayBot.channel, "You don't have privelige to do that")

	@client.event
	async def auto_prune():
		"""Prune members who haven't been active"""
		EffayBot.client.request_offline_members(EffayBot.server)
		mems = 0
		for i in EffayBot.server.members:
			if(mems > 50):
				estim = await EffayBot.client.estimate_pruned_members(EffayBot.server, 3)
				if(estim > 15):
					await EffayBot.client.prune_members(EffayBot.server, 3)
					print("pruned {0} members".format(estim))
				break
		if(mems <= 50 or estim <= 15):
			print("did not prune")

	def check_id(message):
		return(EffayBot.flag_name == message.author.id)

	@client.event
	async def delete_from_time(message):
		"""
		Delete messages from a specified member posted in the last t minutes
		If t is 0, delete will not check for time or member
		"""
		admin = False
		for i in message.author.roles:
			if(i.name == "administration"):
				admin = True
				break
		if(admin is True):
			message_split = message.content.split(" ")
			if(len(message_split) == 3):
				if(message_split[2] == "0"):
					await EffayBot.client.purge_from(EffayBot.channel)
				else:
					EffayBot.flag_name = message_split[1]
					start_time = message.timestamp - datetime.timedelta(minutes=int(message_split[2]))
					await EffayBot.client.purge_from(EffayBot.channel, check=EffayBot.check_id, after=start_time)
		else:
			await EffayBot.client.send_message(EffayBot.channel, "You don't have privelige to do that")
			
	@client.event
	async def generate_help():
		inv = await EffayBot.client.create_invite(EffayBot.channel, max_age=1800)
		await EffayBot.client.send_message(EffayBot.channel,
"""Commands:
	.vote (a, b) :: vote for a or b
	.help :: display this help message

:: 30 min join link ::
{0}""".format(inv.url))

	@client.event
	async def on_member_join(member):
		"""
		Posts a welcome message to new users
		Check for auto prune
		"""
		print("new member")
		message = "Welcome, @{0}!!".format(member.name)
		await EffayBot.client.send_message(EffayBot.channel, message)
		await EffayBot.auto_prune()

	@client.event
	async def on_message(message):
		"""Handle message triggers"""
		if(message.content == ".help"):
			await EffayBot.generate_help()
		elif(message.content.startswith(".clean")):
			await EffayBot.delete_from_time(message)
		elif(message.content == ".quit"):
			await EffayBot.log_off(message)
		