import os, json, re
def clean_json(text):
    text=re.sub(r"^```(?:json)?\\s*","",text.strip(),flags=re.I)
    text=re.sub(r"\\s*```$","",text)
    return json.loads(text)
def validate_questions(items):
    out=[]
    for q in items:
        if isinstance(q,dict) and q.get("question") and isinstance(q.get("options"),list) and len(q["options"])==4 and q.get("answer") in q["options"]:
            out.append({"question":q["question"],"options":q["options"],"answer":q["answer"],"explanation":q.get("explanation","تفسير أكاديمي مستند إلى المصدر.")})
    return out
def generate_gemini(api_key, context, count=5):
    from google import genai
    client=genai.Client(api_key=api_key)
    prompt=f"""أنشئ {count} أسئلة اختيار من متعدد جامعية من المصدر فقط. 4 خيارات، answer يطابق الخيار حرفيًا، وexplanation يشرح الإجابة. لا تخترع معلومات. أعد JSON فقط بالشكل {{\"questions\":[{{\"question\":\"...\",\"options\":[\"a\",\"b\",\"c\",\"d\"],\"answer\":\"...\",\"explanation\":\"...\"}}]}}. المصدر:\n{context[:30000]}"""
    r=client.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"),contents=prompt)
    return validate_questions(clean_json(r.text)["questions"])
def generate_groq(api_key, context, count=5):
    from groq import Groq
    client=Groq(api_key=api_key)
    prompt=f"""Generate {count} MCQs using ONLY the source. Exactly 4 options. Return JSON only with questions, options, answer, explanation. Use Arabic when appropriate. SOURCE:\n{context[:30000]}"""
    r=client.chat.completions.create(model=os.getenv("GROQ_MODEL","llama-3.1-8b-instant"),messages=[{"role":"user","content":prompt}],temperature=.3,response_format={"type":"json_object"})
    return validate_questions(clean_json(r.choices[0].message.content)["questions"])
