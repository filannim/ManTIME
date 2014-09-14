class date_utility:
	@staticmethod
	def get_num_from_literal(literal):
		if numbers.get(literal.strip().lower(),'')!='':
			return numbers[literal.strip().lower()]
		if ordinals.get(literal.strip().lower(),'')!='':
			return ordinals[literal.strip().lower()]
	
	@staticmethod
	def get_literal_nums():
		return numbers.keys()+ordinals.keys()
	   
	@staticmethod
	def get_nums():
		return numbers.values()
	
	@staticmethod
	def int_to_roman(i):
		result = []
		for integer, numeral in numeral_map:
			count = int(i / integer)
			result.append(numeral * count)
			i -= integer * count
		return ''.join(result)

	@staticmethod
	def roman_to_int(n):
		n = unicode(n).upper()
		i = result = 0
		for integer, numeral in numeral_map:
			while n[i:i + len(numeral)] == numeral:
				result += integer
				i += len(numeral)
		return result
		
numbers = {'zero':0,
		   'one':1,
		   'two':2,
		   'three':3,
		   'four':4,
		   'five':5,
		   'six':6,
		   'seven':7,
		   'eight':8,
		   'nine':9,
		   'ten':10,
		   'eleven':11,
		   'twelve':12,
		   'thirteen':13,
		   'fourteen':14,
		   'fifteen':15,
		   'sixteen':16,
		   'seventeen':17,
		   'eighteen':18,
		   'nineteen':19,
		   'twenty':20,
		   'twenty-? ?one':21,
		   'twenty-? ?two':22,
		   'twenty-? ?three':23,
		   'twenty-? ?four':24,
		   'twenty-? ?five':25,
		   'twenty-? ?six':26,
		   'twenty-? ?seven':27,
		   'twenty-? ?eight':28,
		   'twenty-? ?nine':29,
		   'thirty':30,
		   'thirty-? ?one':31,
		   'thirty-? ?two':32,
		   'thirty-? ?three':33,
		   'thirty-? ?four':34,
		   'thirty-? ?five':35,
		   'thirty-? ?six':36,
		   'thirty-? ?seven':37,
		   'thirty-? ?eight':38,
		   'thirty-? ?nine':39,
		   'forty':40,
		   'forty-? ?five':45,
		   'fifty':50,
		   'fifty-? ?five':55,
		   'sixty':60,
		   'sixty-? ?five':65,
		   'seventy':70,
		   'eighty':80,
		   'ninety':90,
		   '(?:one-? ?)?hundred':100,}

ordinals = {'first':1,
		   'second':2,
		   'third':3,
		   'fourth':4,
		   'fifth':5,
		   'sixth':6,
		   'seventh':7,
		   'eighth':8,
		   'ninth':9,
		   'tenth':10,
		   'eleventh':11,
		   'twelfth':12,
		   'thirteenth':13,
		   'fourteenth':14,
		   'fifteenth':15,
		   'sixteenth':16,
		   'seventeenth':17,
		   'eighteenth':18,
		   'nineteenth':19,
		   'twentieth':20,
		   'twenty-? ?first':21,
		   'twenty-? ?second':22,
		   'twenty-? ?third':23,
		   'twenty-? ?fourth':24,
		   'twenty-? ?fifth':25,
		   'twenty-? ?sixth':26,
		   'thirtyth':30,
		   'fourtyth':40,
		   'fiftyth':50,
		   'sixtyth':60}

numeral_map = zip((1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
	('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I'))