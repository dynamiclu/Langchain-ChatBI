from configs.config import *
from chains.chatbi_chain import ChatBiChain
from common.log import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr
import argparse
import uvicorn
import os
import shutil

chain = ChatBiChain()
embedding_model_dict_list = list(embedding_model_dict.keys())

llm_model_dict_list = list(llm_model_dict.keys())

def get_file_list():
    if not os.path.exists("knowledge/content"):
        return []
    return [f for f in os.listdir("knowledge/content")]

file_list = get_file_list()

def upload_file(file):
    if not os.path.exists("knowledge/content"):
        os.mkdir("knowledge/content")
    filename = os.path.basename(file.name)
    shutil.move(file.name, "knowledge/content/" + filename)
    file_list.insert(0, filename)
    return gr.Dropdown(choices=file_list, value=filename)

def reinit_model(llm_model, embedding_model, llm_history_len, top_k, history):
    try:
        chain.init_cfg(llm_model=llm_model,
                         embedding_model=embedding_model,
                         llm_history_len=llm_history_len,
                         top_k=top_k)
        model_msg = """LLM模型已成功重新加载，请选择文件后点击"加载文件"按钮，再发送消息"""
    except Exception as e:
        logger.error(e)
        model_msg = """sorry，模型未成功重新加载，请重新选择后点击"加载模型"按钮"""
    return history + [[None, model_msg]]

def get_answer(query, vs_path, history, top_k):
    if vs_path:
        history = history + [[query, None]]
        result = chain.run_answer(query=query, vs_path=vs_path, chat_history=history, top_k=top_k)
        history = history + [[None, result]]
        return history, ""
    else:
        history = history + [[None, "请先加载文件后，再进行提问。"]]
        return history, ""

def get_vector_store(filepath, history):
    if chain.llm and chain.service:
        vs_path = chain.service.init_knowledge_vector_store(["knowledge/content/" + filepath])
        if vs_path:
            file_status = "文件已成功加载，请开始提问"
        else:
            file_status = "文件未成功加载，请重新上传文件"
    else:
        file_status = "模型未完成加载，请先在加载模型后再导入文件"
        vs_path = None
    return vs_path, history + [[None, file_status]]


def init_model():
    try:
        chain.init_cfg()
        return """模型已成功加载，请选择文件后点击"加载文件"按钮"""
    except:
        return """模型未成功加载，请重新选择后点击"加载模型"按钮"""


block_css = """.importantButton {
    background: linear-gradient(45deg, #7e05ff,#5d1c99, #6e00ff) !important;
    border: none !important;
}

.importantButton:hover {
    background: linear-gradient(45deg, #ff00e0,#8500ff, #6e00ff) !important;
    border: none !important;
}

#chat_bi {
    height: 100%;
    min-height: 455px;
}
"""

webui_title = """
# Langchain-ChatBI 项目
"""
init_message = """欢迎使用ChatBI，需点击'重新加载模型'，若选择Embedding模型，需选择或上传语料，再点击‘加载文件’ """

model_status = init_model()

with gr.Blocks(css=block_css) as demo:
    vs_path, file_status, model_status = gr.State(""), gr.State(""), gr.State(model_status)
    gr.Markdown(webui_title)
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label=init_message, elem_id="chat_bi", show_label=True)
            query = gr.Textbox(show_label=True, placeholder="请输入提问内容，按回车进行提交", label="输入框")
            send = gr.Button("🚀 发送")
        with gr.Column(scale=1):
            llm_model = gr.Radio(llm_model_dict_list,
                                 label="LLM 模型",
                                 value=LLM_MODEL_CHAT_GLM,
                                 interactive=True)
            llm_history_len = gr.Slider(0,
                                        10,
                                        value=5,
                                        step=1,
                                        label="LLM history len",
                                        interactive=True)
            embedding_model = gr.Radio(embedding_model_dict_list,
                                       label="Embedding 模型",
                                       value=EMBEDDING_MODEL_DEFAULT,
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
                           inputs=[selectFile, chatbot],
                           outputs=[vs_path, chatbot],
                           )
    query.submit(get_answer,
                 show_progress=True,
                 inputs=[query, vs_path, chatbot, top_k],
                 outputs=[chatbot, query],
                 )
    # 发送按钮 提交
    send.click(get_answer,
               show_progress=True,
               inputs=[query, vs_path, chatbot, top_k],
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
