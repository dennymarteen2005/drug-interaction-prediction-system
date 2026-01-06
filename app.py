import tkinter as tk
from tkinter import messagebox, filedialog
import pickle
import pandas as pd
import threading
import time
import os
import sys
import winsound
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from nlp_utils import extract_drugs

# ---------------- RESOURCE PATH (EXE SAFE) ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------- LOAD MODEL & DATA ----------------
with open(resource_path("model/interaction_model.pkl"), "rb") as f:
    model, vectorizer, label_encoder = pickle.load(f)

interaction_df = pd.read_csv(resource_path("data/drug_interactions.csv"))
recommendation_df = pd.read_csv(resource_path("data/drug_recommendations.csv"))

all_drugs = interaction_df["drug1"].tolist() + interaction_df["drug2"].tolist()

# ---------------- THEMES ----------------
LIGHT = {"bg": "#eef2ff", "card": "white", "text": "#111827"}
DARK = {"bg": "#020617", "card": "#020617", "text": "white"}
current_theme = LIGHT

# ---------------- TYPING EFFECT ----------------
def type_line(text, tag=None):
    for ch in text:
        output.insert(tk.END, ch, tag)
        output.update()
        time.sleep(0.008)
    output.insert(tk.END, "\n")
    output.see(tk.END)

# ---------------- EXPORT PDF ----------------
def export_pdf():
    content = output.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("No Data", "No result to export.")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not path:
        return

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 40

    for line in content.split("\n"):
        c.drawString(40, y, line)
        y -= 14
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
    messagebox.showinfo("Success", "PDF exported successfully.")
    os.startfile(path)

# ---------------- ANALYZE FUNCTION ----------------
def analyze():
    def task():
        output.config(state="normal")
        output.delete("1.0", tk.END)

        type_line("🔍 Analyzing drug interactions...\n", "info")

        text = input_box.get("1.0", tk.END).strip()
        drugs = extract_drugs(text, all_drugs)

        if len(drugs) < 2:
            type_line("❗ Please enter at least two known medicines.", "error")
            return

        type_line(f"✅ Detected Drugs: {', '.join(drugs)}\n", "header")

        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                pair = drugs[i] + " " + drugs[j]
                X = vectorizer.transform([pair])
                probs = model.predict_proba(X)[0]
                idx = probs.argmax()
                severity = label_encoder.inverse_transform([idx])[0]
                confidence = round(probs[idx] * 100, 2)

                if severity == "mild":
                    color_tag = "mild"
                    desc = "🟢 Mild – Usually safe."
                elif severity == "moderate":
                    color_tag = "moderate"
                    desc = "🟠 Moderate – Caution required."
                else:
                    color_tag = "severe"
                    desc = "🔴 Severe – Avoid combination."
                    winsound.Beep(1200, 600)

                type_line(f"💊 {drugs[i]} + {drugs[j]}", "bold")
                output.insert(tk.END, f"Severity: {severity.upper()} ({confidence}%)\n", color_tag)
                type_line(desc, color_tag)

                if severity in ["moderate", "severe"]:
                    alt = recommendation_df[recommendation_df["drug"] == drugs[j]]
                    if not alt.empty:
                        type_line(f"✅ Safer Alternative: {alt['alternative'].values[0]}", "alt")

                type_line("─" * 60)
                time.sleep(0.3)

        output.config(state="disabled")

    threading.Thread(target=task).start()

# ---------------- TOGGLE THEME ----------------
def toggle_theme():
    global current_theme
    current_theme = DARK if current_theme == LIGHT else LIGHT
    root.configure(bg=current_theme["bg"])
    left_panel.configure(bg=current_theme["card"])
    right_panel.configure(bg=current_theme["card"])

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Drug Interaction Detection System")
root.geometry("1100x720")
root.configure(bg=current_theme["bg"])

# Header
header = tk.Frame(root, bg="#4f46e5", height=70)
header.pack(fill="x")
tk.Label(
    header,
    text="Drug Interaction Detection & Recommendation",
    bg="#4f46e5",
    fg="white",
    font=("Segoe UI", 18, "bold")
).pack(pady=18)

# Main container
main_container = tk.Frame(root, bg=current_theme["bg"])
main_container.pack(fill="both", expand=True, padx=20, pady=15)

# ---------------- LEFT PANEL ----------------
left_panel = tk.Frame(main_container, bg=current_theme["card"], width=330)
left_panel.pack(side="left", fill="y", padx=(0, 15))
left_panel.pack_propagate(False)

tk.Label(left_panel, text="How to Use", font=("Segoe UI", 11, "bold"), bg=current_theme["card"]).pack(anchor="w", padx=10, pady=(10, 2))
tk.Label(
    left_panel,
    text="• Enter medicine names in plain English\n"
         "• Example: I am taking paracetamol and aspirin",
    justify="left",
    bg=current_theme["card"],
    font=("Segoe UI", 10)
).pack(anchor="w", padx=10)

tk.Label(left_panel, text="Severity Legend", font=("Segoe UI", 11, "bold"), bg=current_theme["card"]).pack(anchor="w", padx=10, pady=(10, 2))
tk.Label(
    left_panel,
    text="🟢 Mild → Usually safe\n"
         "🟠 Moderate → Monitoring needed\n"
         "🔴 Severe → Avoid combination",
    justify="left",
    bg=current_theme["card"],
    font=("Segoe UI", 10)
).pack(anchor="w", padx=10)

tk.Label(left_panel, text="Enter medicines:", font=("Segoe UI", 11, "bold"), bg=current_theme["card"]).pack(anchor="w", padx=10, pady=(15, 2))

input_box = tk.Text(left_panel, height=5, font=("Segoe UI", 11))
input_box.pack(padx=10, fill="x")

tk.Button(
    left_panel,
    text="Analyze Interactions",
    bg="#4f46e5",
    fg="white",
    font=("Segoe UI", 11, "bold"),
    bd=0,
    pady=8,
    command=analyze
).pack(padx=10, pady=10, fill="x")

tk.Button(left_panel, text="🌙 Toggle Dark Mode", command=toggle_theme).pack(padx=10, pady=4, fill="x")
tk.Button(left_panel, text="📄 Export PDF", command=export_pdf).pack(padx=10, pady=4, fill="x")

# ---------------- RIGHT PANEL (BIG RESULTS) ----------------
right_panel = tk.Frame(main_container, bg=current_theme["card"])
right_panel.pack(side="right", fill="both", expand=True)

output_frame = tk.Frame(right_panel, bg=current_theme["card"])
output_frame.pack(fill="both", expand=True)

scroll = tk.Scrollbar(output_frame)
scroll.pack(side="right", fill="y")

output = tk.Text(
    output_frame,
    wrap="word",
    yscrollcommand=scroll.set,
    font=("Segoe UI", 11),
    height=35
)
output.pack(side="left", fill="both", expand=True)
scroll.config(command=output.yview)

# Text styles
output.tag_config("mild", foreground="#22c55e")
output.tag_config("moderate", foreground="#f97316")
output.tag_config("severe", foreground="#ef4444")
output.tag_config("header", foreground="#2563eb", font=("Segoe UI", 11, "bold"))
output.tag_config("bold", font=("Segoe UI", 11, "bold"))
output.tag_config("alt", foreground="#16a34a")
output.tag_config("info", foreground="#6366f1")
output.tag_config("error", foreground="#dc2626")

root.mainloop()
