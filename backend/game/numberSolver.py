import random

add = lambda a,b: a+b
sub = lambda a,b: a-b
mul = lambda a,b: a*b
div = lambda a,b: a/b if a % b == 0 else 0/0

operations = [ (add, '+'),
               (sub, '-'),
               (mul, '*'),
               (div, '/')]

# def OneFromTheTop():
#     return [25, 50, 75][random.randint(0,2)]
def OneFromTheTop():
    return [5, 10, 15][random.randint(0,2)]

def OneOfTheOthers():
    return random.randint(1,10)

def Evaluate(stack):
    try:
        total = 0
        lastOper = add
        for item in stack:
            if type(item) is int:
                total = lastOper(total, item)
            else:
                lastOper = item[0]

        return total
    except:
        return 0

def ReprStack(stack):
    reps = [ str(item) if type(item) is int else item[1] for item in stack ]
    return ' '.join(reps)

def Solve(target, numbers):

    def Recurse(stack, nums):
        for n in range(len(nums)):
            stack.append( nums[n] )

            remaining = nums[:n] + nums[n+1:]

            if Evaluate(stack) == target:
                print(ReprStack(stack))

            if len(remaining) > 0:
                for op in operations:
                    stack.append(op)
                    stack = Recurse(stack, remaining)
                    stack = stack[:-1]

            stack = stack[:-1]

        return stack

    Recurse([], numbers)


# target = random.randint(100,1000)
target = random.randint(100,200)

numbers = [ OneFromTheTop() ] + [ OneOfTheOthers() for i in range(4) ]

print("Target: {0} using {1}".format(target, numbers))

Solve(target, numbers)