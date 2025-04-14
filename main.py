import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
import json
import os
from datetime import datetime
import sys
# Save Personal Info

class DrawingCanvas:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg="white", width=800, height=1000, scrollregion=(0, 0, 800, 1000))
        
        # Add scrollbars
        self.v_scrollbar = tk.Scrollbar(parent, orient='vertical', command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(parent, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Draggable elements storage
        self.draggable_items = {}
        self.current_drag = None
        self.drag_start_pos = (0, 0)
        
        # Bind events for dragging
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<Double-Button-1>", self.start_edit)

    def start_drag(self, event):
        # Find which item is being clicked
        item = self.canvas.find_closest(event.x, event.y)
        if item:
            self.current_drag = item[0]
            self.drag_start_pos = (event.x, event.y)
            
    def on_drag(self, event):
        if self.current_drag:
            # Calculate movement
            dx = event.x - self.drag_start_pos[0]
            dy = event.y - self.drag_start_pos[1]
            
            # Move the item
            self.canvas.move(self.current_drag, dx, dy)
            
            # Update start position for next movement
            self.drag_start_pos = (event.x, event.y)
            
    def stop_drag(self, event):
        self.current_drag = None
        
    def start_edit(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            return
            
        item_id = item[0]
        item_type = self.canvas.type(item_id)
        
        if item_type == "text":
            # Get current text
            current_text = self.canvas.itemcget(item_id, "text")
            
            # Get position and font
            coords = self.canvas.coords(item_id)
            font = self.canvas.itemcget(item_id, "font")
            fill = self.canvas.itemcget(item_id, "fill")
            
            # Create editable entry widget
            entry = tk.Entry(self.canvas, font=font, bg="white", fg=fill, 
                           borderwidth=0, highlightthickness=1)
            entry.insert(0, current_text)
            entry.bind("<Return>", lambda e, i=item_id: self.finish_edit(e, i))
            entry.bind("<FocusOut>", lambda e, i=item_id: self.finish_edit(e, i))
            
            # Place entry over the text
            entry_window = self.canvas.create_window(coords[0], coords[1], 
                                                   anchor="nw", window=entry)
            
            # Focus and select all text
            entry.focus_set()
            entry.select_range(0, tk.END)
            
            # Store reference
            self.edit_data = {
                'item_id': item_id,
                'entry': entry,
                'window_id': entry_window
            }
            
    def finish_edit(self, event, item_id):
        if hasattr(self, 'edit_data'):
            new_text = self.edit_data['entry'].get()
            
            # Update the canvas text
            self.canvas.itemconfig(item_id, text=new_text)
            
            # Remove the entry widget
            self.canvas.delete(self.edit_data['window_id'])
            del self.edit_data
            
    def update_preview(self, content):
        self.canvas.delete("all")
        self.draggable_items = {}
        
        # Render content with better formatting
        y_position = 20
        for section, details in content.items():
            # Section header
            section_id = self.canvas.create_text(20, y_position, anchor="nw", 
                                    text=section.replace('_', ' ').title(), 
                                    font=("Arial", 14, "bold"), fill="navy",
                                    tags=("draggable", "section_header"))
            self.draggable_items[section_id] = {'type': 'section_header', 'section': section}
            y_position += 30

            # Render different types of content
            if section == 'personal_info':
                for key, value in details.items():
                    if value:  # Only show if not empty
                        item_id = self.canvas.create_text(20, y_position, 
                                                anchor="nw", 
                                                text=f"{key.replace('_', ' ').title()}: {value}", 
                                                font=("Arial", 12), fill="black",
                                                tags=("draggable", "personal_info"))
                        self.draggable_items[item_id] = {'type': 'personal_info', 'key': key}
                        y_position += 25
            elif isinstance(details, list):
                for item in details:
                    item_id = self.canvas.create_text(20, y_position, 
                                            anchor="nw", 
                                            text=str(item), 
                                            font=("Arial", 12), fill="black",
                                            tags=("draggable", "list_item"))
                    self.draggable_items[item_id] = {'type': 'list_item', 'section': section}
                    y_position += 25
            else:
                # For text fields like profile summary
                item_id = self.canvas.create_text(20, y_position, 
                                        anchor="nw", 
                                        text=str(details), 
                                        font=("Arial", 12), fill="black", 
                                        width=760,  # Wider text area
                                        tags=("draggable", "text_block"))
                self.draggable_items[item_id] = {'type': 'text_block', 'section': section}
                y_position += 50

            y_position += 20  # Space between sections

        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class UKCVBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Professional UK CV Builder")
        self.root.geometry("1200x800")  # Adjust dimensions as needed
        self.root.config(bg="#f0f0f0")

        # Main layout with left input panel and right preview
        left_frame = tk.Frame(self.root, width=600, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Notebook for different sections
        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Content storage
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

        # Create tabs 
        tabs = [
            ("Personal Info", self.create_personal_info_tab),
            ("Profile Summary", self.create_profile_summary_tab),
            ("Work Experience", self.create_work_experience_tab),
            ("Education", self.create_education_tab),
            ("Skills", self.create_skills_tab),
            ("Achievements", self.create_achievements_tab),
        ]

        for title, creator in tabs:
            tab = tk.Frame(notebook, bg="#f0f0f0")
            notebook.add(tab, text=title)
            creator(tab)

        # Right frame for interactive canvas
        right_frame = tk.Frame(self.root, bg="lightblue")  # Temporary color for debugging
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create drawing canvas
        self.drawing_canvas = DrawingCanvas(right_frame)

        # Button frame
        button_frame = tk.Frame(right_frame, bg="lightgreen")  # Temporary color for debugging
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Buttons
        generate_pdf_btn = tk.Button(button_frame, text="Save as PDF", command=self.generate_pdf, 
                              bg="#4CAF50", fg="white", font=("Arial", 12), padx=20)
        generate_pdf_btn.pack(side=tk.LEFT, padx=10)

        save_btn = tk.Button(button_frame, text="Save CV Data", command=self.save_cv_data, 
                           bg="#2196F3", fg="white", font=("Arial", 12), padx=20)
        save_btn.pack(side=tk.LEFT, padx=10)

        load_btn = tk.Button(button_frame, text="Load CV Data", command=self.load_cv_data, 
                           bg="#FF9800", fg="white", font=("Arial", 12), padx=20)
        load_btn.pack(side=tk.LEFT, padx=10)

        # Add a refresh button to update the preview
        refresh_btn = tk.Button(button_frame, text="Refresh Preview", command=self.refresh_preview,
                              bg="#9C27B0", fg="white", font=("Arial", 12), padx=20)
        refresh_btn.pack(side=tk.LEFT, padx=10)

        # Add padding to ensure visibility
        button_frame.pack_propagate(False)
        button_frame.config(height=50)  # Adjust height if needed

    def refresh_preview(self):
        """Force a refresh of the preview canvas"""
        self.drawing_canvas.update_preview(self.content)

    def create_personal_info_tab(self, tab):
        tk.Label(tab, text="Full Name", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.full_name_entry = tk.Entry(tab, font=("Arial", 12), width=40)
        self.full_name_entry.pack(pady=5)

        tk.Label(tab, text="Professional Title", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.professional_title_entry = tk.Entry(tab, font=("Arial", 12), width=40)
        self.professional_title_entry.pack(pady=5)

        tk.Label(tab, text="Email", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.email_entry = tk.Entry(tab, font=("Arial", 12), width=40)
        self.email_entry.pack(pady=5)

        tk.Label(tab, text="Phone", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.phone_entry = tk.Entry(tab, font=("Arial", 12), width=40)
        self.phone_entry.pack(pady=5)

        tk.Label(tab, text="Address", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.address_entry = tk.Entry(tab, font=("Arial", 12), width=40)
        self.address_entry.pack(pady=5)

        tk.Label(tab, text="LinkedIn", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.linkedin_entry = tk.Entry(tab, font=("Arial", 12), width=40)
        self.linkedin_entry.pack(pady=5)

        save_button = tk.Button(tab, text="Save Personal Info", command=self.save_personal_info, 
                              bg="#4CAF50", fg="white", font=("Arial", 12))
        save_button.pack(pady=20)

    def save_personal_info(self):
        self.content['personal_info'] = {
            'full_name': self.full_name_entry.get(),
            'professional_title': self.professional_title_entry.get(),
            'email': self.email_entry.get(),
            'phone': self.phone_entry.get(),
            'address': self.address_entry.get(),
            'linkedin': self.linkedin_entry.get(),
        }
        messagebox.showinfo("Success", "Personal Info saved successfully!")
        self.drawing_canvas.update_preview(self.content)

    def create_profile_summary_tab(self, tab):
        tk.Label(tab, text="Profile Summary", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.profile_summary_text = tk.Text(tab, height=15, width=60, font=("Arial", 12), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(tab, command=self.profile_summary_text.yview)
        self.profile_summary_text.configure(yscrollcommand=scrollbar.set)
        self.profile_summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        save_button = tk.Button(tab, text="Save Profile Summary", command=self.save_profile_summary, 
                              bg="#4CAF50", fg="white", font=("Arial", 12))
        save_button.pack(pady=20)

    def save_profile_summary(self):
        self.content['profile_summary'] = self.profile_summary_text.get("1.0", tk.END).strip()
        messagebox.showinfo("Success", "Profile Summary saved successfully!")
        self.drawing_canvas.update_preview(self.content)

    def create_work_experience_tab(self, tab):
        tk.Label(tab, text="Work Experience (one per line)", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.work_experience_text = tk.Text(tab, height=15, width=60, font=("Arial", 12), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(tab, command=self.work_experience_text.yview)
        self.work_experience_text.configure(yscrollcommand=scrollbar.set)
        self.work_experience_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        save_button = tk.Button(tab, text="Save Work Experience", command=self.save_work_experience, 
                              bg="#4CAF50", fg="white", font=("Arial", 12))
        save_button.pack(pady=20)

    def save_work_experience(self):
        self.content['work_experience'] = self.work_experience_text.get("1.0", tk.END).strip().split('\n')
        messagebox.showinfo("Success", "Work Experience saved successfully!")
        self.drawing_canvas.update_preview(self.content)

    def create_education_tab(self, tab):
        tk.Label(tab, text="Education (one per line)", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.education_text = tk.Text(tab, height=15, width=60, font=("Arial", 12), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(tab, command=self.education_text.yview)
        self.education_text.configure(yscrollcommand=scrollbar.set)
        self.education_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        save_button = tk.Button(tab, text="Save Education", command=self.save_education, 
                              bg="#4CAF50", fg="white", font=("Arial", 12))
        save_button.pack(pady=20)

    def save_education(self):
        self.content['education'] = self.education_text.get("1.0", tk.END).strip().split('\n')
        messagebox.showinfo("Success", "Education saved successfully!")
        self.drawing_canvas.update_preview(self.content)

    def create_skills_tab(self, tab):
        tk.Label(tab, text="Skills (one per line)", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.skills_text = tk.Text(tab, height=15, width=60, font=("Arial", 12), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(tab, command=self.skills_text.yview)
        self.skills_text.configure(yscrollcommand=scrollbar.set)
        self.skills_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        save_button = tk.Button(tab, text="Save Skills", command=self.save_skills, 
                              bg="#4CAF50", fg="white", font=("Arial", 12))
        save_button.pack(pady=20)

    def save_skills(self):
        self.content['skills'] = self.skills_text.get("1.0", tk.END).strip().split('\n')
        messagebox.showinfo("Success", "Skills saved successfully!")
        self.drawing_canvas.update_preview(self.content)

    def create_achievements_tab(self, tab):
        tk.Label(tab, text="Achievements (one per line)", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
        self.achievements_text = tk.Text(tab, height=15, width=60, font=("Arial", 12), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(tab, command=self.achievements_text.yview)
        self.achievements_text.configure(yscrollcommand=scrollbar.set)
        self.achievements_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        save_button = tk.Button(tab, text="Save Achievements", command=self.save_achievements, 
                              bg="#4CAF50", fg="white", font=("Arial", 12))
        save_button.pack(pady=20)

    def save_achievements(self):
        self.content['achievements'] = self.achievements_text.get("1.0", tk.END).strip().split('\n')
        messagebox.showinfo("Success", "Achievements saved successfully!")
        self.drawing_canvas.update_preview(self.content)

    def save_cv_data(self):
        """Save CV data to a JSON file"""
        filename = filedialog.asksaveasfilename(defaultextension=".json", 
                                              filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.content, f, indent=4)
                messagebox.showinfo("Success", f"CV data saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def load_cv_data(self):
        """Load CV data from a JSON file"""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    loaded_content = json.load(f)
                
                # Update content and UI elements
                self.content = loaded_content
                
                # Update Personal Info entries
                personal_info = loaded_content.get('personal_info', {})
                self.full_name_entry.delete(0, tk.END)
                self.full_name_entry.insert(0, personal_info.get('full_name', ''))
                self.professional_title_entry.delete(0, tk.END)
                self.professional_title_entry.insert(0, personal_info.get('professional_title', ''))
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, personal_info.get('email', ''))
                self.phone_entry.delete(0, tk.END)
                self.phone_entry.insert(0, personal_info.get('phone', ''))
                self.address_entry.delete(0, tk.END)
                self.address_entry.insert(0, personal_info.get('address', ''))
                self.linkedin_entry.delete(0, tk.END)
                self.linkedin_entry.insert(0, personal_info.get('linkedin', ''))

                # Update text fields
                self.profile_summary_text.delete('1.0', tk.END)
                self.profile_summary_text.insert('1.0', loaded_content.get('profile_summary', ''))
                
                self.work_experience_text.delete('1.0', tk.END)
                self.work_experience_text.insert('1.0', '\n'.join(loaded_content.get('work_experience', [])))
                
                self.education_text.delete('1.0', tk.END)
                self.education_text.insert('1.0', '\n'.join(loaded_content.get('education', [])))
                
                self.skills_text.delete('1.0', tk.END)
                self.skills_text.insert('1.0', '\n'.join(loaded_content.get('skills', [])))
                
                self.achievements_text.delete('1.0', tk.END)
                self.achievements_text.insert('1.0', '\n'.join(loaded_content.get('achievements', [])))

                # Update preview
                self.drawing_canvas.update_preview(self.content)
                
                messagebox.showinfo("Success", f"CV data loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {e}")

    def generate_pdf(self):
        """Enhanced PDF generation with more robust formatting"""
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = self.content['personal_info']['full_name'].replace(' ', '_') if self.content['personal_info']['full_name'] else "CV"
        default_filename = f"{name}_{timestamp}.pdf"
        filename = os.path.join(output_dir, default_filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Personal Info Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, txt=self.content['personal_info']['full_name'], ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=self.content['personal_info']['professional_title'], ln=True, align='C')
        
        pdf.ln(5)
        pdf.cell(0, 10, txt=f"Email: {self.content['personal_info']['email']} | "
                             f"Phone: {self.content['personal_info']['phone']}", ln=True, align='C')
        pdf.cell(0, 10, txt=f"Address: {self.content['personal_info']['address']} | "
                             f"LinkedIn: {self.content['personal_info']['linkedin']}", ln=True, align='C')

        pdf.ln(10)

        # Sections with bold headers
        sections = [
            ('Profile Summary', 'profile_summary'),
            ('Work Experience', 'work_experience'),
            ('Education', 'education'),
            ('Skills', 'skills'),
            ('Achievements', 'achievements')
        ]

        for header, key in sections:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, txt=header, ln=True)
            pdf.set_font("Arial", size=12)
            
            # Handle different content types
            if key == 'profile_summary':
                pdf.multi_cell(0, 10, txt=str(self.content[key]))
            else:
                # For list-type sections
                content = self.content[key]
                if isinstance(content, list):
                    for item in content:
                        pdf.multi_cell(0, 10, txt=str(item))
                else:
                    pdf.multi_cell(0, 10, txt=str(content))
            
            pdf.ln(5)

        try:
            pdf.output(filename)
            messagebox.showinfo("Success", f"CV saved as:\n{filename}")
            
            # Try to open the PDF automatically
            try:
                if os.name == 'nt':  # For Windows
                    os.startfile(filename)
                elif os.name == 'posix':  # For macOS and Linux
                    os.system(f'open "{filename}"' if sys.platform == 'darwin' else f'xdg-open "{filename}"')
            except:
                pass  # If opening fails, just continue
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PDF: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UKCVBuilder(root)
    root.mainloop()