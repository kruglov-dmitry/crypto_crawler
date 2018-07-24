from analysis.binary_search import binary_search
from data.Deal import Deal
from data.OrderBook import cmp_method_ask, cmp_method_bid

import random

a = []
# for idx in xrange(10):
#  b = Deal(random.uniform(0, 1), random.uniform(0, 1))
#  a.append(b)

a.append(Deal(0.03172795, random.uniform(0, 1)))
a.append(Deal(0.03172796, random.uniform(0, 1)))
a.append(Deal(0.03172798, random.uniform(0, 1)))
a.append(Deal(0.03172801, random.uniform(0, 1)))
a.append(Deal(0.03173, random.uniform(0, 1)))
a.append(Deal(0.03174392, random.uniform(0, 1)))
a.append(Deal(0.0318111, random.uniform(0, 1)))
a.append(Deal(0.03189575, random.uniform(0, 1)))
a.append(Deal(0.03197009, random.uniform(0, 1)))
a.append(Deal(0.03197015, random.uniform(0, 1)))

a = sorted(a, key=lambda x: x.price, reverse=False)

print "Before insertion: "
for aa in a:
  print aa

# b = Deal(0.03172794, 100400.0)
b = Deal(0.03172795, 100400.0)

# smaller_case = Deal(0.000001, random.uniform(0, 1))

# FIND and delete it
# b2 = Deal(0.03835944, random.uniform(0, 1))

# FIND and update volume
# b3 = Deal(0.03835945, 10)

idx = binary_search(a, b, cmp_method_ask)
print "Found index for insertion: ",  idx, b

item_insert_point = binary_search(a, b, cmp_method_ask)
is_present = False
if item_insert_point < len(a):
    is_present = a[item_insert_point] == b

if is_present:
    a[item_insert_point].volume = b.volume
else:
    a.insert(idx, b)

# idx = binary_search(a, b2, cmp_method_ask)
# idx = search(a, b2, cmp_method_ask)
# print "Found index for deletion: ",  idx, b2
# a.insert(idx, b1)
# del a[idx]

# idx = search(a, b3, cmp_method_ask)
# idx = binary_search(a, b3, cmp_method_ask)
# print "Found index for update: ",  idx, b3
# a[idx].volume += b3.volume

print "After insertion: "
for aa in a:
  print aa

"""
idx = binary_search(a, smaller_case, cmp_method_ask)
# idx = search(a, b2, cmp_method_ask)
print "Found index for insertion in front of array: ",  idx, smaller_case
a.insert(idx, smaller_case)


print "After final insertion: "
for aa in a:
  print aa
"""