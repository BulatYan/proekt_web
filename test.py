a = int(input())
s = []
for _ in range(a):
    s.append(int(input()))
max = 0
for i in s:
    if i % 5 == 0 and  i > max:
        max = i
print(max)