from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional
from enum import Enum
from adhd_diagnostic import ADHDDiagnosticFlow

app = FastAPI(title="ADHD Diagnostic API")


class Severity(str, Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class AdditionalCriteria(BaseModel):
    months_present: int = Field(..., ge=0)
    settings_count: int = Field(..., ge=0)
    academic_impact: Severity
    social_impact: Severity
    other_conditions: bool


class DiagnosticRequest(BaseModel):
    age: float = Field(..., ge=0)
    inattention_ratings: Dict[str, int] = Field(..., description="Rating for each inattention symptom (0-4)")
    hyperactivity_ratings: Dict[str, int] = Field(..., description="Rating for each hyperactivity symptom (0-4)")
    additional_criteria: AdditionalCriteria


class DiagnosticResult(BaseModel):
    eligible: bool
    age: float
    inattention_symptoms: int = 0
    hyperactivity_symptoms: int = 0
    presentation: str = ""
    severity: str = ""
    meets_criteria: bool = False
    inattention_percentage: float = 0.0
    hyperactivity_percentage: float = 0.0
    adhd_probability: float = 0.0
    additional_criteria: Dict = {}


class ADHDDiagnostic:
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

    def evaluate_symptoms(self, ratings: Dict[str, int]) -> int:
        return sum(1 for rating in ratings.values() if rating >= 3)

    def calculate_percentages(self, inattention_ratings: Dict[str, int],
                              hyperactivity_ratings: Dict[str, int],
                              additional_criteria: AdditionalCriteria) -> Dict:
        inattention_count = sum(1 for r in inattention_ratings.values() if r >= 3)
        hyperactivity_count = sum(1 for r in hyperactivity_ratings.values() if r >= 3)

        inattention_percentage = (inattention_count / len(self.inattention_criteria)) * 100
        hyperactivity_percentage = (hyperactivity_count / len(self.hyperactivity_criteria)) * 100

        symptom_weight = (inattention_percentage + hyperactivity_percentage) / 2
        additional_score = sum([
            6 * (additional_criteria.months_present >= 6),
            4 * (additional_criteria.settings_count >= 2),
            5 * (additional_criteria.academic_impact != Severity.NONE or
                 additional_criteria.social_impact != Severity.NONE),
            -10 * additional_criteria.other_conditions
        ])

        probability = min(max(symptom_weight + additional_score, 0), 100)

        return {
            "inattention_percentage": round(inattention_percentage, 2),
            "hyperactivity_percentage": round(hyperactivity_percentage, 2),
            "adhd_probability": round(probability, 2)
        }


diagnostic_service = ADHDDiagnostic()


@app.get("/")
async def root():
    return {"message": "ADHD Diagnostic API v1.0"}


@app.get("/criteria")
async def get_criteria():
    return {
        "inattention": diagnostic_service.inattention_criteria,
        "hyperactivity": diagnostic_service.hyperactivity_criteria
    }


@app.post("/diagnose", response_model=DiagnosticResult)
async def diagnose(request: DiagnosticRequest):
    # Validate age
    if request.age < 1 or request.age > 12:
        return DiagnosticResult(
            eligible=False,
            age=request.age,
            presentation="Age not within diagnostic range"
        )

    # Validate ratings
    for ratings in [request.inattention_ratings, request.hyperactivity_ratings]:
        if any(rating < 0 or rating > 4 for rating in ratings.values()):
            raise HTTPException(status_code=400, detail="Ratings must be between 0 and 4")

    try:
        inattention_count = diagnostic_service.evaluate_symptoms(request.inattention_ratings)
        hyperactivity_count = diagnostic_service.evaluate_symptoms(request.hyperactivity_ratings)

        percentages = diagnostic_service.calculate_percentages(
            request.inattention_ratings,
            request.hyperactivity_ratings,
            request.additional_criteria
        )

        # Determine presentation
        if inattention_count >= 6 and hyperactivity_count >= 6:
            presentation = "Combined Presentation"
        elif inattention_count >= 6:
            presentation = "Predominantly Inattentive"
        elif hyperactivity_count >= 6:
            presentation = "Predominantly Hyperactive-Impulsive"
        else:
            presentation = "Does not meet criteria"

        # Determine severity
        severity = max(request.additional_criteria.academic_impact,
                       request.additional_criteria.social_impact)

        meets_criteria = (
                (inattention_count >= 6 or hyperactivity_count >= 6) and
                request.additional_criteria.months_present >= 6 and
                request.additional_criteria.settings_count >= 2 and
                not request.additional_criteria.other_conditions and
                (request.additional_criteria.academic_impact != Severity.NONE or
                 request.additional_criteria.social_impact != Severity.NONE)
        )

        return DiagnosticResult(
            eligible=True,
            age=request.age,
            inattention_symptoms=inattention_count,
            hyperactivity_symptoms=hyperactivity_count,
            presentation=presentation,
            severity=severity,
            meets_criteria=meets_criteria,
            additional_criteria=request.additional_criteria.dict(),
            **percentages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)