import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import socket
import json
import os
from shared import send_frame, recv_frame

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ChatGUI:
    def __init__(self, server_ip, server_port, name):
        self.name = name



        self.win = ctk.CTk()
        self.win.title(f"Chat - {name}")
        self.win.geometry("650x550")



        self.chat_frame = ctk.CTkScrollableFrame(self.win, width=580, height=380)
        self.chat_frame.pack(pady=10)





        bottom = ctk.CTkFrame(self.win)
        bottom.pack(fill="x", pady=5)

        self.entry = ctk.CTkEntry(bottom, width=300)
        self.entry.grid(row=0, column=0, padx=10)
        self.entry.bind("<Return>", lambda e: self.send_message())

        ctk.CTkButton(bottom, text="Send", command=self.send_message).grid(row=0, column=1, padx=5)
        ctk.CTkButton(bottom, text="File", command=self.send_file).grid(row=0, column=2, padx=5)





        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((server_ip, server_port))
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.win.destroy()
            return

        send_frame(self.s, name.encode())
        threading.Thread(target=self.listen_server, daemon=True).start()

   




    def add_text_bubble(self, text, align="left"):
        bubble = ctk.CTkFrame(
            self.chat_frame,
            corner_radius=12,
            fg_color="#3B3B3B" if align == "left" else "#1F6FEB",
        )
        label = ctk.CTkLabel(bubble, text=text, wraplength=380, justify="left")
        label.pack(padx=10, pady=7)

        if align == "left":
            bubble.pack(anchor="w", pady=4, padx=10)
        else:
            bubble.pack(anchor="e", pady=4, padx=10)






    def add_file_bubble(self, sender, filename, filedata, align="left"):
        bubble = ctk.CTkFrame(
            self.chat_frame,
            corner_radius=12,
            fg_color="#3B3B3B" if align == "left" else "#1F6FEB",
        )

        label = ctk.CTkLabel(bubble, text=f"{sender} sent: {filename}", wraplength=380)
        label.pack(padx=10, pady=5)



        def download():
            save_path = filedialog.asksaveasfilename(initialfile=filename)
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(filedata)
                messagebox.showinfo("Download Complete", f"Saved to:\n{save_path}")



        if align == "left":
            dl_btn = ctk.CTkButton(bubble, text="Download File", command=download, width=120)
            dl_btn.pack(pady=5)




        if align == "left":
            bubble.pack(anchor="w", pady=4, padx=10)
        else:
            bubble.pack(anchor="e", pady=4, padx=10)





    def send_message(self):
        msg = self.entry.get().strip()
        if msg:
            packet = b"\x01" + f"{self.name}: {msg}".encode()
            send_frame(self.s, packet)

            self.add_text_bubble(f"You: {msg}", "right")
            self.entry.delete(0, tk.END)





    def send_file(self):
        fname = filedialog.askopenfilename()
        if not fname:
            return

        try:
            with open(fname, "rb") as f:
                filedata = f.read()

            metadata = {
                "sender": self.name,
                "filename": os.path.basename(fname),
                "size": len(filedata),
            }

            send_frame(self.s, b"\x02" + json.dumps(metadata).encode())
            send_frame(self.s, filedata)


            self.add_file_bubble("You", metadata["filename"], filedata, "right")

        except Exception as e:
            messagebox.showerror("File Error", str(e))






    def listen_server(self):
        while True:
            try:
                data = recv_frame(self.s)
                if not data:
                    break

                msg_type = data[0]
                payload = data[1:]


                if msg_type == 0x01:
                    text = payload.decode()

                    if not text.startswith(self.name + ":"):
                        self.add_text_bubble(text, "left")


                elif msg_type == 0x02:
                    metadata = json.loads(payload.decode())
                    filename = metadata["filename"]
                    sender = metadata["sender"]

                    filedata = recv_frame(self.s)


                    if sender != self.name:
                        self.add_file_bubble(sender, filename, filedata, "left")

            except:
                break

        self.s.close()
        self.add_text_bubble("Disconnected from server", "left")

    def run(self):
        self.win.mainloop()






if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python client_gui.py <server_ip> <port> <name>")
        exit()

    ip = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]

    ChatGUI(ip, port, name).run()
