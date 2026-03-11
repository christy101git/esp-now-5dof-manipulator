import customtkinter as ctk
from tkinter import messagebox
import serial
import serial.tools.list_ports
import time
from PIL import Image, ImageEnhance

# --- IMAGE SETUP ---
BG_IMAGE_PATH = "bg.jpg"  # <-- PUT YOUR CUSTOM PHOTO NAME HERE

# --- Initialize Modern Monochrome Glass Theme ---
ctk.set_appearance_mode("dark")  

class RobotArmPro:
    def __init__(self, root):
        self.root = root
        self.root.title("6-Axis Robot Control (Monochrome UI)")
        self.root.geometry("540x850") 
        
        # Absolute pitch black background for maximum contrast depth
        self.root.configure(fg_color="#000000") 
        
        # --- CUSTOM BACKGROUND IMAGE PROCESSING ---
        try:
            bg_image = Image.open(BG_IMAGE_PATH)
            # Darken the image by 70% to create the "low transparency/smoked glass" effect
            enhancer = ImageEnhance.Brightness(bg_image)
            dark_bg = enhancer.enhance(0.3) 
            
            self.bg_img = ctk.CTkImage(light_image=dark_bg, dark_image=dark_bg, size=(540, 850))
            self.bg_label = ctk.CTkLabel(self.root, image=self.bg_img, text="")
            self.bg_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Background image not found or error: {e}")

        self.ser = None
        self.is_powered = False
        self.last_val = {} 

        # --- DYNAMIC PRESET STORAGE ---
        self.pluck_coords = None
        self.unpluck_coords = None

        self.main_container = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.setup_ui()

    def create_glass_frame(self, parent, title):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=15, pady=10)

        # Gradient step 1: Medium gray labels
        lbl = ctk.CTkLabel(container, text=title, font=("Segoe UI", 12, "bold"), text_color="#888888")
        lbl.pack(anchor="w", padx=15, pady=(0, 5))

        # Gradient step 2: Very dark gray panels with slightly lighter borders for edge highlights
        # Using a slightly transparent hex or very dark color to let the background breathe
        glass = ctk.CTkFrame(container, fg_color="#0A0A0A", corner_radius=16, 
                             border_width=1, border_color="#222222")
        glass.pack(fill="x")
        return glass

    def setup_ui(self):
        # --- Connection Section ---
        c_frame = self.create_glass_frame(self.main_container, "USB CONNECTION")
        
        inner_c = ctk.CTkFrame(c_frame, fg_color="transparent")
        inner_c.pack(padx=15, pady=15, fill="x")
        
        self.port_entry = ctk.CTkEntry(inner_c, width=200, placeholder_text="COM Port", 
                                       corner_radius=8, fg_color="#000000", border_width=1, border_color="#333333")
        self.port_entry.pack(side="left", padx=(0, 10))
        
        # Gradient step 3: Pure white buttons with black text
        ctk.CTkButton(inner_c, text="Connect", width=100, corner_radius=8, 
                      fg_color="#FFFFFF", text_color="#000000", hover_color="#CCCCCC", 
                      font=("Segoe UI", 13, "bold"), command=self.toggle_connection).pack(side="left")

        # --- Power Button ---
        self.pwr_btn = ctk.CTkButton(self.main_container, text="ENABLE SYSTEM", fg_color="#111111", hover_color="#222222",
                                     height=55, font=("Segoe UI", 15, "bold"), corner_radius=12, text_color="#555555",
                                     command=self.toggle_power, state="disabled", border_width=1, border_color="#333333")
        self.pwr_btn.pack(fill="x", padx=20, pady=(5, 15))

        # --- Base 360 Control ---
        b_frame = self.create_glass_frame(self.main_container, "BASE ROTATION (360 MG995)")
        inner_b = ctk.CTkFrame(b_frame, fg_color="transparent")
        inner_b.pack(pady=15)
        
        self.bl = ctk.CTkButton(inner_b, text="ROTATE LEFT", width=140, height=40, corner_radius=8,
                                fg_color="#1A1A1A", hover_color="#333333", text_color="#FFFFFF", state="disabled")
        self.bl.grid(row=0, column=0, padx=10)
        self.bl.bind("<ButtonPress-1>", lambda e: self.send_cmd("B:L"))
        self.bl.bind("<ButtonRelease-1>", lambda e: self.send_cmd("B:S"))
        
        self.br = ctk.CTkButton(inner_b, text="ROTATE RIGHT", width=140, height=40, corner_radius=8,
                                fg_color="#1A1A1A", hover_color="#333333", text_color="#FFFFFF", state="disabled")
        self.br.grid(row=0, column=1, padx=10)
        self.br.bind("<ButtonPress-1>", lambda e: self.send_cmd("B:R"))
        self.br.bind("<ButtonRelease-1>", lambda e: self.send_cmd("B:S"))

        # --- Joint Sliders ---
        s_frame = self.create_glass_frame(self.main_container, "JOINT POSITIONS")
        self.create_slider(s_frame, "Shoulder (MG995)", 0, 180,  "A1")
        self.create_slider(s_frame, "Elbow (SG90)", 9, 152, "A2", invert=True)
        self.create_slider(s_frame, "Wrist Pitch (MG995)", 0, 180, "A3")
        self.create_slider(s_frame, "Wrist Roll (SG90)", 0, 180, "A4")

        # --- Gripper Section (Slider) ---
        g_frame = self.create_glass_frame(self.main_container, "GRIPPER CONTROL")

        self.create_slider(g_frame, "Gripper Claw", 0, 90, "G", smooth=False)

        # --- DYNAMIC PRESET SECTION ---
        p_frame = self.create_glass_frame(self.main_container, "DYNAMIC PRESETS (Transport -> Actuate)")
        
        # Pluck Row
        pluck_row = ctk.CTkFrame(p_frame, fg_color="transparent")
        pluck_row.pack(fill="x", padx=15, pady=(15, 5))
        
        # Monochrome outlining instead of colored borders
        self.btn_save_pluck = ctk.CTkButton(pluck_row, text="💾 Save Pluck", width=120, height=35, corner_radius=8,
                                            fg_color="#0A0A0A", hover_color="#222222", border_width=1, 
                                            border_color="#FFFFFF", text_color="#FFFFFF", font=("Segoe UI", 12, "bold"),
                                            state="disabled", command=self.save_pluck)
        self.btn_save_pluck.pack(side="left", padx=5)
        
        self.btn_run_pluck = ctk.CTkButton(pluck_row, text="▶ RUN PLUCK", width=120, height=35, corner_radius=8,
                                           fg_color="#FFFFFF", hover_color="#CCCCCC", text_color="#000000", font=("Segoe UI", 12, "bold"),
                                           state="disabled", command=self.run_pluck)
        self.btn_run_pluck.pack(side="left", padx=5)
        
        self.lbl_pluck = ctk.CTkLabel(pluck_row, text="[Unsaved]", font=("Segoe UI", 12), text_color="#555555")
        self.lbl_pluck.pack(side="left", padx=10)

        # Unpluck Row
        unpluck_row = ctk.CTkFrame(p_frame, fg_color="transparent")
        unpluck_row.pack(fill="x", padx=15, pady=(5, 15))
        
        self.btn_save_unpluck = ctk.CTkButton(unpluck_row, text="💾 Save Unpluck", width=120, height=35, corner_radius=8,
                                              fg_color="#0A0A0A", hover_color="#222222", border_width=1, 
                                              border_color="#FFFFFF", text_color="#FFFFFF", font=("Segoe UI", 12, "bold"),
                                              state="disabled", command=self.save_unpluck)
        self.btn_save_unpluck.pack(side="left", padx=5)
        
        self.btn_run_unpluck = ctk.CTkButton(unpluck_row, text="▶ RUN UNPLUCK", width=120, height=35, corner_radius=8,
                                             fg_color="#FFFFFF", hover_color="#CCCCCC", text_color="#000000", font=("Segoe UI", 12, "bold"),
                                             state="disabled", command=self.run_unpluck)
        self.btn_run_unpluck.pack(side="left", padx=5)
        
        self.lbl_unpluck = ctk.CTkLabel(unpluck_row, text="[Unsaved]", font=("Segoe UI", 12), text_color="#555555")
        self.lbl_unpluck.pack(side="left", padx=10)

    def create_slider(self, parent, label_text, f, t, prefix, invert=False, smooth=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=12)

        lbl_frame = ctk.CTkFrame(row, fg_color="transparent")
        lbl_frame.pack(fill="x", pady=(0, 5))

        lbl = ctk.CTkLabel(lbl_frame, text=label_text, font=("Segoe UI", 13), text_color="#AAAAAA")
        lbl.pack(side="left")

        val_lbl = ctk.CTkLabel(lbl_frame, text=str(f), font=("Segoe UI", 14, "bold"), text_color="#FFFFFF")
        val_lbl.pack(side="right")

        initial_val = t if invert else f
        current_val = [initial_val]
        target_val = [initial_val]
        is_smoothing = [False]

        def smooth_loop():
            if current_val[0] == target_val[0]:
                is_smoothing[0] = False
                return
            
            step = 1 if target_val[0] > current_val[0] else -1
            if abs(target_val[0] - current_val[0]) <= 1:
                current_val[0] = target_val[0]
            else:
                current_val[0] += step
                
            self.send_cmd(f"{prefix}:{current_val[0]}")
            self.root.after(15, smooth_loop)

        def on_slide(v):
            val = int(v)
            val_lbl.configure(text=str(val))
            sent_val = t - (val - f) if invert else val

            if smooth:
                target_val[0] = sent_val
                if not is_smoothing[0]:
                    is_smoothing[0] = True
                    smooth_loop()
            else:
                self.send_cmd(f"{prefix}:{sent_val}")

        # Monochrome slider (Black track, Pure White progress)
        s = ctk.CTkSlider(row, from_=f, to=t, command=on_slide, state="disabled",
                          button_color="#FFFFFF", button_hover_color="#CCCCCC", 
                          progress_color="#FFFFFF", fg_color="#000000", height=14)
        s.set(f)
        s.pack(fill="x", pady=(5, 0))
        
        def set_and_trigger(new_val):
            s.set(new_val)
            on_slide(new_val)
            
        setattr(self, f"set_{prefix}", set_and_trigger)
        setattr(self, f"s_{prefix}", s)

    # --- SAVE PRESET FUNCTIONS ---
    def save_pluck(self):
        self.pluck_coords = {
            'A1': int(self.s_A1.get()), 'A2': int(self.s_A2.get()), 
            'A3': int(self.s_A3.get()), 'A4': int(self.s_A4.get()), 'G': int(self.s_G.get())
        }
        self.lbl_pluck.configure(text="[Saved!]", text_color="#FFFFFF")
        print(f"✅ Pluck Saved: {self.pluck_coords}")

    def save_unpluck(self):
        self.unpluck_coords = {
            'A1': int(self.s_A1.get()), 'A2': int(self.s_A2.get()), 
            'A3': int(self.s_A3.get()), 'A4': int(self.s_A4.get()), 'G': int(self.s_G.get())
        }
        self.lbl_unpluck.configure(text="[Saved!]", text_color="#FFFFFF")
        print(f"✅ Unpluck Saved: {self.unpluck_coords}")

    # --- RUN PRESET FUNCTIONS ---
    def run_pluck(self):
        if self.pluck_coords:
            self.animate_pose(self.pluck_coords, duration=2.0)
        else:
            messagebox.showwarning("Empty", "Please 'Save Pluck' position first!")

    def run_unpluck(self):
        if self.unpluck_coords:
            self.animate_pose(self.unpluck_coords, duration=2.0)
        else:
            messagebox.showwarning("Empty", "Please 'Save Unpluck' position first!")

    # --- SEQUENCED ANIMATOR (Arm first, then Gripper) ---
    def animate_pose(self, targets, duration):
        arm_steps = 50  
        arm_delay_ms = int((duration / arm_steps) * 1000)
        arm_keys = ['A1', 'A2', 'A3', 'A4']

        # Get Starting Positions
        starts = {
            'A1': int(self.s_A1.get()), 'A2': int(self.s_A2.get()), 
            'A3': int(self.s_A3.get()), 'A4': int(self.s_A4.get()), 'G': int(self.s_G.get())
        }
        
        # Calculate increments just for the arm joints
        arm_increments = {k: (targets[k] - starts[k]) / arm_steps for k in arm_keys if k in targets}

        # Lock UI controls during animation safely using CTk
        controls_to_disable = ["s_A1", "s_A2", "s_A3", "s_A4", "s_G", "btn_save_pluck", "btn_run_pluck", "btn_save_unpluck", "btn_run_unpluck"]
        for key in controls_to_disable:
            if hasattr(self, key):
                getattr(self, key).configure(state="disabled")

        # --- PHASE 1: Move the Arm ---
        def step_arm(current_step):
            if current_step <= arm_steps:
                for key in arm_keys:
                    if key in targets:
                        getattr(self, f"set_{key}")(int(starts[key] + arm_increments[key] * current_step))
                self.root.after(arm_delay_ms, step_arm, current_step + 1)
            else:
                # Arm is completely stopped. Proceed to Phase 2.
                if 'G' in targets:
                    actuate_gripper()
                else:
                    finish_animation()

        # --- PHASE 2: Actuate the Gripper ---
        def actuate_gripper():
            target_g = targets['G']
            start_g = starts['G']
            
            # Set the slider to the final recorded value to trigger background smoothing
            getattr(self, "set_G")(target_g)
            
            # Estimate time to close (15ms per degree of change)
            time_to_close_ms = abs(target_g - start_g) * 15
            self.root.after(time_to_close_ms + 100, finish_animation)

        # --- UNLOCK UI ---
        def finish_animation():
            for key in controls_to_disable:
                if hasattr(self, key):
                    getattr(self, key).configure(state="normal")
            print("✅ Sequenced Movement Complete!")

        # Start sequence
        step_arm(1)

    def toggle_connection(self):
        try:
            self.ser = serial.Serial(self.port_entry.get(), 115200, timeout=0.05)
            self.pwr_btn.configure(state="normal")
            messagebox.showinfo("USB", "Connected to Robot!")
        except Exception as e: messagebox.showerror("Error", str(e))

    def toggle_power(self):
        self.is_powered = not self.is_powered
        st = "normal" if self.is_powered else "disabled"
        
        # Pure monochrome toggle: High contrast White when ON, dark grey when OFF
        self.pwr_btn.configure(
            text="SYSTEM ACTIVE" if self.is_powered else "ENABLE SYSTEM", 
            fg_color="#FFFFFF" if self.is_powered else "#111111",
            text_color="#000000" if self.is_powered else "#555555",
            hover_color="#E5E5EA" if self.is_powered else "#222222"
        )
        self.send_cmd("P:ON" if self.is_powered else "P:OFF")
        
        # Enable all interactable buttons safely
        for a in ["bl", "br", "s_A1", "s_A2", "s_A3", "s_A4", "s_G"]:
            if hasattr(self, a): getattr(self, a).configure(state=st)
            
        if self.is_powered:
            self.btn_save_pluck.configure(state="normal")
            self.btn_save_unpluck.configure(state="normal")
            if self.pluck_coords: self.btn_run_pluck.configure(state="normal")
            if self.unpluck_coords: self.btn_run_unpluck.configure(state="normal")
        else:
            self.btn_save_pluck.configure(state="disabled")
            self.btn_save_unpluck.configure(state="disabled")
            self.btn_run_pluck.configure(state="disabled")
            self.btn_run_unpluck.configure(state="disabled")

    def send_cmd(self, cmd):
        if ":" in cmd:
            pre, val = cmd.split(":")
            if self.last_val.get(pre) == val: return
            self.last_val[pre] = val
        if self.ser and self.ser.is_open:
            self.ser.write((cmd + '\n').encode())

if __name__ == "__main__":
    root = ctk.CTk()
    app = RobotArmPro(root)
    root.mainloop()