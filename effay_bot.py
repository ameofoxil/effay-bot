import discord
import asyncio
import datetime
import praw
import random

import voteContainer


class EffayBot():
	"""
	Methods and functionality for a fashion discord bot
	Functions:
		Log on and off
		Delete messages from a specified user posted in the last x time
		Post a welcome message when a new user joins
		Post a help message displaying commands
		Post fashion inspo pictures scrubbed from reddit
		Prune members who haven't been active
		Runs voting for multiple polls

	TODO: Add file IO to preserve polls between restarts
		"""


	client = discord.Client()
	reaction_list = ["🅰", "🇳", "🇬", "🇪", "🇷", "🇾"]
	token = ""
	flag_name = ""
	vote_manager = voteContainer.VoteContainer()
	reddit_handle = None
	blacklist = [251145296900390913, 295983743125159936]

	def __init__(self):
		"""
		Reads sensitive data from a file
		"""
		file = open("data", "r")
		content = file.read().split("\n")
		file.close()
		EffayBot.token = content[0]
		EffayBot.reddit_handle = praw.Reddit(client_id=content[1],
									client_secret=content[2],
									username=content[3],
									password=content[4],
									user_agent=content[5])
		del content

	def start(self):
		"""Starts the bot, connects to the server"""
		EffayBot.client.run(EffayBot.token)

	@client.event
	async def log_off(message):
		"""Closes the connection to discord if the user who gave the command has the administration tag"""
		admin = True
		for i in message.author.roles:
			if(i.name == "administration"):
				admin = True
				break
		if(admin is True):
			await EffayBot.client.logout()
		else:
			await EffayBot.client.send_message(message.channel, "You don't have privelige to do that")

	@client.event
	async def auto_prune(server):
		"""
		Prune members who haven't been active
		Requires permission to remove members
		"""
		EffayBot.client.request_offline_members(server)
		mems = 0
		for i in server.members:
			if(mems > 50):
				estim = await EffayBot.client.estimate_pruned_members(server, 3)
				if(estim > 15):
					await EffayBot.client.prune_members(server, 3)
				break


	def check_id(message):
		"""Helper function for delete_from_time"""
		return(message.author.id == EffayBot.flag_name)

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
			message_split = message.content.split("; ")
			if(len(message_split) == 3):
				if(message_split[2] == "0"):
					await EffayBot.client.purge_from(message.channel)
				else:
					EffayBot.flag_name = message_split[1]
					start_time = message.timestamp - datetime.timedelta(minutes=int(message_split[2]))
					await EffayBot.client.purge_from(message.channel, check=EffayBot.check_id, after=start_time)
		else:
			await EffayBot.client.send_message(message.channel, "You don't have privelige to do that")
		
	@client.event
	async def post_inspo(message):
		"""Post fashion inspo pictures scrubbed from reddit"""
		post = ""
		content = []
		if(message.content == ".inspo"):
			content.append("malefashion")
		else:
			for i in message.content.split("; "):
				content.append(i)
			del content[0]
		for i in content:
			post += "**" + i + "**\n"
			count = 0
			sub = EffayBot.reddit_handle.subreddit(i)
			for j in sub.hot():
				if(j.stickied is False):
					post += (j.url + "\n")
					count += 1
					if(count == 3):
						break
		await EffayBot.client.send_message(message.channel, post)

	@client.event
	async def cron_stay_alive():
		while True:
			await EffayBot.client.send_message(EffayBot.client.get_channel("376258979678126080"), "staying alive")
			await asyncio.sleep(3600)

	@client.event
	async def voting(message):
		contents = message.content.split("; ")
		if(contents[1] == "add"):
			EffayBot.vote_manager.add_object(contents[2], contents[3], contents[4])
		elif(contents[1] == "remove"):
			EffayBot.vote_manager.remove_object()
		elif(contents[1] == "list"):
			await EffayBot.client.send_message(message.channel, EffayBot.vote_manager.list())
		elif(contents[1] == "active"):
			EffayBot.vote_manager.set_active(int(contents[2]))
		elif(contents[1] == "result"):
			await EffayBot.client.send_message(message.channel, EffayBot.vote_manager.make_results())
		else:
			await EffayBot.client.send_message(message.channel, EffayBot.vote_manager.vote(message.author.id, contents[1]))

	@client.event
	async def generate_help(message):
		await EffayBot.client.send_message(message.channel,
"""**__Commands:__**
	.help :: display this help message
	.link :: get a 30min invite link
	.inspo; <subreddit_list> :: get the top 3 images from a subreddit
		Examples: malefashion, femalefashion, wallpapers, etc
		<subreddit_list> defaults to malefashion if no param is entered
		Can take multiple param arguments separated by "; " without quotes
	.vote; <command>; <arg list> :: vote on stuff
		*Specific commands:*
		add; <title>; <option a>; <option b> :: add a vote
		remove :: remove the active vote
		list ::  list all votes and get some info about each one
		active; <number> :: set the voted numbered <number> as active
		result :: get the winner and tally of the active vote
	.vote; a :: vote for option a
	.vote; b :: vote for option b

**__Admin Commands__**
	.clean; <member_id>; <time> :: delete all messages from user <member_id> posted between now and <time> minutes ago
		.clean 0 0 will delete the last 100 messages posted by anyone
	.quit :: turn off the bot

	**Arguments for commands must be separated by "; " without quotes!!**
""")

	@client.event
	async def generate_link(message):
		inv = await EffayBot.client.create_invite(message.channel, max_age=1800)
		await EffayBot.client.send_message(message.channel, inv.url)

	@client.event
	async def on_member_join(member):
		"""
		Posts a welcome message to new users
		Check for auto prune
		"""
		message = "Welcome, {0}!!".format(member.name)
		await EffayBot.client.send_message(member.server.default_channel, message)
		await EffayBot.auto_prune(member.server)

	@client.event
	async def on_message(message):
		"""Handle message triggers"""
		blacklisted = False
		for i in EffayBot.blacklist:
			if(message.author.id == str(i)):
				blacklisted = True

		if(blacklisted is False):
			if(message.content == ".help"):
				await EffayBot.generate_help(message)

			elif(message.content == ".link"):
				await EffayBot.generate_link(message)

			elif(message.content.startswith(".clean")):
				await EffayBot.delete_from_time(message)

			elif(message.content == ".quit"):
				await EffayBot.log_off(message)

			elif(message.content.startswith(".inspo")):
				await EffayBot.post_inspo(message)

			elif(message.content.startswith(".vote")):
				await EffayBot.voting(message)

			elif(message.content.find("😠") is not -1):
				for i in EffayBot.reaction_list:
					await EffayBot.client.add_reaction(message, i)

	@client.event
	async def on_ready():
		await EffayBot.cron_stay_alive()
		