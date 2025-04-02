import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import subprocess
import platform

class FileVersionManager:
    def __init__(self, root):
        self.root = root
        self.root.title("单文件版本管理器1.0——llsky9")
        self.root.geometry("1000x600")
        
        # 数据存储
        self.current_file = None
        self.original_filename = None  # 用于存储原始文件名
        self.branches = {}
        self.current_branch = None
        self.branch_hierarchy = {}  # 用于存储分支层级关系
        self.branch_counter = {}  # 用于生成分支编号
        self.working_directory = None  # 特定的工作目录
        
        # 预设软件配置
        self.software_config = {
            "Notepad": ["notepad.exe"],
            "Python": ["python.exe"]
        }
        
        # 初始化界面
        self.setup_ui()
        
    def setup_ui(self):
        # 主内容区 - 分支树结构
        self.setup_branch_tree()
        
        # 右侧边栏
        self.setup_sidebar()
        
    def setup_branch_tree(self):
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 分支树结构
        self.tree = ttk.Treeview(tree_frame, columns=("description",), show="tree headings")
        self.tree.heading("#0", text="分支结构")
        self.tree.heading("description", text="描述")
        self.tree.column("description", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 右键菜单
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
    def setup_sidebar(self):
        sidebar = tk.Frame(self.root, width=250)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)
        
        # 文件操作
        tk.Label(sidebar, text="文件操作").pack(anchor=tk.W, pady=5)
        tk.Button(sidebar, text="打开文件", command=self.open_file).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(sidebar, text="新建文件", command=self.new_file).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(sidebar, text="加载文件夹", command=self.load_working_directory).pack(fill=tk.X, padx=5, pady=2)
        
        # 分支管理
        tk.Label(sidebar, text="分支管理").pack(anchor=tk.W, pady=5)
        tk.Button(sidebar, text="创建分支", command=self.create_branch).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(sidebar, text="创建子分支", command=self.create_sub_branch).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(sidebar, text="删除分支", command=self.delete_branch).pack(fill=tk.X, padx=5, pady=2)
        tk.Button(sidebar, text="修改描述", command=self.modify_branch_description).pack(fill=tk.X, padx=5, pady=2)
        
        # 预设软件
        tk.Label(sidebar, text="预设软件").pack(anchor=tk.W, pady=5)
        self.software_var = tk.StringVar(value="Notepad")
        
        # 创建可编辑的预设软件列表
        software_frame = tk.Frame(sidebar)
        software_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 固定预设
        for software in self.software_config:
            tk.Radiobutton(software_frame, text=software, variable=self.software_var, 
                          value=software).pack(anchor=tk.W)
        
        # 添加默认编辑器选项
        tk.Radiobutton(software_frame, text="默认编辑器", variable=self.software_var, 
                      value="default_editor").pack(anchor=tk.W)
        
        # 操作按钮
        tk.Button(sidebar, text="打开", command=self.open_in_external_editor).pack(fill=tk.X, padx=5, pady=5)
        
    def show_context_menu(self, event):
        # 右键菜单功能可以在这里实现
        pass
        
    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.tree.item(item, "values")
            text = self.tree.item(item, "text")
            
            # 解析分支编号
            branch_id = text
            
            # 更新当前分支
            for branch, data in self.branches.items():
                if data["id"] == branch_id:
                    self.current_branch = branch
                    break
    
    def new_file(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建文件")
        dialog.geometry("400x250")
        
        # 文件名输入框
        filename_frame = tk.Frame(dialog)
        filename_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(filename_frame, text="文件名:").pack(side=tk.LEFT, padx=5)
        filename_entry = tk.Entry(filename_frame, width=30)
        filename_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 文件夹路径选择框
        location_frame = tk.Frame(dialog)
        location_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(location_frame, text="文件夹路径:").pack(side=tk.LEFT, padx=5)
        location_entry = tk.Entry(location_frame, width=30)
        location_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def select_directory():
            directory = filedialog.askdirectory()
            if directory:
                location_entry.delete(0, tk.END)
                location_entry.insert(0, directory)
        
        tk.Button(location_frame, text="选择文件夹", command=select_directory).pack(side=tk.RIGHT, padx=5)
        
        # 确认按钮
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10, fill=tk.X)
        
        def create_file():
            filename = filename_entry.get()
            location = location_entry.get()
            
            if not filename:
                messagebox.showerror("错误", "请输入文件名")
                return
            
            if not location:
                messagebox.showerror("错误", "请选择文件夹路径")
                return
            
            # 确保文件夹存在
            if not os.path.exists(location):
                messagebox.showerror("错误", "所选文件夹不存在")
                return
            
            full_path = os.path.join(location, filename)
            if os.path.exists(full_path):
                messagebox.showerror("错误", "文件已存在")
                return
            
            with open(full_path, 'w') as f:
                f.write("")
                
            self.working_directory = location
            self.current_file = full_path
            self.original_filename = filename  # 存储原始文件名
            self.branches = {
                "main": {
                    "path": filename,  # 存储相对路径
                    "description": "主分支",
                    "id": "1"
                }
            }
            self.branch_hierarchy = {"main": None}
            self.branch_counter = {"1": 0}
            self.current_branch = "main"
            self.update_tree()
            self.save_branches_to_json()
            dialog.destroy()
            
        # 使用 pack 的 expand 和 fill 选项将按钮居中
        tk.Button(button_frame, text="确认", command=create_file).pack(pady=5, expand=True)
        
    def load_working_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.working_directory = directory
            # 检查是否存在特定的文本文件
            if not os.path.exists(os.path.join(directory, "version_manager.txt")):
                with open(os.path.join(directory, "version_manager.txt"), 'w') as f:
                    f.write("此文件夹用于文件版本管理")
                    
            # 尝试加载分支数据
            json_path = os.path.join(directory, "branches.json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        self.branches = data.get("branches", {})
                        self.branch_hierarchy = data.get("branch_hierarchy", {})
                        self.branch_counter = data.get("branch_counter", {})
                        self.current_branch = data.get("current_branch", None)
                        self.current_file = data.get("current_file", None)
                        self.original_filename = data.get("original_filename", None)
                        
                        # 将路径转换为相对于工作目录的路径
                        for branch, info in self.branches.items():
                            if os.path.isabs(info["path"]):
                                relative_path = os.path.relpath(info["path"], directory)
                                self.branches[branch]["path"] = relative_path
                        
                        self.update_tree()
                except Exception as e:
                    messagebox.showerror("错误", f"无法加载分支数据: {str(e)}")
            else:
                # 初始化新的分支数据
                self.branches = {}
                self.branch_hierarchy = {}
                self.branch_counter = {}
                self.current_branch = None
                self.current_file = None
                self.original_filename = None
                self.update_tree()
                
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            # 选择目标文件夹
            directory = filedialog.askdirectory()
            if directory:
                # 拷贝文件到目标文件夹
                filename = os.path.basename(file_path)
                dest_path = os.path.join(directory, filename)
                shutil.copy2(file_path, dest_path)
                
                self.working_directory = directory
                self.current_file = dest_path
                self.original_filename = filename  # 存储原始文件名
                self.branches = {
                    "main": {
                        "path": filename,  # 存储相对路径
                        "description": "主分支",
                        "id": "1"
                    }
                }
                self.branch_hierarchy = {"main": None}
                self.branch_counter = {"1": 0}
                self.current_branch = "main"
                self.update_tree()
                self.save_branches_to_json()
                
    def save_branches_to_json(self):
        if not self.working_directory:
            return
            
        data = {
            "branches": self.branches,
            "branch_hierarchy": self.branch_hierarchy,
            "branch_counter": self.branch_counter,
            "current_branch": self.current_branch,
            "current_file": self.current_file,
            "original_filename": self.original_filename
        }
        
        json_path = os.path.join(self.working_directory, "branches.json")
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)
            
    def create_branch(self):
        if not self.current_file:
            messagebox.showerror("错误", "请先打开文件")
            return
            
        # 禁止对主分支创建分支
        if self.current_branch == "main":
            messagebox.showerror("错误", "不能对源文件（主分支）创建分支")
            return
            
        # 获取当前分支的父分支
        current_branch_parent = self.branch_hierarchy.get(self.current_branch, None)
        
        # 生成分支编号
        if current_branch_parent is None:
            parent_id = "1"
        else:
            parent_id = self.branches[current_branch_parent]["id"]
        
        # 获取原始文件名和后缀
        file_base, file_ext = os.path.splitext(self.original_filename)
        
        # 生成新分支的文件名
        new_id = f"{parent_id}.{self.branch_counter.get(parent_id, 0) + 1}"
        new_file_name = f"{new_id}_{file_base}{file_ext}"
        
        # 复制父分支的文件到新分支
        if current_branch_parent is None:
            parent_path = self.branches["main"]["path"]
        else:
            parent_path = self.branches[current_branch_parent]["path"]
            
        parent_path_abs = os.path.join(self.working_directory, parent_path)
        new_path_abs = os.path.join(self.working_directory, new_file_name)
        shutil.copy2(parent_path_abs, new_path_abs)
        
        # 更新分支数据
        branch_name = f"分支{len(self.branches) + 1}"
        self.branches[branch_name] = {
            "path": new_file_name,  # 存储相对路径
            "description": "待填写",  # 初始化为“待填写”
            "id": new_id
        }
        
        # 更新计数器
        self.branch_counter[parent_id] = self.branch_counter.get(parent_id, 0) + 1
        
        # 设置新分支的父分支
        self.branch_hierarchy[branch_name] = current_branch_parent
        
        self.current_branch = branch_name
        self.update_tree()
        self.save_branches_to_json()
        
    def create_sub_branch(self):
        if not self.current_file:
            messagebox.showerror("错误", "请先打开文件")
            return
            
        # 生成分支编号
        parent_id = self.branches[self.current_branch]["id"]
        
        # 获取原始文件名和后缀
        file_base, file_ext = os.path.splitext(self.original_filename)
        
        # 生成新分支的文件名
        new_id = f"{parent_id}.{self.branch_counter.get(parent_id, 0) + 1}"
        new_file_name = f"{new_id}_{file_base}{file_ext}"
        
        # 复制父分支的文件到新分支
        parent_path_abs = os.path.join(self.working_directory, self.branches[self.current_branch]["path"])
        new_path_abs = os.path.join(self.working_directory, new_file_name)
        shutil.copy2(parent_path_abs, new_path_abs)
        
        # 更新分支数据
        branch_name = f"分支{len(self.branches) + 1}"
        self.branches[branch_name] = {
            "path": new_file_name,  # 存储相对路径
            "description": "待填写",  # 初始化为“待填写”
            "id": new_id
        }
        
        # 更新计数器
        self.branch_counter[parent_id] = self.branch_counter.get(parent_id, 0) + 1
        
        self.branch_hierarchy[branch_name] = self.current_branch
        self.current_branch = branch_name
        self.update_tree()
        self.save_branches_to_json()
        
    def delete_branch(self):
        if not self.current_file or not self.branches:
            messagebox.showerror("错误", "没有可删除的分支")
            return
            
        if not self.current_branch:
            messagebox.showerror("错误", "请先选择一个分支")
            return
            
        # 获取所有子分支
        branches_to_delete = self.get_all_sub_branches(self.current_branch)
        
        # 弹窗确认
        if messagebox.askyesno("确认", f"确定要删除分支 {self.current_branch} 吗?"):
            # 如果有子分支，额外提醒
            if branches_to_delete:
                messagebox.showinfo("提醒", f"分支 {self.current_branch} 有子分支，将一并删除。")
                
            # 删除分支及其子分支
            for branch in branches_to_delete + [self.current_branch]:
                if branch in self.branches:
                    # 删除文件
                    file_path_abs = os.path.join(self.working_directory, self.branches[branch]["path"])
                    if os.path.exists(file_path_abs):
                        os.remove(file_path_abs)
                    del self.branches[branch]
                if branch in self.branch_hierarchy:
                    del self.branch_hierarchy[branch]
                if branch in self.branch_counter:
                    del self.branch_counter[branch]
                    
            # 更新当前分支
            remaining_branches = list(self.branches.keys())
            if remaining_branches:
                self.current_branch = remaining_branches[0]
            else:
                self.current_branch = None
            self.update_tree()
            self.save_branches_to_json()
            
    def get_all_sub_branches(self, branch):
        # 递归获取所有子分支
        sub_branches = []
        for b in list(self.branch_hierarchy.keys()):
            if self.branch_hierarchy[b] == branch:
                sub_branches.append(b)
                sub_branches.extend(self.get_all_sub_branches(b))
        return sub_branches
        
    def modify_branch_description(self):
        if not self.current_file or not self.branches:
            messagebox.showerror("错误", "没有可修改的分支")
            return
            
        if not self.current_branch:
            messagebox.showerror("错误", "请先选择一个分支")
            return
            
        # 弹出对话框，让用户输入新的描述
        new_desc = simpledialog.askstring("修改描述", "输入新的描述:", initialvalue=self.branches[self.current_branch]["description"])
        if new_desc:
            self.branches[self.current_branch]["description"] = new_desc
            self.update_tree()
            self.save_branches_to_json()
            
    def update_tree(self):
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 添加分支
        added_items = {}
        
        # 首先添加主分支
        if "main" in self.branches:
            main_item = self.tree.insert("", "end", text=self.branches["main"]["id"], values=(self.branches["main"]["description"],))
            added_items["main"] = main_item
            
        # 按层级添加其他分支
        for branch, data in self.branches.items():
            if branch == "main":
                continue
            parent = self.branch_hierarchy.get(branch, None)
            if parent in added_items:
                item_id = self.tree.insert(added_items[parent], "end", text=data["id"], values=(data["description"],))
                added_items[branch] = item_id
            else:
                # 如果父分支尚未添加，则添加到根节点
                item_id = self.tree.insert("", "end", text=data["id"], values=(data["description"],))
                added_items[branch] = item_id
        # 选择当前分支
        if self.current_branch and self.current_branch in added_items:
            self.tree.selection_set(added_items[self.current_branch])
        
        # 展开所有项
        self.expand_all_items("")

    def expand_all_items(self, parent_id):
        for item in self.tree.get_children(parent_id):
            self.tree.item(item, open=True)
            self.expand_all_items(item)
        
    def open_in_external_editor(self):
        if not self.current_file or not self.current_branch:
            messagebox.showerror("错误", "请先打开文件并选择分支")
            return
            
        software = self.software_var.get()
        
        if software == "default_editor":
            # 使用系统默认编辑器打开文件
            file_path_abs = os.path.join(self.working_directory, self.branches[self.current_branch]["path"])
            try:
                if platform.system() == "Windows":
                    os.startfile(file_path_abs)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.call(["open", file_path_abs])
                else:  # Linux
                    subprocess.call(["xdg-open", file_path_abs])
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")
        else:
            if software not in self.software_config:
                messagebox.showerror("错误", f"未配置软件 {software}")
                return
            config = self.software_config[software]
            try:
                cmd = [config[0]]
                if len(config) > 1:
                    cmd.append(config[1])
                file_path_abs = os.path.join(self.working_directory, self.branches[self.current_branch]["path"])
                cmd.append(file_path_abs)
                subprocess.Popen(cmd)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开编辑器: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileVersionManager(root)
    root.mainloop()