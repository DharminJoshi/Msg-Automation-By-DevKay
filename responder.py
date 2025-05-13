import datetime
import json
import random
from pathlib import Path
from termcolor import colored
import pyperclip
import re

class DevKaySmartResponder:
    def __init__(self, sender_name="*Dharmin Joshi", sender_alias="DevKay*", history_file='message_history.json', config_file='config.json'):
        self.sender_name = sender_name
        self.sender_alias = sender_alias
        self.history_file = Path(history_file)
        self.config_file = Path(config_file)
        self.history = self.load_history()
        self.config = self.load_config()

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(colored("Error reading the JSON history file. It might be corrupted.", "red"))
                return []
        return []

    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(colored("Error reading the config file. It might be corrupted.", "red"))
                return {}
        print(colored("Config file not found, using default settings.", "yellow"))
        return {}

    def save_history(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as file:
            json.dump(self.history, file, indent=4)

    def categorize_message(self, message):
        msg = message.lower()
        categories = self.config.get("categories", {})
        triggered = []

        for category, keywords in categories.items():
            if any(keyword in msg for keyword in keywords):
                triggered.append(category)

        return triggered if triggered else ["general"]

    def detect_greeting(self, message):
        greetings = ["hi", "hello", "hey", "greetings"]
        return any(greet in message.lower() for greet in greetings)

    def get_greeting_response(self):
        return random.choice([
            "Hi there! 😊",
            "Hello! 👋",
            "Hey! How can I help you today?",
            "Greetings! Happy to assist."
        ])

    def get_response_for_category(self, category):
        responses = self.config.get("responses", {})
        cat_responses = responses.get(category, [])

        if not cat_responses:
            return self.get_default_response(category)

        selected = random.choice(cat_responses)
        tail = {
            "support_issue": " We're actively looking into it.",
            "request": " Let me know if there's anything else you’d like.",
            "inquiry": " I’ll get back to you with more information shortly.",
            "appreciation": " Your kind words mean a lot to us!",
            "greeting": " Always good to hear from you!"
        }

        return selected + tail.get(category, "")

    def get_default_response(self, category):
        return {
            "support_issue": "We've noted the issue and will investigate it promptly.",
            "request": "Your request has been acknowledged.",
            "inquiry": "Thanks for asking. We'll get back to you shortly.",
            "appreciation": "Thanks for the kind words!",
            "greeting": "Hi there!"
        }.get(category, "Thank you for reaching out. We'll get back to you soon.")

    def build_response_body(self, message, categories):
        segments = []

        # Greet if applicable
        if self.detect_greeting(message):
            segments.append(self.get_greeting_response())

        # Priority-based natural blending
        priority = ['support_issue', 'request', 'inquiry', 'appreciation']
        for cat in priority:
            if cat in categories:
                segments.append(self.get_response_for_category(cat))

        # Add any uncategorized or additional ones
        for cat in categories:
            if cat not in priority:
                segments.append(self.get_response_for_category(cat))

        return " ".join(segments)

    def generate_footer(self, timestamp, category):
        return colored(
            f"\n\nBest regards,\n{self.sender_name} / {self.sender_alias}\n\n"
            f"_Automated message generated from the DevKay Protocol._\n"
            f"_Category: {category} | Timestamp: {timestamp}_\n"
            f"_If you have any questions, feel free to ask. Thank you for your patience._",
            "blue"
        )

    def remove_color_codes(self, text):
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
        return ansi_escape.sub('', text)

    def generate_and_log_response(self, sender_message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        categories = self.categorize_message(sender_message)
        body = self.build_response_body(sender_message, categories)
        footer = self.generate_footer(timestamp, ", ".join(categories))

        full_response = f"{body}\n\n{footer}"
        plain = self.remove_color_codes(full_response)
        pyperclip.copy(plain)

        print(colored("\nResponse copied to clipboard!", "green"))

        self.history.append({
            "timestamp": timestamp,
            "input_message": sender_message,
            "category": ", ".join(categories),
            "automated_response": full_response
        })

        self.save_history()
        return full_response

if __name__ == "__main__":
    bot = DevKaySmartResponder()
    msg = input(colored("Enter sender's message: ", "green"))
    reply = bot.generate_and_log_response(msg)
    print(colored("\n--- Automated Reply ---", "cyan"))
    print(reply)
