import worldvision_ai_project.agent as agent


def test_search_routing(monkeypatch):
    def mock_search(**kwargs):
        return {
            "answer": "검색 테스트 성공",
            "sources": ["test.pdf"],
        }

    monkeypatch.setattr(agent, "run_knowledge_search", mock_search)

    result = agent.invoke_agent({
        "request_type": "search",
        "query": "테스트 질문",
    })

    assert result["error"] is None
    assert result["result"]["answer"] == "검색 테스트 성공"


def test_minutes_routing(monkeypatch):
    def mock_minutes(**kwargs):
        return {
            "summary": "회의록 테스트 성공",
            "key_issues": [],
            "decisions": [],
        }

    monkeypatch.setattr(agent, "process_audio_minutes", mock_minutes)

    result = agent.invoke_agent({
        "request_type": "minutes",
        "file_name": "test.wav",
        "file_bytes": b"fake audio",
    })

    assert result["error"] is None
    assert result["result"]["summary"] == "회의록 테스트 성공"


def test_report_routing(monkeypatch):
    def mock_report(**kwargs):
        return "보고서 테스트 성공"

    monkeypatch.setattr(agent, "generate_ai_report", mock_report)

    result = agent.invoke_agent({
        "request_type": "report",
        "topic": "테스트 주제",
    })

    assert result["error"] is None
    assert result["result"] == "보고서 테스트 성공"


def test_fallback_routing():
    result = agent.invoke_agent({
        "request_type": "invalid",
    })

    assert result["error"] == "INVALID_REQUEST_TYPE"
    assert result["result"]["type"] == "fallback"