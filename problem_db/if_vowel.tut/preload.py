def is_vowel(c):
    """Return True iff 'c' is a vowel.
    
    Parameters:
        c (str): Character to check if it is a vowel
        
    Returns:
        bool: True if 'c' is a vowel, otherwise False 
    
    """
    return c == 'a' or c == 'e' or c == 'i' or c == 'o' or c == 'u'

# The above definition uses or, below is an alternative definition that uses in 
#
# def is_vowel(c):
#     return c in 'aeiou'

char = input('Please enter a character: ')
