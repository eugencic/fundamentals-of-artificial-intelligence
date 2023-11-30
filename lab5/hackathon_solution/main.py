from flask import Flask, jsonify
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import preprocess_string
from region_data import region_data
from train_data import training_data
from user_data import user_data

app = Flask(__name__)

# Define a route to get region data
@app.route('/get_region_data', methods=['GET'])
def get_region_data():
    return jsonify(region_data)

# Function to train an LDA model
def train_lda_model(training_data, num_topics=50, passes=10):
    processed_training_data = [preprocess_string(text) for text in training_data]  # Preprocess training data
    dictionary = corpora.Dictionary(processed_training_data)  # Create a dictionary for the training data
    corpus = [dictionary.doc2bow(processed_text) for processed_text in processed_training_data]  # Convert text to bag-of-words
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes)  # Train an LDA model
    return lda_model, dictionary  # Return the trained model and dictionary

# Function to identify topics in a given sentence using an LDA model
def identify_topics(input_sentence, lda_model, dictionary, topn=3):
    processed_input = preprocess_string(input_sentence)  # Preprocess input sentence
    input_bow = dictionary.doc2bow(processed_input)  # Convert input to bag-of-words
    topics = lda_model[input_bow]  # Get topics from the LDA model
    sorted_topics = sorted(topics, key=lambda x: x[1], reverse=True)  # Sort topics by probability

    identified_topics = []
    for i in range(min(topn, len(sorted_topics))):
        topic_id, probability = sorted_topics[i]
        main_topic_words = lda_model.show_topic(topic_id, topn=3)  # Get top words for the main topic
        topic_terms = [word for word, _ in main_topic_words]
        identified_topics.append((topic_id, topic_terms, probability))

    return identified_topics

# Train the LDA model
lda_model, dictionary = train_lda_model(training_data)

# Get unique topics identified by LDA
unique_lda_topics = set()
for text in training_data:
    identified_topics = identify_topics(text, lda_model, dictionary)
    for _, topic_terms, _ in identified_topics:
        unique_lda_topics.update(topic_terms)

# Define the HumanTraffickingRules class
class HumanTraffickingRules:
    def __init__(self, region_probabilities, trafficking_related_words):
        self.region_probabilities = region_probabilities  # Store region probabilities
        self.probability = 0  # Initialize probability
        self.trafficking_related_words = trafficking_related_words  # Store trafficking-related words

    # Reset the probability to 0
    def reset_probability(self):
        self.probability = 0

    # Check if trafficking-related words are present in the identified topics
    def check_input_words(self, lda_topics):
        for word in self.trafficking_related_words:
            if word in lda_topics:
                self.probability += 0.02

    # Check the region and update the probability
    def check_region(self, region):
        if region is not None and region in self.region_probabilities:
            self.probability += self.region_probabilities[region]

    # Check the age and update the probability
    def check_age(self, age):
        if age is not None:
            if age < 18:
                self.probability += 0.2
            elif 18 <= age <= 30:
                self.probability += 0.1

    # Evaluate the human trafficking risk based on various factors
    def evaluate_human_trafficking_risk(self, user_data, lda_model, dictionary):
        self.reset_probability()  # Reset probability for each evaluation

        # Identify topics using LDA model
        identified_topics = identify_topics(user_data["text"], lda_model, dictionary)
        lda_topic_words = [word for _, words, _ in identified_topics for word in words]

        # Check factors using the expert system
        self.check_input_words(lda_topic_words)
        self.check_region(user_data.get("region"))
        self.check_age(user_data.get("age"))

        # Adjusted weights for each factor
        topic_weight = 0.3
        region_weight = 0.2
        age_weight = 0.05
        budget_weight = 0.05

        total_weight = topic_weight + region_weight + age_weight + budget_weight

        # Normalize the weights to ensure they sum to 1
        topic_weight /= total_weight
        region_weight /= total_weight
        age_weight /= total_weight
        budget_weight /= total_weight

        # Combine the weighted factors to get the normalized probability
        normalized_probability = (
                topic_weight * self.probability +
                region_weight * self.region_probabilities.get(user_data.get("region", ""), 0) +
                age_weight * (0.2 if user_data.get("age", 0) < 18 else 0.1) +
                budget_weight * (0.4 if user_data.get("budget") == "limited" else 0.2)
        )

        # Scale the normalized_probability to be within the range [0, 1]
        scaled_probability = min(max(normalized_probability, 0), 1)

        # Adjusted thresholds for risk levels
        low_risk_threshold = 0.3
        medium_risk_threshold = 0.5

        # Categorize the risk level based on the scaled probability
        if scaled_probability < low_risk_threshold:
            return "Low Risk", scaled_probability
        elif scaled_probability < medium_risk_threshold:
            return "Medium Risk", scaled_probability
        else:
            return "High Risk", scaled_probability

# Function to start the process of evaluating human trafficking risk for user data
def start():
    # Use the unique topics in the expert system
    user_results = []

    # Evaluate risk for each user
    for user_datum in user_data:
        risk_evaluator = HumanTraffickingRules(region_data, unique_lda_topics)
        risk_level, probability = risk_evaluator.evaluate_human_trafficking_risk(user_datum, lda_model, dictionary)

        # Append the results to the user_results list
        user_results.append((user_datum["text"], user_datum["region"], risk_level, probability))

    # Print unique topics
    print("\nIdentified Topics:")
    for topic in unique_lda_topics:
        print(f" - {topic}")

    # Print results after the loop
    for result in user_results:
        text, region, risk_level, probability = result
        print(
            f"\nFor user input: \"{text}\" from \"{region}\" the risk level is {risk_level}, probability is {probability:.2f}.")

    # Define the fixed influence for each user on the region's probability
    user_influence = 0.05

    # Print results and update region probabilities after the loop
    for result in user_results:
        text, region, risk_level, probability = result
        print(
            f"\nFor user input: \"{text}\" from \"{region}\" the risk level is {risk_level}, probability is {probability:.2f}.")

        # Update the region probability based on the new user's probability with a fixed influence
        current_region_probability = region_data.get(region, 0)
        updated_region_probability = current_region_probability + user_influence
        region_data[region] = updated_region_probability

    # Print updated region probabilities
    print("\nUpdated Region Probabilities:")
    for region, probability in region_data.items():
        print(f" - {region}: {probability:.2f}")

if __name__ == '__main__':
    start()
    app.run(host='0.0.0.0', port=5000, debug=True)
