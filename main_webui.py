from configs.config import *
from chains.chatbi_chain import ChatBiChain
from common.log import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr
import argparse
import uvicorn
import os
import re
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
        model_msg = """The LLM model has been successfully reloaded. Please select the file and click the "Load File" button to send the message again"""
    except Exception as e:
        logger.error(e)
        model_msg = """sorry，If the model does not reload successfully, click "Load model" button"""
    return history + [[None, model_msg]]


def get_answer(query, vs_path, history, top_k):
    if vs_path:
        history = history + [[query, None]]
        code = chain.run_answer(query=query, vs_path=vs_path, chat_history=history, top_k=top_k)

        html = """
           <head>
             <title>Awesome-pyecharts</title>
             <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.1/dist/echarts.min.js"></script>
           </head>

           <body>
             <div id="main" style="width: 300px;height:200px;"></div>
             <script>
               var myChart = echarts.init(document.getElementById("main"));

               var option = echarts_code;

               myChart.setOption(option);
             </script>
           </body>
           """
        html = html.replace("echarts_code", str(code))

        result = f"""<iframe style="width: 100%; height: 240px" srcdoc='{html}'></iframe>"""
        history = history + [[None, result]]
        return history, ""
    else:
        history = history + [[None, "Please load the file before you ask questions."]]
        return history, ""


def get_vector_store(filepath, history):
    if chain.llm and chain.service:
        vs_path = chain.service.init_knowledge_vector_store(["knowledge/content/" + filepath])
        if vs_path:
            file_status = "The file has been successfully loaded. Please start asking questions"
        else:
            file_status = "The file did not load successfully, please upload the file again"
    else:
        file_status = "The model did not finished loading, please load the model before loading the file"
        vs_path = None
    return vs_path, history + [[None, file_status]]


def init_model():
    try:
        chain.init_cfg()
        return """The model has been loaded successfully, please select the file and click the "Load file" button"""
    except:
        return """The model did not load successfully, please click "Load model" button"""


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
# Langchain-ChatBI Project
"""
init_message = """Welcome to the ChatBI, click 'Reload the model', if you choose the Embedding model, select or upload the corpus, and then click 'Load the File' """

model_status = init_model()

with gr.Blocks(css=block_css) as demo:
    vs_path, file_status, model_status = gr.State(""), gr.State(""), gr.State(model_status)
    gr.Markdown(webui_title)
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label=init_message, elem_id="chat_bi", show_label=True)
            query = gr.Textbox(show_label=True,
                               placeholder="Please enter the questions and submit them according to the return",
                               label="Input Field")
            send = gr.Button(" Submit")
        with gr.Column(scale=1):
            llm_model = gr.Radio(llm_model_dict_list,
                                 label="LLM Model",
                                 value=LLM_MODEL_CHAT_GLM,
                                 interactive=True)
            llm_history_len = gr.Slider(0,
                                        10,
                                        value=5,
                                        step=1,
                                        label="LLM history len",
                                        interactive=True)
            embedding_model = gr.Radio(embedding_model_dict_list,
                                       label="Embedding Model",
                                       value=EMBEDDING_MODEL_DEFAULT,
                                       interactive=True)
            top_k = gr.Slider(1,
                              20,
                              value=6,
                              step=1,
                              label="top k",
                              interactive=True)
            load_model_button = gr.Button("Reload Model")

            with gr.Tab("select"):
                selectFile = gr.Dropdown(file_list,
                                         label="content file",
                                         interactive=True,
                                         value=file_list[0] if len(file_list) > 0 else None)
            with gr.Tab("upload"):
                file = gr.File(label="content file",
                               file_types=['.txt', '.md', '.docx', '.pdf']
                               )  # .style(height=100)
            load_file_button = gr.Button("Load File")
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
