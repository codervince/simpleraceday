import time
from functools import wraps
'''
has wrapper function any args  
*args, **kwargs
func is original unwrapped function
@wraps.func needed for metadata (name, metadata, calling signature,...)
to get signature call from inspect import signature >> signature(function_name)
'''

def timethis(func):
	'''
	decorator report execution time
	'''
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.time()
		result = func(*args, **kwargs)
		end = time.time()
		print(func,__name__, end-start)
		return result
	return wrapper

