
import sys
sys.path.append("/Users/kunnath/Projects/Chaos Monkey")
from chaos_monkey import ChaosMonkey

monkey = ChaosMonkey()
print("🐒 Running quick chaos experiments...")

# Run 3 quick experiments
for i in range(3):
    print(f"Experiment {i+1}/3")
    monkey.cpu_stress_test(duration=15, intensity=50)
    print("Waiting 10 seconds...")
    import time
    time.sleep(10)

print("🐒 Chaos experiments completed")
