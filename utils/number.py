import re
from typing import Optional, Tuple, Union

class BracketNumberTool:
    """
    用于提取和处理文本中括号里的数字，支持多种格式：
    - (31/35)
    - （31 / 35）
    - ( 31 / 35 )
    ---用   法---
    text = "看视频领元宝(31/35)"
    print(BracketNumberTool.extract(text))      # (31, 35)
    print(BracketNumberTool.compare(text))      # True (默认 lt)
    print(BracketNumberTool.compare(text, "eq"))# False
    print(BracketNumberTool.difference(text))   # 4
    print(BracketNumberTool.progress(text))     # 0.8857142857142857
    """

    pattern = re.compile(r'[\(（]\s*(\d+)\s*/\s*(\d+)\s*[\)）]')

    @classmethod
    def extract(cls, text: str) -> Optional[Tuple[int, int]]:
        """
        提取括号内的两个数字
        """
        match = cls.pattern.search(text)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None

    @classmethod
    def compare(cls, text: str, mode: str = "lt") -> Optional[bool]:
        """
        比较两个数字
        mode:
            "lt"  -> num1 < num2
            "le"  -> num1 <= num2
            "eq"  -> num1 == num2
            "gt"  -> num1 > num2
            "ge"  -> num1 >= num2
        """
        nums = cls.extract(text)
        if not nums:
            return None
        num1, num2 = nums
        if mode == "lt":
            return num1 < num2
        elif mode == "le":
            return num1 <= num2
        elif mode == "eq":
            return num1 == num2
        elif mode == "gt":
            return num1 > num2
        elif mode == "ge":
            return num1 >= num2
        else:
            raise ValueError(f"未知比较模式: {mode}")

    @classmethod
    def difference(cls, text: str) -> Optional[int]:
        """
        返回 num2 - num1 的差值
        """
        nums = cls.extract(text)
        if not nums:
            return None
        return nums[1] - nums[0]

    @classmethod
    def progress(cls, text: str) -> Optional[float]:
        """
        返回进度百分比 (0~1)
        """
        nums = cls.extract(text)
        if not nums:
            return None
        return nums[0] / nums[1] if nums[1] != 0 else None
