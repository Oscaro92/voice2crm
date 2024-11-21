# * import libraries
import os, shutil
from openai import OpenAI
from pyairtable import Api
from decouple import config
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import AirtableLoader


class AppointmentInfo(BaseModel):
    id: str = Field(description="L'id du client dans le CRM", default="")
    action: str = Field(description="Action à attribuer dans le CRM : 'Target', '1er message', '2eme message', '1er RDV', '2eme RDV', 'Contrat', 'Signé'", default="")


class AgentCRM():
    def __init__(self):
        temperature = 0.0
        model = "gpt-4o-mini"
        os.environ["OPENAI_API_KEY"] = config('OPENAI_API_KEY')

        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.api_key = config('AIRTABLE_API_KEY')
        self.base_id = config('BASE_ID')
        self.table_id = config('TABLE_ID')


    def loadDoc(self)->list:
        '''
        Load all items from airtable

        :return: list of fields Airtable (Document)
        '''

        loader = AirtableLoader(self.api_key, self.table_id, self.base_id)
        docs = loader.load()

        return docs


    def saveDoc(self, docs: list):
        '''
        Save docs in ChromaDB

        :param docs: list of documents (here google Chrome files)
        :return: void
        '''
        if os.path.exists("chroma"):
            shutil.rmtree("chroma")

        db = Chroma.from_documents(docs, self.embeddings, persist_directory="chroma")
        db.persist()

        print(f"Saved {len(docs)} chunks to chroma.")


    def whisper(self, path: str)->str:
        '''
        Conversion speech to text

        :param path: path of local audio file
        :return: transcription
        '''
        client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

        audio_file = open(path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
            language='fr'
        )

        return transcription


    def similarity(self, query:str):
        '''
        Get doc with similarity score

        :param query: user request
        :return: list of similarities
        '''

        db = Chroma(persist_directory="chroma", embedding_function=self.embeddings)
        results = db.similarity_search_with_relevance_scores(query, k=3)

        result_filter = [result for result in results if result[1] >= 0.10]

        return result_filter


    def updateDoc(self, id: str, action: str)->str:
        '''
        Update status of client

        :param id: id of client
        :param action: action to update
        :return: updated or error
        '''
        try:
            api = Api(self.api_key)
            table = api.table(self.base_id, self.table_id)

            table.update(id, {"Status": action})

            return "updated"
        except:
            return "error"


    def chat(self, query: str, docs: list)->str:
        '''
        Chat with llm

        :param query: human text
        :param docs: docs loaded in RAG
        :return: 'ok' or 'error'
        '''

        parser = JsonOutputParser(pydantic_object=AppointmentInfo)
        parser = OutputFixingParser.from_llm(parser=parser, llm=self.llm)

        jason = {
            "id": "rec...",
            "action": ""
        }

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Tu es un assistant qui doit déterminer si une action est à faire à partir de cette liste : Target, 1er message, 2eme message, 1er RDV, 2eme RDV, Contrat, Signé.\n"
                    "Tu dois retourner l'id du client demandé parmis les documents suivant : {docs} \n"
                    "La réponse doit être au format json suivant : {jason}"
                    "SI aucune action correspond la valeur action est égal à nothing"
                ),
                ("human", "{query}"),
            ]
        )

        chain = prompt | self.llm | parser
        response = chain.invoke(
            {
                "docs": docs,
                "query": query,
                "jason": jason
            }
        )

        resp_return = self.updateDoc(response['id'], response['action'])

        if resp_return == 'error':
            return 'error'
        else:
            return 'ok'

