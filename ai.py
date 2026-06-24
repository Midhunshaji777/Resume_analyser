import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError


load_dotenv()

client = genai.Client()

def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a senior software engineer and hiring manager.

evaluate the resume based on the user's goal.

User goal = {user_goal}

STRICT RULES:

-Extract only relavant skills for this goal.
-REMOVE irrelavant tools [excel for backend, etc]
-Identify real gaps
-Generate roadmap only for missing fields.
-MAKE output different based on goal
-Make the result in good formatting by removing special characters,for good visiblilty and understanding

Return only JSON
{{
"skills": [],
"missing_skills": [],
"roadmap": [],
"interview_questions": []

}}

Resume:
{resume_text}
    
"""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )

            content = response.text.strip()

            start = content.find("{")
            end = content.rfind("}") + 1

            if start != -1 and end != 0:
                return json.loads(content[start:end])
            else:
                return json.loads(content)
        except APIError as e:
            print(f"Server busy (Status Code: {e.code}). Attempt {attempt + 1} failed. Retrying...")
            if attempt == 2:
                break
            time.sleep(2)
        except Exception:
            if attempt == 2:
                break
            time.sleep(1)

    return {
        "skills": [],
        "missing_skills": [],
        "roadmap": [],
        "interview_questions": [],
        "error": "The AI service is currently busy. Please try again in a few moments."
    }
    