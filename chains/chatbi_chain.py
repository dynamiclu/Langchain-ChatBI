from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers.json import parse_json_markdown
from langchain.chains import RetrievalQA, LLMChain
from langchain.memory import ConversationBufferWindowMemory
from common.structured import StructuredOutputParser, ResponseSchema
from common.log import logger
from common.llm_output import out_json_data
from configs.config import *
from knowledge.source_service import SourceService
from models.llm_chatglm import ChatGLM
from models.llm_baichuan import LLMBaiChuan
from models.llm_tongyi import LLMTongyi
from query_data.query_execute import exe_query
import datetime

line_template = '\t"{name}": {type} '

time_today = datetime.date.today()
class ChatBiChain:
    llm: object = None
    service: object = None
    memory: object = None
    top_k: int = LLM_TOP_K
    llm_model: str
    his_query: str

    def init_cfg(self,
                 llm_model: str = LLM_MODEL_CHAT_GLM,
                 embedding_model: str = EMBEDDING_MODEL_DEFAULT,
                 llm_history_len=LLM_HISTORY_LEN,
                 top_k=LLM_TOP_K
                 ):
        self.init_mode(llm_model, llm_history_len)
        self.service = SourceService(embedding_model, LOCAL_EMBEDDING_DEVICE)
        self.his_query = ""
        self.top_k = top_k
        logger.info("--" * 30 + "ChatBiChain init " + "--" * 30)

    def init_mode(self, llm_model: str = LLM_MODEL_CHAT_GLM, llm_history_len: str = LLM_HISTORY_LEN):
        self.llm_model = llm_model
        self.memory = ConversationBufferWindowMemory(k=llm_history_len)
        if llm_model == LLM_MODEL_CHAT_GLM:
            self.llm = ChatGLM()
            self.llm.load_model(model_name_or_path=llm_model_dict[LLM_MODEL_CHAT_GLM],
                                llm_device=LOCAL_LLM_DEVICE)
            self.llm.history_len = llm_history_len
        elif llm_model == LLM_MODEL_BAICHUAN:
            self.llm = LLMBaiChuan()
        elif llm_model == LLM_MODEL_QIANWEN:
            self.llm = LLMTongyi()

    def run_answer(self, query, vs_path, chat_history, top_k=VECTOR_SEARCH_TOP_K):
        result_dict = {"data": "sorry，the query is fail"}
        out_dict = self.get_intent_identify(query)
        out_str = out_dict["info"]
        if out_dict["code"] == 200 and "回答:" in out_str:
            if "意图:完整" in out_str or "意图: 完整" in out_str:
                query = out_str.split("回答:")[1]
                # chat_history = chat_history + [[None, query]]
            else:
                result_dict["data"] = out_str.split("回答:")[1]
                return result_dict, chat_history
        else:
            result_dict["data"] = out_str
            return result_dict, chat_history
        try:
            resp = self.get_answer(query, vs_path, top_k)
            res_dict = parse_json_markdown(resp["result"])
            out_json = out_json_data(res_dict)
            result_dict["data"] = str(exe_query(out_json))
        except Exception as e:
            logger.error(e)
        return result_dict, chat_history

    def get_intent_identify(self, query: str):
        template = """ 你是智能数据分析助手，根据上下文和Human提问，识别对方数据分析意图('完整'、'缺失'、'闲聊')
                        ## 背景知识
                        完整：对方上下文信息中必须同时包含指标和时间范围，否则是缺失，例如：微博过去一个月的访问量，为完整
                        缺失：对方上下文信息不完整，只有时间段或只有指标，例如：微博的访问量量或过去一个月的访问量，都为缺失
                        闲聊：跟数据查询无关，如：你是谁

                        ## 回答约束
                        若数据分析意图为完整，要根据上下文信息总结成一句完整的语句，否则礼貌询问对方需要查询什么

                        ## 输出格式
                        意图:#，回答:#

                        {history}
                        Human: {human_input}
                    """
        out_dict = {"code": 500}
        prompt = PromptTemplate(
            input_variables=["history", "human_input"],
            template=template
        )
        _chain = LLMChain(llm=self.llm, prompt=prompt, verbose=True, memory=self.memory)
        try:
            out_dict["info"] = _chain.predict(human_input=query)
            out_dict["code"] = 200
        except Exception as e:
            print(e)
            out_dict["info"] = "sorry，LLM model (%s) is fail，wait a minute..." % self.llm_model
        return out_dict

    def get_answer(self, query: object, vs_path: str = VECTOR_STORE_PATH, top_k=VECTOR_SEARCH_TOP_K):
        response_schemas = [
            ResponseSchema(name="data_indicators", description="数据指标: 如 PV、UV"),
            ResponseSchema(name="operator_type", description="计算类型: 明细，求和，最大值，最小值，平均值"),
            ResponseSchema(name="time_type", description="时间类型: 天、周、月、小时"),
            ResponseSchema(name="dimensions", description="维度"),
            ResponseSchema(name="filters", description="过滤条件"),
            ResponseSchema(name="filter_type", description="过滤条件类型：大于，等于，小于，范围"),
            ResponseSchema(name="date_range", description="日期范围,需按当前日期计算，假如当前日期为：2023-12-01，问 过去三个月或近几个月，则输出2023-09-01，2023-11-30；问过去一个月或上个月，则输出2023-11-01，2023-11-30；问八月或8月，则输出2023-08-01，2023-08-31；"),
            ResponseSchema(name="compare_type", description="比较类型：无，同比，环比")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions(only_json=False)
        prompt = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    "从问题中抽取准确的信息，若不匹配，返回空，\n{format_instructions}，输出时，去掉备注 \n 当前日期:%s  \n 已知内容:{context}  \n 问题：{question}  " % time_today
                )
            ],
            input_variables=["context", "question"],
            partial_variables={"format_instructions": format_instructions}
        )
        vector_store = self.service.load_vector_store(vs_path)
        knowledge_chain = RetrievalQA.from_llm(
            llm=self.llm,
            retriever=vector_store.as_retriever(search_kwargs={"k": top_k}),
            prompt=prompt
        )
        knowledge_chain.combine_documents_chain.document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )
        knowledge_chain.return_source_documents = True
        result_dict = {}
        try:
            result_dict = knowledge_chain({"query": query})
        except Exception as e:
            logger.error(e)
            result_dict["result"] = "sorry，LLM model (%s) is fail，wait a minute..." % self.llm_model
        return result_dict
