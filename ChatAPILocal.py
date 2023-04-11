import threading
import tkinter as tk
from tkinter import ttk

import openai
from pyperclip import copy


class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("Chat with OpenAI")

        # Create API key input box
        self.api_key_frame = tk.Frame(master)
        self.api_key_frame.grid(row=0, column=0, padx=10, pady=10)

        self.api_key_label = tk.Label(self.api_key_frame, text="OpenAI API Key:")
        self.api_key_label.grid(row=0, column=0, padx=5)

        self.api_key_box = tk.Entry(self.api_key_frame, width=50)
        self.api_key_box.grid(row=0, column=1, padx=5)
        self.api_key_box.insert(tk.END, "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")

        # Create model selection frame
        self.model_selection_frame = tk.Frame(master)
        self.model_selection_frame.grid(row=1, column=0, padx=10, pady=10)

        self.model_label = tk.Label(self.model_selection_frame, text="选择模型:")
        self.model_label.grid(row=0, column=0, padx=5)

        # Create a variable to store the selected model
        self.selected_model = tk.StringVar()

        # Create radio buttons for each model option
        models = [
            ("gpt-3.5-turbo", "gpt-3.5-turbo")
        ]

        for i, (model, model_name) in enumerate(models):
            button = ttk.Radiobutton(self.model_selection_frame, text=model, variable=self.selected_model,
                                     value=model_name)
            button.grid(row=0, column=i + 1, padx=5)

        self.selected_model.set("gpt-3.5-turbo")
        # Create slider for temperature value
        self.temperature_label = tk.Label(self.model_selection_frame, text="Temperature:")
        self.temperature_label.grid(row=1, column=0, padx=5)

        self.temperature_slider = tk.Scale(self.model_selection_frame, from_=0.1, to=2.0, resolution=0.1,
                                           orient=tk.HORIZONTAL,
                                           length=200)
        self.temperature_slider.grid(row=1, column=1, padx=5)
        self.temperature_slider.set('0.2')
        # Create slider for max token value
        self.max_token_label = tk.Label(self.model_selection_frame, text="Max Token:")
        self.max_token_label.grid(row=2, column=0, padx=5)

        self.max_token_slider = tk.Scale(self.model_selection_frame, from_=10, to=2000, resolution=10,
                                         orient=tk.HORIZONTAL,
                                         length=200)
        self.max_token_slider.grid(row=2, column=1, padx=5)
        self.max_token_slider.set('1000')
        # Create task input box
        self.input_task_frame = tk.Frame(master)
        self.input_task_frame.grid(row=2, column=0, padx=10, pady=10)

        self.input_task_label = tk.Label(self.input_task_frame, text="当前任务（可选）")
        self.input_task_label.grid(row=0, column=0, padx=5)

        self.input_task_box = tk.Entry(self.input_task_frame, width=50)
        self.input_task_box.grid(row=0, column=1, padx=5)
        self.input_task_box.insert(tk.END, "请帮我翻译")

        # Create message input box
        self.input_frame = tk.Frame(master)
        self.input_frame.grid(row=3, column=0, padx=10, pady=10)

        self.input_label = tk.Label(self.input_frame, text="输入文字（回复会复制到剪切板）")
        self.input_label.grid(row=0, column=0, padx=5)

        self.input_box = tk.Entry(self.input_frame, width=50)
        self.input_box.grid(row=0, column=1, padx=5)

        self.send_button = ttk.Button(self.input_frame, text="发送", command=self.send_message)
        self.send_button.grid(row=0, column=2, padx=5)

        # Create chat log box
        self.chatlog = tk.Text(master, state=tk.DISABLED)
        self.chatlog.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        self.chatlog.configure(state=tk.NORMAL)
        self.chatlog.insert(tk.END, "Chat with OpenAI")
        self.chatlog.configure(state=tk.DISABLED)

    def send_message(self):
        # Get API key and set it
        api_key = self.api_key_box.get()
        openai.api_key = api_key

        message = self.input_box.get()
        prompt = self.input_task_box.get()
        self.input_box.delete(0, tk.END)

        self.chatlog.configure(state=tk.NORMAL)
        self.chatlog.insert(tk.END, "\nYou: {}".format(prompt + message))
        self.chatlog.insert(tk.END, "\nChatGPT: ")
        self.chatlog.configure(state=tk.DISABLED)

        try:
            def get_response():
                response = openai.ChatCompletion.create(
                    messages=[
                        {'role': 'user', 'content': prompt + message}
                    ],
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.2,
                    model=self.selected_model.get(),
                    stream=True
                )
                chatGPT_response = ""
                line = next(response, '[DONE]')
                while line != '[DONE]':
                    if 'content' in line.choices[0].delta:  # 处理返回的数据
                        chatGPT_response += line.choices[0].delta.content
                        self.chatlog.configure(state=tk.NORMAL)
                        self.chatlog.insert(tk.END, "{}".format(line.choices[0].delta.content))
                        self.chatlog.configure(state=tk.DISABLED)
                    else:
                        self.chatlog.configure(state=tk.NORMAL)
                        self.chatlog.insert(tk.END, "\n[非文本响应]\n")
                        self.chatlog.configure(state=tk.DISABLED)
                        print(line)

                    line = next(response, '[DONE]')

                # 将响应复制到剪贴板
                copy(chatGPT_response)

            # 创建线程并启动
            threading.Thread(target=get_response).start()
        except Exception as e:
            print(e)
            self.chatlog.configure(state=tk.NORMAL)
            self.chatlog.insert(tk.END, "\n{}\n".format(e))
            self.chatlog.configure(state=tk.DISABLED)



root = tk.Tk()
gui = ChatGUI(root)
root.mainloop()
