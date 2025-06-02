
import sys
sys.path.append("/Users/kunnath/Projects/Chaos Monkey")
from load_tester import LoadTester

tester = LoadTester()
print("🧪 Running 60-second load test...")
tester.start_load_test(requests_per_second=2.0, duration=60, num_threads=2)
