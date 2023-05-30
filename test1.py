a = int(input())
s = []
for _ in range(a):
    s.append(int(input()))
a1 = []
for i in s:
    if i % 3 == 0:
        a1.append(i)
count = 0
for i in a1:
    count += i
print(count)
