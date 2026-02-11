from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.tools import tool
import http.client
import json

# 1. 다양한 툴 정의 (확장 가능)

@tool
def get_weather(location: str) -> str:
    return f"{location}의 날씨는 맑고 28도입니다."

@tool
def get_schedule(date: str) -> str:
    return "10시 팀 회의, 14시 고객사 미팅 예정입니다."

@tool
def send_email(content: str) -> str:
    return f"이메일 전송 완료: \n---\n{content}"

@tool
def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"

@tool
def search_serper(query: str) -> str:
    """Serper.dev를 사용하여 Google 검색 결과를 가져옵니다."""
    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": query,
            "gl": "kr",
            "hl": "ko"
        })

        headers = {
            'X-API-KEY': 'your-serper-api-key',  # 여기에 본인의 Serper API 키 입력
            'Content-Type': 'application/json'
        }

        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        results = json.loads(data)

        organic = results.get("organic", [])[:3]
        return "\n".join(f"{i+1}. {item['title']} - {item['link']}" for i, item in enumerate(organic)) \
            if organic else "검색 결과가 없습니다."
    except Exception as e:
        return f"검색 중 오류 발생: {str(e)}"

# 2. Agent 초기화

llm = ChatOpenAI(model="gpt-4o")

tools = [get_weather, get_schedule, send_email, calculate, search_serper]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# 3. 사용 예시

agent.run("강남역 브런치 맛집 검색해서 정리해줘.")
agent.run("오늘 서울 날씨 알려주고, 일정 확인해서 이메일 보내줘.")
agent.run("123 * 456 계산해줘.")
