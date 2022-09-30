# inspired by https://docs.quantifiedcode.com/python-anti-patterns/correctness/not_using_get_to_return_a_default_value_from_a_dictionary.html

if __name__ == '__main__':
    '''
    Instead of checking if a key is in a dict, and then getting it,
    should use dict.get(key, default).
    '''

    dictionary = {"message": "Hello, World!"}
    data = ""
    if "message" in dictionary:
        data = dictionary["message"]
    print(data)
