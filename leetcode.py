import subprocess
import tempfile
import os
from app import Question
import random


def run_leetcode_command(cmd_args):
	cmd_args = ["leetcode"] + cmd_args
	return subprocess.check_output(cmd_args)

class LeetcodeAPI:
	def __init__(self):
		pass

	# language is something like .py, etc 
	def submit_solution(self, problemid, language, code):
		# save the code into a file name like <problemid>.<anything>.ext
		# use tempfile here to create a temporary file
		# mkstemp returns (fd, fname) where fd is a filedescriptor
		_, fname = tempfile.mkstemp(prefix="%s." % problemid, suffix=".%s" % language)
		print "MADE TEMP FILE", fname
		with open(fname, "w") as f:
			f.write(code)

		# call leetcode CLI with leetcode submit <filename> and retrieve output
		try:
			output = run_leetcode_command(["submit", fname])
			if output.find("Accepted") != -1:
				print "ACCEPTED", output
				submission = Question.create(leetcode_id = problemid, submission = code, status = True)
			elif output.find("Wrong Answer") != -1:
				print "WRONG ANSWER", output
				submission = Question.create(leetcode_id = problemid, submission = code, status = False)
			else:
				print "UNKNOWN", output
				submission = Question.create(leetcode_id = problemid, submission = code, status = False)
			return output
		finally:
			print "REMOVING", fname
			os.remove(fname)

	def get_problem(self, problemid, lang="python"):
		pass

	def all_problems(self):
		output = run_leetcode_command(["list"]).decode("utf-8")
		output = output.splitlines()
		locked_questions = []
		

		for q in output:
			if q.find(u"\U0001F512") != -1:
				k = (q[q.find("[")+1:q.find("]")])
				k = int(k)
				locked_questions.append(k)

		pick_num = random.randint(1, 989)

		if pick_num in locked_questions:
			self.all_problems()
				
		return pick_num

	def list_problems(self, difficulty):
		output = run_leetcode_command(["list", "-q", difficulty]).decode("utf-8")
		output = output.splitlines()
		listing = {}

		#extra parameters to include
		# list -q D == all questions incompleted
		
		for v in output:
			if v.find(u"\U0001F512") != -1:
				continue
			else:
			#extract only the problem number
				k = (v[v.find("[")+1:v.find("]")])
				k = int(k)
				k = str(k)

				listing[k] = v
	
		return listing

	# we need to pull from the database here and get existing submission if it exists
	def get_file(self, problemid, lang="python"):
		problemid = str(problemid)
		output = run_leetcode_command(["show", "-g", problemid, "-l", lang])
		filename = None
		lines = output.splitlines()
		for line in lines:
			if line.find('Source Code') != -1:
				filename = line.split(':')
		filename = filename[1].strip()
		with open(filename, "r") as f:
			output = f.read()

		if filename:
			os.remove(filename)

		return output
		
		#print(lines)

TWO_SUM_SOLUTIONS="""
class Solution(object):
    def twoSum(self, nums, target):
        result = []
        for i in range(len(nums)):
            for j in range(i+1, len(nums)):
                if nums[i] + nums[j] == target:
                    result.append(i)
                    result.append(j)
                    
        return result

"""
if __name__ == "__main__":
	api = LeetcodeAPI()
	# api.submit_solution(1, "py", TWO_SUM_SOLUTIONS)
	print api.get_file(1)
