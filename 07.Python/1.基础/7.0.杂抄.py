

变量的绑定时机
    ### 示例1,变量值中途被修改了 ####
    def create_multipliers():
        return [lambda x : i * x for i in range(5)]

    for multiplier in create_multipliers():
        print multiplier(2)

    # 期望打印值是: 0, 2, 4, 6, 8
    # 实际打印值是: 8, 8, 8, 8, 8

    '''
    解析,闭包的变量值,会被外部函数改变
    这示例实际使用时, i 的值随着外部改变,已经是最后一个值了,即 i= 4

    另外，由于 create_multipliers 函数比较难懂，这里写个易懂的等价函数来
    def create_multipliers():
        l = []
        for i in range(5):
            l.append(lambda x: i * x)
        return l
    '''

    ### 示例2,用传参把当时变量定型下来 ###
    def create_multipliers():
        return [lambda x, i=i : i * x for i in range(5)] # 定义 lambda 函数时,需要设定参数默认值，此时定下了参数值

    for multiplier in create_multipliers():
        print multiplier(2)


    ### 示例3,利用元组不能改变的特性把当时变量定型下来 ###
    def create_multipliers():
        return (lambda x: i * x for i in range(5))

    for multiplier in create_multipliers():
        print multiplier(2)


判断奇数
    # 经典的写法，对2求余
    if a % 2: print 'it is even'

    # 自然是使用位操作最快了
    if a & 1: print 'it is even'


计算任何数的阶乘
    # Python 2.x.
    result= (lambdak: reduce(int.__mul__,range(1,k+1),1))(3)
    print(result) #-> 6

    # Python 3.x.
    import functools
    result= (lambdak: functools.reduce(int.__mul__,range(1,k+1),1))(3)
    print(result) #-> 6


找到列表中出现最频繁的数
    # 利用 list 的 count 函数
    list1 = [1,2,3,4,2,2,3,1,4,4,4]
    print(max(set(list1),key=list1.count)) # -> 4


重置递归限制
    # Python 限制递归次数到 1000，我们可以重置这个值
    # 请只在必要的时候采用。
    import sys
    x = 1001
    print(sys.getrecursionlimit()) # -> 1000
    sys.setrecursionlimit(x)
    print(sys.getrecursionlimit()) # -> 1001



检查一个对象的内存使用
    # 在 Python 2.7 中，一个 32 比特的整数占用 24 字节，在 Python 3.5 中利用 28 字节。为确定内存使用，我们可以调用 getsizeof 方法：

    # 在 Python 2.7 中
    import sys
    x=1
    print(sys.getsizeof(x)) # -> 24

    # 在 Python 3.5 中
    import sys
    x=1
    print(sys.getsizeof(x)) # -> 28


一行代码搜索字符串的多个前后缀
    print('http://www.google.com'.startswith(('http://','https://'))) # -> True
    print('http://www.google.co.uk'.endswith(('.com','.co.uk'))) # -> True

