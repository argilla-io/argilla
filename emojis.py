def jslen(string):
    return int(len(string.encode(encoding='utf_16_le'))/2)


array = [
  'This is a message with a 👍',
  'This is a message with a 👍🏾',
  'This is a message with a 👍🏾👍',
]

for i in array:
  print(i, jslen(i))