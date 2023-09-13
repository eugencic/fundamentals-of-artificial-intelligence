from rules import *
from production import *


class Choice:
    def __init__(self):
        self.solo_tourist_questions = SoloRules().add()
        self.family_tourist_questions = FamilyRules().add()
        self.budget_tourist_questions = BudgetRules().add()
        self.luxury_tourist_questions = LuxuryRules().add()
        self.medical_tourist_questions = MedicalRules().add()
        self.conclusions = [SoloRules.conclusion,
                            FamilyRules.conclusion,
                            BudgetRules.conclusion,
                            LuxuryRules.conclusion,
                            MedicalRules.conclusion
                            ]
        self.choice = ""

    def combine_questions(self):
        return list(
            set(self.solo_tourist_questions +
                self.family_tourist_questions +
                self.budget_tourist_questions +
                self.luxury_tourist_questions +
                self.medical_tourist_questions
                )
        )

    def forward(self, name):
        print(f"Choose the facts about you, divided by comma and space (ex: 3, 5, 9): ")
        for index, fact in enumerate(self.combine_questions()):
            fact = fact.replace("(?x)", "")
            print(f"\t{index + 1} : {fact}")
        self.choice = input("Choose:\n")
        chain = []
        for index in self.choice.split(", "):
            try:
                fact_index = int(index) - 1
                fact = self.combine_questions()[fact_index]
                chain.append(fact.replace("(?x)", name))
            except (ValueError, IndexError):
                continue
        chained_data = forward_chain(TOURIST_RULES, chain)

        hints = []
        for conclusion in self.conclusions:
            dec_conclusion = conclusion.replace("(?x)", name)
            if dec_conclusion in chained_data:
                hints.append(dec_conclusion)
        if not hints:
            return f"{name} might be a Loonie."
        return hints

    def backward(self, name):
        print(f"Choose the tourist type from the list to execute backward chaining: ")
        for index, conclusion in enumerate(self.conclusions):
            conclusion = conclusion.replace("(?x)", name)
            print(index + 1, conclusion)
        selected = int(input("Choose: \n"))
        if 0 <= selected < 5:
            goal = (self.conclusions[int(selected) - 1]).replace("(?x)", name)
            backward_chain_result = backward_chain(TOURIST_RULES, goal)
            return backward_chain_result
        else:
            return f"There is no such type of tourist."


if __name__ == '__main__':
    print("Welcome to Expert System!")
    print("-----------------------------")
    print("Let's find your tourist type.")
    print("-----------------------------")

    choice = Choice()

    while True:
        user_name = input("Please, write your name: \n")
        print("-----------------------------")
        print("Hello, " + user_name + "!")
        print("-----------------------------")
        print("Choose the algorithm you want to use: ")
        algorithm = input("1 forward chaining\n2 backward chaining\n")
        print("-----------------------------")
        if algorithm == "1":
            print(choice.forward(user_name))
        elif algorithm == "2":
            print(choice.backward(user_name))
        else:
            print("Please, write a valid number")
        print("-----------------------------")
        exit_command = input(
            "Do you want to continue? (write yes/any other input to proceed):\n")
        print("-----------------------------")
        if exit_command != "yes":
            print("Exiting...")
            break
