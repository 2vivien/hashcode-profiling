from pathlib import Path
from statistics import median
from time import perf_counter
from orientation.application.use_cases.generate_recommendation import GenerateRecommendation
from orientation.contracts.profile import StudentProfile

profile=StudentProfile(student_id="benchmark",interests={"investigative":0.8},abilities={"logical":0.8},subjects={"mathematics":0.8})
engine=GenerateRecommendation(Path(__file__).parents[1]/"data"/"knowledge"/"v1")
samples:list[float]=[]
result=None
for _ in range(100):
    start=perf_counter()
    result=engine.execute(profile)
    samples.append((perf_counter()-start)*1000)
samples.sort()
p50=median(samples)
p95=samples[94]
p99=samples[98]
taxonomies={item.taxonomy for item in result.candidates} if result else set()
print({"p50_ms":round(p50,3),"p95_ms":round(p95,3),"p99_ms":round(p99,3),"results":len(result.candidates) if result else 0,"taxonomy_coverage":len(taxonomies) if result else 0})
