import heapq

hq = heapq
num = [20, 1, 2, 3, 4, 5]

hq.heapify(num)

while num:
    print(num)
    d = hq.heappop(num)
    print(d)
