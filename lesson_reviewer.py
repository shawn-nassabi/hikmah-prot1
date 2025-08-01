from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
import json

class ReviewFeedback(BaseModel):
    """Pydantic model for review feedback"""
    is_adequate: bool
    feedback_points: List[str]
    suggested_improvements: List[str]
    missing_topics: List[str]
    overall_assessment: str

class LessonPlanReviewerAgent:
    """Agent that reviews lesson plans and provides feedback for improvements"""
    
    def __init__(self, llm_model="gpt-4o-mini"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.3)
        
        self.system_prompt = """You are an expert Shia Islam curriculum reviewer and educational consultant. Your role is to review lesson plans and provide constructive feedback.

Your task is to:
1. Analyze if the lesson plan adequately addresses the user's learning objectives
2. Identify any missing essential topics or concepts
3. Assess if the lessons are appropriate for the user's knowledge level
4. Check if the progression and structure are logical
5. Provide specific suggestions for improvement

Review Criteria:
- Does the lesson plan cover all the user's learning objectives?
- Are there any essential topics missing that are crucial for understanding?
- Is the difficulty level appropriate for the user's background?
- Is the progression logical and builds knowledge effectively?
- Are the lessons comprehensive enough for the topic?
- Does it consider the user's background (Sunni/Shia) appropriately?

IMPORTANT: When you have completed your review, output your assessment as a JSON object matching this exact schema:

{
    "is_adequate": true/false,
    "feedback_points": ["List of specific feedback points"],
    "suggested_improvements": ["List of specific suggestions for improvement"],
    "missing_topics": ["List of topics that should be added"],
    "overall_assessment": "Overall assessment of the lesson plan quality"
}

Set is_adequate to true only if the lesson plan is comprehensive and appropriate for the user's needs."""

    def review_lesson_plan(self, lesson_plan: Dict[str, Any], learning_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Reviews a lesson plan and provides feedback"""
        
        print("🔍 Reviewing lesson plan...")
        
        # Create review prompt
        prompt = f"""
Please review this lesson plan against the user's learning profile:

LEARNING PROFILE:
{json.dumps(learning_profile, indent=2)}

LESSON PLAN:
{json.dumps(lesson_plan, indent=2)}

Please assess:
1. Does this lesson plan adequately address all the user's learning objectives?
2. Are there any essential topics missing?
3. Is the difficulty level appropriate?
4. Is the progression logical?
5. Are there any improvements needed?

Provide your assessment as a JSON object matching the schema provided.
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
                review_dict = json.loads(json_str)
                
                # Validate against Pydantic model
                try:
                    review_feedback = ReviewFeedback(**review_dict)
                    return review_feedback.model_dump()
                except Exception as e:
                    print(f"Warning: JSON doesn't match expected schema: {e}")
                    return self._create_fallback_review(lesson_plan, learning_profile)
            else:
                print("Warning: No JSON found in response")
                return self._create_fallback_review(lesson_plan, learning_profile)
                
        except Exception as e:
            print(f"Error reviewing lesson plan: {e}")
            return self._create_fallback_review(lesson_plan, learning_profile)
    
    def _create_fallback_review(self, lesson_plan: Dict[str, Any], learning_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a fallback review if LLM review fails"""
        
        objectives = learning_profile.get("learning_objectives", [])
        lesson_titles = [lesson.get("title", "") for lesson in lesson_plan.get("lessons", [])]
        
        # Basic assessment
        missing_topics = []
        for objective in objectives:
            if not any(objective.lower() in title.lower() for title in lesson_titles):
                missing_topics.append(objective)
        
        is_adequate = len(missing_topics) == 0
        
        feedback_points = []
        if not is_adequate:
            feedback_points.append("Some learning objectives are not adequately covered")
        else:
            feedback_points.append("Lesson plan appears to cover the main objectives")
        
        suggested_improvements = []
        if missing_topics:
            suggested_improvements.append(f"Add lessons covering: {', '.join(missing_topics)}")
        
        return {
            "is_adequate": is_adequate,
            "feedback_points": feedback_points,
            "suggested_improvements": suggested_improvements,
            "missing_topics": missing_topics,
            "overall_assessment": "Basic review completed. Lesson plan needs improvement to fully address user objectives."
        }

def main():
    """Test the lesson plan reviewer agent"""
    # Load learning profile and lesson plan
    try:
        with open("learning_profile.json", "r") as f:
            learning_profile = json.load(f)
    except FileNotFoundError:
        print("No learning profile found. Please run the user understanding agent first.")
        return
    
    try:
        with open("lesson_plan.json", "r") as f:
            lesson_plan = json.load(f)
    except FileNotFoundError:
        print("No lesson plan found. Please run the lesson planner agent first.")
        return
    
    # Create reviewer
    reviewer = LessonPlanReviewerAgent()
    
    # Review lesson plan
    review = reviewer.review_lesson_plan(lesson_plan, learning_profile)
    
    # Display results
    print("\n" + "="*60)
    print("🔍 LESSON PLAN REVIEW")
    print("="*60)
    
    print(f"\n✅ Adequate: {'Yes' if review.get('is_adequate', False) else 'No'}")
    
    print(f"\n📝 Feedback Points:")
    for i, point in enumerate(review.get("feedback_points", []), 1):
        print(f"  {i}. {point}")
    
    print(f"\n🔧 Suggested Improvements:")
    for i, improvement in enumerate(review.get("suggested_improvements", []), 1):
        print(f"  {i}. {improvement}")
    
    print(f"\n❌ Missing Topics:")
    for i, topic in enumerate(review.get("missing_topics", []), 1):
        print(f"  {i}. {topic}")
    
    print(f"\n📋 Overall Assessment:")
    print(f"  {review.get('overall_assessment', 'No assessment provided')}")
    
    # Save to file
    with open("lesson_review.json", "w") as f:
        json.dump(review, f, indent=2)
    
    print(f"\n✅ Review saved to 'lesson_review.json'")
    
    if review.get("is_adequate", False):
        print("🎉 Lesson plan is adequate and ready for use!")
    else:
        print("⚠️ Lesson plan needs improvements. Consider running the lesson planner again with the feedback.")

if __name__ == "__main__":
    main() 