from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
import json

class Lesson(BaseModel):
    """Pydantic model for individual lesson structure"""
    lesson_number: int
    title: str
    overview: str
    important_points: List[str]
    estimated_duration: str
    prerequisites: List[str]

class LessonPlan(BaseModel):
    """Pydantic model for complete lesson plan"""
    topic: str
    total_lessons: int
    target_audience: str
    learning_objectives: List[str]
    lessons: List[Lesson]
    overall_approach: str

class LessonPlannerAgent:
    """Agent that generates lesson plans based on user learning profile"""
    
    def __init__(self, llm_model="gpt-4o-mini"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.3)
        
        self.system_prompt = """You are an expert Shia Islam educator and curriculum designer. Your role is to create comprehensive lesson plans based on user learning profiles.

Your task is to:
1. Analyze the user's learning objectives and knowledge level
2. Create a structured lesson plan with appropriate number of lessons
3. Provide detailed overview and important points for each lesson
4. Ensure lessons build upon each other progressively
5. Consider the user's background and learning preferences

Guidelines:
- Create lessons that are appropriate for the user's knowledge level
- Ensure comprehensive coverage of the requested topics
- Include both historical context and theological understanding where relevant
- Consider the user's background (Sunni/Shia) and adjust content accordingly
- Make lessons engaging and accessible
- Include important points that must be covered in each lesson

IMPORTANT: When you have created the lesson plan, output it as a JSON object matching this exact schema:

{
    "topic": "Main topic of the lesson plan",
    "total_lessons": number,
    "target_audience": "Description of who this is designed for",
    "learning_objectives": ["List of overall learning objectives"],
    "lessons": [
        {
            "lesson_number": 1,
            "title": "Lesson title",
            "overview": "Detailed overview of what this lesson covers",
            "important_points": ["List of key points that must be covered"],
            "estimated_duration": "Estimated time (e.g., '45 minutes')",
            "prerequisites": ["What the user should know before this lesson"]
        }
    ],
    "overall_approach": "Description of the overall teaching approach"
}"""

    def generate_lesson_plan(self, learning_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a lesson plan based on the learning profile"""
        
        print("📚 Generating personalized lesson plan...")
        
        # Create prompt with learning profile
        prompt = f"""
Based on this learning profile, create a comprehensive lesson plan:

Learning Profile:
{json.dumps(learning_profile, indent=2)}

Please create a lesson plan that:
1. Addresses all the learning objectives mentioned
2. Is appropriate for the user's knowledge level
3. Considers their background and preferences
4. Provides comprehensive coverage of the topics
5. Builds knowledge progressively

Output the lesson plan as a JSON object matching the schema provided.
"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ])
            
            # Extract JSON from response
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                lesson_plan_dict = json.loads(json_str)
                
                # Validate against Pydantic model
                try:
                    lesson_plan = LessonPlan(**lesson_plan_dict)
                    return lesson_plan.model_dump()
                except Exception as e:
                    print(f"Warning: JSON doesn't match expected schema: {e}")
                    return self._create_fallback_lesson_plan(learning_profile)
            else:
                print("Warning: No JSON found in response")
                return self._create_fallback_lesson_plan(learning_profile)
                
        except Exception as e:
            print(f"Error generating lesson plan: {e}")
            return self._create_fallback_lesson_plan(learning_profile)
    
    def generate_lesson_plan_with_feedback(self, learning_profile: Dict[str, Any], review_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a lesson plan incorporating feedback from the reviewer"""
        
        print("📚 Generating improved lesson plan based on feedback...")
        
        # Create prompt with learning profile and feedback
        prompt = f"""
Based on this learning profile and review feedback, create an improved lesson plan:

LEARNING PROFILE:
{json.dumps(learning_profile, indent=2)}

REVIEW FEEDBACK:
{json.dumps(review_feedback, indent=2)}

Please create an improved lesson plan that:
1. Addresses all the learning objectives mentioned
2. Incorporates the feedback and suggestions from the reviewer
3. Adds any missing topics identified in the review
4. Is appropriate for the user's knowledge level
5. Considers their background and preferences
6. Provides comprehensive coverage of the topics
7. Builds knowledge progressively

Pay special attention to:
- Missing topics mentioned in the review
- Suggested improvements from the reviewer
- Any feedback points that need to be addressed

Output the lesson plan as a JSON object matching the schema provided.
"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ])
            
            # Extract JSON from response
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response.content[json_start:json_end]
                lesson_plan_dict = json.loads(json_str)
                
                # Validate against Pydantic model
                try:
                    lesson_plan = LessonPlan(**lesson_plan_dict)
                    return lesson_plan.model_dump()
                except Exception as e:
                    print(f"Warning: JSON doesn't match expected schema: {e}")
                    return self._create_fallback_lesson_plan(learning_profile)
            else:
                print("Warning: No JSON found in response")
                return self._create_fallback_lesson_plan(learning_profile)
                
        except Exception as e:
            print(f"Error generating lesson plan with feedback: {e}")
            return self._create_fallback_lesson_plan(learning_profile)
    
    def _create_fallback_lesson_plan(self, learning_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a fallback lesson plan if LLM generation fails"""
        
        objectives = learning_profile.get("learning_objectives", [])
        knowledge_level = learning_profile.get("current_knowledge_level", "")
        
        # Determine number of lessons based on objectives
        total_lessons = min(len(objectives) + 2, 8)  # Cap at 8 lessons
        
        lessons = []
        for i in range(total_lessons):
            if i == 0:
                lesson = {
                    "lesson_number": 1,
                    "title": "Introduction to the Topic",
                    "overview": "Basic introduction and foundational concepts",
                    "important_points": ["Historical context", "Key terminology", "Basic concepts"],
                    "estimated_duration": "45 minutes",
                    "prerequisites": ["Basic understanding of Islam"]
                }
            elif i == total_lessons - 1:
                lesson = {
                    "lesson_number": total_lessons,
                    "title": "Conclusion and Synthesis",
                    "overview": "Bringing together all concepts learned",
                    "important_points": ["Summary of key points", "Integration of concepts", "Final understanding"],
                    "estimated_duration": "60 minutes",
                    "prerequisites": [f"Completion of lessons 1-{total_lessons-1}"]
                }
            else:
                lesson = {
                    "lesson_number": i + 1,
                    "title": f"Lesson {i + 1}: {objectives[i-1] if i-1 < len(objectives) else 'Advanced Topics'}",
                    "overview": f"Detailed exploration of {objectives[i-1] if i-1 < len(objectives) else 'advanced concepts'}",
                    "important_points": ["Key concepts", "Historical context", "Theological implications"],
                    "estimated_duration": "60 minutes",
                    "prerequisites": [f"Completion of lesson {i}"]
                }
            lessons.append(lesson)
        
        return {
            "topic": "Shia Islam Learning",
            "total_lessons": total_lessons,
            "target_audience": "Users with basic Islamic knowledge",
            "learning_objectives": objectives,
            "lessons": lessons,
            "overall_approach": "Progressive learning with historical and theological context"
        }

def main():
    """Test the lesson planner agent"""
    # Load learning profile
    try:
        with open("learning_profile.json", "r") as f:
            learning_profile = json.load(f)
    except FileNotFoundError:
        print("No learning profile found. Please run the user understanding agent first.")
        return
    
    # Create lesson planner
    planner = LessonPlannerAgent()
    
    # Generate lesson plan
    lesson_plan = planner.generate_lesson_plan(learning_profile)
    
    # Display results
    print("\n" + "="*60)
    print("📚 GENERATED LESSON PLAN")
    print("="*60)
    
    print(f"\n🎯 Topic: {lesson_plan.get('topic', 'Not specified')}")
    print(f"📊 Total Lessons: {lesson_plan.get('total_lessons', 0)}")
    print(f"👥 Target Audience: {lesson_plan.get('target_audience', 'Not specified')}")
    
    print(f"\n🎯 Learning Objectives:")
    for i, objective in enumerate(lesson_plan.get("learning_objectives", []), 1):
        print(f"  {i}. {objective}")
    
    print(f"\n📚 Lessons:")
    for lesson in lesson_plan.get("lessons", []):
        print(f"\n  📖 Lesson {lesson.get('lesson_number', '?')}: {lesson.get('title', 'Untitled')}")
        print(f"     ⏰ Duration: {lesson.get('estimated_duration', 'Not specified')}")
        print(f"     📝 Overview: {lesson.get('overview', 'Not specified')}")
        print(f"     🎯 Important Points:")
        for point in lesson.get("important_points", []):
            print(f"       • {point}")
    
    print(f"\n📋 Overall Approach: {lesson_plan.get('overall_approach', 'Not specified')}")
    
    # Save to file
    with open("lesson_plan.json", "w") as f:
        json.dump(lesson_plan, f, indent=2)
    
    print(f"\n✅ Lesson plan saved to 'lesson_plan.json'")
    print("This plan can now be reviewed by the lesson plan reviewer agent.")

if __name__ == "__main__":
    main() 