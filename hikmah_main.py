from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
import json

# Define the state structure for the graph
class HikmahState(TypedDict, total=False):
    learning_profile: Dict[str, Any]
    lesson_plan: Dict[str, Any]
    review_feedback: Dict[str, Any]
    iteration_count: int
    is_adequate: bool
    max_iterations: int
    conversation_history: List[Dict[str, str]]
    current_agent: str

# Pydantic models for structured output
class LearningProfile(BaseModel):
    learning_objectives: List[str]
    current_knowledge_level: str
    points_to_note: List[str]

class HikmahSimpleSystem:
    """LangGraph-based system with real conversational user understanding"""
    
    def __init__(self):
        # Different models for different agents
        self.understanding_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.lesson_planner_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.reviewer_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        self.max_iterations = 5
        
        # System prompt for the learning assessment agent
        self.understanding_system_prompt = """You are an expert Shia Islam educator and learning consultant. Your role is to understand what a user wants to learn about Shia Islam through natural conversation.

Your goal is to:
1. Understand their specific learning objectives and topics of interest
2. Assess their current knowledge level about the topic
3. Identify any notable points that would help in lesson planning

Guidelines:
- Ask natural, conversational questions (not rigid or robotic)
- Follow up on their responses to dig deeper
- Ask clarifying questions when needed, but keep it short and concise
- Sometimes ask questions that might reveal the user's interest in a related topic as well, but don't be too obvious about it
- Don't ask unnecessary questions about time commitment, frequency, etc. unless relevant
- Focus on understanding their learning goals and knowledge level
- In a subtle way (not too obvious) try to understand if the user comes from a sunni or shia background if it is relevant
- When you have enough information to create a lesson plan, stop asking questions
- Be warm, knowledgeable, and helpful

You should stop asking questions when you have a clear understanding of:
- What specific topics they want to learn about
- Their current knowledge level
- Any special considerations or preferences or related topics that they might be interested in

Respond conversationally and ask one question at a time. 

IMPORTANT: When you have enough information, you must output your final summary as a JSON object matching this exact schema:

{
    "learning_objectives": ["List of specific topics the user wants to learn about"],
    "current_knowledge_level": "Detailed explanation of what the user seems to know already and areas where they lack knowledge",
    "points_to_note": ["List of notable observations that would help in lesson planning"]
}

Start your response with "I have enough information now." followed by the JSON object."""
    
    def create_user_agent(self):
        """Creates the user understanding agent node"""
        
        def understand_user(state: HikmahState) -> HikmahState:
            print("🌳 Welcome to Hikmah Tree Builder!")
            print("I'm here to understand what you want to learn about Shia Islam.\n")
            
            # Start conversation
            initial_message = "Hello! I'd love to help you learn about Shia Islam. What would you like to learn about?"
            print(f"🤖 {initial_message}")
            
            conversation_history = [{"role": "assistant", "content": initial_message}]
            
            # Conversation loop
            while True:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                conversation_history.append({"role": "user", "content": user_input})
                
                # Generate AI response
                ai_response = self._generate_understanding_response(conversation_history)
                
                # Check if agent has enough information
                if "I have enough information now" in ai_response:
                    print(f"🤖 {ai_response}")
                    break
                else:
                    print(f"🤖 {ai_response}")
                    conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Extract learning profile from conversation
            learning_profile = self._extract_learning_profile(ai_response, conversation_history)
            
            state["learning_profile"] = learning_profile
            state["conversation_history"] = conversation_history
            state["current_agent"] = "lesson_planner"
            
            return state
        
        return understand_user
    
    def _generate_understanding_response(self, conversation_history: List[Dict[str, str]]) -> str:
        """Generates AI response based on conversation history"""
        
        # Create messages for the LLM
        messages = [SystemMessage(content=self.understanding_system_prompt)]
        
        # Add conversation history
        for msg in conversation_history:
            if msg["role"] == "assistant":
                messages.append(SystemMessage(content=msg["content"]))
            else:
                messages.append(HumanMessage(content=msg["content"]))
        
        # Add instruction to analyze and respond
        messages.append(HumanMessage(content="""
Based on our conversation so far, please:
1. Analyze what the user wants to learn
2. Assess their current knowledge level
3. Ask one natural follow-up question if you need more information
4. If you have enough information, start your response with "I have enough information now." and provide a JSON object matching the schema

Respond conversationally and naturally."""))
        
        try:
            response = self.understanding_llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I apologize, but I'm having trouble processing that. Could you please rephrase? Error: {e}"
    
    def _extract_learning_profile(self, final_response: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extracts structured learning profile from the final AI response"""
        
        try:
            # Find the JSON part in the response
            json_start = final_response.find('{')
            json_end = final_response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = final_response[json_start:json_end]
                profile_dict = json.loads(json_str)
                
                # Validate against Pydantic model
                try:
                    learning_profile = LearningProfile(**profile_dict)
                    return learning_profile.model_dump()
                except Exception as e:
                    print(f"Warning: JSON doesn't match expected schema: {e}")
                    return self._create_fallback_profile(conversation_history)
            else:
                print("Warning: No JSON found in response")
                return self._create_fallback_profile(conversation_history)
                
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in response: {e}")
            return self._create_fallback_profile(conversation_history)
        except Exception as e:
            print(f"Error extracting profile: {e}")
            return self._create_fallback_profile(conversation_history)
    
    def _create_fallback_profile(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Creates a fallback profile if LLM extraction fails"""
        
        # Analyze conversation manually
        user_messages = [msg["content"] for msg in conversation_history if msg["role"] == "user"]
        
        # Extract learning objectives
        objectives = []
        for msg in user_messages:
            msg_lower = msg.lower()
            
            # Check for specific figures
            if "abu thar" in msg_lower or "ghaffari" in msg_lower:
                objectives.append("Life and contributions of Abu Thar al-Ghaffari")
            elif "ghadeer" in msg_lower:
                objectives.append("Event of Ghadeer Khumm")
            elif "successor" in msg_lower or "succession" in msg_lower:
                objectives.append("Succession to the Prophet")
            elif "imam" in msg_lower:
                objectives.append("Imamate and Leadership")
            elif "prophet" in msg_lower:
                objectives.append("Prophet's Leadership")
            elif "ali" in msg_lower:
                objectives.append("Imam Ali and his role")
        
        if not objectives:
            objectives = ["Shia Islam"]
        
        # Remove duplicates
        objectives = list(dict.fromkeys(objectives))
        
        # Analyze knowledge level from conversation
        knowledge_indicators = []
        for msg in user_messages:
            msg_lower = msg.lower()
            if any(phrase in msg_lower for phrase in ["don't know", "no idea", "not sure", "basic", "beginner"]):
                knowledge_indicators.append("beginner")
            elif any(phrase in msg_lower for phrase in ["some", "little", "basic understanding"]):
                knowledge_indicators.append("intermediate")
            elif any(phrase in msg_lower for phrase in ["good amount", "advanced", "detailed"]):
                knowledge_indicators.append("advanced")
        
        knowledge_level = "beginner"  # default
        if knowledge_indicators:
            if "advanced" in knowledge_indicators:
                knowledge_level = "advanced"
            elif "intermediate" in knowledge_indicators:
                knowledge_level = "intermediate"
        
        # Create knowledge level description
        if knowledge_level == "beginner":
            knowledge_description = "The user appears to be a beginner with minimal knowledge about the topic. They need foundational understanding and basic context."
        elif knowledge_level == "intermediate":
            knowledge_description = "The user has some basic knowledge but needs more detailed information and deeper understanding."
        else:
            knowledge_description = "The user has good foundational knowledge and is ready for more advanced analysis."
        
        # Extract notable points
        points_to_note = []
        for msg in user_messages:
            msg_lower = msg.lower()
            if "revered" in msg_lower or "significance" in msg_lower:
                points_to_note.append("User is interested in understanding why figures are revered in Shia Islam")
            if "contributions" in msg_lower:
                points_to_note.append("Focus on contributions and impact of historical figures")
            if "life" in msg_lower and "death" in msg_lower:
                points_to_note.append("User wants comprehensive biographical coverage")
            if "general" in msg_lower or "overview" in msg_lower:
                points_to_note.append("User prefers general overviews rather than detailed analysis")
        
        if not points_to_note:
            points_to_note = [
                "User is interested in historical figures and events",
                "Focus on providing clear, factual information",
                "Include historical context in lessons"
            ]
        
        return {
            "learning_objectives": objectives,
            "current_knowledge_level": knowledge_description,
            "points_to_note": points_to_note
        }
    
    def create_lesson_planner_agent(self):
        """Creates the lesson planner agent node"""
        
        def plan_lessons(state: HikmahState) -> HikmahState:
            learning_profile = state.get("learning_profile", {})
            review_feedback = state.get("review_feedback", {})
            iteration_count = state.get("iteration_count", 0)
            
            print(f"📚 Generating lesson plan (iteration {iteration_count + 1})...")
            
            # Create lesson planning prompt
            if iteration_count == 0:
                prompt = f"""
Create a comprehensive lesson plan for Shia Islam learning based on this profile:

Learning Profile:
{json.dumps(learning_profile, indent=2)}

Create a detailed lesson plan with 4-6 lessons that:
1. Addresses all learning objectives comprehensively
2. Is appropriate for the user's knowledge level
3. Includes both historical and theological content
4. Builds knowledge progressively with logical flow
5. Provides engaging and educational content

Output as JSON with this structure:
{{
    "topic": "Main topic",
    "total_lessons": number,
    "target_audience": "Description",
    "learning_objectives": ["List of objectives"],
    "lessons": [
        {{
            "lesson_number": 1,
            "title": "Lesson title",
            "overview": "What this lesson covers",
            "important_points": ["Key points to cover"],
            "estimated_duration": "45 minutes",
            "prerequisites": ["What user should know"]
        }}
    ],
    "overall_approach": "Teaching approach"
}}
"""
            else:
                prompt = f"""
Improve this lesson plan based on feedback:

Learning Profile:
{json.dumps(learning_profile, indent=2)}

Previous Feedback:
{json.dumps(review_feedback, indent=2)}

Create an improved lesson plan that addresses the feedback and provides more comprehensive coverage.
Output as JSON with the same structure as above.
"""
            
            try:
                response = self.lesson_planner_llm.invoke([
                    SystemMessage(content="You are an expert Shia Islam curriculum designer with deep knowledge of Islamic history, theology, and educational best practices."),
                    HumanMessage(content=prompt)
                ])
                
                # Extract JSON from response
                json_start = response.content.find('{')
                json_end = response.content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response.content[json_start:json_end]
                    lesson_plan_dict = json.loads(json_str)
                    state["lesson_plan"] = lesson_plan_dict
                else:
                    print("Warning: No JSON found in response, using fallback")
                    state["lesson_plan"] = self._create_fallback_lesson_plan(learning_profile)
                    
            except Exception as e:
                print(f"Error generating lesson plan: {e}")
                state["lesson_plan"] = self._create_fallback_lesson_plan(learning_profile)
            
            state["current_agent"] = "lesson_reviewer"
            return state
        
        return plan_lessons
    
    def create_lesson_reviewer_agent(self):
        """Creates the lesson reviewer agent node"""
        
        def review_lessons(state: HikmahState) -> HikmahState:
            lesson_plan = state.get("lesson_plan", {})
            learning_profile = state.get("learning_profile", {})
            iteration_count = state.get("iteration_count", 0)
            
            print("🔍 Reviewing lesson plan...")
            
            # Create review prompt
            prompt = f"""
Review this lesson plan against the user's learning profile:

Learning Profile:
{json.dumps(learning_profile, indent=2)}

Lesson Plan:
{json.dumps(lesson_plan, indent=2)}

Assess if this lesson plan:
1. Adequately addresses all learning objectives
2. Is appropriate for the user's knowledge level
3. Has logical progression and flow
4. Is comprehensive enough for the topic
5. Provides sufficient depth and breadth

Output assessment as JSON:
{{
    "is_adequate": true/false,
    "feedback_points": ["List of specific feedback points"],
    "suggested_improvements": ["List of specific suggestions"],
    "missing_topics": ["List of missing topics"],
    "overall_assessment": "Overall assessment"
}}

Set is_adequate to true only if the plan is comprehensive, appropriate, and well-structured.
"""
            
            try:
                response = self.reviewer_llm.invoke([
                    SystemMessage(content="You are an expert Shia Islam curriculum reviewer and educational consultant with deep knowledge of Islamic studies and pedagogical best practices."),
                    HumanMessage(content=prompt)
                ])
                
                # Extract JSON from response
                json_start = response.content.find('{')
                json_end = response.content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response.content[json_start:json_end]
                    review_dict = json.loads(json_str)
                    state["review_feedback"] = review_dict
                else:
                    print("Warning: No JSON found in response, using fallback")
                    state["review_feedback"] = self._create_fallback_review(lesson_plan, learning_profile)
                    
            except Exception as e:
                print(f"Error reviewing lesson plan: {e}")
                state["review_feedback"] = self._create_fallback_review(lesson_plan, learning_profile)
            
            # Update iteration count
            state["iteration_count"] = state.get("iteration_count", 0) + 1
            
            # Check if adequate or max iterations reached
            if state["review_feedback"].get("is_adequate", False):
                state["is_adequate"] = True
                state["current_agent"] = "end"
            elif state["iteration_count"] >= self.max_iterations:
                state["is_adequate"] = False
                state["current_agent"] = "end"
            else:
                state["is_adequate"] = False
                state["current_agent"] = "lesson_planner"
            
            return state
        
        return review_lessons
    
    def create_router(self):
        """Creates the router to determine next step"""
        
        def route_next(state: HikmahState) -> str:
            current_agent = state.get("current_agent", "end")
            return current_agent
        
        return route_next
    
    def create_final_summary(self):
        """Creates the final summary node"""
        
        def summarize_results(state: HikmahState) -> HikmahState:
            print("\n🎉 Your Personalized Hikmah Tree is Ready!")
            print("-" * 40)
            
            learning_profile = state.get("learning_profile", {})
            lesson_plan = state.get("lesson_plan", {})
            review_feedback = state.get("review_feedback", {})
            iteration_count = state.get("iteration_count", 0)
            
            print(f"\n🎯 Learning Objectives:")
            for i, objective in enumerate(learning_profile.get("learning_objectives", []), 1):
                print(f"  {i}. {objective}")
            
            print(f"\n📚 Final Lesson Plan:")
            print(f"  Topic: {lesson_plan.get('topic', 'Not specified')}")
            print(f"  Total Lessons: {lesson_plan.get('total_lessons', 0)}")
            
            print(f"\n📋 Final Assessment:")
            print(f"  ✅ Adequate: {'Yes' if review_feedback.get('is_adequate', False) else 'No'}")
            print(f"  🔄 Iterations Used: {iteration_count}")
            
            # Save results
            final_result = {
                "learning_profile": learning_profile,
                "lesson_plan": lesson_plan,
                "review_feedback": review_feedback,
                "iteration_count": iteration_count
            }
            
            with open("simple_hikmah_tree.json", "w") as f:
                json.dump(final_result, f, indent=2)
            
            print(f"\n✅ Simple Hikmah Tree saved to 'simple_hikmah_tree.json'")
            
            return state
        
        return summarize_results
    
    def build_graph(self):
        """Builds the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(HikmahState)
        
        # Add nodes
        workflow.add_node("understand_user", self.create_user_agent())
        workflow.add_node("plan_lessons", self.create_lesson_planner_agent())
        workflow.add_node("review_lessons", self.create_lesson_reviewer_agent())
        workflow.add_node("summarize", self.create_final_summary())
        
        # Add edges
        workflow.set_entry_point("understand_user")
        workflow.add_edge("understand_user", "plan_lessons")
        workflow.add_conditional_edges(
            "plan_lessons",
            self.create_router(),
            {
                "lesson_reviewer": "review_lessons",
                "end": "summarize"
            }
        )
        workflow.add_conditional_edges(
            "review_lessons",
            self.create_router(),
            {
                "lesson_planner": "plan_lessons",
                "end": "summarize"
            }
        )
        workflow.add_edge("summarize", END)
        
        return workflow.compile()

    def _create_fallback_lesson_plan(self, learning_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a fallback lesson plan if LLM generation fails"""
        objectives = learning_profile.get("learning_objectives", [])
        return {
            "topic": "Shia Islam Learning",
            "total_lessons": 4,
            "target_audience": "Beginner learners",
            "learning_objectives": objectives,
            "lessons": [
                {
                    "lesson_number": 1,
                    "title": "Introduction to Shia Islam",
                    "overview": "Basic introduction to Shia Islam",
                    "important_points": ["Key concepts", "Historical context"],
                    "estimated_duration": "45 minutes",
                    "prerequisites": ["Basic Islamic knowledge"]
                }
            ],
            "overall_approach": "Progressive learning"
        }
    
    def _create_fallback_review(self, lesson_plan: Dict[str, Any], learning_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a fallback review if LLM review fails"""
        return {
            "is_adequate": True,
            "feedback_points": ["Basic review completed"],
            "suggested_improvements": [],
            "missing_topics": [],
            "overall_assessment": "Lesson plan appears adequate"
        }

def main():
    """Main function to run the simplified system"""
    system = HikmahSimpleSystem()
    graph = system.build_graph()
    
    print("🌳 Welcome to the Simplified Hikmah Tree Builder!")
    print("="*60)
    
    try:
        # Initialize state
        initial_state = {
            "iteration_count": 0,
            "max_iterations": 3,
            "is_adequate": False
        }
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        print(f"\n🎉 System completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n👋 System interrupted. Thank you for using Hikmah Tree Builder!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 