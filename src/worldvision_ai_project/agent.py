from typing import TypedDict, Literal, Optional, Any

from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langfuse import get_client

from worldvision_ai_project.services.search import run_knowledge_search
from worldvision_ai_project.services.minutes import process_audio_minutes
from worldvision_ai_project.services.report import generate_ai_report

import logging
import time


load_dotenv()

langfuse = get_client()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


class AgentState(TypedDict, total=False):
    request_type: Literal["search", "minutes", "report"]

    # 지식검색
    query: Optional[str]
    session_id: Optional[str]
    embedding_model: Optional[str]
    top_k: Optional[int]
    search_type: Optional[str]
    filters: Optional[dict]

    # 회의록
    file_name: Optional[str]
    file_bytes: Optional[bytes]

    # 보고서
    topic: Optional[str]

    # 공통 출력
    result: Any
    error: Optional[str]


def log_node_execution(
    node_name: str,
    start_time: float,
    error: Optional[str] = None
):
    latency = time.perf_counter() - start_time

    logger.info(
        "node=%s | success=%s | latency=%.3fs | error=%s",
        node_name,
        error is None,
        latency,
        error
    )


def search_node(state: AgentState):
    start_time = time.perf_counter()

    if not state.get("query"):
        error = "MISSING_QUERY"

        log_node_execution(
            node_name="search",
            start_time=start_time,
            error=error
        )

        return {
            "error": error,
            "result": {
                "type": "search",
                "message": "지식검색을 위한 query가 없습니다."
            }
        }

    result = run_knowledge_search(
        query=state["query"],
        session_id=state.get(
            "session_id",
            "default_session"
        ),
        embedding_model=state.get(
            "embedding_model",
            "text-embedding-3-large"
        ),
        top_k=state.get(
            "top_k",
            10
        ),
        search_type=state.get(
            "search_type",
            "similarity"
        ),
        filters=state.get("filters")
    )

    log_node_execution(
        node_name="search",
        start_time=start_time,
        error=None
    )

    return {
        "result": result,
        "error": None
    }


def minutes_node(state: AgentState):
    start_time = time.perf_counter()

    if not state.get("file_bytes"):
        error = "MISSING_AUDIO_FILE"

        log_node_execution(
            node_name="minutes",
            start_time=start_time,
            error=error
        )

        return {
            "error": error,
            "result": {
                "type": "minutes",
                "message": "회의록 생성을 위한 음성 파일이 없습니다."
            }
        }

    result = process_audio_minutes(
        audio_file_bytes=state["file_bytes"],
        file_name=state.get("file_name", "unknown_audio")
    )

    log_node_execution(
        node_name="minutes",
        start_time=start_time,
        error=None
    )

    return {
        "result": result,
        "error": None
    }


def report_node(state: AgentState):
    start_time = time.perf_counter()

    if not state.get("topic"):
        error = "MISSING_TOPIC"

        log_node_execution(
            node_name="report",
            start_time=start_time,
            error=error
        )

        return {
            "error": error,
            "result": {
                "type": "report",
                "message": "보고서 생성을 위한 topic이 없습니다."
            }
        }

    result = generate_ai_report(
        topic=state["topic"]
    )

    log_node_execution(
        node_name="report",
        start_time=start_time,
        error=None
    )

    return {
        "result": result,
        "error": None
    }


def route_request(state: AgentState):
    request_type = state.get("request_type")

    if request_type in ["search", "minutes", "report"]:
        return request_type

    return "fallback"


def fallback_node(state: AgentState):
    start_time = time.perf_counter()
    error = "INVALID_REQUEST_TYPE"

    log_node_execution(
        node_name="fallback",
        start_time=start_time,
        error=error
    )

    return {
        "result": {
            "type": "fallback",
            "message": "지원하지 않는 요청 유형입니다."
        },
        "error": error
    }


builder = StateGraph(AgentState)

builder.add_node("search", search_node)
builder.add_node("minutes", minutes_node)
builder.add_node("report", report_node)
builder.add_node("fallback", fallback_node)

builder.add_conditional_edges(
    START,
    route_request,
    {
        "search": "search",
        "minutes": "minutes",
        "report": "report",
        "fallback": "fallback",
    },
)

builder.add_edge("search", END)
builder.add_edge("minutes", END)
builder.add_edge("report", END)
builder.add_edge("fallback", END)

graph = builder.compile()


def invoke_agent(state: AgentState):
    with langfuse.start_as_current_observation(
        as_type="agent",
        name="worldvision-agent"
    ) as observation:

        result = graph.invoke(state)

        observation.update(
            output={
                "request_type": result.get("request_type"),
                "error": result.get("error"),
            }
        )

        return result