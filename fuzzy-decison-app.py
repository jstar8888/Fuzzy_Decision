import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy  as np
import json, os
class FuzzyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng quyết định mờ đa chủ đề")
        self.topics = {}  # lưu dữ liệu: topic_name -> {'criteria':[], 'alternatives':[]}
        self.alt_trees = {}
        self.alt_frame={}
        welcome_lbl = tk.Label(root, text="CHÀO MỪNG ĐẾN VỚI HỆ HỖ TRỢ QUYẾT ĐỊNH", font=("Segoe UI bold", 11),)
        welcome_lbl.pack(padx=10,pady=10)

        # --- Nhập chủ đề ---
        frame_topic = tk.Frame(root, padx=10, pady=10)
        frame_topic.pack()
        
        ttk.Button(frame_topic, text="Thêm chủ đề", command=self.add_topic_popup).pack(side="left", padx=5)

        ttk.Button(frame_topic, text="Mở", command=self.load_file).pack(side="left", padx=5)
        # --- Tab cho các chủ đề ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

    def add_topic_popup(self):
     
        win = tk.Toplevel(self.root)
        win.title("Tạo chủ đề")
        win.resizable(False, False)

        # ===== GẮN POPUP VỚI ROOT =====
        win.transient(self.root)
        win.grab_set()

        # ===== CĂN GIỮA THEO ROOT =====
        win.update_idletasks()
        w, h = 300, 150

        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()

        x = root_x + (root_w - w) // 2
        y = root_y + (root_h - h) // 2

        win.geometry(f"{w}x{h}+{x}+{y}")

        win.focus_force()

        ttk.Label(win, text="Đặt tên chủ đề: ").pack(pady=10)

        entry_topic = ttk.Entry(win, justify="center")
        entry_topic.pack()

        def confirm():
            val = entry_topic.get()
            if val=="":
                messagebox.showinfo("Thông báo", "Vui lòng nhập tên chủ đề!")
                return
            
            if val in self.topics:
                messagebox.showwarning("Trùng tên", "Tab này đã tồn tại.")
                return
            self.add_topic(val)
            win.destroy()

        ttk.Button(win, text="Xác nhận", command=confirm).pack(pady=15)
     
    def add_topic(self,topic_name):

        self.topics[topic_name] = {'criteria': [], 'alternatives': []}
        
        # Tạo tab mới cho chủ đề
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text=topic_name)
        self.notebook.select(tab)
        # Khung tiêu chí
        frame_crit = tk.LabelFrame(tab, text="Tiêu chí", padx=5, pady=5, height=220)
        frame_crit.pack(fill='x', pady=5)
        frame_crit.pack_propagate(False)
        btn_frame = tk.Frame(frame_crit)
        btn_frame.pack(pady=5)
        
        scroll_frame = tk.Frame(frame_crit)
        scroll_frame.pack(fill="x", expand=True)
        canvas = tk.Canvas(scroll_frame, height=150)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical",
                         command=canvas.yview)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")
        crit_container = tk.Frame(canvas)
        canvas.create_window((0, 0), window=crit_container, anchor="nw")
        crit_container.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
        

        frame_alter = tk.LabelFrame(tab, text="Phương án", padx=5, pady=5, height=180)
        frame_alter.pack(fill='x', pady=5)
        frame_alter.pack_propagate(False)
        child_frame = tk.Frame(frame_alter)
        child_frame.pack(fill="x")

        def del_tab():
            
            ans = messagebox.askyesno(
                "Cảnh báo",
                f"Bạn chắc chắn muốn xóa chủ đề {topic_name} chứ?"

                
            )
            if not ans:
                return
            
            self.topics.pop(topic_name,None)
            self.alt_trees.pop(topic_name,None)
            self.alt_frame.pop(topic_name,None)
            self.notebook.forget(tab)

        btn_add_crit = ttk.Button(btn_frame, text="Thêm tiêu chí",
                                 command=lambda f=crit_container, t=topic_name: self.add_criteria_popup(f, t))
        btn_add_crit.pack(side="left", padx=5)

        btn_create_table = ttk.Button(btn_frame, text="Tạo bảng",
                                 command=lambda f=child_frame, t=topic_name: self.create_alternative_table(f, t))
        btn_create_table.pack(side="left", padx=5)

        btn_update_table = ttk.Button(btn_frame, text="Cập nhật bảng",
                                command=lambda  t=topic_name: self.update_table(t))
        btn_update_table.pack(side="left", padx=5)
        
        btn_close = ttk.Button(btn_frame, text="Đóng chủ đề", command=del_tab)
        btn_close.pack(side="right", padx=5)

        frame_cal = tk.Frame(tab,padx=5,pady=5)
        frame_cal.pack(fill="x",padx=5)

        lblexpect= tk.Label(frame_cal,text="Mức độ kì vọng:")
        lblexpect.pack(side="left")
    
        # Hàm cập nhật label khi scale thay đổi
        expected_var = tk.DoubleVar(value=0.01)
        scale = ttk.Scale(frame_cal, from_=0.01, to=1, orient="horizontal", length=250, variable=expected_var)
        scale.pack(side= "right",padx=10, pady=10,)
        def update_label(*arg):
             expected=round(float(expected_var.get()),2)
             if expected > 0.8:
                lblexpect.config(text=f"Mức độ kì vọng: Cao")
             elif expected <0.3:
                lblexpect.config(text=f"Mức độ kì vọng: Thấp")
             else:
                 lblexpect.config(text=f"Mức độ kì vọng: Trung bình")
        expected_var.trace_add("write", update_label)

        result_var = tk.StringVar(value="")

        btn_compute = ttk.Button(tab, text="Tính quyết định mờ",
                                command=lambda t=topic_name, e=expected_var, r=result_var : self.compute_fuzzy(t,e,r))
        btn_compute.pack(pady=10)

        result_lbl=tk.Label(tab,padx=10,pady=10,text="",font=("Segoe UI", 10, "bold"), textvariable=result_var )
        result_lbl.pack()

        return {
        "tab": tab,
        "crit_container": crit_container,
        "alt_frame": child_frame
    }
           
    def add_criteria_popup(self,frame_crit, topic_name):
     
        win = tk.Toplevel(self.root)
        win.title("Thêm tiêu chí")
        win.resizable(False, False)

        # ===== GẮN POPUP VỚI ROOT =====
        win.transient(self.root)
        win.grab_set()

        # ===== CĂN GIỮA THEO ROOT =====
        win.update_idletasks()
        w, h = 300, 150

        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()

        x = root_x + (root_w - w) // 2
        y = root_y + (root_h - h) // 2

        win.geometry(f"{w}x{h}+{x}+{y}")

        win.focus_force()

        ttk.Label(win, text="Số tiêu chí muốn thêm: ").pack(pady=10)

        entry_num = ttk.Entry(win, justify="center")
        entry_num.pack()

        def confirm():
            val = entry_num.get()
            if not val.isdigit() or int(val) <= 0:
                messagebox.showerror("Lỗi", "Nhập số nguyên dương")
                return
            for _ in range(int(val)):
                self.add_criteria(frame_crit, topic_name)
            win.destroy()

        ttk.Button(win, text="Xác nhận", command=confirm).pack(pady=15)
        
    def add_criteria(self, frame_crit, topic_name):
        
        crit_frame = tk.Frame(frame_crit)
        crit_frame.pack(fill='x', pady=2)
        tk.Label(crit_frame, text="Tên tiêu chí:").pack(side='left')
        entry_name = tk.Entry(crit_frame)
        entry_name.pack(side='left', padx=5)

        weight_var = tk.DoubleVar(value=0.1)
    
        scale = ttk.Scale(crit_frame, from_=0.1, to=1, orient="horizontal", length=150, variable=weight_var)
        scale.pack(side= "left",padx=10, pady=10,)

        lbl_weight = tk.Label(crit_frame, width=30, text="Độ ưu tiên:", anchor="w")
        lbl_weight.pack(side='left',padx=10, pady=10)

        # ---- Khi scale thay đổi → cập nhật label ----
        def on_scale_change(*args):
            value=round(float(weight_var.get()),2)
            if value > 0.8:
                lbl_weight.config(text="Độ ưu tiên: Cao")
            elif value < 0.3:
                lbl_weight.config(text="Độ ưu tiên: Thấp")
            else :
                lbl_weight.config(text="Độ ưu tiên: Trung bình")

        weight_var.trace_add("write", on_scale_change)
        # Nút xóa
        def remove_frame():
            
            
            if len(self.topics[topic_name]["criteria"])<2:
                messagebox.showwarning("Cảnh báo", "Phải có ít nhận 1 tiêu chí.")
                return
            
            ans = messagebox.askyesno(
                "Xác nhận",
                "Xóa tiêu chí đã chọn?"
            )
            if not ans:
                return 
            
            criteria = self.topics[topic_name]["criteria"]

            idx = next(
                (i for i, c in enumerate(criteria) if c[2] == crit_frame),
                None
            )


            criteria.pop(idx)

            for alt in self.topics[topic_name]["alternatives"]:
                if idx < len(alt["values"]):
                   alt["values"].pop(idx) 

            crit_frame.destroy()
            self.rebuild_alternative_table(topic_name)


        btn_remove = tk.Button(crit_frame, text="Xóa", command=remove_frame)
        btn_remove.pack(side='left', padx=5)
        self.topics[topic_name]['criteria'].append((entry_name, weight_var,crit_frame))
        
        
        if len(self.topics[topic_name]["alternatives"])>0:
            
            for alt in self.topics[topic_name]["alternatives"]:
                alt["values"].append(None)

    
    
    def create_alternative_table(self, frame_alt, topic_name):
       if topic_name in self.alt_trees:
           return
       
       criteria = self.topics[topic_name]["criteria"]
       if len(criteria)<=0:
           messagebox.showwarning("Lỗi", "Chưa có tiêu chí")
           return
       
       for entry, _, _ in criteria:
        
            if not entry.get().strip():
                messagebox.showwarning(
                    "Thiếu dữ liệu",
                    "Có tiêu chí chưa nhập tên"
                )
                return
       
       
       
       cols = ["name"] + [c[0].get() for c in criteria]
       
       scroll_y = ttk.Scrollbar(frame_alt, orient="vertical")
       scroll_y.pack(side="right", fill="y")
       tree = ttk.Treeview(frame_alt, columns=cols, show="headings", height=0, yscrollcommand=scroll_y.set)
       
       tree.heading("name", text="Tên phương án", anchor="center")
       tree.column("name", width=200, anchor="center", stretch=False)

       for c in cols[1:]:
          tree.heading(c, text=c, anchor="center")
          tree.column(c, width=80, anchor="center")
       
       scroll_y.config(command=tree.yview)
       tree.pack(fill="x", pady=5)
       
       tree.bind("<Double-1>", lambda e: self.edit_cell(e, topic_name))

       self.alt_trees[topic_name] = tree
       self.alt_frame[topic_name] = frame_alt
       
       def add_row():
         num_cols = len(tree["columns"])   # số cột của bảng
         empty_row = [""] * num_cols       # tạo hàng trống đúng số cột

         tree.insert("", "end", values=empty_row)

         current_height=tree.cget("height")
         if current_height<4:
             tree.config(height=current_height+1)
         else:
             tree.yview_moveto(1.0)
         criteria = tree["columns"][1:]  # bỏ cột tên
         num_criteria = len(criteria)
         self.topics[topic_name]['alternatives'].append({
            "name": "",
            "values": [None] * num_criteria
        })
   
       def delete_row():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Hãy chọn 1 hàng để xóa!")
            return
        
        ans = messagebox.askyesno(
                "Xác nhận",
                "Bạn chắc chắn muốn xóa phương án này chứ?"
            )
        if not ans:
            return 
        # chỉ xóa 1 hàng
        item = selected[0]

        # index của hàng trong tree
        idx = tree.index(item)

        # xóa trong dữ liệu
        alternatives = self.topics[topic_name]["alternatives"]
        if 0 <= idx < len(alternatives):
            alternatives.pop(idx)

        # xóa trên tree
        tree.delete(item)

        # cập nhật chiều cao
        tree.config(height=len(alternatives))

       btn_add = ttk.Button(frame_alt, text="➕ Thêm phương án", command=add_row)
       btn_add.pack(side="left", padx=10)

       btn_delete = ttk.Button(frame_alt, text="➖ Bỏ phương án", command=delete_row)
       btn_delete.pack(side="left", padx=10)
       
       btn_save= ttk.Button(frame_alt, text="Lưu", command=self.save_file)
       btn_save.pack(side="left", padx=5)
    
    def validate_score(self, value):
        if value == "":
            return True  # cho phép xóa để gõ lại
        try:
            v = float(value)
            return 1 <= v <= 10 and value.count('.') <= 1
        except ValueError:
            return False

    def edit_cell(self, event, topic_name):
        tree = self.alt_trees[topic_name]
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)

        if not item or not column:
            return

        col_idx = int(column[1:]) - 1
        x, y, w, h = tree.bbox(item, column)

        old_value = tree.item(item, "values")[col_idx]

        if col_idx == 0:
            entry = tk.Entry(tree)  # cột tên → nhập text
        else:
            vcmd = (tree.register(self.validate_score), "%P")
            entry = tk.Entry(
                tree,
                validate="key",
                validatecommand=vcmd
            )
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, old_value)
        entry.focus()

        def save(event=None):
            value = entry.get()
            row_index=tree.index(item)
            alt = self.topics[topic_name]['alternatives'][row_index]

            if col_idx == 0:
                alt["name"] = value
            else:
                if value == "":
                    alt["values"][col_idx - 1] = None
                else:
                    alt["values"][col_idx - 1] = float(value)

            tree_values = list(tree.item(item, "values"))
            tree_values[col_idx] = value
            tree.item(item, values=tree_values)

            entry.destroy()

        entry.bind("<Return>", save)
        entry.bind("<FocusOut>", save)
        

    def compute_fuzzy(self, topic_name, expected_var,result_var):
        criteria = self.topics[topic_name]["criteria"]
        alternatives = self.topics[topic_name]["alternatives"]
        
        crit_names = [c[0].get() for c in criteria]
        weights = [c[1].get() for c in criteria]
        weight_series = pd.Series(weights, index=crit_names)

        if len(criteria)<1:
            messagebox.showwarning("Thiếu dữ liệu", "Bạn chưa có tiêu chí đánh giá nào.")
            return
        
        if len(alternatives)<2:
            messagebox.showwarning("Thiếu dữ liệu", "Hãy nhập ít nhất 2 phương án.")
            return
        
        for entry, _, _ in criteria:
        
            if not entry.get().strip():
                messagebox.showwarning(
                    "Thiếu dữ liệu",
                    "Có tiêu chí chưa nhập tên"
                )
                return
            
        for alt in alternatives:
            if alt["name"] == "":
                messagebox.showwarning(
                    "Thiếu dữ liệu",
                    "Tên phương án không được để trống"
                )
                return

            for i, v in enumerate(alt["values"]):
                if v is None:
                    messagebox.showwarning(
                        "Thiếu dữ liệu",
                        "Hãy nhập đủ điểm đánh giá hoặc Cập nhật lại bảng"
                    )
                    return

       
        

        df = pd.DataFrame([
            [alt["values"][i] for i in range(len(crit_names))]
            for alt in alternatives
        ],
        columns=crit_names)
        df.insert(0, "Phuong an", [alt["name"] for alt in alternatives])  # thêm cột tên phương án
        expected=float(expected_var.get())
        chosen=self.fuzzy_cal(df,weight_series,expected)
        result_var.set(f"Phương án lựa chọn là {chosen}")
        
        
    def fuzzy_cal(self,df,sr,weight):
        
        sr=sr.astype(float)
        sr=sr/sr.sum()
        print(sr)
        # Lấy cột số, bỏ "Phuong an"
        num_cols = df.columns.drop("Phuong an")
        df[num_cols]=df[num_cols].astype(float)
        # Chuẩn hóa giá trị từ 0-10 → 0-1
        df[num_cols] = df[num_cols] / 10.0
        print(df[num_cols])
        # Tính expected
        expected = np.prod(np.power(df[num_cols], sr), axis=1)
        print(expected)
        # Tính ne_expected
        ne_expected = 1 - np.prod(np.power(1-df[num_cols], sr), axis=1)
        print(ne_expected)
        # Tính xác suất fuzzy
        probability = np.power(expected, weight) * np.power(ne_expected, 1 - weight)
        
        # Lấy phương án có xác suất cao nhất
        print(probability)
        chosen = df["Phuong an"].loc[probability.idxmax()]
    
        return chosen
        
    def save_file(self):
        current = self.notebook.select()
        if not current:
            messagebox.showwarning("Thông báo", "Không có chủ đề để lưu")
            return

        topic_name = self.notebook.tab(current, "text")
        topic = self.topics[topic_name]
        
        if len(topic["alternatives"])<2:
            messagebox.showwarning("Thiếu dữ liệu", "Hãy nhập ít nhất 2 phương án.")
            return
        
        for entry, _, _ in topic["criteria"]:
        
            if not entry.get().strip():
                messagebox.showwarning(
                    "Thiếu dữ liệu",
                    "Có tiêu chí chưa nhập tên."
                )
                return
            
        for alt in topic["alternatives"]:
            if alt["name"] == "":
                messagebox.showwarning(
                    "Thiếu dữ liệu",
                    "Tên phương án không được để trống."
                )
                return

            for i, v in enumerate(alt["values"]):
                if v is None:
                    messagebox.showwarning(
                        "Thiếu dữ liệu",
                        "Hãy nhập đủ điểm đánh giá hoặc Cập nhật lại bảng."
                    )
                    return
        data = {
            "criteria": [
                {
                    "name": c[0].get(),
                    "weight": c[1].get()
                }
                for c in topic["criteria"]
            ],
            "alternatives": topic["alternatives"]
        }

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON file", "*.json")]
        )
        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        messagebox.showinfo("Thành công", "Đã lưu file")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON file", "*.json")]
        )
        if not file_path:
            return

        
        topic_name = os.path.splitext(os.path.basename(file_path))[0]

        if topic_name in self.topics:
            messagebox.showwarning("Trùng tên", "Tab này đã tồn tại")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ---- TẠO TAB MỚI ----
        
        frames = self.add_topic(topic_name)
        crit_container = frames["crit_container"]
        alt_frame = frames["alt_frame"]
        
        

        for c in data["criteria"]:
            self.add_criteria(crit_container, topic_name)
            entry, var, _ = self.topics[topic_name]["criteria"][-1]
            entry.insert(0, c["name"])
            var.set(c["weight"])

        self.topics[topic_name]["alternatives"] = data["alternatives"]
        # ---- BẢNG PHƯƠNG ÁN ----
        
        self.create_alternative_table(alt_frame, topic_name)

        tree = self.alt_trees[topic_name]
        for alt in data["alternatives"]:
           tree.insert("", "end", values=[alt["name"]] + alt["values"])
           current_height=tree.cget("height")
           if current_height<4:
                tree.config(height=current_height+1)

    def rebuild_alternative_table(self, topic_name):
            if topic_name not in self.alt_trees:
                return
            
            criteria = self.topics[topic_name]["criteria"]
            for entry, _, _ in criteria:
        
                if not entry.get().strip():
                    messagebox.showwarning(
                        "Thiếu dữ liệu",
                        "Có tiêu chí chưa nhập tên"
                    )
                    return
            
            old_tree = self.alt_frame[topic_name]
            parent = old_tree.master
            old_tree.destroy()
            del self.alt_trees[topic_name]
            del self.alt_frame[topic_name]
            # Tạo lại Treeview
            new_frame = tk.Frame(parent)
            new_frame.pack(fill="x")
            self.create_alternative_table(new_frame, topic_name)

            tree = self.alt_trees[topic_name]

            for alt in self.topics[topic_name]["alternatives"]:
                values = [alt["name"]] + alt["values"]
                tree.insert("", "end", values=values)

            tree.config(height=len(self.topics[topic_name]["alternatives"]))

     
    def update_table (self,topic_name):
            if topic_name not in self.alt_trees:
                return
            
            criteria = self.topics[topic_name]["criteria"]
            for entry, _, _ in criteria:
        
                if not entry.get().strip():
                    messagebox.showwarning(
                        "Thiếu dữ liệu",
                        "Có tiêu chí chưa nhập tên"
                    )
                    return
            ans = messagebox.askyesno(
                "Thông báo",
                "Cập nhật lại toàn bộ bảng ?"
            )
            if not ans:
               return 
            self.rebuild_alternative_table(topic_name)

if __name__ == "__main__":
    root = tk.Tk()
    
    # ===== KÍCH THƯỚC =====
    w, h = 900, 700

    # ===== ÉP VỊ TRÍ GIỮA MÀN HÌNH =====
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    x = (screen_w - w) // 2
    y = (screen_h - h) // 2

    root.geometry(f"{w}x{h}+{x}+{y}")

    # ===== TẮT RESIZE =====
    root.resizable(False, False)

    # ===== ÉP WINDOWS CHẤP NHẬN VỊ TRÍ =====
    root.attributes("-topmost", True)
    root.attributes("-topmost", False)
    app = FuzzyApp(root)
    root.mainloop()
