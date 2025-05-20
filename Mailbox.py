import tkinter 
import sqlite3
import time
import threading

def get_usernames():
    con = sqlite3.connect("users.db")
    cur=con.cursor()
    cur.execute("SELECT name FROM users")
    users = [row[0] for row in cur.fetchall()]
    con.close()
    return users

def get_unlocking_user():
    con = sqlite3.connect("users.db")
    cur=con.cursor()
    cur.execute("SELECT name FROM users WHERE is_unlocker=1 limit 1")
    user= cur.fetchone()
    con.close()
    return user[0] if user else None

def set_unlocking_user(name):
    con = sqlite3.connect("users.db")
    cur=con.cursor()
    cur.execute("UPDATE users set is_unlocker = 0")
    cur.execute("UPDATE users set is_unlocker =1 WHERE name = ?",(name,))
    print(f"{name} is the unlocking user")
    con.commit()
    con.close()
    
def validate_pin(name,pin):
    con = sqlite3.connect("users.db")
    cur=con.cursor()
    cur.execute("SELECT pin FROM users WHERE name = ? AND is_unlocker=1",(name,))
    result=cur.fetchone()
    con.close()
    return result and result[0]==pin

class Mailbox:
    def __init__(self,root):
        self.root=root
        self.root.attributes("-fullscreen",True)
        self.root.configure(bg='black')
        self.pin=tkinter.StringVar()
        self.status=tkinter.StringVar()
        self.build_page()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
    def build_page(self):
        self.clear()
        tkinter.Button(self.root, text="⚙️", font=("Arial", 20), command=self.show_admin_login).pack(side="right")

        tkinter.Label(self.root, text="Mailbox Access", font=("Arial", 25), fg='white', bg='black').pack(pady=20)
       
        unlocker=get_unlocking_user()
        if unlocker:
            tkinter.Label(self.root, text="Mailbox is locked. Tap To Unlock",font=("Arial", 20),fg='white',bg='black').pack(pady=10)
            tkinter.Button(self.root,text=unlocker, font=("Arial", 20), command=lambda: self.ask_for_pin(unlocker)).pack(pady=20)
        else:
            tkinter.Label(self.root, text="Mailbox is unlocked",font=("Arial", 20),fg='white',bg='black').pack(pady=10)
            tkinter.Label(self.root, text="Who is locking it?",font=("Arial", 20),fg='white',bg='black').pack(pady=10)
            for user in get_usernames():
                tkinter.Button(self.root,text=f"{user}",font=("Arial", 20), command=lambda u=user: self.lock_helper(u)).pack(pady=10)

        tkinter.Label(self.root, textvariable=self.status, font=("Arial", 20), fg='white', bg='black').pack(pady=10)


    def ask_for_pin(self,name):
        self.clear()
        self.status.set("")
        tkinter.Label(self.root, text=f"Enter Pin for {name}",font=("Arial", 20),fg='white',bg='black').pack(pady=20)
        tkinter.Entry(self.root,font=("Arial",24),show='*',textvariable=self.pin).pack()
        tkinter.Button(self.root,text="Submit",font=("Arial", 20),command=lambda: self.pin_entered(name)).pack(pady=20)
        tkinter.Label(self.root, textvariable=self.status, font=("Arial", 20), fg='white', bg='black').pack(pady=10)

     
    def pin_entered(self, name):
        if validate_pin(name,self.pin.get()):
            set_unlocking_user(None)
            #relay signal goes here
            self.status.set("unlocked")
            self.root.after(5000, lambda:self.status.set(""))

            self.root.after(2000, self.build_page)
        else:
            self.status.set("Pin is incorrect")
            self.root.after(5000, lambda:self.status.set(""))

   

    def lock_helper(self,name):
        set_unlocking_user(name)
        self.build_page()

    def show_admin_login(self):
        self.clear()
        username=tkinter.StringVar()
        password=tkinter.StringVar()


        tkinter.Label(self.root, text="Enter Admin Credentials", font=("Arial", 20), fg='white', bg='black').pack(pady=10)
        tkinter.Entry(self.root, font=("Arial", 20), textvariable=username).pack(pady=10)
        tkinter.Entry(self.root, font=("Arial", 20),show="*", textvariable=password ).pack(pady=10)
        def attempt_login():
            con = sqlite3.connect("users.db")
            cur=con.cursor()
            cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (username.get(), password.get()))
            result=cur.fetchone()
            con.close()
            if result:
                self.show_admin_settings()
            else:
                self.status.set("Incorrect Credentials")
                self.root.after(5000, lambda:self.status.set(""))

        tkinter.Button(self.root, text="Login", font=("Arial", 20), command=attempt_login).pack(pady=10)
        tkinter.Label(self.root, textvariable=self.status, font=("Arial", 20), fg='white', bg='black').pack(pady=10)

    def remove_user(self):
        
        self.clear()
        target_user=tkinter.StringVar()

        tkinter.Label(self.root, text="Enter User to Remove", font=("Arial", 20), fg='white', bg='black').pack(pady=10)
        tkinter.Entry(self.root, font=("Arial", 20), textvariable=target_user).pack(pady=10)

        def remove_user():
            if not target_user.get():
                self.status.set("Please enter a user")
                self.root.after(5000, lambda:self.status.set(""))

                return
            con = sqlite3.connect("users.db")
            cur=con.cursor()
            try:
                cur.execute("DELETE FROM users WHERE name=?", (target_user.get(),))
                con.commit()
                self.status.set(f"Removed {target_user.get()}")
                self.root.after(5000, lambda:self.status.set(""))

            except sqlite3.IntegrityError:
                self.status.set("User does not exist")
                self.root.after(5000, lambda:self.status.set(""))

            finally:
                con.close()
                self.show_admin_settings()
            con.close()
            self.status.set(f"Removed {target_user.get()}")
            self.root.after(5000, lambda:self.status.set(""))

            self.root.after(2000, self.build_page)
        tkinter.Button(self.root, text="Remove", font=("Arial", 20), command=remove_user).pack(pady=10)

    def add_user(self):
        self.clear()

        new_user=tkinter.StringVar()
        new_pin=tkinter.StringVar()

        tkinter.Label(self.root, text="Enter New User", font=("Arial", 20), fg='white', bg='black').pack(pady=10)
        tkinter.Entry(self.root, font=("Arial", 20), textvariable=new_user).pack(pady=10)
        tkinter.Label(self.root, text="Enter New Pin", font=("Arial", 20), fg='white', bg='black').pack(pady=10)
        tkinter.Entry(self.root, font=("Arial", 20), show='*', textvariable=new_pin).pack(pady=10)
   

        def add_user():
            if not new_user.get() or not new_pin.get():
                self.status.set("Please enter both fields")
                self.root.after(5000, lambda:self.status.set(""))
                return
            con = sqlite3.connect("users.db")
            cur=con.cursor()
            try:
                cur.execute("INSERT INTO users (name, pin) VALUES (?, ?)", (new_user.get(), new_pin.get()))
                con.commit()
                self.status.set(f"Added {new_user.get()}")
                self.root.after(5000, lambda:self.status.set(""))

            except sqlite3.IntegrityError:
                self.status.set("User already exists")
                self.root.after(5000, lambda:self.status.set(""))
            finally:
                con.close()
                self.show_admin_settings()
            con.close()
            self.status.set(f"Added {new_user.get()}")
            self.root.after(2000, self.build_page)
        button_frame=tkinter.Frame(self.root)
        button_frame.pack(pady=20)
            
        tkinter.Button(button_frame, text="Add", font=("Arial", 20), command=add_user).pack(side="left",padx=10)
        tkinter.Button(button_frame, text="Back", font=("Arial", 20), command=self.show_admin_settings).pack(side="left",padx=10)
        tkinter.Label(self.root, textvariable=self.status, font=("Arial", 20), fg='white', bg='black').pack(pady=10)

            

    def show_admin_settings(self):
        self.clear()
        tkinter.Label(self.root,text="Admin Settings",font=("Arial", 25),fg='white',bg='black').pack(pady=20)
        button_frame=tkinter.Frame(self.root)
        button_frame.pack(pady=20)
        #add user 
        tkinter.Button(button_frame,text="Add User",font=("Arial", 20),command=self.add_user).pack(side="left",padx=10)
        #remove user
        tkinter.Button(button_frame,text="Remove User",font=("Arial", 20),command=self.remove_user).pack(side="left",padx=10)

        tkinter.Button(self.root,text="Back",font=("Arial", 20),command=self.build_page).pack(pady=10)






      

if __name__=="__main__":
    root=tkinter.Tk()
    app=Mailbox(root)
    root.mainloop()
