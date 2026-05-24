from typing import Optional, List, Dict

class ModerationException(Exception):
    """
    Ném khi AI từ chối nội dung.
    Controller sẽ bắt và trả về HTTP 400 với chi tiết.
    """
    def __init__(
        self,
        reason: str,
        violated_categories: Optional[List[str]] = None,
        scores: Optional[Dict[str, float]] = None,
        confidence: float = 0.0
    ):
        self.reason = reason
        self.violated_categories = violated_categories or []
        self.scores = scores or {}
        self.confidence = confidence
        super().__init__(reason)
