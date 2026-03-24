"""
示例 2：生成器在“逐行处理大数据”场景中的价值。

前一个例子主要讲的是：
生成器如何暂停和继续。

这个例子进一步讲：
为什么生成器在真实项目里很有用。

核心原因是：
生成器可以“边处理、边产出”，而不是把所有结果都先堆到内存里。

这特别适合：
- 大文件处理
- 数据流清洗
- 流式接口返回
- 边计算边输出

这和后面 SSE 接口里的 `yield chunk` 思路是完全一致的。
"""


# 模拟一个较大的数据源。
#
# 在真实场景里，这可能是：
# - 文件中的每一行
# - 数据库游标中的每一条记录
# - 网络流中的一段数据
raw_data_source = ["Row 1", "Row 2", "   ", "Row 4", "Row 5"]


def process_large_file(data):
    """
    逐条处理输入数据，并用生成器逐步返回结果。

    为什么这里不用列表收集全部结果再返回？
    因为当数据量很大时，那样会造成不必要的内存占用。

    生成器的优势是：
    处理一条，就交付一条。
    """

    for line in data:
        # 模拟数据清洗逻辑。
        # `strip()` 会去掉首尾空白字符。
        cleaned_line = line.strip()

        # 空行直接跳过。
        if not cleaned_line:
            continue

        # 假设这里还有更复杂、甚至更耗时的逻辑，比如：
        # - 数据校验
        # - 规则清洗
        # - 数据库查询
        # - 调用外部接口

        # 关键点：
        # 一旦这条数据处理完，就立刻通过 `yield` 交出去，
        # 而不是继续积压在内存中等待全部处理结束。
        yield f"Processed: {cleaned_line}"


# 使用生成器。
#
# 此时 `processor` 不是最终结果列表，
# 而是一个“可逐步产出结果”的生成器对象。
processor = process_large_file(raw_data_source)


# `for` 循环会自动反复调用 `next(processor)`，
# 直到生成器抛出 `StopIteration` 为止。
for item in processor:
    print(f"获得结果 -> {item}")
