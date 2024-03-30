import dataclasses
import pickle
from abc import abstractmethod
from typing import Dict
import os.path
import jinja2

@dataclasses.dataclass
class Message:
    """
    A class encapsualating an LLM message.
    Role should be either "assistant" or "user".
    "Assistant" means its a message from the LLM.
    "User" means its a message from the MUD or this bridge.
    """
    role: str
    content: str


@dataclasses.dataclass
class LLMMessage:
    """
    A class encapsulating the broken down messages from the LLM.
    "OOC" means its an out of context/character message
    "System" means its a system message (To be used by the bridge)
    "Command" means its a command for the MUD
    """
    role: str
    content: str


class BaseLLMProvider:

    def __init__(self, model: str, api_key: str):
        """
        Initialize the class with the provided model and API key.
        Parameters:
            model (type): Description of the model parameter.
            api_key (type): Description of the api_key parameter.
        Returns:
            None
        """
        self.system = None
        self.is_new_buffer = True
        self.include_system = False
        self.messages = []
        self.parsed_message = None
        self.llm_messages = []
        self.model = model
        self.api_key = api_key
        self.reset_messages()
        self.max_tokens = 256
        self.filename = None

    def load_buffer(self, filename):
        """
        Load buffer data from a specified file and store it in the object.
        Parameters:
            filename (str): The name of the file to load the buffer from.

        Returns:
            None
        """
        self.filename = "Buffers/"+ filename + '.pkl'
        self.is_new_buffer = not os.path.exists(self.filename)
        if not self.is_new_buffer:
            self.messages = pickle.load(open(self.filename, 'rb'))
            print("Loaded buffer from: " + self.filename)
        else:
            print("Buffer not found: " + self.filename)
            self.messages = []

    def writeHTML(self):
        """
        A function that writes HTML content to a file based on a template and the buffer.
        Parameters:
        - No explicit parameters
        Returns:
        - No return value
        """
        html = jinja2.Template(open('template/template.html').read()).render(messages=self.messages)
        fn = self.filename.replace('.pkl', '.html')
        with open(fn, 'w') as f:
            f.write(html)


    def save_buffer(self):
        """
        Save the buffer to a file if a filename is provided.
        Parameters:
            None
        Returns:
            None
        """
        if self.filename is not None:
            pickle.dump(self.messages, open(self.filename, 'wb'))

    def set_token_limit(self, max_tokens):
        """
        Set the maximum number of tokens for token limit.
        Parameters:
            max_tokens (int): The maximum number of tokens to be set.
        Return:
            None
        """
        self.max_tokens = max_tokens


    def set_system(self, system: str):
        """
        Set the system message.

        Args:
            system (str): The system message.
        """
        self.system = system

    def add_message(self, role, content):
        """
        Add a new message to the messages list.

        Args:
            role (str): The role of the sender.
            content (str): The content of the message.
        """
        self.messages.append(Message(role, content))

    def reset_messages(self):
        """
        Reset the messages list.
        """
        self.messages = []

    def parse_message(self, message: Message) -> Dict[str, any]:
        """
        Parse a message into a dictionary. Override this if we want to use a different format

        Args:
            message (Message): The message to parse.

        Returns:
            Dict[str, any]: The parsed message.
        """
        self.parsed_message = {
            "role": message.role,
            "content": message.content
        }
        return self.parsed_message

    def get_messages(self) -> [Dict[str, any]]:
        """
        Get the list of messages.

        Returns:
            [Message]: The list of messages.
        """
        l =  [self.parse_message(message) for message in self.messages]
        if self.include_system:
            l.insert(0,self.parse_message(Message("system", self.system)))
        return l

    @abstractmethod
    def login(self):
        """
        Abstract method. Put the initialization in HERE.
        """
        print("Login not implemented")
        assert False

    @abstractmethod
    def send(self):
        """
        Abstract method. Put the code that sends the message buffer to the LLM here.
        :return:
        """
        print("send_messages not implemented")
        assert False


    def text_to_parts(self, text: str) -> [LLMMessage]:
        """
         Splits the given text into parts based on newline characters and converts each part into an LLMMessage object.
         Args:
             text (str): The text to be split into parts.
         Returns:
             List[LLMMessage]: A list of LLMMessage objects representing the parts of the text.
         """
        parts = text.split("\n")
        results = []
        for part in parts:
            if part[:4] == "OOC>":
                message = part[4:]
                results.append(LLMMessage(role="OOC", content=message))
            elif part[:7] == "System>":
                message = part[7:]
                results.append(LLMMessage(role="System", content=message))
            elif part[:8] == "Command>":
                message = part[8:]
                results.append(LLMMessage(role="Command", content=message))
            else:
                print(f"Unrecognized part: {part}")
        self.llm_messages = results
        return results
