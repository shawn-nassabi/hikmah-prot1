# 🌳 Hikmah Tree Builder

A multi-agent LangGraph-based system for creating personalized Shia Islam learning plans. The system uses intelligent conversation to understand user learning goals and generates comprehensive lesson plans through a feedback loop between lesson planning and reviewing agents.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd hikmah-prot1
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up OpenAI API key**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Running the Program

```bash
python hikmah_main.py
```

The program will:

1. Start a conversational interface to understand your learning goals
2. Generate a personalized lesson plan
3. Review and refine the plan through feedback loops
4. Save the final results to `simple_hikmah_tree.json`

## 🔄 System Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           HIKMAH TREE SYSTEM FLOW                                 │
│                              LangGraph-Based Multi-Agent System                    │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   INITIAL STATE │
│                 │
│ • iteration_count: 0
│ • max_iterations: 5
│ • is_adequate: false
│ • conversation_history: []
└─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          1. USER UNDERSTANDING AGENT                                │
│                              (gpt-4o-mini)                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ INPUT: None (starts conversation)                                                   │
│                                                                                     │
│ PROCESS:                                                                            │
│ ├─ Starts conversation with user                                                    │
│ ├─ Asks natural questions about learning goals                                      │
│ ├─ Assesses current knowledge level                                                 │
│ ├─ Extracts learning objectives and preferences                                     │
│ └─ Determines when enough information is gathered                                   │
│                                                                                     │
│ OUTPUT: Learning Profile                                                            │
│ ├─ learning_objectives: ["topic1", "topic2", ...]                                   │
│ ├─ current_knowledge_level: "detailed description"                                  │
│ └─ points_to_note: ["observation1", "observation2", ...]                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          2. LESSON PLANNER AGENT                                    │
│                                (gpt-4o)                                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ INPUT: Learning Profile + Review Feedback (if iteration > 1)                        │
│                                                                                     │
│ PROCESS:                                                                            │
│ ├─ Analyzes learning objectives and knowledge level                                 │
│ ├─ Creates comprehensive lesson plan (4-6 lessons)                                  │
│ ├─ Includes historical and theological content                                      │
│ ├─ Builds progressive learning structure                                            │
│ └─ Incorporates feedback from previous iterations                                   │
│                                                                                     │
│ OUTPUT: Lesson Plan                                                                 │
│ ├─ topic: "Main topic"                                                              │
│ ├─ total_lessons: number                                                            │
│ ├─ target_audience: "Description"                                                   │
│ ├─ learning_objectives: ["List of objectives"]                                      │
│ ├─ lessons: [Lesson1, Lesson2, ...]                                                 │
│ └─ overall_approach: "Teaching approach"                                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          3. LESSON REVIEWER AGENT                                   │
│                                (gpt-4o)                                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ INPUT: Lesson Plan + Learning Profile                                               │
│                                                                                     │
│ PROCESS:                                                                            │
│ ├─ Reviews lesson plan against learning objectives                                  │
│ ├─ Assesses appropriateness for knowledge level                                     │
│ ├─ Checks logical progression and comprehensiveness                                 │
│ ├─ Identifies missing topics and improvements needed                                │
│ └─ Determines if plan is adequate                                                   │
│                                                                                     │
│ OUTPUT: Review Feedback                                                             │
│ ├─ is_adequate: true/false                                                          │
│ ├─ feedback_points: ["point1", "point2", ...]                                       │
│ ├─ suggested_improvements: ["improvement1", ...]                                    │
│ ├─ missing_topics: ["topic1", "topic2", ...]                                        │
│ └─ overall_assessment: "Detailed assessment"                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                             4. ROUTER DECISION                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│ IF review_feedback.is_adequate == True:                                             │
│   └─ Route to: "end" (Final Summary)                                                │
│                                                                                     │
│ IF review_feedback.is_adequate == False:                                            │
│   ├─ IF iteration_count < max_iterations:                                           │
│   │   └─ Route to: "lesson_planner" (Feedback Loop)                                 │
│   └─ IF iteration_count >= max_iterations:                                          │
│       └─ Route to: "end" (Final Summary)                                            │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          5. FINAL SUMMARY AGENT                                     │
│                              (No LLM - Display)                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ INPUT: Complete State (Learning Profile + Lesson Plan + Review Feedback)            │
│                                                                                     │
│ PROCESS:                                                                            │
│ ├─ Displays learning objectives                                                     │
│ ├─ Shows final lesson plan details                                                  │
│ ├─ Reports adequacy status and iterations used                                      │
│ ├─ Saves complete results to JSON file                                              │
│ └─ Provides user-friendly summary                                                   │
│                                                                                     │
│ OUTPUT: Final Results                                                               │
│ ├─ Display: Formatted summary in console                                            │
│ └─ File: simple_hikmah_tree.json                                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              FEEDBACK LOOP DETAILS                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│ ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                   │
│ │ Lesson Planner  │───▶│ Lesson Reviewer │───▶│ Router Decision │                   │
│ │ (gpt-4o)       │    │ (gpt-4o)       │    │                 │                     │
│ └─────────────────┘    └─────────────────┘    └─────────────────┘                   │
│         ▲                       │                       │                          │
│         │                       ▼                       ▼                         │
│         └───────────────────────┼───────────────────────┼─────────────────────────┘
│                                 │                       │
│                                 ▼                       ▼
│                         ┌─────────────────┐    ┌─────────────────┐
│                         │ Update State    │    │ Final Summary   │
│                         │ • iteration_count++ │    │ (END)         │
│                         │ • review_feedback  │    └─────────────────┘
│                         └─────────────────┘
│
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 🤖 Agent Details

### 1. User Understanding Agent (gpt-4o-mini)

- **Purpose**: Conducts natural conversation to understand user learning goals
- **Model**: gpt-4o-mini (temperature: 0.7)
- **Process**:
  - Asks conversational questions about learning interests
  - Assesses current knowledge level
  - Extracts specific learning objectives
  - Determines when enough information is gathered
- **Output**: Structured learning profile with objectives, knowledge level, and notable points

### 2. Lesson Planner Agent (gpt-4o)

- **Purpose**: Creates comprehensive lesson plans based on user profile
- **Model**: gpt-4o (temperature: 0.7)
- **Process**:
  - Analyzes learning objectives and knowledge level
  - Generates 4-6 detailed lessons
  - Includes both historical and theological content
  - Builds progressive learning structure
  - Incorporates feedback from previous iterations
- **Output**: Complete lesson plan with topic, lessons, and teaching approach

### 3. Lesson Reviewer Agent (gpt-4o)

- **Purpose**: Reviews lesson plans for adequacy and quality
- **Model**: gpt-4o (temperature: 0.7)
- **Process**:
  - Reviews lesson plan against learning objectives
  - Assesses appropriateness for knowledge level
  - Checks logical progression and comprehensiveness
  - Identifies missing topics and improvements
  - Determines if plan is adequate
- **Output**: Review feedback with adequacy status and improvement suggestions

### 4. Router

- **Purpose**: Decides next step based on review feedback
- **Process**:
  - If adequate: Route to Final Summary
  - If not adequate and iterations < max: Route back to Lesson Planner
  - If max iterations reached: Route to Final Summary

### 5. Final Summary Agent

- **Purpose**: Displays results and saves to file
- **Process**:
  - Shows learning objectives
  - Displays lesson plan details
  - Reports adequacy status and iterations used
  - Saves complete results to JSON file

## 🔄 How Agents Work Together

### State Management

The system uses a shared state (`HikmahState`) that persists throughout the workflow:

```python
class HikmahState(TypedDict, total=False):
    learning_profile: Dict[str, Any]      # From User Understanding Agent
    lesson_plan: Dict[str, Any]           # From Lesson Planner Agent
    review_feedback: Dict[str, Any]       # From Lesson Reviewer Agent
    iteration_count: int                   # Tracks feedback loop iterations
    is_adequate: bool                      # Whether plan meets requirements
    max_iterations: int                    # Maximum allowed iterations
    conversation_history: List[Dict[str, str]]  # User conversation history
    current_agent: str                     # Current agent for routing
```

### Feedback Loop Mechanism

1. **Lesson Planner** creates initial lesson plan
2. **Lesson Reviewer** assesses the plan
3. **Router** decides if plan is adequate
4. If not adequate and iterations < max:
   - **Lesson Planner** creates improved plan using feedback
   - **Lesson Reviewer** reassesses
   - Loop continues until adequate or max iterations reached
5. **Final Summary** displays results

### Error Handling

Each agent has fallback mechanisms:

- **User Understanding**: Manual extraction from conversation if LLM fails
- **Lesson Planner**: Basic fallback lesson plan if generation fails
- **Lesson Reviewer**: Basic approval if review fails

## 📊 Example Usage

### Sample Conversation

```
🤖 Hello! I'd love to help you learn about Shia Islam. What would you like to learn about?
You: I want to learn about successorship to the Prophet
🤖 That's a great topic to explore! Are you looking to understand the historical context, the key figures involved, or perhaps the theological implications of his succession?
You: theological and historical context too. I want to know who the rightful successor was
🤖 I have enough information now. Here's a summary of what I've gathered:
{
    "learning_objectives": ["The rightful successor to the Prophet Muhammad", "The historical context of Ali and Abu Bakr", "The theological implications of succession in Shia Islam"],
    "current_knowledge_level": "User knows that Ali was a companion of the Prophet and is aware that Abu Bakr was the first caliph, but lacks detailed understanding of the events and arguments surrounding their roles.",
    "points_to_note": ["User is specifically interested in factual information about the rightful successor", "User is looking for a balanced view of historical events and theological perspectives"]
}
```

### Sample Output

The system generates a comprehensive lesson plan with 5 detailed lessons covering:

- Introduction to the Succession Issue
- Historical Context: The Events at Saqifah
- Ali ibn Abi Talib: His Life and Role in Early Islam
- Theological Perspectives: Sunni and Shia Views on Succession
- Legacy and Impact of the Succession Dispute

## 📁 File Structure

```
hikmah-prot1/
├── hikmah_main.py              # Main system with all agents
├── requirements.txt             # Python dependencies
├── README.md                   # This documentation
├── simple_hikmah_tree.json     # Sample output file
├── venv/                       # Virtual environment
├── .gitignore                  # Git ignore file
└── .git/                       # Git repository
```

## 🔧 Configuration

### Model Configuration

- **User Understanding**: gpt-4o-mini (cost-effective for conversation)
- **Lesson Planning**: gpt-4o (high-quality curriculum design)
- **Lesson Reviewing**: gpt-4o (high-quality assessment)

### System Parameters

- **Max Iterations**: 5 (prevents infinite loops)
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Output Format**: JSON (structured and parseable)

## 🎯 Key Features

- **Natural Conversation**: No rigid questionnaires, intelligent Q&A
- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Feedback Loops**: Continuous improvement until adequate
- **State Persistence**: All data maintained throughout workflow
- **Error Handling**: Robust fallback mechanisms
- **Structured Output**: JSON format for easy integration
- **High-Quality Content**: Uses advanced LLMs for lesson planning

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with LangGraph for multi-agent orchestration
- Powered by OpenAI's GPT models
- Designed for Shia Islam education and learning
