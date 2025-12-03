import os
from src.core.voice import speak, listen_command, get_text_command

class NoteManager:
    def __init__(self, notes_dir=None):
        self.notes_dir = os.path.abspath(notes_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'Notes'))
        os.makedirs(self.notes_dir, exist_ok=True)

    def create_note(self, title):
        filename = os.path.join(self.notes_dir, f"{title}.txt")
        speak("What should I write in the note?")
        content = listen_command() or get_text_command()
        if content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            speak(f"Note '{title}' created.")

    def add_to_note(self, title):
        filename = os.path.join(self.notes_dir, f"{title}.txt")
        if os.path.exists(filename):
            speak("What would you like to add?")
            content = listen_command() or get_text_command()
            if content:
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write('\n' + content)
                speak(f"Added to note '{title}'.")
        else:
            speak(f"Note '{title}' does not exist.")

    def read_note(self, title):
        filename = os.path.join(self.notes_dir, f"{title}.txt")
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            speak(f"Here is the content of {title}: {content}")
        else:
            speak(f"Note '{title}' not found.")

    def list_notes(self):
        files = os.listdir(self.notes_dir)
        notes = [f[:-4] for f in files if f.endswith('.txt')]
        if notes:
            speak("Your notes are: " + ", ".join(notes))
        else:
            speak("You have no notes.")

    def delete_note(self, title):
        filename = os.path.join(self.notes_dir, f"{title}.txt")
        if os.path.exists(filename):
            os.remove(filename)
            speak(f"Deleted note '{title}'")
        else:
            speak(f"Note '{title}' not found.")

note_manager = NoteManager()

def handle_note_operations(command):
    try:
        if 'note' in command:
            if 'create' in command:
                speak("What would you like to title your note?")
                title = listen_command() or get_text_command()
                if title:
                    note_manager.create_note(title)

            elif 'add to' in command:
                speak("Which note would you like to add to?")
                title = listen_command() or get_text_command()
                if title:
                    note_manager.add_to_note(title)

            elif 'read' in command:
                speak("Which note would you like to read?")
                title = listen_command() or get_text_command()
                if title:
                    note_manager.read_note(title)

            elif 'list' in command:
                note_manager.list_notes()

            elif 'delete' in command:
                speak("Which note would you like to delete?")
                title = listen_command() or get_text_command()
                if title:
                    note_manager.delete_note(title)

            else:
                speak("Please specify what you'd like to do with notes: create, add to, read, list, or delete")
    except Exception as e:
        speak(f"An error occurred while handling notes: {e}")
