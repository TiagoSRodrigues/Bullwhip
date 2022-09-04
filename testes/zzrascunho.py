

from itertools import zip_longest
from typing import List


def twoSum( nums: List[int], target: int) -> List[int]:
    size=len(nums)
    for first in range(size):
        for sec in range(size-first-1):
            sec=sec+first+1
            if nums[first]+nums[sec] == target:
                return [first, sec]
        
            



print(
    twoSum(nums=[3,3], target= 6)
    )