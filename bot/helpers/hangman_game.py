"""
Hangman Game Implementation
Interactive word guessing game with ASCII art visualization.

Author: Afnan Ahmed
Created: 2025
Description: Complete hangman game logic with visual representation,
             hint system, and difficulty progression.
Features: ASCII art display, word categories, hint system,
          attempt tracking, win/loss detection.
License: MIT
"""

import random

HANGMAN_PICS = [
    """
     +---+
         |
         |
         |
        ===
    """,
    """
     +---+
     O   |
         |
         |
        ===
    """,
    """
     +---+
     O   |
     |   |
         |
        ===
    """,
    """
     +---+
     O   |
    /|   |
         |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
         |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
    /    |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
    / \\  |
        ===
    """
]

WORDS_WITH_HINTS = [
    # Programming & Computer Science
    {"word": "python", "hint": "A popular programming language."},
    {"word": "javascript", "hint": "A scripting language used for web development."},
    {"word": "algorithm", "hint": "A process or set of rules to solve problems."},
    {"word": "debug", "hint": "To fix code errors."},
    {"word": "function", "hint": "A reusable block of code."},
    {"word": "variable", "hint": "A storage location in programming."},
    {"word": "syntax", "hint": "The structure of statements in a programming language."},
    {"word": "loop", "hint": "A sequence of instructions that repeats."},
    {"word": "array", "hint": "A collection of items stored at contiguous memory locations."},
    {"word": "recursion", "hint": "A function that calls itself."},
    {"word": "compiler", "hint": "A program that translates code into machine language."},
    {"word": "boolean", "hint": "A data type with two possible values: true or false."},
    
    # Web Development
    {"word": "discord", "hint": "A chat platform for communities."},
    {"word": "html", "hint": "The standard markup language for web pages."},
    {"word": "css", "hint": "A stylesheet language for designing web pages."},
    {"word": "react", "hint": "A JavaScript library for building user interfaces."},
    {"word": "backend", "hint": "The server-side part of a web application."},
    {"word": "api", "hint": "A set of protocols for building software applications."},
    {"word": "cookie", "hint": "A small piece of data stored on the user's computer."},
    {"word": "http", "hint": "A protocol for transmitting hypertext over the internet."},
    
    # Gaming & Entertainment
    {"word": "hangman", "hint": "A classic word-guessing game."},
    {"word": "minecraft", "hint": "A sandbox video game with blocks."},
    {"word": "chess", "hint": "A strategic board game for two players."},
    {"word": "pixel", "hint": "The smallest unit of a digital image."},
    {"word": "controller", "hint": "A device used to interact with video games."},
    {"word": "vr", "hint": "Short for Virtual Reality."},
    
    # Science & Technology
    {"word": "neural", "hint": "Related to artificial intelligence and brain-like networks."},
    {"word": "quantum", "hint": "A branch of physics dealing with subatomic particles."},
    {"word": "blockchain", "hint": "A decentralized digital ledger technology."},
    {"word": "encryption", "hint": "The process of converting data into a secure format."},
    {"word": "robot", "hint": "A machine capable of carrying out complex tasks automatically."},
    
    # Everyday Objects
    {"word": "keyboard", "hint": "An input device with keys for typing."},
    {"word": "monitor", "hint": "A screen that displays computer output."},
    {"word": "mouse", "hint": "A pointing device used with computers."},
    {"word": "printer", "hint": "A device that produces physical copies of digital documents."},
    
    # Nature & Animals
    {"word": "elephant", "hint": "The largest land animal."},
    {"word": "giraffe", "hint": "A tall African mammal with a long neck."},
    {"word": "dolphin", "hint": "A highly intelligent marine mammal."},
    {"word": "volcano", "hint": "A mountain that erupts with lava and ash."},
    
    # Geography & Countries
    {"word": "japan", "hint": "An island nation known for sushi and technology."},
    {"word": "canada", "hint": "The second-largest country in the world by land area."},
    {"word": "amazon", "hint": "The largest rainforest in the world."},
    {"word": "everest", "hint": "The highest mountain on Earth."},
    
    # Food & Drinks
    {"word": "pizza", "hint": "A popular Italian dish with toppings."},
    {"word": "sushi", "hint": "A Japanese dish made with vinegared rice and seafood."},
    {"word": "chocolate", "hint": "A sweet treat made from cocoa beans."},
    {"word": "espresso", "hint": "A strong black coffee."},
    
    # Sports
    {"word": "soccer", "hint": "The world's most popular sport, known as football outside the U.S."},
    {"word": "basketball", "hint": "A game played with a hoop and a bouncing ball."},
    {"word": "tennis", "hint": "A racket sport played on a rectangular court."},
    {"word": "olympics", "hint": "An international multi-sport event held every four years."},
        # Medical Terminology
    {"word": "stethoscope", "hint": "A device used to listen to heart and lung sounds."},
    {"word": "diagnosis", "hint": "Identification of a disease or condition."},
    {"word": "prognosis", "hint": "The likely course of a medical condition."},
    {"word": "anatomy", "hint": "The study of body structures."},
    {"word": "physiology", "hint": "The study of body functions."},
    {"word": "pathology", "hint": "The study of disease causes and effects."},
    {"word": "etiology", "hint": "The cause of a disease."},
    {"word": "symptom", "hint": "A physical or mental feature indicating illness."},
    {"word": "syndrome", "hint": "A group of symptoms that consistently occur together."},
    {"word": "epidemic", "hint": "A widespread occurrence of an infectious disease."},
    {"word": "pandemic", "hint": "A global outbreak of a disease."},
    {"word": "antibiotic", "hint": "A drug used to treat bacterial infections."},
    {"word": "antiviral", "hint": "A medication that fights viral infections."},
    {"word": "analgesic", "hint": "A pain-relieving drug."},
    {"word": "anesthesia", "hint": "Loss of sensation for medical procedures."},
    {"word": "hemoglobin", "hint": "Protein in red blood cells that carries oxygen."},
    {"word": "hypertension", "hint": "High blood pressure."},
    {"word": "hypotension", "hint": "Abnormally low blood pressure."},
    {"word": "tachycardia", "hint": "Abnormally rapid heart rate."},
    {"word": "bradycardia", "hint": "Abnormally slow heart rate."},
    {"word": "dialysis", "hint": "A procedure to filter blood when kidneys fail."},
    {"word": "defibrillator", "hint": "A device that shocks the heart to restore rhythm."},
    {"word": "intubation", "hint": "Inserting a tube into the airway for breathing."},
    {"word": "suture", "hint": "A stitch used to close wounds."},
    {"word": "fracture", "hint": "A broken bone."},
    {"word": "concussion", "hint": "A traumatic brain injury from a blow to the head."},
    {"word": "seizure", "hint": "Sudden, uncontrolled electrical brain disturbance."},
    {"word": "immunity", "hint": "The body's ability to resist infection."},
    {"word": "vaccine", "hint": "A substance that stimulates immunity to a disease."},
    {"word": "sterile", "hint": "Free from bacteria or other microorganisms."},
    {"word": "aseptic", "hint": "Techniques to prevent infection during procedures."},
    {"word": "malignant", "hint": "A term for cancerous growths."},
    {"word": "benign", "hint": "A non-cancerous growth."},
    {"word": "metastasis", "hint": "The spread of cancer to other body parts."},
    {"word": "chemotherapy", "hint": "Drug treatment for cancer."},
    {"word": "radiology", "hint": "Medical imaging like X-rays and MRIs."},
    {"word": "ultrasound", "hint": "Imaging using high-frequency sound waves."},
    {"word": "biopsy", "hint": "Removal of tissue for diagnostic testing."},

    # Nursing & Patient Care
    {"word": "nurse", "hint": "A healthcare professional providing patient care."},
    {"word": "patient", "hint": "A person receiving medical treatment."},
    {"word": "vitals", "hint": "Measurements like pulse, temperature, and blood pressure."},
    {"word": "catheter", "hint": "A tube inserted into the body to drain fluids."},
    {"word": "bandage", "hint": "A strip of material used to cover wounds."},
    {"word": "gauze", "hint": "A thin fabric used for dressing wounds."},
    {"word": "injection", "hint": "Administering medication via a needle."},
    {"word": "intravenous", "hint": "Delivering fluids or drugs directly into veins (IV)."},
    {"word": "ambulatory", "hint": "Able to walk; not bedridden."},
    {"word": "palliative", "hint": "Care focused on relieving symptoms, not curing."},
    {"word": "rehabilitation", "hint": "Therapy to restore function after illness/injury."},
    {"word": "geriatrics", "hint": "Medical care for elderly patients."},
    {"word": "pediatrics", "hint": "Medical care for children."},
    {"word": "neonatal", "hint": "Relating to newborn infants."},
    {"word": "triage", "hint": "Prioritizing patients based on urgency."},
    {"word": "codeblue", "hint": "A hospital emergency for cardiac/respiratory arrest."},

    # Common Diseases & Conditions
    {"word": "diabetes", "hint": "A condition affecting blood sugar regulation."},
    {"word": "asthma", "hint": "A chronic respiratory condition causing breathing difficulties."},
    {"word": "arthritis", "hint": "Inflammation of the joints."},
    {"word": "osteoporosis", "hint": "A condition causing weak, brittle bones."},
    {"word": "alzheimer", "hint": "A progressive neurodegenerative disease."},
    {"word": "pneumonia", "hint": "Infection inflaming the air sacs in the lungs."},
    {"word": "appendicitis", "hint": "Inflammation of the appendix requiring surgery."},
    {"word": "migraine", "hint": "A severe, recurring headache."},
    {"word": "anemia", "hint": "A deficiency of red blood cells or hemoglobin."},
    {"word": "jaundice", "hint": "Yellowing of the skin due to liver/bilirubin issues."},
    {"word": "sepsis", "hint": "A life-threatening response to infection."},
    {"word": "stroke", "hint": "A sudden interruption of blood flow to the brain."},
    {"word": "epilepsy", "hint": "A neurological disorder causing recurrent seizures."},
    {"word": "autism", "hint": "A developmental disorder affecting communication and behavior."},
    {"word": "dementia", "hint": "A decline in cognitive function affecting memory."},
    {"word": "obesity", "hint": "A medical condition involving excess body fat."},
    {"word": "allergy", "hint": "An immune system reaction to a foreign substance."},
    {"word": "influenza", "hint": "A contagious viral infection (the flu)."},
    {"word": "tuberculosis", "hint": "A bacterial infection primarily affecting the lungs."},
    {"word": "malaria", "hint": "A mosquito-borne infectious disease."},
    
    # Add more entries...
]

class HangmanGame:
    def __init__(self, difficulty="normal"):
        word_data = random.choice(WORDS_WITH_HINTS)
        self.word = word_data["word"].lower()
        self.hint = word_data["hint"]
        self.attempts = 6
        self.max_attempts = 6
        self.guessed = set()
        self.display = ["_" for _ in self.word]

    def guess(self, letter):
        if letter in self.guessed:
            return False, "already guessed"
        self.guessed.add(letter)
        if letter in self.word:
            for i, l in enumerate(self.word):
                if l == letter:
                    self.display[i] = letter
            return True, "correct"
        else:
            self.attempts -= 1
            return False, "incorrect"

    def is_won(self):
        return "_" not in self.display

    def is_lost(self):
        return self.attempts <= 0

    def get_display(self):
        return " ".join(self.display)

    def get_visual(self):
        return HANGMAN_PICS[self.max_attempts - self.attempts]

    def get_guessed(self):
        return ", ".join(sorted(self.guessed)) if self.guessed else "None"
