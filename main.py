import json
import math
import requests
import streamlit as st
import google.generativeai as genai

# ----------------- Dynamic Weather Tool (India & Global) -----------------
def get_weather(location: str) -> str:
    """భారతదేశంలోని లేదా ప్రపంచంలోని ఎక్కడైనా ఇచ్చిన నగరం/ఊరి యొక్క ప్రస్తుత వాతావరణాన్ని లైవ్‌లో తెలియజేస్తుంది."""
    try:
        # wttr.in అనేది ఉచిత వెదర్ API (API Key అవసరం లేదు)
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            temp_c = current['temp_C']
            condition = current['weatherDesc'][0]['value']
            
            weather_info = {
                "location": location,
                "temperature": f"{temp_c}°C",
                "condition": condition
            }
            return json.dumps(weather_info)
        else:
            return json.dumps({"error": "దయచేసి సరైన ఊరి పేరు ఇవ్వండి, వాతావరణ సమాచారం దొరకలేదు."})
            
    except Exception as e:
        return json.dumps({"error": f"వాతావరణ డేటా తెచ్చుకోవడంలో లోపం:কারীর {str(e)}"})

# ----------------- Calculator Tool -----------------
def calculate(expression: str) -> str:
    """గణిత సమీకరణాలను (Mathematical Expressions) సాల్వ్ చేస్తుంది."""
    try:
        allowed_names = {"sqrt": math.sqrt, "pow": math.pow, "pi": math.pi}
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"error": f"గణన చేయడంలో లోపం: {str(e)}"})

available_tools = {"get_weather": get_weather, "calculate": calculate}

st.sidebar.header("Configuration")
api_key_input = st.sidebar.text_input("Gemini API Key", type="password")

if not api_key_input:
    st.warning("దయచేసి మీ Gemini API Key ని సైడ్‌బార్‌లో ఎంటర్ చేయండి.")
    st.stop()

# Gemini Config & Model setup
genai.configure(api_key=api_key_input)

model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    tools=[get_weather, calculate],
    system_instruction="మీరు భారతదేశ వాతావరణం మరియు ఇతర వివరాలు చెప్పగల తెలివైన AI Agent."
)
# Chat History మెమరీ కోసం
# Gemini Chat Session
if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = model.start_chat(enable_automatic_function_calling=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# పాత మెసేజ్‌లను స్క్రీన్ పై చూపించడం
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# యూజర్ నుండి ఇన్‌పుట్ తీసుకోవడం
if user_input := st.chat_input("ఉదా: తిరుపతిలో వాతావరణం ఎలా ఉంది?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Agent Response
    with st.chat_message("assistant"):
        with st.status("Agent లైవ్ డేటాను పరిశీలిస్తోంది...", expanded=True) as status:
            try:
                response = st.session_state.gemini_chat.send_message(user_input)
                final_answer = response.text
                status.update(label="సమాచారం సిద్ధమైంది!", state="complete", expanded=False)
            except Exception as e:
                final_answer = f"లోపం సంభవించింది: {str(e)}"
                status.update(label="లోపం!", state="error", expanded=False)
        
        st.markdown(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})