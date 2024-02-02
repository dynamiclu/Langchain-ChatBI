from configs.config import *
import gradio as gr
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil


embedding_model_dict_list = list(embedding_model_dict.keys())

llm_model_dict_list = list(llm_model_dict.keys())

dialogue_dict_list = list(dialogue_dict.keys())


def get_file_list():
    if not os.path.exists("content"):
        return []
    return [f for f in os.listdir("content")]


file_list = get_file_list()


def upload_file(file):
    if not os.path.exists("content"):
        os.mkdir("content")
    filename = os.path.basename(file.name)
    shutil.move(file.name, "content/" + filename)
    # file_list首位插入新上传的文件
    file_list.insert(0, filename)
    return gr.Dropdown(choices=file_list, value=filename)

def reinit_model():
    return  ""

def get_answer(query, vs_path, history, top_k, embedding_model,llm_history_len):
     return history, ""



def get_vector_store(filepath, history, embedding_model):

    return vs_path, history + [[None, file_status]]


def init_model():
    try:
        return """模型已成功加载，请选择文件后点击"加载文件"按钮"""
    except:
        return """模型未成功加载，请重新选择后点击"加载模型"按钮"""


block_css = """.importantButton {
    background: linear-gradient(45deg, #7e0570,#5d1c99, #6e00ff) !important;
    border: none !important;
}

.importantButton:hover {
    background: linear-gradient(45deg, #ff00e0,#8500ff, #6e00ff) !important;
    border: none !important;
}

#chat_ai_bi {
    height: 100%;
    min-height: 540px;
}
"""

webui_title = """
# 🎉Langchain-ChatBI 项目🎉
"""
init_message = """欢迎使用ChatBI，需点击'重新加载模型'，若选择Embedding模型，需选择或上传语料，再点击‘加载文件’ """

model_status = init_model()

with gr.Blocks(css=block_css) as demo:
    vs_path, file_status, model_status = gr.State(""), gr.State(""), gr.State(model_status)
    gr.Markdown(webui_title)
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label=init_message, elem_id="chat_ai_bi", show_label=True)
            query = gr.Textbox(show_label=True, placeholder="请输入提问内容，按回车进行提交", label="输入框")
            send = gr.Button("🚀 发送")
        with gr.Column(scale=1):
            llm_model = gr.Radio(llm_model_dict_list,
                                 label="LLM 模型",
                                 value=LLM_MODEL,
                                 interactive=True)
            llm_history_len = gr.Slider(0,
                                        10,
                                        value=5,
                                        step=1,
                                        label="LLM history len",
                                        interactive=True)
            embedding_model = gr.Radio(embedding_model_dict_list,
                                       label="Embedding 模型",
                                       value=WEB_EMBEDDING_MODEL_DEFAULT,
                                       interactive=True)
            top_k = gr.Slider(1,
                              20,
                              value=6,
                              step=1,
                              label="向量匹配 top k",
                              interactive=True)
            load_model_button = gr.Button("重新加载模型")

            with gr.Tab("select"):
                selectFile = gr.Dropdown(file_list,
                                         label="content file",
                                         interactive=True,
                                         value=file_list[0] if len(file_list) > 0 else None)
            with gr.Tab("upload"):
                file = gr.File(label="content file",
                               file_types=['.txt', '.md', '.docx', '.pdf']
                               )  # .style(height=100)
            load_file_button = gr.Button("加载文件")
    load_model_button.click(reinit_model,
                            show_progress=True,
                            inputs=[llm_model, embedding_model, llm_history_len, top_k, chatbot],
                            outputs=chatbot
                            )
    # 将上传的文件保存到content文件夹下,并更新下拉框
    file.upload(upload_file,
                inputs=file,
                outputs=selectFile)
    load_file_button.click(get_vector_store,
                           show_progress=True,
                           inputs=[selectFile, chatbot, embedding_model],
                           outputs=[vs_path, chatbot],
                           )
    query.submit(get_answer,
                 show_progress=True,
                 inputs=[query, vs_path, chatbot, top_k, embedding_model, llm_history_len],
                 outputs=[chatbot, query],
                 )
    # 发送按钮 提交
    send.click(get_answer,
               show_progress=True,
               inputs=[query, vs_path, chatbot, top_k, embedding_model, llm_history_len],
               outputs=[chatbot, query],
               )


app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default=WEB_SERVER_NAME)
    parser.add_argument("--port", type=int, default=WEB_SERVER_PORT)
    parser.add_argument("--async", type=int, default=0)
    args = parser.parse_args()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(app, host=args.host, port=args.port)
