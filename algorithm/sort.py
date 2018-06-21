import copy
import random
import cProfile

exam = list(range(10000))
random.shuffle(exam)


def bubble_sort_simple(lis):
    """
        最简单的交换排序，时间复杂度O(n^2)
    """
    _lis = copy.copy(lis)
    length = len(_lis)
    for i in range(length):
        for j in range(i + 1, length):
            if _lis[i] > _lis[j]:
                _lis[i], _lis[j] = _lis[j], _lis[i]
    print(_lis)


def bubble_sort(lis):
    """
        冒泡排序，时间复杂度O(n^2)
    """
    _lis = copy.copy(lis)
    length = len(_lis)
    for i in range(length):
        for j in range(length - 1):
            if _lis[j] > _lis[j + 1]:
                _lis[j], _lis[j + 1] = _lis[j + 1], _lis[j]

    print(_lis)


def bubble_sort_advance(lis):
    """
        冒泡排序改进算法，时间复杂度O(n^2)
        设置flag，当一轮比较中未发生交换动作，则说明后面的元素其实已经有序排列了。
        对于比较规整的元素集合，可提高一定的排序效率。
    """
    _lis = copy.copy(lis)
    length = len(_lis)
    for i in range(length):
        # 上轮是否发生交换
        flag = False
        if not flag:
            for j in range(length - 1):
                if _lis[j] > _lis[j + 1]:
                    flag = True
                    _lis[j], _lis[j + 1] = _lis[j + 1], _lis[j]

    print(_lis)


def insert_sort(array):
    """
        直接插入排序
        时间复杂度：O(n²)
        空间复杂度：O(1)
        稳定性：稳定
    """

    for i in range(len(array)):
        for j in range(i):
            if array[i] < array[j]:
                array.insert(j, array.pop(i))
                break
    return array


def shell_sort(array):
    """
        希尔排序
        时间复杂度：O(n)
        空间复杂度：O(n√n)
        稳定性：不稳定
    """
    gap = len(array)
    while gap > 1:
        gap = gap // 2
        for i in range(gap, len(array)):
            for j in range(i % gap, i, gap):
                if array[i] < array[j]:
                    array[i], array[j] = array[j], array[i]
    return array


def select_sort(array):
    """
        简单选择排序
        时间复杂度：O(n²)
        空间复杂度：O(1)
        稳定性：不稳定
        始时在序列中找到最小（大）元素，放到序列的起始位置作为已排序序列；然后，再从剩余未排序元素中继续寻找最小（大）元素，放到已排序序列的末尾。以此类推，直到所有元素均排序完毕。
    """

    for i in range(len(array)):
        x = i  # min index
        for j in range(i, len(array)):
            if array[j] < array[x]:
                x = j
        array[i], array[x] = array[x], array[i]
    return array


def heap_sort(array):
    """
        堆排序
        时间复杂度：O(nlog₂n)
        空间复杂度：O(1)
        稳定性：不稳定
        
        堆排序是指利用堆这种数据结构所设计的一种选择排序算法。堆是一种近似完全二叉树的结构（通常堆是通过一维数组来实现的），
        并满足性质：以最大堆（也叫大根堆、大顶堆）为例，其中父结点的值总是大于它的孩子节点。
        
        堆排序的过程：
            由输入的无序数组构造一个最大堆，作为初始的无序区
            把堆顶元素（最大值）和堆尾元素互换
            把堆（无序区）的尺寸缩小1，并调用heapify(A, 0)从新的堆顶元素开始进行堆调整
            重复步骤2，直到堆的尺寸为1
    """
    def heap_adjust(parent):
        child = 2 * parent + 1  # left child
        while child < len(heap):
            if child + 1 < len(heap):
                if heap[child + 1] > heap[child]:
                    child += 1  # right child
            if heap[parent] >= heap[child]:
                break
            heap[parent], heap[child] = \
                heap[child], heap[parent]
            parent, child = child, 2 * child + 1

    heap, array = array.copy(), []
    for i in range(len(heap) // 2, -1, -1):
        heap_adjust(i)
    while len(heap) != 0:
        heap[0], heap[-1] = heap[-1], heap[0]
        array.insert(0, heap.pop())
        heap_adjust(0)
    return array


def main():
    # cProfile.run('bubble_sort_simple(exam)')
    # cProfile.run('bubble_sort(exam)')
    # cProfile.run('select_sort(exam)')
    cProfile.run('heap_sort(exam)')


if __name__ == '__main__':
    main()
