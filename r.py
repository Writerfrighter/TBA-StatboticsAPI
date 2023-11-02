import this

print(this.d)
print(this.s)


string = this.s
keys = this.d

result = ""

for char in string:
    if char in keys.keys():
        result += keys[char]
    else: result += char

print(result)