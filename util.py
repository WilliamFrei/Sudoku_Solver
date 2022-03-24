

def magnitude_sign(lit: int):
	"""
	Converts a literal from a twos-complement representation to a magnitude-sign representation.
	
	This way, flipping the last binary digit gives the complementary literal,
	and there's also a subtraction of 1 included to shift the numbers from the range [1, n] to [0, n - 1] so that the literals can be used for zero-based indexing.
	"""
	magn = abs(lit) - 1
	sign = 0 if lit > 0 else 1 # 0 = positive, 1 = negative
	return 2 * magn + sign

def twos_complement(lit: int):
	"""
	Inverse to the 'magnitude_sign' function.
	"""
	sign = 1 if lit % 2 == 0 else -1 # this 'sign' is used as a multiplier, thus it is 1 or -1
	magn = lit // 2 + 1 # add back the 1 that was subtracted above
	return magn * sign

def magnitude(lit: int):
	"""
	Convenience function to extract the magnitude from a literal in magnitude-sign representation.
	"""
	return lit // 2

def is_positive(lit: int):
	"""
	Convenience function to extract the polarity (sign) from a literal in magnitude-sign representation.
	"""
	return bool(1 - (lit & 1))

def complement(lit: int):
	"""
	Convenience function to get the complementary literal from a literal in magnitude-sign representation.
	"""
	return lit ^ 1 # flip the least significant bit which encodes the polarity with a binary XOR

def test_repr_conversion():
	forward_map = {}
	# for simplicity's sake, the literals that would appear in sudoku are tested
	for l in range(1, 9 ** 3  + 1):
		assert  l == twos_complement(magnitude_sign( l))
		assert -l == twos_complement(magnitude_sign(-l))
		assert magnitude_sign( l) not in forward_map, f"{ l}, {magnitude_sign( l)}, {forward_map[magnitude_sign( l)]}"
		forward_map[magnitude_sign( l)] = l
		assert magnitude_sign(-l) not in forward_map, f"{-l}, {magnitude_sign(-l)}, {forward_map[magnitude_sign(-l)]}"
		forward_map[magnitude_sign(-l)] = -l
	
	backward_map = {}
	for l in range(2 * 9 ** 3):
		assert l == magnitude_sign(twos_complement(l))
		assert twos_complement(l) not in backward_map, f"{l}, {twos_complement(l)}, {forward_map[twos_complement(l)]}"
		backward_map[twos_complement(l)] = l


# test_repr_conversion()

