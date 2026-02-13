import streamlit as st
from services.agent_service import AgentService
from models.release_context import ReleaseContext
from services.release_service import execute_release
import time

def render_chat_interface(context: ReleaseContext):
    """
    Renders the NLP Chat Interface with modern styling.
    """
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <span style="font-size: 2rem; vertical-align: middle;">💬</span>
        <span style="font-family: 'Poppins', sans-serif; font-size: 1.5rem; font-weight: 700;
                     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                     margin-left: 0.5rem; vertical-align: middle;">
            ChatOps Assistant
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    if "agent" not in st.session_state:
        st.session_state.agent = AgentService()
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ex: 'Release BANKING-123 to CIT on SSA'"):
        # User message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

         # Agent processing
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text, updates, ready_to_execute = st.session_state.agent.process_prompt(prompt, context)
                
                # Show updates in a nice way
                if updates:
                    update_msg = "**Updates applied:**\n" + "\n".join([f"- {k}: `{v}`" for k, v in updates.items()])
                    st.markdown(update_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": update_msg})
                
                st.markdown(response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})

                # Handle Execution
                if ready_to_execute:
                    st.warning("🚀 Starting Release Execution...")
                    try:
                        execute_release(context)
                        success_msg = f"✅ **SUCCESS**: Release to {context.cluster.upper()} {context.environment.value} completed!"
                        st.success(success_msg)
                        st.balloons()
                        st.session_state.chat_history.append({"role": "assistant", "content": success_msg})
                    except Exception as e:
                        error_msg = f"❌ **FAILED**: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

                
        # Force a rerun to update the UI forms below
        st.rerun()
