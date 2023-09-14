from rules import *
from production import *


class Choices:
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
        print(f"Choose the facts about you:")
        facts = ""
        for index, fact in enumerate(self.combine_questions()):
            fact = fact.replace("(?x)", "")
            answer = input(f"{index + 1} {fact} (yes/any key to continue)\n")
            if answer == "yes":
                facts = facts + " " + str(index)
                print(facts)
        print("-----------------------------")
        chain = []
        for index in facts.split(" "):
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
        hints_str = ', '.join(map(str, hints))
        return hints_str

    def backward(self, name):
        print(f"Choose the tourist type from the list to execute backward chaining: ")
        for index, conclusion in enumerate(self.conclusions):
            conclusion = conclusion.replace("(?x)", name)
            print(index + 1, conclusion)
        selected = int(input("Choose: \n"))
        print("-----------------------------")
        if 0 <= selected < 5:
            goal = (self.conclusions[int(selected) - 1]).replace("(?x)", name)
            backward_chain_result = backward_chain(TOURIST_RULES, goal)
            backward_chain_result_str = ', '.join(map(str, backward_chain_result))
            return backward_chain_result_str
        else:
            return f"There is no such type of tourist."


if __name__ == '__main__':
    print("Welcome to Expert System!")
    print("-----------------------------")
    print("Let's find your tourist type.")
    print("-----------------------------")

    choices = Choices()

    user_name = input("Please, write your name: \n")
    print("-----------------------------")
    print("Hello, " + user_name + "!")
    print("-----------------------------")

    while True:
        print("Choose the algorithm you want to use: ")
        algorithm = input("1 forward chaining\n2 backward chaining\n")
        print("-----------------------------")
        if algorithm == "1":
            print(choices.forward(user_name))
        elif algorithm == "2":
            print(choices.backward(user_name))
        else:
            print("Please, write a valid number")
        print("-----------------------------")
        exit_command = input("Do you want to continue? (write yes/any key to exit the program):\n")
        print("-----------------------------")
        if exit_command != "yes":
            print("Exiting...")
            break
