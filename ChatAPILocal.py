import threading
import tkinter as tk
import openai
from tkinter import ttk
from pyperclip import copy


class ChatGUI:

    def update_chatlog(self, content):
        self.chatlog.configure(state=tk.NORMAL)
        self.chatlog.insert(tk.END, content)
        self.chatlog.configure(state=tk.DISABLED)

    def __init__(self, master):
        self.master = master
        master.title("Chat with OpenAI")
        for i in range(4):
            self.master.grid_rowconfigure(i, weight=1)
        self.master.grid_rowconfigure(4, weight=99)
        self.master.grid_columnconfigure(0, weight=1)
        # Create API key input box
        self.api_key_frame = tk.Frame(master)
        self.api_key_frame.grid(row=0, column=0, padx=10, pady=10)

        self.api_key_label = tk.Label(self.api_key_frame, text="OpenAI API Key:")
        self.api_key_label.grid(row=0, column=0, padx=5)

        self.api_key_box = tk.Entry(self.api_key_frame)
        self.api_key_box.grid(row=0, column=1, padx=5, columnspan=3, sticky="ew")
        self.api_key_box.insert(tk.END, "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")
        # Create model selection frame
        self.model_selection_frame = tk.Frame(master)
        self.model_selection_frame.grid(row=1, column=0, padx=10, pady=10)

        self.model_label = tk.Label(self.model_selection_frame, text="选择模型:")
        self.model_label.grid(row=0, column=0, padx=5)

        # Create a variable to store the selected model
        self.selected_model = tk.StringVar()

        # Create dropdown for selecting the model
        models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"]
        self.model_dropdown = tk.OptionMenu(self.model_selection_frame, self.selected_model, *models)
        self.model_dropdown.grid(row=0, column=1, padx=5, columnspan=3, sticky="ew")

        self.selected_model.set(models[0])

        # Create slider for temperature value
        self.temperature_label = tk.Label(self.model_selection_frame, text="Temperature:")
        self.temperature_label.grid(row=1, column=0, padx=5)

        self.temperature_slider = tk.Scale(self.model_selection_frame, from_=0, to=2.0, resolution=0.01,
                                           orient=tk.HORIZONTAL,
                                           length=200)
        self.temperature_slider.grid(row=1, column=1, padx=5, columnspan=3, sticky="ew")

        self.temperature_slider.set('0.2')
        # Create slider for max token value
        self.top_p_label = tk.Label(self.model_selection_frame, text="Top_p:")
        self.top_p_label.grid(row=2, column=0, padx=5)

        self.top_p_slider = tk.Scale(self.model_selection_frame, from_=0, to=1, resolution=0.01,
                                     orient=tk.HORIZONTAL,
                                     length=200)
        self.top_p_slider.grid(row=2, column=1, padx=5, columnspan=3, sticky="ew")
        self.top_p_slider.set('1')
        # Create task input box
        self.input_task_frame = tk.Frame(master)
        self.input_task_frame.grid(row=2, column=0, padx=10, pady=10)

        self.input_task_label = tk.Label(self.input_task_frame, text="System:")
        self.input_task_label.grid(row=0, column=0, padx=5)

        self.input_task_box = tk.Entry(self.input_task_frame, width=50)
        self.input_task_box.grid(row=0, column=1, padx=5)
        self.input_task_box.insert(tk.END, "You are a helpful assistant that translates English to Chinese")

        # Create message input box
        self.input_frame = tk.Frame(master)
        self.input_frame.grid(row=3, column=0, padx=10, pady=10)

        self.input_label = tk.Label(self.input_frame, text="User")
        self.input_label.grid(row=0, column=0, padx=5)

        self.input_box = tk.Entry(self.input_frame, width=50)
        self.input_box.grid(row=0, column=1, padx=5)

        self.send_button = ttk.Button(self.input_frame, text="发送", command=self.send_message)
        self.send_button.grid(row=0, column=2, padx=5)

        # Create chat log box
        self.chatlog = tk.Text(master, state=tk.DISABLED)
        self.chatlog.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        self.update_chatlog("Chat with OpenAI")

    def send_message(self):
        self.send_button.configure(text="请求中...")
        self.send_button.config(state=tk.DISABLED)
        # Get API key and set it
        api_key = self.api_key_box.get()
        openai.api_key = api_key

        message = self.input_box.get()
        prompt = self.input_task_box.get()
        self.input_box.delete(0, tk.END)

        self.update_chatlog("\nSystem:" + prompt + "\nYou:" + message + "\nChatGPT: ")

        try:
            def get_response():
                response = openai.ChatCompletion.create(
                    messages=[
                        {"role": "system", "content": prompt},
                        {'role': 'user', 'content': message}
                    ],
                    top_p=self.top_p_slider.get(),
                    n=1,
                    stop=None,
                    temperature=self.temperature_slider.get(),
                    model=self.selected_model.get(),
                    stream=True
                )
                chatGPT_response = ""
                line = next(response, '[DONE]')
                while line != '[DONE]':
                    if 'content' in line.choices[0].delta:  # 处理返回的数据
                        chatGPT_response += line.choices[0].delta.content
                        self.update_chatlog(line.choices[0].delta.content)
                    elif line.choices[0].finish_reason == "stop":
                        # 将响应复制到剪贴板
                        copy(chatGPT_response)
                        self.update_chatlog("\n[结束]\n[回复已复制到剪切板]\n")
                        self.send_button.configure(text="发送")
                        self.send_button.config(state=tk.NORMAL)
                    elif 'role' in line.choices[0].delta:
                        self.update_chatlog("\n[开始]\n")
                    else:
                        # 将响应复制到剪贴板
                        copy(chatGPT_response)
                        self.update_chatlog("\n[错误]\n[回复已复制到剪切板]\n")
                        self.send_button.configure(text="发送")
                        self.send_button.config(state=tk.NORMAL)
                        print(line)

                    line = next(response, '[DONE]')

            # 创建线程并启动
            threading.Thread(target=get_response).start()
        except Exception as e:
            print(e)
            self.update_chatlog("\n" + str(e) + "\n")


root = tk.Tk()
gui = ChatGUI(root)
root.mainloop()
