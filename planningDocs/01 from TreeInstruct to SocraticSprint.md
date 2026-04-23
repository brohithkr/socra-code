# Socratic Sprint: Architectural Reconstruction, Implementation Strategy, and Pedagogical Enhancement of the TreeInstruct Framework for Automated Code Debugging

## 1. Introduction: The Alignment Paradox in Educational AI

The deployment of Large Language Models (LLMs) in educational settings has precipitated a fundamental conflict between the optimization objectives of generative AI and the pedagogical requirements of effective learning. Standard LLMs, such as GPT-4 and Claude 3.5 Sonnet, are fine-tuned via Reinforcement Learning from Human Feedback (RLHF) to maximize "helpfulness". In general information retrieval, helpfulness is synonymous with efficiency: providing the direct answer to a user's query with minimal friction. However, in the domain of computer science education—specifically code debugging—this efficiency is pedagogically detrimental. It short-circuits the cognitive process of "productive struggle," wherein a learner must generate hypotheses, isolate variables, and mentally trace execution flows to identify errors. When an AI instantly diagnoses a bug and provides corrected code, it transforms an active learning opportunity into a passive consumption event, undermining long-term retention and skill acquisition.

This report outlines a comprehensive technical strategy for the "Socratic Sprint" final year project. The objective is to develop an AI-driven tutoring system that adheres to the "Instruct, Not Assist" paradigm, specifically leveraging the **TreeInstruct** architecture proposed by Kargupta et al. (2024). The core innovation of TreeInstruct is the decoupling of _domain knowledge_ (knowing the answer) from _pedagogical strategy_ (guiding the student). Unlike standard chatbots that act as "Single-Turn Assistants," TreeInstruct operates as a "Multi-Turn Planner," dynamically constructing a decision tree of questions based on a rigorous estimation of the student's current knowledge state.

This document serves as an exhaustive implementation manual and research extension for a seven-day development sprint. It reconstructs the proprietary architecture of TreeInstruct from available research snippets, details the specific prompt engineering required for its dual-agent system, and proposes significant value-add features—specifically **LLM-based Knowledge Tracing (KT)** and **Affective Guardrails**—to elevate the project beyond mere replication into novel research territory.

### 1.1 The Pedagogical Imperative: Socratic Reasoning

The Socratic method involves a dialectical exchange where the teacher guides the student to truth through a series of probing questions rather than declarative statements. Implementing this in a stochastic model requires constraining the model's output space. The model must recognize the solution but be explicitly inhibited from stating it. Instead, it must calculate the "distance" between the student's current understanding and the target state, and generate a question that bridges a fraction of that gap.

Recent findings indicate that while LLMs can simulate Socratic questioning, they suffer from "solution leakage"—the tendency to give up and provide the answer when the student struggles, or to provide hints that are too direct. The TreeInstruct framework addresses this by interposing a planning layer between the student and the LLM. This planner, driven by a **Verifier Agent**, dictates the _intent_ of the next turn (e.g., "ask a sibling question to clarify the previous concept") before the **Instructor Agent** generates the actual text. This separation of concerns is the architectural cornerstone of the system.

### 1.2 Project constraints and Objectives

Given the strict one-week timeline for the "Socratic Sprint," the implementation strategy prioritizes architectural fidelity and modularity over scale. The focus is strictly on the AI backend and interaction logic, bypassing complex multiplayer synchronization features. The key objectives are:

1. **Architectural Fidelity:** accurately reconstructing the Instructor-Verifier loop and the State Space Planning algorithm (Algorithm 1) described in the base paper.
    
2. **Implementation Viability:** Developing a functioning prototype using accessible frameworks (Python, LangChain/OpenAI API, Pydantic) without access to the original codebase.
    
3. **Research Contribution:** Integrating a novel feature—**Knowledge Tracing**—that addresses a documented limitation of the base paper (statelessness across problems).
    
4. **Rigorous Evaluation:** Designing a "Simulated Student" benchmark to quantify the system's pedagogical effectiveness compared to baseline LLMs.
    

---

## 2. Architectural Reconstruction: The TreeInstruct Framework

The analysis of the research literature reveals that TreeInstruct is not a single model, but a **Multi-Agent System (MAS)** orchestrated by a central control loop. This architecture is designed to maintain a coherent "Thread of Truth" throughout a debugging session, preventing the AI from hallucinating bugs or forgetting the original problem context.

### 2.1 The Dual-Agent System

The system is composed of two primary agents: the **Verifier** and the **Instructor**. Their relationship is hierarchical; the Verifier acts as the "brain" or the planner, while the Instructor acts as the "voice" or the executor.

#### 2.1.1 The Verifier Agent (The Planner)

The Verifier is the critical innovation of the TreeInstruct paper. In standard chatbot interactions, the model relies on the immediate context window to judge correctness. However, in debugging, a student's answer might be linguistically coherent but logically flawed regarding the specific bug. The Verifier anchors the session in ground truth.

The Verifier performs four distinct high-level functions, which must be implemented as separate prompt chains or function calls:

1. **State Space Estimation (`GenerateState`):**
    
    - **Input:** The Problem Statement ($P$), the Student's Buggy Code ($B$), and the Ground Truth Solution ($C$).
        
    - **Mechanism:** The Verifier performs a semantic diff between $B$ and $C$. It does not just look for syntax errors; it identifies logical gaps.
        
    - **Output:** A structured list of "Tasks" ($\tau_1, \tau_2,..., \tau_k$). Each task represents a discrete unit of knowledge or a specific fix the student must perform (e.g., "Initialize the counter variable outside the loop," "Correct the recursion base case"). This list constitutes the "State Space" for the session.
        
    - **Significance:** This transforms the nebulous goal of "fix the code" into a concrete checklist of sub-goals.
        
2. **Response Verification (`VerifyResponse`):**
    
    - **Input:** The current active Task ($\tau_{current}$), the Instructor's last Question ($q$), and the Student's Response ($r$).
        
    - **Mechanism:** The Verifier acts as a boolean judge. It determines if $r$ correctly answers $q$. Crucially, it also extracts the _reason_ ($w$) for any error.
        
    - **Output:** A tuple $(v, w)$ where $v \in \{True, False\}$ and $w$ is the rationale (e.g., "Student confused index with value").
        
3. **Understanding Assessment (`UpdateUnderstanding`):**
    
    - **Input:** A correct student response ($r$) and the conversation history ($H$).
        
    - **Mechanism:** This is a "Depth Check." A student might guess the right answer ("Is it n-1?" "Yes"). The Verifier checks for evidence of deep understanding (e.g., "Because arrays are 0-indexed").
        
    - **Output:** A state variable $S[\tau]$ indicating if the task is fully resolved or requires further probing.
        
4. **Termination Check (`isResolved`):**
    
    - **Input:** The student's proposed fix (natural language or code snippet).
        
    - **Mechanism:** It checks for "isomorphism" between the student's fix and the ground truth logic. The fix doesn't need to be syntactically identical, but it must be functionally equivalent.
        

#### 2.1.2 The Instructor Agent (The Interface)

The Instructor is a conditioned text generation agent. Unlike a generic chatbot, it has no autonomy over _what_ to teach, only _how_ to phrase it.

- **Constraint Checklist:** The Instructor is prompted with "Negative Constraints" :
    
    - NEVER reveal the code solution.
        
    - NEVER write code segments in the output.
        
    - ALWAYS end the turn with a question.
        
- **Dynamic Modes:** The Instructor generates questions based on the Verifier's directives:
    
    - **Root Question:** Introduces a new Task ($\tau$). Example: "Let's look at how you are calculating the sum. What variable holds the total?"
        
    - **Sibling Question:** Generated when the student is incorrect ($v=False$). It rephrases the previous concept without advancing complexity. Example: "Not quite. Think about the initial value of that variable. Is it zero?".
        
    - **Child Question:** Generated when the student is correct but understanding is shallow ($v=True, S[\tau]=Pending$). It probes deeper. Example: "Correct. Why does starting at 1 cause an error in this specific list?"
        

### 2.2 The Planning Algorithm (Algorithm 1 Reconstruction)

The "Tree" in TreeInstruct refers to the dynamic interaction graph created by this back-and-forth. The algorithm traverses this tree. Based on the snippet , which explicitly lists lines of the algorithm, the logic flow is reconstructed below.

**Algorithm 1: Tree-Based Socratic Planning**

1. **Initialization:**
    
    - Receive Inputs: Problem ($P$), Buggy Code ($B$), Solution ($C$).
        
    - **Verifier:** `GenerateState(P, B, C)` $\rightarrow$ List of Tasks $\{\tau_1, \tau_2,... \tau_k\}$.
        
    - Set `Current_Task_Index` $l = 0$.
        
    - Initialize `History` $H =$.
        
2. **Main Loop (While $l < k$):**
    
    - **Step 1: Select Task.** Let $\tau = \text{Tasks}[l]$.
        
    - **Step 2: Generate Question.**
        
        - If it's the start of the task, Instructor generates `RootQuestion(\tau)`.
            
        - Else, use the previous logic to determine the question type.
            
    - **Step 3: Interaction.**
        
        - Display Question $q$ to student.
            
        - Capture Response $r$.
            
        - Append $(q, r)$ to $H$.
            
    - **Step 4: Verification (The Fork).**
        
        - **Verifier:** `VerifyResponse(q, r, \tau)` $\rightarrow$ Correctness $v$, Reason $w$.
            
    - **Step 5: Branching Logic.**
        
        - **IF $v$ is False (Incorrect):**
            
            - Instructor generates `SiblingQuestion(\tau, w)`. (Reframes based on error $w$).
                
            - _Loop repeats Step 3._ (Stays on same node breadth).
                
        - **ELSE (Correct):**
            
            - **Verifier:** `UpdateUnderstanding(H, r, \tau)` $\rightarrow$ Resolved $S_{\tau}$.
                
            - **IF $S_{\tau}$ is False (Shallow):**
                
                - Instructor generates `ChildQuestion(\tau)`. (Drills down depth).
                    
                - _Loop repeats Step 3._
                    
            - **ELSE (Resolved):**
                
                - Instructor confirms understanding.
                    
                - Prompt student for fix: "How would you change your code now?"
                    
                - **Verifier:** `isResolved(StudentFix, \tau)`.
                    
                - If Resolved: Increment $l$ (Proceed to next task $\tau_{l+1}$).
                    
                - If Not Resolved: Generate `SiblingQuestion` regarding the implementation details.
                    
3. **Termination:**
    
    - When $l = k$ (all tasks resolved), the system congratulates the student and presents the fully corrected code (optional, or asks student to run it).
        

### 2.3 Data Structures and State Management

To implement this efficiently, the system requires a rigid state definition. We can infer the necessary data structures from the functional requirements.

**Table 1: Core Data Structures for TreeInstruct**

|**Structure**|**Component**|**Description**|
|---|---|---|
|**Task Object**|`id` (int)|Unique identifier for the bug/concept.|
||`description` (str)|Natural language description (e.g., "Fix off-by-one error").|
||`concept_tag` (str)|Pedagogical category (e.g., "Loops", "Recursion").|
||`status` (enum)|`PENDING`, `IN_PROGRESS`, `RESOLVED`.|
|**Interaction Node**|`turn_id` (int)|Sequential turn number.|
||`type` (enum)|`ROOT`, `SIBLING`, `CHILD`.|
||`question` (str)|Text displayed to student.|
||`response` (str)|Student input.|
||`verification` (json)|Output from Verifier (correctness boolean, reasoning).|
|**Session State**|`tasks` (List)|The roadmap for the current problem.|
||`current_ptr` (int)|Index of the active task.|
||`history` (List[Node])|Complete conversation log for context injection.|

---

## 3. Implementation Strategy: The 7-Day Sprint

This section translates the architectural theory into a concrete build plan. Given the short timeline, the recommendation is to use **Python** with **LangChain** (for LLM orchestration) and **Streamlit** (for the user interface). These tools allow for rapid prototyping of the chat interface and state management.

### 3.1 Technology Stack Selection

- **Backend:** Python 3.9+
    
- **LLM Interface:** OpenAI API (Direct calls recommended over LangChain for the complex Verifier logic to ensure strict JSON adherence).
    
- **Models:**
    
    - **Verifier:** `gpt-4o` (Must have high reasoning capability for code analysis and state estimation).
        
    - **Instructor:** `gpt-4o-mini` or `gpt-3.5-turbo` (Sufficient for conversational generation once the plan is set).
        
- **Data Validation:** `Pydantic` (Crucial for enforcing the Verifier's output schema).
    
- **Frontend:** `Streamlit` (Allows building a chat interface in <50 lines of code).
    

### 3.2 Prompt Engineering Reconstruction

Since the original code is unavailable, we must reverse-engineer the prompts based on the functional descriptions in the snippets.

#### 3.2.1 The Verifier Prompts

**Prompt 1: State Generation (The "Planner")**

SYSTEM ROLE:

You are an expert Computer Science Pedagogy Verifier. Your job is to analyze buggy code and define a learning plan.

INPUTS:

1. Problem Description
    
2. Buggy Code (Student Submission)
    
3. Correct Code (Ground Truth)
    

INSTRUCTIONS:

Compare the Buggy Code and Correct Code. Identify distinct logical or syntactical errors.

For each error, define a "Task" that represents the knowledge gap the student needs to bridge.

The tasks should be ordered logically (e.g., fix variable initialization before using it in a loop).

OUTPUT SCHEMA (JSON):

{

"tasks":

}

**Prompt 2: Response Verification (The "Judge")**

SYSTEM ROLE:

You are a strict Logic Verifier. You assess student responses in a debugging session.

INPUTS:

1. Current Task: {task_description}
    
2. Instructor Question: {last_question}
    
3. Student Response: {student_response}
    

INSTRUCTIONS:

Determine if the student's response is factually correct relative to the question.

Analyze if the response demonstrates deep understanding or just guessing.

If incorrect, identify the specific misconception.

OUTPUT SCHEMA (JSON):

{

"is_correct": boolean,

"reasoning": "string explaining why it is correct/incorrect",

"misconception": "string or null",

"understanding_depth": "shallow" | "deep" | "none",

"next_move_recommendation": "sibling" | "child" | "next_task"

}

#### 3.2.2 The Instructor Prompts

**Prompt 3: Dynamic Question Generation (The "Tutor")**

SYSTEM ROLE:

You are a Socratic Tutor for Python programming.

Your Goal: Guide the student to fix their code themselves.

Constraint 1: NEVER provide the code solution or write code snippets.

Constraint 2: NEVER explicitly state the bug location (e.g., "Line 5 is wrong").

Constraint 3: Ask short, probing questions.

CONTEXT:

Problem: {problem_description}

Current Focus Task: {current_task.socratic_goal}

Student's Last Status: {verifier.is_correct? "Correct" : "Incorrect"}

Verifier Feedback: {verifier.reasoning}

INSTRUCTION:

Based on the Verifier's feedback, generate the next question.

- If status is Incorrect, ask a SIBLING question: Rephrase the concept, simplify the scope, or ask them to trace a specific variable.
    
- If status is Correct (Shallow), ask a CHILD question: Ask "Why?" or "What if?" to verify depth.
    
- If this is a new Task, ask a ROOT question: Direct attention to the logic component (not the line number).
    

OUTPUT:

[Just the natural language question]

### 3.3 The Control Loop Logic (Python Pseudocode)

The following logic must be implemented in the main application file (e.g., `app.py`).

```Python
def main_loop(state):
    # 1. Check if we have active tasks
    if not state.tasks:
        state.tasks = Verifier.generate_state(problem, buggy_code, correct_code)
        state.current_task_idx = 0
    
    current_task = state.tasks[state.current_task_idx]
    
    # 2. Get Student Input (from UI)
    student_response = get_user_input()
    
    # 3. Verify Response
    last_question = state.history[-1].question if state.history else "START"
    verification = Verifier.verify(current_task, last_question, student_response)
    
    # 4. Update State & Plan Next Move
    if not verification.is_correct:
        # User is stuck -> Sibling Question
        next_q = Instructor.generate_sibling(current_task, verification.misconception)
    
    elif verification.understanding_depth == "shallow":
        # User is right but vague -> Child Question
        next_q = Instructor.generate_child(current_task)
        
    else:
        # User is fully correct -> Resolve Task
        current_task.status = "RESOLVED"
        state.current_task_idx += 1
        
        if state.current_task_idx >= len(state.tasks):
            return "CONGRATULATIONS! You've fixed the code."
            
        # Start next task
        next_task = state.tasks[state.current_task_idx]
        next_q = Instructor.generate_root(next_task)

    # 5. Output to User
    display(next_q)
    state.history.append(Interaction(question=next_q, response=student_response))
```

---

## 4. Strategic Value Addition: Enhancing the Research

The original request explicitly states the need to "add value" and "features" beyond replication. The analysis of the research snippets highlights a significant gap: **TreeInstruct is stateless across problems.** It treats every debugging session as an isolated event. It does not learn that Student A struggles with recursion, or Student B excels at arrays but fails at boundary conditions.

To address this, and to elevate the final year project, I propose implementing **LLM-based Knowledge Tracing (KT)**.

### 4.1 Value Add 1: Integrated Knowledge Tracing (KCGen-KT)

Knowledge Tracing (KT) is the task of modeling a student's mastery of specific skills (Knowledge Components or KCs) over time. Traditional KT uses Bayesian networks (BKT). However, recent research suggests using LLMs to _generate_ KCs dynamically and track them.

**Implementation Plan:**

1. **KC Tagging:**
    
    - Modify the `Verifier.GenerateState` prompt. In addition to generating tasks, it must assign a standardized `concept_tag` from a predefined taxonomy (e.g., `Control Flow`, `Data Structures`, `Syntax`, `Algorithmic Logic`).
        
    - _Snippet Reference:_ describes "KCGen-KT" where GPT-4o identifies KCs from AST representations.
        
2. **User Model Persistence:**
    
    - Create a simple JSON file store (`student_profiles.json`).
        
    - Structure:
        
        JSON
        
        ```
        "user_123": {
            "mastery_scores": {
                "Control Flow": 0.4,
                "Data Structures": 0.8
            },
            "history": [...]
        }
        ```
        
3. **Adaptive Prompt Injection:**
    
    - This is the critical "Value Add." Before the Instructor generates a question, inject the student's mastery profile into the context.
        
    - _Modified Instructor Prompt:_
        
        > "User Profile: This student has LOW mastery (0.4) in Control Flow. When asking about the while loop, be extra granular and define terms if necessary. Do not assume prior knowledge of loop termination conditions."
        
4. **Benefits:** This turns the system from a "Debugger" into a "Personalized Tutor." It satisfies the requirement for "added features" and demonstrates deep engagement with current literature on "LLM-based Knowledge Tracing".
    

### 4.2 Value Add 2: Affective Guardrails (Sentiment-Awareness)

Another limitation of pure Socratic questioning is user frustration. If a student is stuck in a loop of Socratic questions, they may disengage.

**Implementation Plan:**

1. **Sentiment Check:** In the `Verifier.VerifyResponse` step, add a field `sentiment_score` (1-10, where 10 is angry/frustrated).
    
2. **Logic Switch:**
    
    - If `sentiment_score > 7`: Trigger a "Bail Out" mechanism.
        
    - Instead of a Socratic Question, the Instructor provides a **Scaffolding Hint** (a direct clue, though still not the code).
        
    - _Rationale:_ This mimics a human teacher who senses frustration and temporarily relaxes the Socratic rigor to keep the student motivated.
        

---

## 5. Benchmarking and Experimental Design

For a final year project, qualitative claims ("it feels better") are insufficient. You must provide quantitative data. Since recruiting human subjects for a one-week project is unfeasible, the recommended approach is **LLM-based Simulation**.

### 5.1 The "Simulated Student" Methodology

You will create an LLM agent that _pretends_ to be a student. This allows you to run hundreds of test sessions automatically.

**The Simulated Student Prompt:**

> "You are a Novice Python Programmer. You have written the following buggy code: {buggy_code}. You DO NOT know where the bug is. You are interacting with an AI tutor. Answer their questions based ONLY on the code you see. You make frequent logical errors regarding array indexing. If the tutor asks a very difficult question, say 'I don't know'."

### 5.2 Evaluation Metrics

You will compare your **TreeInstruct+KT** system against a **Baseline** (Standard GPT-4o "Help me fix this" prompt).

**Table 2: Proposed Evaluation Metrics**

|**Metric**|**Definition**|**Goal**|
|---|---|---|
|**Success Rate (SR)**|Percentage of sessions where the _Simulated Student_ successfully fixes the code.|Prove effectiveness.|
|**Average Turns**|Mean number of dialogue turns to reach solution.|**TreeInstruct** should be _higher_ than Baseline (because it teaches), but not infinite.|
|**Socratic Index (SI)**|A novel metric derived from the literature. $SI = \frac{N_{questions}}{N_{total\_turns}}$.|**TreeInstruct** should aim for SI > 0.8. Baseline usually has SI < 0.2.|
|**Code Isomorphism**|Semantic similarity between the final student code and the ground truth.|Ensure the fix is valid.|
|**Knowledge Gain (Proxy)**|If using KT, measure if the Simulated Student requires fewer turns to solve a _second_ similar problem.|Prove the KT module works.|

### 5.3 Experimental Procedure

1. **Dataset:** Select 5 distinct LeetCode-style problems (e.g., Fibonacci, Palindrome, Two Sum).
    
2. **Bug Injection:** Manually introduce specific bugs (e.g., off-by-one, infinite loop) into the solutions.
    
3. **Run:** Execute the Simulated Student against the Baseline (10 runs per problem) and TreeInstruct (10 runs per problem).
    
4. **Analyze:** Collect logs and compute the metrics in Table 2.
    

---

## 6. Execution Roadmap: The 7-Day Sprint

This schedule is designed to ensure a deliverable project by the deadline.

**Day 1: Infrastructure and Data**

- **Goal:** Environment setup and Dataset creation.
    
- **Tasks:**
    
    - Set up Python environment (`pip install langchain openai streamlit pydantic`).
        
    - Create `data/problems.json` containing 5 problems. Each entry must have: `problem_text`, `buggy_code`, `correct_code`.
        
    - Create `data/student_profiles.json` (empty structure).
        

**Day 2: The Core Verifier**

- **Goal:** Implement the "Brain".
    
- **Tasks:**
    
    - Implement `verifier.py`.
        
    - Draft and test the `GenerateState` prompt. Ensure it reliably outputs JSON tasks for your 5 problems.
        
    - Draft `VerifyResponse` prompt. Test it with manual inputs (mock student answers).
        

**Day 3: The Instructor and Interface**

- **Goal:** Basic Chat Loop.
    
- **Tasks:**
    
    - Implement `instructor.py` with the "Negative Constraint" prompts.
        
    - Build a minimal Streamlit app (`st.chat_input`, `st.chat_message`) that connects the Instructor to the User.
        
    - _Milestone:_ You can chat with the bot, but it has no memory/planning yet.
        

**Day 4: The Planning Algorithm**

- **Goal:** Algorithm 1 Logic.
    
- **Tasks:**
    
    - Implement the state machine in `main.py`.
        
    - Connect Verifier outputs to Instructor inputs.
        
    - Implement the branching logic (Sibling vs. Child questions).
        
    - _Milestone:_ The bot effectively guides you through one problem.
        

**Day 5: Value Add Implementation (Knowledge Tracing)**

- **Goal:** Intelligence layer.
    
- **Tasks:**
    
    - Update Verifier to tag KCs.
        
    - Implement `profile_manager.py` to read/write mastery scores.
        
    - Inject profile data into Instructor prompts.
        
    - Test: Solve problem 1 (Recursion), then see if Problem 2 (Recursion) dialogue changes (should be faster/less detailed).
        

**Day 6: Simulation and Benchmarking**

- **Goal:** Gather Data.
    
- **Tasks:**
    
    - Write `simulate.py` using the Simulated Student prompt.
        
    - Run the batch of 50 simulations (5 problems * 10 runs).
        
    - Save logs to CSV.
        
    - Calculate Socratic Index.
        

**Day 7: Reporting and Final Polish**

- **Goal:** Final Submission.
    
- **Tasks:**
    
    - Generate charts (SI comparison, Success Rate).
        
    - Write the final report using the structure defined in Section 1-5 of this document.
        
    - Record a concise demo video showing the "Knowledge Tracing" adaptation (e.g., "See how the bot remembers I'm bad at loops?").
        

## 7. Conclusion

This report has outlined a robust path to replicating and extending the "Instruct, Not Assist" framework. By reconstructing the **Verifier-Instructor** dual-agent architecture, the project ensures fidelity to the Socratic method, preventing the common failure mode of LLM "solution leakage." The implementation of **Algorithm 1** provides the necessary state-space planning to guide students through complex debugging tasks systematically.

Furthermore, the integration of **LLM-based Knowledge Tracing** significantly enhances the research value of the project. It addresses the stateless nature of the original TreeInstruct model, moving the system towards a true **Intelligent Tutoring System (ITS)** that adapts to long-term learner profiles. The proposed "Simulated Student" benchmarking methodology provides a rigorous, quantitative basis for evaluation, ensuring the final deliverable is not just a software prototype, but a validated piece of educational technology research. The seven-day sprint plan provides a feasible, high-velocity roadmap to achieve these objectives within the strict timeline.