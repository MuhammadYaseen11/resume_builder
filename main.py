import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import colorchooser
from fpdf import FPDF

class UKCVBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional UK CV Builder")
        self.root.geometry("1400x800")

        # Enhanced content storage with more detailed sections
        self.content = {
            'personal_info': {
                'full_name': '',
                'professional_title': '',
                'email': '',
                'phone': '',
                'address': '',
                'linkedin': '',
            },
            'profile_summary': '',
            'work_experience': [],
            'education': [],
            'skills': [],
            'languages': [],
            'achievements': []
        }

        # Create main UI
        self.create_ui()

    def create_ui(self):
        # Main layout with left input panel and right preview
        left_frame = tk.Frame(self.root, width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Notebook for different sections
        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        tabs = [
            ("Personal Info", self.create_personal_info_tab),
            ("Profile Summary", self.create_profile_summary_tab),
            ("Work Experience", self.create_work_experience_tab),
            ("Education", self.create_education_tab),
            ("Skills", self.create_skills_tab),
            ("Achievements", self.create_achievements_tab)
        ]

        for title, creator in tabs:
            tab = tk.Frame(notebook)
            notebook.add(tab, text=title)
            creator(tab)

        # Buttons Panel
        buttons_frame = tk.Frame(left_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        # Generate PDF Button
        generate_btn = tk.Button(buttons_frame, text="Generate PDF", command=self.generate_pdf)
        generate_btn.pack(side=tk.LEFT, expand=True, padx=5)

        # Preview Frame
        right_frame = tk.Frame(self.root, width=900)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Preview Label
        preview_label = tk.Label(right_frame, text="CV Preview", font=('Arial', 16, 'bold'))
        preview_label.pack(pady=10)

        # Preview Text Widget
        self.preview_text = tk.Text(right_frame, wrap=tk.WORD, font=('Arial', 12))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_personal_info_tab(self, frame):
        fields = [
            ('Full Name', 'full_name'),
            ('Professional Title', 'professional_title'),
            ('Email', 'email'),
            ('Phone', 'phone'),
            ('Full Address', 'address'),
            ('LinkedIn Profile', 'linkedin')
        ]

        for i, (label_text, key) in enumerate(fields):
            label = tk.Label(frame, text=label_text)
            label.grid(row=i, column=0, sticky='w', padx=5, pady=2)

            entry = tk.Entry(frame, width=50)
            entry.grid(row=i, column=1, padx=5, pady=2)

            entry.bind('<KeyRelease>', lambda e, k=key: self.update_content('personal_info', k, e))

    def create_profile_summary_tab(self, frame):
        label = tk.Label(frame, text="Professional Profile Summary:")
        label.pack(pady=5)

        self.summary_text = tk.Text(frame, height=6, width=50, wrap=tk.WORD)
        self.summary_text.pack(pady=5)

        save_btn = tk.Button(frame, text="Save Summary",
                             command=lambda: self.update_content('profile_summary', 'summary',
                                                                 self.summary_text))
        save_btn.pack(pady=5)

    def create_work_experience_tab(self, frame):
        # Company Name
        tk.Label(frame, text="Company Name:").pack()
        company_entry = tk.Entry(frame, width=50)
        company_entry.pack()

        # Job Title
        tk.Label(frame, text="Job Title:").pack()
        job_title_entry = tk.Entry(frame, width=50)
        job_title_entry.pack()

        # Dates
        date_frame = tk.Frame(frame)
        date_frame.pack(pady=5)
        tk.Label(date_frame, text="Start Date:").pack(side=tk.LEFT)
        start_date_entry = tk.Entry(date_frame, width=15)
        start_date_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(date_frame, text="End Date:").pack(side=tk.LEFT)
        end_date_entry = tk.Entry(date_frame, width=15)
        end_date_entry.pack(side=tk.LEFT)

        # Responsibilities
        tk.Label(frame, text="Key Responsibilities:").pack()
        responsibilities_text = tk.Text(frame, height=4, width=50, wrap=tk.WORD)
        responsibilities_text.pack()

        def add_experience():
            experience = {
                'company': company_entry.get(),
                'job_title': job_title_entry.get(),
                'start_date': start_date_entry.get(),
                'end_date': end_date_entry.get(),
                'responsibilities': responsibilities_text.get("1.0", tk.END).strip()
            }
            self.content['work_experience'].append(experience)

            # Clear entries
            for entry in [company_entry, job_title_entry, start_date_entry, end_date_entry]:
                entry.delete(0, tk.END)
            responsibilities_text.delete("1.0", tk.END)

            self.update_preview()

        add_btn = tk.Button(frame, text="Add Experience", command=add_experience)
        add_btn.pack(pady=5)

    def create_education_tab(self, frame):
        # Institution
        tk.Label(frame, text="Institution Name:").pack()
        institution_entry = tk.Entry(frame, width=50)
        institution_entry.pack()

        # Degree
        tk.Label(frame, text="Degree/Qualification:").pack()
        degree_entry = tk.Entry(frame, width=50)
        degree_entry.pack()

        # Graduation Date
        tk.Label(frame, text="Graduation Date:").pack()
        graduation_date_entry = tk.Entry(frame, width=50)
        graduation_date_entry.pack()

        # Additional Details
        tk.Label(frame, text="Additional Details:").pack()
        details_text = tk.Text(frame, height=4, width=50, wrap=tk.WORD)
        details_text.pack()

        def add_education():
            education = {
                'institution': institution_entry.get(),
                'degree': degree_entry.get(),
                'graduation_date': graduation_date_entry.get(),
                'details': details_text.get("1.0", tk.END).strip()
            }
            self.content['education'].append(education)

            # Clear entries
            for entry in [institution_entry, degree_entry, graduation_date_entry]:
                entry.delete(0, tk.END)
            details_text.delete("1.0", tk.END)

            self.update_preview()

        add_btn = tk.Button(frame, text="Add Education", command=add_education)
        add_btn.pack(pady=5)

    def create_skills_tab(self, frame):
        tk.Label(frame, text="Add Skills (Press Enter after each skill):").pack()

        skills_entry = tk.Entry(frame, width=50)
        skills_entry.pack()

        skills_listbox = tk.Listbox(frame, width=50, height=10)
        skills_listbox.pack(pady=5)

        def add_skill(event=None):
            skill = skills_entry.get().strip()
            if skill:
                skills_listbox.insert(tk.END, skill)
                skills_entry.delete(0, tk.END)
                self.content['skills'] = list(skills_listbox.get(0, tk.END))
                self.update_preview()

        def remove_skill():
            selected = skills_listbox.curselection()
            if selected:
                skills_listbox.delete(selected)
                self.content['skills'] = list(skills_listbox.get(0, tk.END))
                self.update_preview()

        skills_entry.bind('<Return>', add_skill)

        remove_btn = tk.Button(frame, text="Remove Selected Skill", command=remove_skill)
        remove_btn.pack(pady=5)

    def create_achievements_tab(self, frame):
        tk.Label(frame, text="Add Achievements:").pack()

        achievement_entry = tk.Entry(frame, width=50)
        achievement_entry.pack()

        achievements_listbox = tk.Listbox(frame, width=50, height=10)
        achievements_listbox.pack(pady=5)

        def add_achievement(event=None):
            achievement = achievement_entry.get().strip()
            if achievement:
                achievements_listbox.insert(tk.END, achievement)
                achievement_entry.delete(0, tk.END)
                self.content['achievements'] = list(achievements_listbox.get(0, tk.END))
                self.update_preview()

        def remove_achievement():
            selected = achievements_listbox.curselection()
            if selected:
                achievements_listbox.delete(selected)
                self.content['achievements'] = list(achievements_listbox.get(0, tk.END))
                self.update_preview()

        achievement_entry.bind('<Return>', add_achievement)

        remove_btn = tk.Button(frame, text="Remove Selected Achievement", command=remove_achievement)
        remove_btn.pack(pady=5)

    def update_content(self, section, key, event):
        if isinstance(event, tk.Event):
            value = event.widget.get()
        else:
            value = event.get("1.0", tk.END).strip()

        if section == 'personal_info':
            self.content['personal_info'][key] = value
        elif section == 'profile_summary':
            self.content[section] = value

        self.update_preview()

    def update_preview(self):
        self.preview_text.delete(1.0, tk.END)

        # Preview personal information
        personal_info = self.content['personal_info']
        self.preview_text.insert(tk.END, f"{personal_info['full_name']}\n")
        self.preview_text.insert(tk.END, f"{personal_info['professional_title']}\n")
        self.preview_text.insert(tk.END, f"Email: {personal_info['email']}\n")
        self.preview_text.insert(tk.END, f"Phone: {personal_info['phone']}\n")
        self.preview_text.insert(tk.END, f"Address: {personal_info['address']}\n")
        self.preview_text.insert(tk.END, f"LinkedIn: {personal_info['linkedin']}\n\n")

        # Preview Profile Summary
        self.preview_text.insert(tk.END, "Profile Summary:\n")
        self.preview_text.insert(tk.END, self.content['profile_summary'] + "\n\n")

        # Preview Work Experience
        self.preview_text.insert(tk.END, "Work Experience:\n")
        for exp in self.content['work_experience']:
            self.preview_text.insert(tk.END, f"{exp['job_title']} at {exp['company']}\n")
            self.preview_text.insert(tk.END, f"{exp['start_date']} - {exp['end_date']}\n")
            self.preview_text.insert(tk.END, f"Responsibilities: {exp['responsibilities']}\n\n")

        # Preview Education
        self.preview_text.insert(tk.END, "Education:\n")
        for edu in self.content['education']:
            self.preview_text.insert(tk.END, f"{edu['degree']} from {edu['institution']}\n")
            self.preview_text.insert(tk.END, f"Graduated: {edu['graduation_date']}\n")
            self.preview_text.insert(tk.END, f"Details: {edu['details']}\n\n")

        # Preview Skills
        self.preview_text.insert(tk.END, "Skills:\n")
        for skill in self.content['skills']:
            self.preview_text.insert(tk.END, f"{skill}\n")

        # Preview Achievements
        self.preview_text.insert(tk.END, "Achievements:\n")
        for achievement in self.content['achievements']:
            self.preview_text.insert(tk.END, f"{achievement}\n")

    def generate_pdf(self):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Adding title and personal information
        personal_info = self.content['personal_info']
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, txt=personal_info['full_name'], ln=True, align='C')
        pdf.set_font('Arial', 'I', 12)
        pdf.cell(200, 10, txt=personal_info['professional_title'], ln=True, align='C')
        pdf.ln(10)
        pdf.set_font('Arial', '', 12)

        # Adding email, phone, and LinkedIn
        pdf.cell(200, 10, f"Email: {personal_info['email']}", ln=True)
        pdf.cell(200, 10, f"Phone: {personal_info['phone']}", ln=True)
        pdf.cell(200, 10, f"LinkedIn: {personal_info['linkedin']}", ln=True)
        pdf.cell(200, 10, f"Address: {personal_info['address']}", ln=True)
        pdf.ln(10)

        # Adding Profile Summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, "Profile Summary", ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, self.content['profile_summary'])
        pdf.ln(10)

        # Adding Work Experience
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, "Work Experience", ln=True)
        pdf.set_font('Arial', '', 12)
        for exp in self.content['work_experience']:
            pdf.cell(200, 10, f"{exp['job_title']} at {exp['company']}", ln=True)
            pdf.cell(200, 10, f"{exp['start_date']} - {exp['end_date']}", ln=True)
            pdf.multi_cell(0, 10, f"Responsibilities: {exp['responsibilities']}")
            pdf.ln(5)

        # Adding Education
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, "Education", ln=True)
        pdf.set_font('Arial', '', 12)
        for edu in self.content['education']:
            pdf.cell(200, 10, f"{edu['degree']} from {edu['institution']}", ln=True)
            pdf.cell(200, 10, f"Graduated: {edu['graduation_date']}", ln=True)
            pdf.multi_cell(0, 10, f"Details: {edu['details']}")
            pdf.ln(5)

        # Adding Skills
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, "Skills", ln=True)
        pdf.set_font('Arial', '', 12)
        for skill in self.content['skills']:
            pdf.cell(200, 10, skill, ln=True)
        pdf.ln(5)

        # Adding Achievements
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, "Achievements", ln=True)
        pdf.set_font('Arial', '', 12)
        for achievement in self.content['achievements']:
            pdf.cell(200, 10, achievement, ln=True)

        # Saving PDF to file
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf.output(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = UKCVBuilder(root)
    root.mainloop()
