import os
import pickle

password = "hardcoded_secret"
user_input = input("cmd> ")
os.system(user_input)
data = pickle.loads(user_input)
