
# This function check if an array is monotonic increasing or decreasing
def method(nums: [float]) -> bool:
    a = []  # to store increasing flags
    b = []  # to store decreasing flags

    # iterate over the list, starting from first element
    for i in range(len(nums) - 1):
        # monotone increasing check: is this element equal or larger than next element?
        a.append(nums[i] <= nums[i + 1])

        # monotone decreasing check: is this element equal or smaller than next element?
        b.append(nums[i] >= nums[i + 1])

    # return true if either monotone increasing or decreasing; false otherwise
    return all(a) or all(b)


# Entry point where execution enters the program.
if __name__ == '__main__':
    x = [6, 5, 4, 4]
    y = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]
    z = [1, 1, 2, 3, 7]

    print(method(x))
    print(method(y))
    print(method(z))
