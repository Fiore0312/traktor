import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
import json
from datetime import datetime
import sqlite3
import asyncio
from typing import Dict, Any, List

# Import persistent memory system
from .persistent_memory import (
    get_memory_system,
    save_current_session,
    get_conversation_context,
    query_knowledge_base,
    add_knowledge
)

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Single model: Claude 3.5 Sonnet (supports tools API on OpenRouter)
# Note: Llama 3.1 via OpenRouter doesn't support function calling, so we use Claude only
LLM_MODEL = 'anthropic/claude-3.5-sonnet'

# Create LLM with moderate temperature for balanced analysis + creativity
llm = ChatOpenAI(
    model=LLM_MODEL,
    openai_api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2,  # Balanced: precise but creative
    max_tokens=2000
)

# Import existing tools from generated modules
from . import energy_analyzer
# Note: agent_history may not exist yet - handle gracefully
try:
    from .agent_history import save_mix
except ImportError:
    def save_mix(state, decision):
        """Placeholder for save_mix if module doesn't exist"""
        pass

@tool
def analyze_track_energy(track_data: str) -> str:
    """Analyze energy level for a track.

    Args:
        track_data: JSON string with track metadata (bpm, key, genre)

    Returns:
        JSON string with energy score (0.0-1.0)
    """
    try:
        track = json.loads(track_data)
        energy = energy_analyzer.analyze_energy(track)
        return json.dumps({'energy': energy, 'track_id': track.get('id', 'unknown')})
    except Exception as e:
        return json.dumps({'error': str(e)})

@tool
def calculate_transition_energy(from_track_data: str, to_track_data: str) -> str:
    """Calculate energy transition between two tracks.

    Args:
        from_track_data: JSON string with source track metadata
        to_track_data: JSON string with destination track metadata

    Returns:
        JSON string with transition characteristics
    """
    try:
        from_track = json.loads(from_track_data)
        to_track = json.loads(to_track_data)
        transition = energy_analyzer.calculate_energy_transition(from_track, to_track)
        return json.dumps(transition)
    except Exception as e:
        return json.dumps({'error': str(e)})

# Add more tools as needed, e.g., harmonic_compatibility_check

tools = [analyze_track_energy, calculate_transition_energy]

# DJ Rules Prompt
DJ_RULES = """
You are an expert DJ assistant for an autonomous DJ system controlling Traktor Pro 3 via MIDI.
Follow these strict rules:

1. AUTO Mode: Do not manually set MASTER during transitions; let AUTO handle based on volume.
2. First track: Manual MASTER, no SYNC, high volume (85%).
3. Subsequent tracks: Enable SYNC, start low volume (0-20%), ramp up for transition.
4. Pre-playback: Set crossfader, volumes, EQ neutral BEFORE play.
5. Prioritize harmonic mixing, energy flow, BPM compatibility.
6. Output decisions as JSON format with fields: next_track (path), transition_type (crossfade or cut), reasoning (string), master_sync (deck and action).
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", DJ_RULES),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
    ("human", "{input}"),
])
# Note: state and history are included in enhanced_input within get_llm_decision()

# Use persistent memory system (get the ConversationBufferMemory for agents)
_persistent_memory_system = get_memory_system()
# Create a simple wrapper for LangChain compatibility
class ConversationMemoryWrapper:
    def __init__(self, memory_system):
        self.memory_system = memory_system
        self.chat_memory = self

    def add_user_message(self, content):
        self.memory_system.conversation_history.append(HumanMessage(content=content))

    def add_ai_message(self, content):
        self.memory_system.conversation_history.append(AIMessage(content=content))

conversation_memory = ConversationMemoryWrapper(_persistent_memory_system)

# Create single agent with Claude 3.5 (works with tools API)
agent = create_openai_functions_agent(llm, tools, prompt)

# Create executor WITHOUT memory (we handle memory manually in get_llm_decision)
# Memory parameter causes "One input key expected" error
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

async def get_llm_decision(input_query: str, state: Dict[str, Any], task_type: str = 'analysis') -> Dict[str, Any]:
    """Async LLM decision with Claude 3.5 Sonnet and persistent memory.

    Args:
        input_query: Question/request for the LLM
        state: Current DJ system state
        task_type: 'analysis' or 'creative' (ignored, kept for API compatibility)

    Returns:
        Dict with LLM decision including next_track, reasoning, etc.
    """
    # Use single executor (Claude 3.5 only)

    # Get persistent conversation context (limited to prevent token overflow)
    conversation_context = get_conversation_context(max_messages=5, as_string=True)

    # Query knowledge base for similar past decisions
    try:
        knowledge_results = query_knowledge_base(
            input_query,
            decision_type=task_type,
            limit=3
        )
        knowledge_context = "\n".join([
            f"Past decision: {doc.page_content[:200]}..."
            for doc in knowledge_results
        ])
    except Exception as e:
        print(f"Warning: Could not query knowledge base: {e}")
        knowledge_context = ""

    try:
        # Include knowledge base and conversation context in the prompt
        enhanced_input = f"""
CONVERSATION HISTORY:
{conversation_context}

PAST KNOWLEDGE:
{knowledge_context}

CURRENT QUERY:
{input_query}
        """.strip()

        # Pass only required inputs (memory handled manually via enhanced_input)
        response = await executor.ainvoke({
            "input": enhanced_input
        })

        # Manually add to conversation memory after successful response
        _persistent_memory_system.conversation_memory.chat_memory.add_user_message(enhanced_input)
        _persistent_memory_system.conversation_memory.chat_memory.add_ai_message(response['output'])

        # Parse JSON from response (handle markdown wrapped JSON and Unicode issues)
        try:
            output_text = response['output']
            import re

            # Extract JSON from markdown or find first JSON object
            json_text = None

            # Try markdown code blocks first
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', output_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r'```\s*(\{.*?\})\s*```', output_text, re.DOTALL)
            if not json_match:
                # Find first complete JSON object
                json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', output_text, re.DOTALL)

            if json_match:
                json_text = json_match.group(1)
            else:
                json_text = output_text

            # Try parsing with strict=False to allow control characters
            try:
                decision = json.loads(json_text, strict=False)
            except Exception as parse_error:
                # If still fails, escape control characters and retry
                # Replace problematic Unicode chars
                json_text_clean = json_text.replace('±', '+/-').replace('–', '-').replace('—', '-')
                # Remove control characters
                json_text_clean = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_text_clean)
                try:
                    decision = json.loads(json_text_clean, strict=False)
                except:
                    # Final fallback: return raw output
                    decision = {"error": f"JSON parse failed: {str(parse_error)}", "raw_output": output_text}

            # Add metadata
            if not decision.get('error'):
                decision['memory_used'] = True
                decision['knowledge_found'] = len(knowledge_results) > 0
                decision['model_used'] = LLM_MODEL
        except Exception as e:
            decision = {"error": f"JSON parse failed: {str(e)}", "raw_output": response['output']}
            decision['memory_used'] = True
            decision['model_used'] = LLM_MODEL

    except Exception as e:
        print(f"Error with Claude 3.5: {e}")
        return {"error": "LLM request failed", "details": str(e), "model": LLM_MODEL}

    # Log tokens and cost
    if hasattr(response, 'llm_output') and hasattr(response['llm_output'], 'response_metadata'):
        tokens = response['llm_output'].response_metadata.get('token_usage', {})
        log_usage(tokens)

    # Save knowledge entry if this is a successful decision
    if not decision.get('error') and 'memory_used' in decision:
        try:
            metadata = {
                'genre': state.get('current_genre', 'unknown'),
                'energy_level': state.get('current_energy', 'unknown'),
                'bpm_range': state.get('bpm_range', 'unknown'),
                'task_type': task_type,
                'timestamp': datetime.now().isoformat()
            }

            if 'next_track' in decision:
                metadata['decision_type'] = 'track_selection'
                decision_content = f"Selected track: {decision.get('next_track', 'unknown')}. Reasoning: {decision.get('reasoning', 'No reasoning provided')}"
            elif 'transition_type' in decision:
                metadata['decision_type'] = 'transition_planning'
                decision_content = f"Planned {decision.get('transition_type', 'unknown')} transition. Reasoning: {decision.get('reasoning', 'No reasoning provided')}"
            else:
                metadata['decision_type'] = task_type
                decision_content = f"Made {task_type} decision: {decision.get('raw_output', input_query[:200])}"

            # Add to knowledge base with success score
            success_score = 0.8 if not decision.get('error') else 0.0
            add_knowledge(
                decision_type=metadata['decision_type'],
                content=decision_content,
                metadata=metadata,
                success_score=success_score
            )

        except Exception as e:
            print(f"Warning: Could not save knowledge entry: {e}")

    # Save current session
    save_current_session()

    save_mix(state, decision)
    return decision

def log_usage(tokens: Dict) -> None:
    """Log LLM usage to data/llm_logs.json"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tokens_prompt": tokens.get('prompt_tokens', 0),
        "tokens_completion": tokens.get('completion_tokens', 0),
        "total_tokens": tokens.get('total_tokens', 0),
        # Cost calculation approximate for OpenRouter
        "estimated_cost": (tokens.get('total_tokens', 0) * 0.0001)  # Placeholder
    }
    logs_file = "C:/djfiore/data/llm_logs.json"
    try:
        with open(logs_file, 'r') as f:
            data = json.load(f)
            # Handle both old list format and new dict format
            if isinstance(data, list):
                logs = {"calls": data}
            else:
                logs = data
    except FileNotFoundError:
        logs = {"calls": []}

    logs['calls'].append(log_entry)

    with open(logs_file, 'w') as f:
        json.dump(logs, f, indent=2)