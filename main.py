# This is a sample Python script.
import time
from telnetlib import Telnet
from anthropic import Anthropic
from colored import Fore, Back
import dotenv
import os

dotenv.load_dotenv()

from LLMProviders.BaseLLMProvider import LLMMessage
from LLMProviders.ClaudeProvider import ClaudeProvider

API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")
MUD_ANTICIPATE_LOGIN = os.getenv("MUD_ANTICIPATE_LOGIN")
MUD_LOGIN_STR = os.getenv("MUD_LOGIN_STR")
MUD_HOST = os.getenv("MUD_HOST")
MUD_PORT = int(os.getenv("MUD_PORT"))

client = Anthropic(
    # This is the default and can be omitted
    api_key=API_KEY,
)

system =  open("data/claud_simple_prompt.txt", "r").read()
messages = []
buffer="<Reconnect after disconnect>"
newbuffer = ""
buffer=""
provider = ClaudeProvider(model=MODEL, api_key=API_KEY)

provider.set_system(system)
x = input("Buffer name> ")
provider.load_buffer(x)
if provider.is_new_buffer:
    buffer = open("data/compact_manual.txt").read()

provider.login()
print(f'Connecting to {MUD_HOST}:{MUD_PORT}')
def telnet_generator(tn, idle_timeout):
    start_time = time.time()
    while True:
        data = tn.read_eager()
        if data:
            print(Fore.black + Back.white + data.decode('utf-8'),)
            start_time = time.time()  # Reset the start time if there is incoming data
            yield data.decode('utf-8')
        elif time.time() - start_time > idle_timeout:
            yield None
with Telnet(MUD_HOST, MUD_PORT) as tn:
    print(f'Established... waiting for {MUD_ANTICIPATE_LOGIN} ')

    tn.read_until(MUD_ANTICIPATE_LOGIN.encode(),timeout=120)
    print(f'Logging in with {MUD_LOGIN_STR}')

    tn.write(((MUD_LOGIN_STR)+"\n").encode())
    idle_timeout = 20  # Adjust the idle timeout as needed
    telnet_gen = telnet_generator(tn, idle_timeout)

    while True:
        data = next(telnet_gen)
        if data:
            buffer += data
        else:
            provider.add_message("user", buffer)
            message = provider.send()
            reply: [LLMMessage] = provider.text_to_parts(message)
            commands = [v.content for v in reply if v.role == "Command"]

            for command in commands:
                print(Fore.yellow + Back.blue + "Claude:", command)
                tn.write((command + "\n").encode())

                command_buffer = ""
                while True:
                    data = next(telnet_gen)
                    if data:
                        command_buffer += data
                    else:
                        buffer += command_buffer
                        break

            ooc_messages = [v.content for v in reply if v.role == "OOC"]
            for ooc in ooc_messages:
                print(Fore.yellow + Back.white + "OOC:", ooc)

            provider.add_message("assistant", message)
            provider.save_buffer()
            provider.writeHTML()
