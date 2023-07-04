from langchain import PromptTemplate, LLMChain, HuggingFaceHub
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from dotenv import load_dotenv, find_dotenv
import os
import streamlit as st
# from streamlit_chat import message
# from streamlit_extras.colored_header import colored_header
# from streamlit_extras.add_vertical_space import add_vertical_space
import datetime as dt
import random

# Retrieve Hugging Face Hub API token from .env file
load_dotenv()
huggingfacehub_api_token = os.environ['HUGGINGFACEHUB_API_TOKEN']

st.set_page_config(page_title='Falcon-7B-Instruct chat',
                   page_icon=':parrot:', layout="wide",
                   initial_sidebar_state="auto", menu_items=None)

def generate_response(input_text):
    """
    Predict text using the LLM conversation chain
    Parameters: input_text : str
    -----------
    Returns: response : str
    --------
    """
    response = conversation.predict(input=input_text,stop=['User',
                                                      '>>COMMENT<<','>>QUESTION<<','>>ANSWER<<',
                                                     '>>TITLE<<'])
    return response

def cache_chat():
    """
    Save any current chat history as a stored session
    """
    st.session_state['stored_sessions'].append(record)

def reset_session():
    """
    Clear the chat history container and the chatbot's memory
    """
    st.session_state['generated_history']=[]
    st.session_state['user_history']=[]
    if 'memory' in st.session_state:
        st.session_state.memory.clear()

def clear_stored_sessions():
    """
    Clear the list of stored chat sessions
    """
    del st.session_state.stored_sessions

def choose_example(string):
    """
    Populate the input textbox with
    the provided string
    """
    st.session_state['input']=string

# In function so we can use @st.cache to avoid
# repeating upon re-runs
# @st.cache_resource
def generate_random_falcon():
    """
    Generates a random falcon image
    """
    falcon_num = random.choice(range(4))
    st.image(image=f'./img/falcon{falcon_num}.jpeg',caption='generated by Stable Diffusion 2.1')

def generate_random_avatar():
    """
    Generates a random user avatar image
    """
    avatar_num = random.choice(range(5))
    return f'https://e-tweedy.github.io/images/user_avatar{avatar_num}.jpeg'

print(st.cache_resource)

# Set session states
if 'generated_history' not in st.session_state:
    st.session_state['generated_history']=[]
if 'user_history' not in st.session_state:
    st.session_state['user_history']=[]
if 'input' not in st.session_state:
    st.session_state['input']=''
if 'stored_sessions' not in st.session_state:
    st.session_state['stored_sessions']=[]
if 'user_avatar' not in st.session_state:
    st.session_state['user_avatar'] = generate_random_avatar()

falcon_image_container = st.sidebar.container()
with falcon_image_container:
    generate_random_falcon()
    
settings_container = st.sidebar.container()
sessions_container = st.sidebar.container()

with settings_container:
    st.caption('Chat settings:')
    with st.expander('Click to expand'):
        st.caption('Warning: Changing settings with reset LLM memory and chat history!')
        with st.form(key='settings_form',clear_on_submit=False):
            temperature = st.select_slider(label = 'temperature',
                                          value=0.1,options=[x/10 for x in range(1,21)],
                                          help='''
                                          Scaling factor in the exponents of the
                                          LLM output softmax function.
                                          Higher temperature will lead to more diverse output,
                                          but also increase likelihood of the LLM straying from
                                          the context.
                                          ''')
            top_p = st.select_slider(label = 'p for nucleus sampling',
                                     value=0.9,options=[x/100 for x in range(10,100)],
                                    help='''
                                    The LLM will select only from the minimum number of words
                                    whose probabilities sum to at least p.  Larger values of p
                                    allow the LLM to deviate from the most likely words.
                                    ''')
            max_new_tokens = st.select_slider(label = 'max tokens to output',
                                              value=256,options=range(10,513),
                                             help='''
                                             The maximum number of tokens in each response
                                             generated by the LLM.  Small values can lead to
                                             truncated responses, and large values can cause
                                             issues if model memory is too long.
                                             ''')
            repetition_penalty = st.select_slider(label = 'repetition penalty',
                                                  value=1.2,options=[x/10 for x in range(10,31)],
                                                 help='''
                                                 A scaling factor in the exponents of the LLM output
                                                 which discourage repetition in the output.  Setting this to
                                                 1 corresponds to no penalty, while higher values penalize
                                                 repetition more heavily.
                                                 ''')
            k = st.select_slider(label = 'memory length',
                                value=3,options=range(11),
                                help='''
                                The length of the chat session's memory, i.e. how many prior messages in the
                                chat thread the LLM will be provided on each generation.  Higher values can
                                cause issues if max tokens to output is also high.
                                ''')
            settings_submitted = st.form_submit_button('Confirm settings')
            if settings_submitted:
                del st.session_state.memory
                st.session_state['generated_history']=[]
                st.session_state['user_history']=[]

# Initialize LLM model
repo_id = "tiiuae/falcon-7b-instruct"
llm = HuggingFaceHub(huggingfacehub_api_token=huggingfacehub_api_token, 
                     repo_id=repo_id, 
                     model_kwargs={"temperature":temperature, "max_new_tokens":max_new_tokens,
                                  'repetition_penalty':repetition_penalty,'top_p':top_p})

# Set the prompt using a prompt template
template = """
Below is a conversation between a Human and a helpful and polite AI Assistant.  The AI gives responses that are both precise and concise.  If the AI does not know the answer to the Human's query, the AI will NOT guess, but will simply reply "I don't know".
{history}
>>QUESTION<<{input}
>>ANSWER<<
"""
prompt = PromptTemplate(template=template, input_variables=["input","history"])
record = []

# Initialize entity memory and conversation chain
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferWindowMemory(k=k)
conversation = ConversationChain(llm=llm, prompt = prompt,
                                 memory=st.session_state.memory)

st.header('Chat with Falcon-7B-Instruct')
st.caption('Mobile device users: use the arrow in the top left corner to access settings and stored sessions.')
st.markdown('''
Use this app to chat with Falcon-7B-Instruct, at 7-billion parameter instruction-tuned large language model released by the [Technology Innovation Institute](https://www.tii.ae/).

Visit [the model card](https://huggingface.co/tiiuae/falcon-7b-instruct) on [🤗](https://huggingface.co/) or try out the chat below.  Thanks to TII for making this model available to all!
''')

# Initialize containers for user input and chat feed
input_container = st.container()
st.divider()
response_container = st.container()

examples = ['Give me a synopsis of the movie "Up"',
            'How do I make a sandwich?',
            "What's the difference between nuclear fission and nuclear fusion?"]

# Form which collects user input and generates and stores LLM response
with input_container:
    st.caption('Choose an example or write your own.')
    for example in examples:
        st.button(label=example,on_click=choose_example,args=(example,))
    with st.form(key='input_form',clear_on_submit=True):
        user_input = st.text_input(label="You: ", value=st.session_state['input'],
                                                  key="input_box",label_visibility='hidden',
                                                  placeholder="I'm your AI assistant, How may I help you?")
        st.session_state['input']=user_input
        prompt_submitted = st.form_submit_button("Submit")
        if prompt_submitted:
            with st.spinner('Generating response...'):
                response = generate_response(user_input)
            st.session_state.user_history.append(user_input)
            st.session_state.generated_history.append(response)
            st.session_state['input']=''

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:       
    if st.session_state['generated_history']:
        for i in range(len(st.session_state['generated_history'])):
            with st.chat_message('user',avatar=st.session_state.user_avatar):
                st.write(st.session_state['user_history'][i])
            with st.chat_message('falcon',avatar='https://e-tweedy.github.io/images/falcon_avatar.jpeg'):
                st.write(st.session_state['generated_history'][i])
            # message(st.session_state['user_history'][i], is_user=True, key=str(i) + '_user')
            # message(st.session_state['generated_history'][i], key=str(i))
            record.append('\nHuman: '+st.session_state["user_history"][i])
            record.append('\nAI: '+st.session_state['generated_history'][i])
    record = dt.datetime.now().strftime("%m/%d/%Y, %H:%M")+'\n'+'\n'.join(record)
    no_record = False if record else True
    col1,col2,col3= st.columns(3)
    with col1:
        st.download_button(label='Download chat history',data = record,
                           key='download',disabled=no_record)
    with col2:
        st.button(label='Save chat history',on_click = cache_chat,
                           key='save',disabled=no_record)
    with col3:
        st.button(label='Reset chat session',on_click=reset_session,
                           key='reset',disabled=no_record)
    
with sessions_container:
    # Allow the user to clear all stored conversation sessions
    none_stored = True
    if 'stored_sessions' in st.session_state:
        if len(st.session_state.stored_sessions)>0:
            none_stored=False
    st.caption('Stored chat sessions:')
    st.button("Delete stored sessions", on_click = clear_stored_sessions,
                  disabled = none_stored)
    st.download_button("Download stored sessions",
                           data = '\n\n'.join(st.session_state.stored_sessions),
                           disabled = none_stored)
    for i, session in enumerate(st.session_state.stored_sessions):
        with st.expander(label=f'Conversation session {i+1}'):
            st.caption(session)
