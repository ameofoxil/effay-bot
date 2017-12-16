from voting import Vote

class VoteContainer:
	"""Functionality to manage multiple vote objects"""


	def __init__(self):
		self.object_list = []
		self.active = -1

	def add_object(self, t, a, b):
		"""Appends a vote object to the list and sets it it as active"""
		self.object_list.append([t, Vote(a, b)])
		self.active += 1

	def remove_object(self):
		"""
		Removes active vote object
		sets active to -1
		"""
		del self.object_list[self.active]
		self.active = -1

	def list(self):
		message = ""
		for i in range(len(self.object_list)):
			message += "**Vote {0}: {1}**".format(i + 1, self.object_list[i][0])
			if(i == self.active):
				message += " - *active*"
			message += "\n{0}\n\n".format(self.object_list[i][1].generate_print())
		return message

	def set_active(self, n):
		"""sets the active vote"""
		if(n - 1 <= len(self.object_list)):
			self.active = n - 1

	def vote(self, member_id, option):
		"""add a vote to the active vote object"""
		return self.object_list[self.active][1].add(member_id, option)

	def make_results(self):
		message = self.object_list[self.active][1].tally()
		self.remove_object()
		return message
		