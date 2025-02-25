import sys
import os
import json
from pathlib import Path
from llama_cpp import Llama
from jinja2 import Environment, FileSystemLoader

def load_model():
    return Llama(
        model_path="models/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
        n_gpu_layers=20, 
        n_ctx=128000,
        n_threads=8,
        n_threads_batch=16,
        n_batch = 256,
        offload_kqv=True,      # Offload attention matrices to CPU
        main_gpu=0,           # Explicitly use primary GPU
        tensor_split=[0.9]     # Reserve 10% VRAM headroom
    )

def latex_escape(text):
    escapes = {
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '&': r'\&'
    }
    return ''.join(escapes.get(c, c) for c in str(text))

def process_job_description(model, job_desc, user_context):
    prompt = f"""
    Analyze this job description: {job_desc}
    
    User Background:
    - Personal Information: {user_context['personal_info']}
    - Experiences: {user_context['experiences']}
    - Projects: {user_context['projects']}
    - Skills: {user_context['skills']}
    - Achievements: {user_context['achievements']}
    
    Task:
    4. Format output as JSON matching this structure:
       {{
        "personal_info": {{
            "name": "<Full Name>",
            "phone": "<Phone with Country Code>",
            "email": "<professional.email@domain.com>",
            "roll_number": "<University ID>",
            "degree": "<Degree Name>",
            "university": "<University Name, City>",
            "github_url": "<https://github.com/username>",
            "github_display": "<GitHub Profile>",
            "linkedin_url": "<https://linkedin.com/in/username>",
            "linkedin_display": "<LinkedIn Profile>"
        }},
        "education": [
            {{
            "title": "<Degree Title> (e.g.: B.Tech Computer Science)",
            "right_bottom": "<Metrics> (e.g.: GPA: 3.8/4.0)",
            "left_bottom": "<Institution Details> (e.g.: MIT, Cambridge MA)",
            "right_top": "<Date Range> (e.g.: 2020-2024)"
            }}
        ],
        "projects": [
            {{
            "title": "<Project Name>",
            "subtitle": "<Brief Context> (e.g.: AI-Powered Document Analyzer)",
            "dates_top_right": "<Duration> (e.g.: Jan-Apr 2023)",
            "details_bottom_right": "<Technical Specs> (e.g.: Python, PyTorch)",
            "description": [
                "<Quantified Achievement> (e.g.: Reduced processing time by 40%)",
                "<Technical Detail> (e.g.: Implemented transformer model)"
            ]
            }}
        ],
        "experience": [
            {{
            "title": "<Role> (e.g.: Cloud Engineering Intern)",
            "right_bottom": "<Location/Type> (e.g.: Remote)",
            "left_bottom": "<Company> (e.g.: Google Cloud)",
            "right_top": "<Dates> (e.g.: Summer 2023)",
            "description": [
                "<Impactful Verb> + <Metric> (e.g.: Optimized AWS costs by $12k/year)",
                "<Technical Scope> (e.g.: Migrated 50+ EC2 instances)"
            ]
            }}
        ],
        "skills": [
            {{
            "category": "<Category> (e.g.: Languages)",
            "items": "<Comma-Separated List> (e.g.: Python, Java)"
            }}
        ],
        "por_items": [
            {{
            "title": "<Position> (e.g.: Event Coordinator)",
            "organization": "<Organization> (e.g.: ACM Student Chapter)",
            "dates": "<Dates> (e.g.: Fall 2022)",
            "description": [
                "<Action + Result> (e.g.: Organized hackathon with 200+ participants)"
            ]
            }}
        ]
        }}

    Rules:
    - Prioritize technical keywords from job description
    - Quantify achievements where possible
    - Provide well worded descriptions that are concise, using active verbs
    - The user may have provided more experience than necessary, only use what is most relevant, aiming for 2-3 recent and relevant work experiences and 2 relevant projects
    """

    print("PROMPT: ", prompt)
    
    response = model.create_chat_completion(
        messages=[{"role": "user", "content": prompt}]
    )

    print("RESPONSE:", response)

    return response['choices'][0]['message']['content']

def extract_json(response: str) -> dict:
    """Extract first valid JSON from markdown response"""
    import re
    
    # Find JSON code block
    match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)
    
    # Fallback: Find outermost JSON
    start = response.find('{')
    end = response.rfind('}') + 1
    return json.loads(response[start:end])

def parse_llm_output(llm_output):
    try:
        # Extract clean JSON
        clean_data = extract_json(llm_output)
        
        # Validate structure
        required = ['personal_info', 'education', 'experience']
        for section in required:
            if section not in clean_data:
                raise ValueError(f"Missing {section}")
                
        return clean_data
    except Exception as e:
        print(f"Parse Error: {e}")
        return {}


def generate_resume_content(model, job_desc, user_context):
    raw_output = process_job_description(model, job_desc, user_context)
    parsed = parse_llm_output(raw_output)
    
    # Merge with base template
    with open('templates/data.json') as f:
        base = json.load(f)
        
    return {**base, **parsed}  # Base ensures required fields

def render_template(data):
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['latex_escape'] = latex_escape
    template = env.get_template('resume_template.tex')
    return template.render(data)

def compile_latex(latex_content, output_dir="data/output"):
    os.makedirs(output_dir, exist_ok=True)
    tex_path = Path(output_dir) / "resume.tex"
    pdf_path = tex_path.with_suffix('.pdf')
    
    with open(tex_path, 'w') as f:
        f.write(latex_content)
    
    os.system(f"pdflatex -output-directory {output_dir} {tex_path}")
    return pdf_path

def main():
    model = load_model()
    
    # if len(sys.argv) < 2:
    #     print("Usage: python main.py <job_description_file>")
    #     return
    
    # input_path = Path(sys.argv[1])
    # if not input_path.exists():
    #     print(f"File {input_path} not found")
    #     return
    
    # with open(input_path, 'r') as f:
    #     job_desc = f.read()
    
    # resume_data = generate_resume_content(model, job_desc)

    with open('data/input/user_context.json') as f:
        user_context = json.load(f)

    with open('data/input/job_description.txt') as f:
        job_desc = f.read()

    # with open ('templates/data.json') as f:
    #     resume_data = json.load(f)

    resume_data = generate_resume_content(model, job_desc, user_context)
    latex_content = render_template(resume_data)
    output_pdf = compile_latex(latex_content)
    
    print(f"Resume generated at: {output_pdf}")

if __name__ == "__main__":
    main()