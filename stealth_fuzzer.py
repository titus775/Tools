import asyncio
import random
import sys
from curl_cffi.requests import AsyncSession

async def fuzz_path(session, url, path, delay=1.0):
   
    await asyncio.sleep(random.uniform(0.5, delay))
    
    full_url = url.replace("FUZZ", path)
    try:
       
        response = await session.get(full_url, impersonate="chrome124")
        
     
        if response.status_code in [200, 201, 202, 204, 301, 302, 307, 308, 401, 403, 405, 500]:
            print(f"[{response.status_code}] {full_url} (Length: {len(response.content)})")
       
    except Exception as e:
        
        pass

async def main():
    if len(sys.argv) < 3:
        print("Usage: python stealth_fuzzer.py <target_url> <wordlist_file>")
        print("Example: python stealth_fuzzer.py https://example.com/FUZZ paths.txt")
        sys.exit(1)

    target_url = sys.argv[1]
    wordlist_file = sys.argv[2]

   
    with open(wordlist_file, "r") as f:
        paths = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(paths)} paths. Starting stealth fuzzing on {target_url}...")
    print("=" * 50)

   
    async with AsyncSession() as session:
        
        batch_size = 5
        for i in range(0, len(paths), batch_size):
            batch = paths[i:i+batch_size]
            tasks = [fuzz_path(session, target_url, path, delay=2.0) for path in batch]
            await asyncio.gather(*tasks)
        
            await asyncio.sleep(random.uniform(1.0, 3.0))

    print("=" * 50)
    print("Fuzzing complete.")

if __name__ == "__main__":
    asyncio.run(main())