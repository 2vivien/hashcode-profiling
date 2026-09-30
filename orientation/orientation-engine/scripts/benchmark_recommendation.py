from pathlib import Path
from time import perf_counter
from orientation.application.use_cases.generate_recommendation import GenerateRecommendation
from orientation.contracts.profile import StudentProfile

profile=StudentProfile(student_id="benchmark",interests={"investigative":0.8},abilities={"logical":0.8},subjects={"mathematics":0.8})
engine=GenerateRecommendation(Path(__file__).parents[1]/"data"/"knowledge"/"v1")
start=perf_counter()
result=engine.execute(profile)
print({"duration_ms":round((perf_counter()-start)*1000,3),"results":len(result.candidates)})
