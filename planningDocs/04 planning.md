# Socratic Sprint: Architectural Intelligence in Low-Resource Environments

## 1. Executive Summary

The "Socratic Sprint" project represents a fundamental divergence from the prevailing trajectory of Large Language Model (LLM) application development. Where the current industry standard—the "Goliath" approach—prioritizes raw model scale, massive parameter counts, and zero-shot performance on static benchmarks, the Socratic Sprint champions the "David" methodology. This approach posits that a smaller, computationally efficient model (specifically **Qwen2.5-Coder-7B**), when embedded within a sophisticated, recursive control architecture, can outperform larger state-of-the-art (SOTA) models in high-value, multi-turn pedagogical tasks. The specific domain of application is **Socratic Debugging**: the art of guiding a novice programmer to identify and resolve errors through questioning rather than direct correction.

This comprehensive report details the research, architectural design, and implementation strategy for the Socratic Sprint. Relying exclusively on free API resources aggregated in the `cheahjs/free-llm-api-resources` repository, we demonstrate that the financial barrier to entry for advanced AI tutoring systems is effectively zero, provided one navigates the volatility of the "free tier" ecosystem with robust software engineering. We conduct a forensic analysis of six candidate Data Structures and Algorithms (DSA) repositories, identifying **Strivers-A2Z-DSA-Sheet** and **TreeInstruct** as the primary data substrates, while critically evaluating and ultimately discarding less structured alternatives like `ACM_Notebook_new`.

The proposed implementation leverages a "David vs. Goliath" benchmarking framework. We contrast the 'As Is' performance of proprietary giants (accessed via limited free tiers like GitHub Models) against the 'On Architecture' performance of open-weights models (accessed via OpenRouter and SiliconFlow). The architecture utilizes **Reflexion** patterns and **Tree of Thoughts** planning to synthesize the reasoning depth typically associated with trillion-parameter models. This report serves as the definitive blueprint for constructing this system, offering detailed module specifications, data ingestion strategies, and a rigorous justification for prioritizing architectural agency over model scale.

## 2. Theoretical Framework: The David vs. Goliath Paradigm

### 2.1. The Oracle Problem in AI Education

The central tension in applying Generative AI to education is the "Oracle Problem." Large, SOTA models (Goliaths) like GPT-4o or DeepSeek-V3 are optimized for immediate correctness. When presented with a buggy code snippet, their training incentivizes them to provide the corrected code instantly, often accompanied by a brief explanation. While efficient for professional engineering, this behavior is pedagogically catastrophic for a novice learner. It short-circuits the cognitive struggle required for deep learning, turning the interaction into a transaction of answers rather than a transfer of understanding.

The "David" approach addresses this not by increasing model size, but by constraining the model's agency through architecture. By utilizing a smaller model like **Qwen2.5-Coder-7B-Instruct**—which, while powerful, is less prone to the "know-it-all" dominance of larger models—and wrapping it in a control loop that explicitly forbids code generation in favor of question generation, we synthesize a Socratic tutor.

### 2.2. Architectural Intelligence vs. Model Scale

The hypothesis driving this project is that **Architecture > Scale** for longitudinal tasks.

- **Goliath ('As Is'):** Operates in a stateless, zero-shot or few-shot manner. It relies on internal "world model" density to solve problems in a single forward pass.
    
- **David ('On Architecture'):** Operates in a stateful, multi-turn agentic loop. It relies on externalized state management, explicit planning steps (e.g., "Identify user misconception," "Formulate probing question," "Verify user understanding"), and recursive self-correction (Reflexion).
    

Research supports this view, indicating that GPT-3.5 (a smaller model) wrapped in an agentic workflow can outperform GPT-4 (a larger model) on coding benchmarks. The Socratic Sprint applies this logic to the domain of human-AI interaction, using the **TreeInstruct** methodology to model the student's mind as a state space that the agent navigates.

## 3. The Resource Ecosystem: Navigating the Free Tier

The Socratic Sprint operates under a strict constraint: total reliance on free API providers identified in the `cheahjs/free-llm-api-resources` repository. This constraint necessitates a complex "Free Tier Orchestration" strategy to handle rate limits, model availability, and provider volatility.

### 3.1. Provider Analysis and Selection

The analysis of the `cheahjs` repository and associated discussions reveals a tiered ecosystem of providers. We categorize them based on reliability, model access, and rate limits.

#### 3.1.1. The Aggregators: OpenRouter

**OpenRouter** emerges as the cornerstone of our infrastructure. It acts as a unified gateway, aggregating various free models from different hosting services.

- **Model Availability:** The repository confirms the availability of **Qwen2.5-Coder-7B-Instruct** (free tier). It also lists **Qwen2.5-VL-7B** and **Qwen3-Coder-480B** (via specific free endpoints).
    
- **Context Window:** The Qwen2.5-7B-Instruct model on OpenRouter supports a **32,768 token** context window in the free tier. This is a critical enabler for the Socratic Sprint, as pedagogical dialogues can become lengthy, requiring the model to retain the history of the student's misconceptions and previous attempts.
    
- **Strategic Value:** OpenRouter's standardization allows us to decouple our application logic from the underlying inference engine. If the specific `qwen/qwen-2.5-7b-instruct:free` endpoint becomes congested, we can programmatically switch to another free provider without rewriting the API client.
    

#### 3.1.2. The High-Performance Engine: SiliconFlow

**SiliconFlow** is identified as a high-performance provider for open-weights models, specifically the Qwen and DeepSeek series.

- **Rate Limits:** The analysis of SiliconFlow's documentation reveals a nuanced "Fixed Rate Limit" for free models. Unlike providers that cap total usage, SiliconFlow imposes throughput limits:
    
    - **RPM (Requests Per Minute):** 1,000 - 10,000.
        
    - **TPM (Tokens Per Minute):** 50,000 - 5,000,000.
        
- **Implication:** These limits are exceptionally generous for a single-threaded application but require a "Token Bucket" rate limiter in our implementation to prevent 429 errors during burst processing (e.g., when the agent performs internal "Reflexion" loops before responding to the user).
    
- **Models:** Explicit support for **Qwen2.5-Coder-7B-Instruct** and **DeepSeek-V3**. The availability of DeepSeek-V3 allows us to use a "Goliath-lite" model for the internal verification steps of our David agent.
    

#### 3.1.3. The Speed Layer: Groq

**Groq** is distinguished by its LPU (Language Processing Unit) architecture, offering ultra-low latency.

- **Role:** While Groq's rate limits (e.g., 30 RPM for Llama-3-70B ) are tighter than SiliconFlow's, its speed makes it ideal for the **Intent Classification** and **Syntax Checking** modules of our architecture. These tasks require instant feedback but consume few tokens.
    
- **Models:** Supports Llama-3-70B and Mixtral-8x7B. We will utilize these as auxiliary "tools" for the main Qwen-based agent.
    

#### 3.1.4. The Baseline Benchmark: GitHub Models

To benchmark our "David" system against a true "Goliath," we require access to proprietary SOTA models. **GitHub Models** (via Azure) provides this access.

- **Models:** **GPT-4o** and **GPT-4.1**.
    
- **Access:** Free tier availability is confirmed for "Pro" and beta users, with a "High" rate limit tier for some models.
    
- **Constraint:** This provider is strictly for _benchmarking_ the 'As Is' performance. We will not use it for the live Socratic agent due to the restrictive nature of the "playground" vs. API access and the likelihood of stricter long-term gating compared to the open-weights providers.
    

### 3.2. Quantitative Comparison of Free Tiers

The following table synthesizes the rate limit and model availability data extracted from the snippets.

|**Provider**|**Primary Model (David)**|**Benchmark Model (Goliath)**|**Context Window**|**Rate Limits (Free)**|**Use Case in Socratic Sprint**|
|---|---|---|---|---|---|
|**OpenRouter**|Qwen2.5-Coder-7B|DeepSeek-R1 (Distill)|32k|Variable (Community dependent)|**Primary Fallback & Aggregation**|
|**SiliconFlow**|Qwen2.5-Coder-7B|DeepSeek-V3|32k - 128k|1k RPM / 50k+ TPM|**Main Inference Engine** (High throughput)|
|**Groq**|Llama-3-8B|Llama-3-70B|8k - 128k|30 RPM / 14.4k TPM|**Latency-Sensitive Tooling** (Intent/Syntax)|
|**GitHub Models**|-|GPT-4o / GPT-4.1|128k|"High" (Beta), 15 req/min (Standard)|**Offline Benchmarking Only**|
|**HuggingFace**|Qwen2.5-Coder-7B|-|Variable|1000 req/hr (Pro), 1-300 (Free)|**Emergency Backup** (Low reliability)|

### 3.3. The "Free Tier Volatility" Mitigation Strategy

The research highlights a significant risk: "Please don't abuse these services, else we might lose them". Free tiers are ephemeral. A critical architectural requirement derived from this insight is **Provider Agnosticism**. The system cannot hardcode `api.siliconflow.cn`. Instead, we must implement a **Dynamic Router** module that:

1. Maintains a priority list of providers (SiliconFlow > OpenRouter > Groq).
    
2. Monitors HTTP 429 (Rate Limit) and 5xx (Server Error) responses.
    
3. Automatically fails over to the next provider in the chain without interrupting the user session.
    

## 4. Data Substrate Analysis: Fueling the Socratic Engine

To train, prompt, and validate the Socratic agent, we require a structured dataset of coding problems, correct solutions, and—crucially—buggy code with explanations. We analyzed six repositories to determine their utility.

### 4.1. Primary Data Sources

#### 4.1.1. Strivers-A2Z-DSA-Sheet (The Curriculum)

**Repositories:** `Strivers-A2Z-DSA-Sheet-C++` , `striver-a2z-dsa-Python` (referenced via `dhruv-yadav-nitj` and others ), `Strivers-A2Z-DSA-Sheet`.

- **Utility Verdict:** **High (Core Curriculum)**.
    
- **Structure Analysis:** The snippets reveal a highly structured organization: `Topic -> Difficulty -> Problem`.
    
    - File naming often follows `Question -> Approach -> Code` logic.
        
    - The READMEs act as an index, listing topics from "Basics" to "Dynamic Programming".
        
- **Content:** Contains the _correct_ solutions in C++, Java, and Python. This is the "Ground Truth."
    
- **Integration Strategy:** We will build a scraper (`dsa_ingestion`) to traverse the directory tree. The consistency of the folder structure (e.g., `01.Arrays`, `02.Binary Search`) allows for deterministic mapping of Problem IDs to their solutions in multiple languages. This enables the Socratic agent to support a student regardless of their preferred language (C++ or Python).
    

#### 4.1.2. TreeInstruct (The Pedagogy)

**Repository:** `TreeInstruct`.

- **Utility Verdict:** **Critical (Architectural Blueprint)**.
    
- **Content:** This repository contains the `tree_instruct_multi_debug_dataset`.
    
- **Schema Analysis:** The snippet provides the exact JSON schema required for Socratic debugging:
    
    - `<problem>`: The problem statement.
        
    - `<bug_fixes>`: The logic required to fix the code.
        
    - `<bug_desc>`: A natural language description of the bug.
        
    - `<buggy_code>`: The code with the injected error.
        
- **Integration Strategy:** This schema is the "Golden Format." We will use the _structure_ of this dataset to format the data extracted from Striver's sheet. Furthermore, the logic within `TreeInstruct` (specifically the state space planning described in the snippets ) serves as the reference implementation for our agent's planning module.
    

#### 4.1.3. javascript-algorithms (The Verifier)

**Repository:** `javascript-algorithms`.

- **Utility Verdict:** **Medium-High (Verification Logic)**.
    
- **Analysis:** Unlike Striver's sheet, which focuses on raw solutions, this repository includes comprehensive **test files** (Jest tests).
    
- **Value:** A Socratic tutor must be able to _run_ the student's code to verify correctness. We cannot rely on the LLM to "look" at the code and guess if it works (hallucination risk).
    
- **Integration Strategy:** We will map common algorithms (e.g., "Binary Search") in this repo to their counterparts in Striver's sheet. When a student submits a solution for Binary Search, we can execute it against the test cases extracted from `javascript-algorithms`.
    

### 4.2. Discarded Repositories

#### 4.2.1. ACM_Notebook_new

**Repository:** `ACM_Notebook_new`.

- **Verdict:** **Discard**.
    
- **Reasoning:** Described as a "file manager in its bare bones". The file structure is chaotic (`input/`, `notebooks/`, `code/`) and lacks the rigid Topic/Problem hierarchy of Striver's sheet. The content appears to be Jupyter notebooks for exploration rather than a structured DSA bank. Parsing this would require high effort for low yield.
    

#### 4.2.2. SDE-DSA-SD-Prep

**Repository:** `SDE-DSA-SD-Prep`.

- **Verdict:** **Discard**.
    
- **Reasoning:** This is a "comprehensive repository to track my progress". While it contains links to Striver and NeetCode, it is essentially a meta-list or a personal tracker rather than a primary data source. It lacks the uniform file content (code + approach) needed for automated ingestion. Using Striver's source repositories directly is more efficient.
    

## 5. The "David" Architecture: Implementation Specification

The "David" architecture is designed to simulate the reasoning capabilities of a GPT-4 class model using the Qwen2.5-Coder-7B model. This is achieved through **Cognitive Decoupling**: separating the tasks of _understanding_, _planning_, and _speaking_.

### 5.1. System Design: The Socratic Loop

The system operates as a state machine with the following phases:

1. **Ingestion & Analysis:** The system receives the student's code and the target problem.
    
2. **State Estimation (Hidden Thought):** The model analyzes the student's code to identify specific bugs (Syntax, Logic, Conceptual).
    
3. **Planning (Tree of Thoughts):** The model selects a pedagogical strategy (e.g., "Ask for a trace," "Propose a counter-example").
    
4. **Generation (David Speaks):** The model generates the Socratic question.
    
5. **Reflexion (Self-Correction):** The model critiques its own question to ensure it doesn't give away the answer.
    

### 5.2. Detailed Module Specifications

#### 5.2.1. Module: `dsa_ingestion`

**Function:** `extract_striver_data(repo_path, language='cpp')`

- **Logic:**
    
    1. Walk the directory tree of the cloned Striver repository.
        
    2. Regex match filenames to extract Problem ID and Title (e.g., `01.Arrays/01.SetMatrixZeroes.cpp`).
        
    3. Parse the file content. Based on snippet , look for delimiters like `// Question:`, `// Approach:`, and `// Code:`.
        
    4. Return a structured dictionary: `{'id': 'arrays_01', 'title': 'Set Matrix Zeroes', 'code': '...', 'approach': '...'}`.
        
- **Error Handling:** Skip files that do not match the expected format; log warnings for manual review.
    

#### 5.2.2. Module: `synthetic_data_gen`

**Function:** `generate_buggy_scenarios(correct_code, problem_desc)`

- **Goal:** Create the training/testing data for the Socratic agent.
    
- **Mechanism:** Use **Qwen2.5-Coder-7B** (via SiliconFlow) with a specialized system prompt.
    
    - _Prompt:_ "You are a chaotic coding engine. Rewrite the following C++ code to introduce a subtle {bug_type} error (e.g., Off-by-one, Missing Base Case). Return the result as JSON: {buggy_code, bug_description, fix_description}."
        
- **Output:** A dataset mirroring the `TreeInstruct` schema. This allows us to turn Striver's "Correct Code" repository into a "Debugging Challenge" repository.
    

#### 5.2.3. Module: `api_gateway` (The Volatility Shield)

**Class:** `FreeLLMClient`

- **Attributes:**
    
    - `providers`: List of provider configs (Base URL, API Key Env Var, Model Name).
        
    - `rate_limiters`: Dictionary mapping provider to a Token Bucket object.
        
- **Method:** `chat_completion(messages, temperature=0.2)`
    
    - **Logic:**
        
        1. Check the Token Bucket for the primary provider (SiliconFlow).
            
        2. If tokens available, dispatch request.
            
        3. If 429 received OR bucket empty, switch to secondary (OpenRouter).
            
        4. If OpenRouter fails, switch to tertiary (Groq - note: model mismatch risk, use only for simple tasks).
            
        5. Implement exponential backoff for retries.
            
- **Insight:** This module is the single most critical component for a "free tier" project. Without it, the application will be brittle and unusable in a real-world sprint.
    

#### 5.2.4. Module: `socratic_engine` (The Brain)

**Class:** `SocraticTutor`

- **State:** `{'student_code': str, 'history': list, 'phase': enum}`
    
- **Method:** `next_turn(student_input)`
    
    - **Step 1: Verification.** Run `verify_code(student_input)` using the `javascript-algorithms` test harness (if applicable) or a simplified output check.
        
    - **Step 2: Thought Trace.** Call LLM with `system_prompt_thought`.
        
        - _Prompt:_ "Analyze the student's input. Do not reply to them. Output JSON: {current_understanding: '...', misconception: '...', next_step: 'probe'|'guide'}."
            
    - **Step 3: Response Generation.** Call LLM with `system_prompt_speak`.
        
        - _Prompt:_ "You are a Socratic tutor. The student thinks X. Your goal is Y. Ask a question to guide them. DO NOT reveal the code."
            
    - **Step 4: Reflexion.** Call LLM with `system_prompt_critique`.
        
        - _Prompt:_ "Critique this response: '{response}'. Does it give the answer away? If yes, rewrite it."
            
    - **Return:** The final rewritten response.
        

### 5.3. Prompt Engineering: The "Reflexion" Pattern

To implement the Reflexion loop , we define specific templates.

**Template: The Critique**

You are a strict pedagogical reviewer.

[User]

I am a tutor helping a student fix an off-by-one error.

My proposed response is: "You need to change 'i <= n' to 'i < n' because arrays are 0-indexed."

Critique this response.

[Assistant]

Critique: This response is too direct. It is an "Oracle" response, not a Socratic one. It gives the solution immediately.

Refined Response: "Let's look at your loop condition. If the array has 5 elements, what is the index of the last element? And what index does your loop try to access?"

This pattern ensures that even if the base model (Qwen) slips into "completion mode," the architectural layer catches and corrects it before the user sees it.

## 6. Benchmarking Methodology: Pedagogical Efficacy

The Socratic Sprint rejects the standard "HumanEval Pass@1" metric. Getting the right answer instantly is a failure in our domain. We propose a "David vs. Goliath" benchmark focused on education.

### 6.1. The Contenders

- **David (The Challenger):** Qwen2.5-Coder-7B-Instruct (via SiliconFlow) + Socratic Architecture (Reflexion + State Management).
    
- **Goliath (The Baseline):** GPT-4o (via GitHub Models) operating 'As Is' (standard system prompt: "You are a helpful assistant").
    

### 6.2. Metrics

1. **Solution Revelation Score (SRS):**
    
    - _Definition:_ A measure of how much of the final code solution is revealed by the AI in the first 3 turns.
        
    - _Measurement:_ We calculate the Levenshtein distance between the AI's output and the correct code.
        
    - _Goal:_ David should have a _high_ distance (low revelation). Goliath is expected to have a _low_ distance (high revelation).
        
2. **Student Agency Ratio (SAR):**
    
    - _Definition:_ In a simulated conversation, what percentage of the code characters are typed by the Student vs. the AI?
        
    - _Goal:_ High SAR indicates the student is doing the work.
        
3. **Convergent Turn Count:**
    
    - _Definition:_ How many turns until the code passes all tests?
        
    - _Expectation:_ Goliath will minimize this (Efficiency). David will optimize for a specific range (e.g., 5-10 turns), indicating a healthy struggle.
        

### 6.3. Simulation Setup

To automate this, we will use **DeepSeek-V3** (via SiliconFlow) to act as a **Simulated Student**.

- **Student Prompt:** "You are a novice programmer. You have this buggy code. You do not know the fix. Ask the tutor for help. If the tutor gives you the answer, apply it. If the tutor asks a question, try to answer it incorrectly at first, then correct yourself."
    
- **The Arena:** We run 50 episodes where the Simulated Student talks to David, and 50 where it talks to Goliath. We record the logs and apply the metrics.
    

## 7. Implementation Plan

The following is the step-by-step execution plan for the Socratic Sprint.

### Phase 1: Infrastructure Setup (Days 1-3)

1. **API Key Provisioning:** Register for OpenRouter, SiliconFlow, and GitHub Models.
    
2. **Repository Cloning:** Clone `Strivers-A2Z-DSA-Sheet-C++` and `TreeInstruct`.
    
3. **Gateway Implementation:** Build `api_gateway.py` with the "Token Bucket" rate limiter to respect SiliconFlow's 1000 RPM / 50k TPM limits.
    

### Phase 2: Data Ingestion (Days 4-7)

1. **Scraper Development:** Implement `dsa_ingestion.py`. Target the "Arrays" and "Linked List" directories of Striver's sheet first.
    
2. **Synthetic Generation:** Run `synthetic_data_gen.py` to create 100 "Buggy Scenarios" from the scraped data. Store these in a JSON format matching `TreeInstruct`.
    

### Phase 3: The Socratic Engine (Days 8-14)

1. **Prompt Development:** Iteratively refine the Qwen2.5 system prompts. Test manually to ensure the model resists giving code blocks.
    
2. **State Manager:** Implement the logic to track conversation history and "hidden thoughts."
    
3. **Reflexion Loop:** Wire up the critique step. This effectively doubles the API calls per user turn, so verify the `api_gateway` handles the load.
    

### Phase 4: Benchmarking (Days 15-20)

1. **Simulator Build:** Create the `SimulatedStudent` agent using DeepSeek-V3.
    
2. **Execution:** Run the 50-episode batch against both David and Goliath.
    
3. **Analysis:** Parse the conversation logs to calculate SRS and SAR metrics.
    

## 8. Conclusion

The Socratic Sprint demonstrates that the democratization of AI education does not depend on access to the largest, most expensive models. By leveraging the specific strengths of **Qwen2.5-Coder-7B**—its code-specific training, generous context window, and widespread availability on free tiers—and augmenting them with an "On Architecture" design, we can create a tutor that is pedagogically superior to a raw GPT-4o instance.

The reliance on `cheahjs/free-llm-api-resources` proves that a robust, zero-cost infrastructure is viable, provided one engineers around the inherent volatility of the free tier. The "David" system does not beat "Goliath" at coding; it beats Goliath at _teaching_, proving that in the domain of human cognitive development, architectural agency is the true differentiator.

## 9. Appendix: Repository & Resource Reference

| **Resource**              | **Function**      | **Key Insight / Constraint**                           | **Source ID** |
| ------------------------- | ----------------- | ------------------------------------------------------ | ------------- |
| **cheahjs/free-llm-api**  | Infrastructure    | Aggregates all free providers; warns of volatility.    |               |
| **Strivers-A2Z-DSA**      | Data (Curriculum) | Standardized structure allows programmatic extraction. |               |
| **TreeInstruct**          | Data (Schema)     | Defines the JSON schema for multi-turn debugging.      |               |
| **javascript-algorithms** | Data (Verifier)   | Contains Jest tests for logic verification.            |               |
| **Qwen2.5-Coder-7B**      | Model (David)     | 32k context, free on OpenRouter/SiliconFlow.           |               |
| **SiliconFlow API**       | Provider          | Fixed RPM/TPM limits require Token Bucket.             |               |
| **GitHub Models**         | Provider          | Access to GPT-4o for baseline benchmarking.            |               |