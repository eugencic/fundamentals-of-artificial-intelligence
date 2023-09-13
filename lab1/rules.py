from production import IF, AND, THEN, OR


class CommonRules:
    relaxation = "(?x) prioritizes relaxation"

    treatments = "(?x) looks for spa and wellness treatments"

    def add(self):
        return [self.relaxation]


class SoloRules:
    monotony = "(?x) is tired of monotonous life"
    socialization = "(?x) is open to meeting new people and making spontaneous decisions"
    challenge = "(?x) likes to challenge him/herself personally and culturally"

    friendships = "(?x) seeks new friendships"
    intensity = "(?x) wants a very intensive journey"
    conclusion = "(?x) is a solo tourist"

    def add(self):
        return [self.monotony, self.socialization, self.challenge]


class FamilyRules:
    safety = "(?x) prioritizes safety"
    children = "(?x) has children"
    cultures = "(?x) wants to study more about different cultures"

    safe_accommodation = "(?x) looks for safe accommodations"
    education = "(?x) looks for trips that involve educational experience"

    conclusion = "(?x) is a family tourist"

    def add(self):
        return [self.safety, self.children, self.cultures]


class BudgetRules:
    no_money = "(?x) doesn't have a lot of money"
    budget_deals = "(?x) enjoys finding budget deals"
    extended_trips = "(?x) likes extended trips"

    deal_hunter = "(?x) is a good deal hunter"
    multiple_destinations = "(?x) wants to explore multiple destinations in a trip"

    conclusion = "(?x) is a budget tourist"

    def add(self):
        return [self.no_money, self.budget_deals, self.extended_trips]


class CommonRules:
    relaxation = "(?x) prioritizes relaxation"

    treatments = "(?x) looks for spa and wellness treatments"

    def add(self):
        return [self.relaxation]


class LuxuryRules(CommonRules):
    plenty_of_money = "(?x) has plenty of money"
    quality = "(?x) prioritizes quality"

    qualitative_accommodation = "(?x) is ready to pay more for a qualitative accommodation"

    conclusion = "(?x) is a luxury tourist"

    def add(self):
        return [self.plenty_of_money, self.quality,
                self.relaxation]


class MedicalRules(CommonRules):
    operation = "(?x) has recently had an operation"
    privacy_and_comfort = "(?x) prefers privacy and comfort"

    recovery = "(?x) required post operative recovery"
    serene_environments = "(?x) looks for destinations with serene environments"
    private_villas = "(?x) looks for private villas"

    conclusion = "(?x) is a medical tourist"

    def add(self):
        return [self.operation, self.privacy_and_comfort, self.relaxation]


TOURIST_RULES = (
    # solo tourist
    IF(AND(SoloRules.monotony, SoloRules.socialization),
       THEN(SoloRules.friendships)),

    IF(AND(SoloRules.challenge, SoloRules.monotony),
       THEN(SoloRules.intensity)),

    IF(OR(SoloRules.friendships, SoloRules.intensity),
       THEN(SoloRules.conclusion)),

    # family tourist
    IF(AND(FamilyRules.safety),
       THEN(FamilyRules.safe_accommodation)),

    IF(AND(FamilyRules.children, FamilyRules.cultures),
       THEN(FamilyRules.education)),

    IF(AND(FamilyRules.safe_accommodation, FamilyRules.education),
       THEN(FamilyRules.conclusion)),

    # budget tourist
    IF(AND(BudgetRules.no_money, BudgetRules.budget_deals),
       THEN(BudgetRules.deal_hunter)),

    IF(AND(BudgetRules.budget_deals),
       THEN(BudgetRules.multiple_destinations)),

    IF(AND(BudgetRules.extended_trips),
       THEN(BudgetRules.multiple_destinations)),

    IF(OR(BudgetRules.deal_hunter, BudgetRules.multiple_destinations),
       THEN(BudgetRules.conclusion)),

    # common rule
    IF(AND(CommonRules.relaxation),
       THEN(LuxuryRules.treatments, MedicalRules.treatments)),

    # luxury tourist
    IF(AND(LuxuryRules.plenty_of_money, LuxuryRules.quality),
       THEN(LuxuryRules.qualitative_accommodation)),

    IF(AND(LuxuryRules.relaxation),
       THEN(LuxuryRules.treatments)),

    IF(AND(LuxuryRules.qualitative_accommodation, LuxuryRules.treatments),
       THEN(LuxuryRules.conclusion)),

    # medical tourist
    IF(AND(MedicalRules.operation),
       THEN(MedicalRules.recovery)),

    IF(AND(MedicalRules.privacy_and_comfort),
       THEN(MedicalRules.private_villas)),

    IF(AND(MedicalRules.recovery, MedicalRules.treatments),
       THEN(MedicalRules.serene_environments)),

    IF(AND(MedicalRules.private_villas, MedicalRules.serene_environments),
       THEN(MedicalRules.conclusion))
)
