import sys
import os
from pathlib import Path
from llama_cpp import Llama
from jinja2 import Environment, FileSystemLoader

def load_model():
    return Llama(
        model_path="models/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
        n_ctx=2048,
        n_threads=4
    )

def process_job_description(model, job_desc):
    response = model.create_chat_completion(
        messages=[{
            "role": "user",
            "content": f"Analyze this job description: {job_desc}. Extract key skills, experience, and achievements."
        }]
    )
    return response['choices'][0]['message']['content']

def parse_llm_output(llm_output):
    sections = {"skills": [], "experience": [], "achievements": []}
    current_section = None
    
    for line in llm_output.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.lower() in ['skills:', 'experience:', 'achievements:']:
            current_section = line.lower().replace(':', '')
        elif current_section and current_section in sections:
            sections[current_section].append(line)
    
    return sections

def generate_resume_content(model, job_desc):
    llm_output = process_job_description(model, job_desc)
    return {
        "resume_title": "AI-Tailored Resume",
        "resume_author": "Your Name",
        **parse_llm_output(llm_output)
    }

def render_template(data):
    env = Environment(loader=FileSystemLoader('templates'))
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
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <job_description_file>")
        return
    
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"File {input_path} not found")
        return
    
    with open(input_path, 'r') as f:
        job_desc = f.read()
    
    resume_data = generate_resume_content(model, job_desc)
    latex_content = render_template(resume_data)
    output_pdf = compile_latex(latex_content)
    
    print(f"Resume generated at: {output_pdf}")

if __name__ == "__main__":
    main()
