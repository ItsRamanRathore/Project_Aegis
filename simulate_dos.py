import asyncio
import aiohttp
import time

URL = "http://127.0.0.1:8000/api/alerts-history"
TOTAL_REQUESTS = 150 # Should trigger the 100/min per-IP limit

async def fetch(session, i):
    try:
        async with session.get(URL) as response:
            status = response.status
            print(f"[{i}] Status: {status}")
            return status
    except Exception as e:
        print(f"[{i}] Error: {e}")
        return None

async def main():
    print(f"[*] Launching Simulated DoS Attack against {URL}...")
    start_time = time.time()
    
    # We use aiohttp to fire requests concurrently, creating a burst
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, i) for i in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
    end_time = time.time()
    ok_count = results.count(200)
    blocked_count = results.count(429) + results.count(503)
    
    print("\n--- DoS Simulation Complete ---")
    print(f"Total Requests Fired: {TOTAL_REQUESTS}")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")
    print(f"Successful (200): {ok_count}")
    print(f"Blocked by Aegis (429/503): {blocked_count}")
    print("-------------------------------")
    
    if blocked_count > 0:
        print("[SUCCESS] The API Rate Limiter successfully intercepted the flood.")
    else:
        print("[FAILURE] All requests passed through. The Rate Limiter failed.")

if __name__ == "__main__":
    asyncio.run(main())
