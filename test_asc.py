class Deal:
    def __init__(self, price, volume):
        self.price = price
        self.volume = volume

    def __str__(self):
        attr_list = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        str_repr = "["
        for every_attr in attr_list:
            str_repr += every_attr + " - " + str(getattr(self, every_attr)) + " "

        str_repr += "]"

        return str_repr

    def __eq__(self, other):
        print "EQ"
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            # FIXME ROUNDING
            return self.price == other.price
        return False

    def __lt__(self, other):
        """
        Used by biset.insert to maintain ordered asks\bids of order book
        :param other:
        :return:
        """
        print "comparing", self.price, "and", other.price, " result", self.price < other.price   
        return self.price > other.price

def search(some_list, target, cmp_method):
    min_idx = 0
    max_idx = len(some_list) - 1
    mid_idx = (min_idx + max_idx) / 2

    # uncomment next line for traces
    print "Elem for insertion: ", target, mid_idx
    print "Current list:"
    for b in some_list:
        print b

    if mid_idx < 0:
        return 0 
    elif min_idx == max_idx: 
        # i.e. single element
        if cmp_method(some_list[mid_idx], target):
            return mid_idx + 1
        else:
            return mid_idx

    while min_idx < max_idx:
        print mid_idx
        if some_list[mid_idx].price == target.price:
        # if some_list[mid_idx] == target:
            print "return"
            return mid_idx
        elif cmp_method(some_list[mid_idx], target):
            print "Go deeper: ", mid_idx + 1
            return mid_idx + 1 + search(some_list[mid_idx + 1:], target, cmp_method)
        else:
            print "Back"
            return search(some_list[:mid_idx], target, cmp_method)

def cmp_method_bid(a, b):
    return a.price < b.price

def cmp_method_ask(a, b):
    return a.price > b.price

import random

a = []
for idx in xrange(10):

  b = Deal(random.uniform(0, 1), random.uniform(0, 1))
  # a.append(b)

a = sorted(a, key=lambda x: x.price, reverse=True)
# a = sorted(a, key=lambda x: x.price, reverse=False)

print "Before insertion: "
for aa in a:
  print aa

b = Deal(random.uniform(0, 1), random.uniform(0, 1))
b1 = Deal(random.uniform(0, 1), random.uniform(0, 1))

import bisect

# bisect.insort_left(a, b)
# bisect.insort_left(a, b1)
idx = search(a, b, cmp_method_ask)
print "Found index for insertion: ",  idx, b
a.insert(idx, b)
idx = search(a, b1, cmp_method_ask)
print "Found index for insertion: ",  idx, b1
a.insert(idx, b1)


print "After insertion: "
for aa in a:
  print aa
