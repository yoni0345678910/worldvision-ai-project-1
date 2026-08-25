from typing import List, Dict
from collections import defaultdict

class ConversationHistoryManager:
    def __init__(self, max_history: int = 5):
        # session_id별 대화 기록 (최근 max_history 쌍 유지)
        self.history: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.max_history = max_history

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """해당 세션의 이전 대화 내역을 가져옵니다."""
        return self.history[session_id]

    def add_user_message(self, session_id: str, content: str):
        """사용자 질문 저장"""
        self.history[session_id].append({"role": "user", "content": content})
        self._trim_history(session_id)

    def add_assistant_message(self, session_id: str, content: str):
        """AI 답변 저장"""
        self.history[session_id].append({"role": "assistant", "content": content})
        self._trim_history(session_id)

    def _trim_history(self, session_id: str):
        """메모리 관리를 위해 최근 대화만 남기고 오래된 대화 삭제"""
        if len(self.history[session_id]) > self.max_history * 2:
            self.history[session_id] = self.history[session_id][-self.max_history * 2:]

# 전역 인스턴스 생성
history_manager = ConversationHistoryManager(max_history=5)