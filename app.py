import os
import tempfile
from datetime import date
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from transcribe import transcribe_audio
from agent import build_agent
from config import MAX_ITERATIONS

load_dotenv()

st.set_page_config(page_title="Meeting Notes Agent", layout="centered")

st.title("Meeting Notes Agent")
st.caption("Upload a meeting recording and get structured notes, action items, and follow-ups.")

# Sidebar
with st.sidebar:
    st.header("How it works")
    st.markdown(
        "1. **Upload** an audio/video recording\n"
        "2. **Whisper** transcribes the audio\n"
        "3. **LangGraph agent** processes the transcript:\n"
        "   - Checks past meetings in Airtable\n"
        "   - Extracts summary, action items, decisions\n"
        "   - Flags open follow-ups from previous meetings\n"
        "   - Saves notes to Airtable\n"
    )
    st.divider()
    st.subheader("Tech Stack")
    st.write("LangGraph / LangSmith / Whisper / Airtable / Streamlit")

# File upload
uploaded_file = st.file_uploader(
    "Upload meeting recording",
    type=["mp3", "mp4", "m4a", "wav", "webm"],
)

meeting_date = st.date_input("Meeting date", value=date.today())

# Option to paste transcript directly
with st.expander("Or paste a transcript instead"):
    pasted_transcript = st.text_area(
        "Paste transcript here",
        height=200,
        placeholder="Speaker 1: Let's discuss the project timeline...",
    )

process = st.button("Process Meeting", type="primary")

if process:
    transcript = None

    # Get transcript from upload or pasted text
    if uploaded_file:
        with st.status("Transcribing audio with Whisper...") as status:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
            ) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            transcript = transcribe_audio(tmp_path)
            os.unlink(tmp_path)
            status.update(label="Transcription complete", state="complete")

    elif pasted_transcript.strip():
        transcript = pasted_transcript.strip()
    else:
        st.error("Please upload a recording or paste a transcript.")

    if transcript:
        # Show transcript
        with st.expander("Transcript"):
            st.text(transcript)

        # Run the agent
        st.divider()
        with st.spinner("Agent is processing..."):
            graph, initial_messages = build_agent(transcript, str(meeting_date))
            result = graph.invoke(
                {"messages": initial_messages},
                config={
                    "metadata": {"meeting_date": str(meeting_date)},
                    "recursion_limit": MAX_ITERATIONS,
                },
            )

        # Show agent steps
        tool_calls_made = []
        final_answer = ""

        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_calls_made.append(tc)
                elif msg.content:
                    final_answer = msg.content

        with st.expander(f"Agent made {len(tool_calls_made)} tool calls"):
            for i, tc in enumerate(tool_calls_made, 1):
                args_preview = ", ".join(
                    f"{k}={str(v)[:50]}" for k, v in tc["args"].items()
                )
                st.markdown(f"**Step {i}:** `{tc['name']}({args_preview})`")

        # Show the structured notes
        st.subheader("Meeting Notes")
        if final_answer:
            st.markdown(final_answer)
        else:
            st.warning("Agent did not produce meeting notes.")
