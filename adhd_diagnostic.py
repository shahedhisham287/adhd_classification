
class ADHDDiagnosticFlow:
    def __init__(self):
        self.inattention_criteria = {
            "fails_attention": "Often fails to give close attention to details or makes careless mistakes",
            "difficulty_sustaining": "Often has difficulty sustaining attention in tasks or play",
            "not_listening": "Often does not seem to listen when spoken to directly",
            "not_following": "Often does not follow through on instructions and fails to finish tasks",
            "difficulty_organizing": "Often has difficulty organizing tasks and activities",
            "avoids_mental_tasks": "Often avoids, dislikes, or is reluctant to engage in tasks requiring mental effort",
            "loses_things": "Often loses things necessary for tasks or activities",
            "easily_distracted": "Is often easily distracted by extraneous stimuli",
            "forgetful": "Is often forgetful in daily activities"
        }

        self.hyperactivity_criteria = {
            "fidgets": "Often fidgets with or taps hands/feet or squirms in seat",
            "leaves_seat": "Often leaves seat in situations when remaining seated is expected",
            "runs_climbs": "Often runs about or climbs in situations where inappropriate",
            "unable_quiet": "Often unable to play or engage in leisure activities quietly",
            "on_the_go": "Is often 'on the go' acting as if 'driven by a motor'",
            "talks_excessive": "Often talks excessively",
            "blurts": "Often blurts out an answer before a question has been completed",
            "difficulty_waiting": "Often has difficulty waiting their turn",
            "interrupts": "Often interrupts or intrudes on others"
        }

    def check_age_criteria(self):
        """Check if age is appropriate for ADHD diagnosis"""
        while True:
            try:
                age = float(input("Enter patient's age when you notice the symptoms: "))
                if age < 1:
                    return False, "Patient too young for standard ADHD diagnosis"
                elif age > 12:
                    return False, "Consider adult ADHD criteria"
                return True, age
            except ValueError:
                print("Please enter a valid age")

    def evaluate_symptoms(self, criteria_dict, domain_name):
        """Evaluate symptoms for a given domain (inattention or hyperactivity)"""
        print(f"\nEvaluating {domain_name} symptoms:")
        print("Rate each symptom: 0=Never, 1=Rarely, 2=Sometimes, 3=Often, 4=Very Often")

        symptoms_count = 0
        symptoms_details = {}

        for key, symptom in criteria_dict.items():
            while True:
                try:
                    rating = int(input(f"{symptom} (0-4): "))
                    if 0 <= rating <= 4:
                        if rating >= 3:  # Count symptoms rated as "Often" or "Very Often"
                            symptoms_count += 1
                        symptoms_details[key] = rating
                        break
                    else:
                        print("Please enter a value between 0 and 4")
                except ValueError:
                    print("Please enter a valid number")

        return symptoms_count, symptoms_details

    def check_additional_criteria(self):
        """Check additional diagnostic criteria"""
        criteria = {}

        # Symptom duration
        while True:
            try:
                months = int(input("\nHow many months have symptoms been present? "))
                criteria['duration_met'] = months >= 6
                break
            except ValueError:
                print("Please enter a valid number of months")

        # Multiple settings
        while True:
            try:
                settings = int(input("In how many settings are symptoms present? (e.g., home=1, school=1): "))
                criteria['settings_met'] = settings >= 2
                break
            except ValueError:
                print("Please enter a valid number")

        # Functional impairment: daily life
        criteria['academic_impact'] = input(
            "How much do symptoms affect academic performance? (none/mild/moderate/severe): ").lower()
        criteria['social_impact'] = input(
            "How much do symptoms affect social interactions? (none/mild/moderate/severe): ").lower()

        # Other conditions
        criteria['impairment'] = input("Is there clear evidence of functional impairment? (yes/no): ").lower() == 'yes'
        criteria['other_conditions'] = input(
            "Are symptoms better explained by another condition? (yes/no): ").lower() == 'yes'

        return criteria

    def determine_presentation(self, inattention_count, hyperactivity_count):
        """Determine ADHD presentation type"""
        if inattention_count >= 6 and hyperactivity_count >= 6:
            return "Combined Presentation"
        elif inattention_count >= 6:
            return "Predominantly Inattentive Presentation"
        elif hyperactivity_count >= 6:
            return "Predominantly Hyperactive-Impulsive Presentation"
        return "Does not meet criteria for any presentation"

    def determine_severity(self, total_symptoms, impairment_level):
        """Determine severity level"""
        if impairment_level == 'mild':
            return "Mild"
        elif impairment_level == 'severe':
            return "Severe"
        else:
            return "Moderate"

    def calculate_symptom_percentages(self, inattention_details, hyperactivity_details, additional_criteria):
        """Calculate detailed symptom percentages"""
        # Calculate percentage of symptoms rated ≥3
        inattention_high_symptoms = sum(1 for rating in inattention_details.values() if rating >= 3)
        hyperactivity_high_symptoms = sum(1 for rating in hyperactivity_details.values() if rating >= 3)

        inattention_percentage = (inattention_high_symptoms / len(self.inattention_criteria)) * 100
        hyperactivity_percentage = (hyperactivity_high_symptoms / len(self.hyperactivity_criteria)) * 100

        # Weighted calculation considering multiple factors
        def calculate_adhd_probability(inattention_pct, hyperactivity_pct, additional_criteria):
            symptom_weight = (inattention_pct + hyperactivity_pct) / 2

            additional_criteria_score = sum([
                6 * additional_criteria['duration_met'],
                4 * additional_criteria['settings_met'],
                5 * additional_criteria['impairment'],
                -10 * additional_criteria['other_conditions']
            ])

            probability = min(max(symptom_weight + additional_criteria_score, 0), 100)
            return probability

        adhd_probability = calculate_adhd_probability(
            inattention_percentage,
            hyperactivity_percentage,
            additional_criteria
        )

        return {
            "inattention_percentage": round(inattention_percentage, 2),
            "hyperactivity_percentage": round(hyperactivity_percentage, 2),
            "adhd_probability": round(adhd_probability, 2)
        }

    def run_diagnostic_flow(self):
        """Execute the complete diagnostic flow"""
        # Step 1: Check age criteria
        age_appropriate, age_result = self.check_age_criteria()
        if not age_appropriate:
            return {"eligible": False, "reason": age_result}

        # Step 2: Evaluate symptoms
        inattention_count, inattention_details = self.evaluate_symptoms(
            self.inattention_criteria, "inattention")
        hyperactivity_count, hyperactivity_details = self.evaluate_symptoms(
            self.hyperactivity_criteria, "hyperactivity/impulsivity")

        # Step 3: Check additional criteria
        additional_criteria = self.check_additional_criteria()

        # Step 4: Determine presentation
        presentation = self.determine_presentation(inattention_count, hyperactivity_count)

        # Step 5: Calculate results
        meets_criteria = (
                (inattention_count >= 6 or hyperactivity_count >= 6) and
                additional_criteria['duration_met'] and
                additional_criteria['settings_met'] and
                additional_criteria['impairment'] and
                not additional_criteria['other_conditions']
        )

        # Step 6: Determine severity
        impairment_level = input("\nRate the level of impairment (mild/moderate/severe): ").lower()
        severity = self.determine_severity(inattention_count + hyperactivity_count, impairment_level)

        # Calculate percentages
        percentages = self.calculate_symptom_percentages(
            inattention_details,
            hyperactivity_details,
            additional_criteria
        )

        # Compile results
        results = {
            "eligible": True,
            "age": age_result,
            "inattention_symptoms": inattention_count,
            "hyperactivity_symptoms": hyperactivity_count,
            "presentation": presentation,
            "severity": severity,
            "meets_criteria": meets_criteria,
            "additional_criteria": additional_criteria,
            "detailed_inattention": inattention_details,
            "detailed_hyperactivity": hyperactivity_details,
            **percentages  # Unpack percentages into results
        }

        return results


def print_diagnostic_report(results):
    """Print formatted diagnostic results"""
    if not results["eligible"]:
        print(f"\nDiagnostic Result: {results['reason']}")
        return

    print("\n=== ADHD Diagnostic Report ===")
    print(f"\nAge: {results['age']}")
    print(f"Inattention Symptoms: {results['inattention_symptoms']}/9")
    print(f"Inattention Symptom Percentage: {results.get('inattention_percentage', 0)}%")

    print(f"Hyperactivity/Impulsivity Symptoms: {results['hyperactivity_symptoms']}/9")
    print(f"Hyperactivity Symptom Percentage: {results.get('hyperactivity_percentage', 0)}%")

    print(f"ADHD Probability: {results.get('adhd_probability', 0)}%")

    # Probability Interpretation
    prob = results.get('adhd_probability', 0)
    if prob < 34:
        print("Interpretation: Low ADHD Likelihood")
    elif 34 <= prob < 67:
        print("Interpretation: Moderate ADHD Likelihood")
    else:
        print("Interpretation: High ADHD Likelihood")

    print(f"Presentation: {results['presentation']}")
    print(f"Severity: {results['severity']}")

    print("\nAdditional Criteria Met:")
    for criterion, met in results['additional_criteria'].items():
        print(f"- {criterion.replace('_', ' ').title()}: {'Yes' if met else 'No'}")

    print(f"\nOverall Diagnosis:")
    if results['meets_criteria']:
        print("Meets DSM-5 criteria for ADHD")
    else:
        print("Does not meet full DSM-5 criteria for ADHD")

    print("\nIMPORTANT NOTE:")
    print("This is a screening tool based on DSM-5 criteria.")
    print("Final diagnosis must be made by a qualified healthcare professional.")


def main():
    diagnostic_flow = ADHDDiagnosticFlow()
    results = diagnostic_flow.run_diagnostic_flow()
    print_diagnostic_report(results)


if __name__ == "__main__":
    main()