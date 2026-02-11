import random

class wrong_press():
    def __init__(self):
        self.response_list = [
            "Press your own buttons!",
            "MageGPT, generate a button that IShowWizardry users will love to press!",
            "That's someone else's button!",
            "Did you press the wrong button?",
            "Is there something wrong with you?",
            "I hate you.",
            "Stop that",
            "You can't do that!",
            "The wizard council has deemed you unworthy of pressing this button.",
            "I see more buttons in your future...",
            "Try a different button"
        ]
        
        self.response = random.choice(self.response_list)