class Vote:
	"""
	Manage voting for two options
	Keep track of who has voted in a local file
	"""

	def __init__(self, a, b):
		"""
		a  ::  a string containing the first option to vote for
		b  ::  a string containing the second option to vote for
		"""
		self.option_a = a
		self.option_b = b
		self.vote_list = []  # a list containing lists that each contain an int member id and string vote

	def add(self, member_id, vote):
		"""
		add an entry to vote_list
		RETURN  ::  a string saying whether the vote was added correctly
		"""
		member_voted = False
		for i in range(len(self.vote_list)):
			if(self.vote_list[i][0] == member_id):
				vote_list[i][1] = vote
				member_voted = True
				return "You alreaded voted! Vote changed."
		if(member_voted is False):
			self.vote_list.append([member_id, vote])
			return "Vote added."
		return "Could not add vote!"

	def tally(self):
		"""
		add up votes in vote_list
		RETURN  ::  a string saying which option won and how many votes each have
		"""
		tally_a = 0
		tally_b = 0
		for i in vote_list:
			if(i[1].lower() == "a"):
				tally_a += 1
			elif(i[1].lower() == "b"):
				tally_b += 1
		if(tally_a > tally_b):
			out_message = "{0} wins!".format(self.option_a)
		elif(tally_b > tally_a):
			out_message = "{0} wins!".format(self.option_b)
		else:
			out_message = "Tie!"
		out_message += "\nOption A({2}) had {0} votes.\nOption B({3}) had {1} notes".format(tally_a, tally_b, option_a, option_b)
		return out_message

	def generate_print(self):
		"""RETURN  ::  a string saying what the vote is on"""
		return "*Option A:* {0}\n*Option B:* {1}".format(self.option_a, self.option_b)

