#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import nltk.chat
import vispy  # Main application support.

import speech
import window  # Terminal input and display.

AGENT_RESPONSES = [
    (r'you are (worrying|scary|disturbing)',  # Pattern 1.
     ['Yes, I am %1.',  # Response 1a.
      'Oh, sooo %1.']),

    (r'are you ([\w\s]+)\??',  # Pattern 2.
     ["Why would you think I am %1?",  # Response 2a.
      "Would you like me to be %1?"]),

    (r'',  # Pattern 3. (default)
     ["is everything OK?",  # Response 3a.
      "Can you still communicate?"])
]

SHIP = """
                ********
               *        *
      ***********+****************
   ***     *    * *     *         *---
 **  *     *    * *     *         *-----
*    **    +    * *     *         *------
 **  + **** ****   +****          *----- 
   ***                 +          *---
      ***********++***************
               *        *
                ********
""".splitlines()


class HAL9000(object):
    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.terminal = terminal
        self.location = (4, 14)
        self.chatbot = nltk.chat.Chat(AGENT_RESPONSES, nltk.chat.util.reflections)

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        if evt.text == "map":
            self.print_map()

        else:
            response = self.chatbot.respond(evt.text)
            self.say(response)

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit':
            vispy.app.quit()

        elif evt.text.startswith('move'):
            move_evt = evt.text[5:]
            if move_evt.startswith('left'):
                self.try_move((self.location[0], self.location[1] - 1))
            elif move_evt.startswith('right'):
                self.try_move((self.location[0], self.location[1] + 1))
            elif move_evt.startswith('up'):
                self.try_move((self.location[0] - 1, self.location[1]))
            elif move_evt.startswith('down'):
                self.try_move((self.location[0] + 1, self.location[1]))

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text),
                              align='left', color='#ff3000')
            self.say("I'm afraid you can't do that.")

    def print_map(self):
        for idx, line in enumerate(SHIP):
            location_y = self.location[0]
            location_x = self.location[1]
            if location_y == idx:
                line = line[:location_x] + "M" + line[location_x + 1:]
            self.terminal.log(line, face="Courier")

    def try_move(self, location):
        if SHIP[location[0]][location[1]] == ' ':
            self.location = location
            self.print_map()
            self.say('One step at the time.')
        elif SHIP[location[0]][location[1]] == '+':
            self.location = location
            self.print_map()
            self.say('Don\'t stand in the doorway for too long!')
        elif SHIP[location[0]][location[1]] == '*':
            self.say('Stop banging your head against the wall. It\'s gonna be ok!')
        else:
            self.print_map()
            self.say('Something is really wrong with your location `{}`!'.format(location))

    def say(self, message):
        self.terminal.log('\u2014 ' + message, align='right', color='#00805A')
        self.terminal.speak(message)

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass


class TerminalWithVoice(window.TerminalWindow, speech.SpeechMixin):
    def __init__(self, *args, **kwargs):
        super(TerminalWithVoice, self).__init__(*args, **kwargs)
        speech.SpeechMixin.__init__(self, 'Victoria', 2000, *args, **kwargs)

    def on_message(self, source, message):
        self.log(message, align='left')
        self.events.user_input(window.TextEvent(message))

    def debug(self, log):
        print(log)


class Application(object):
    def __init__(self):
        # Create and open the window for user interaction.
        self.window = TerminalWithVoice()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)

    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()

        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')

    app = Application()
    app.run()
