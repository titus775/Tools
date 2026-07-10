import asyncio
from curl_cffi.requests import AsyncSession
import sys


MAX_CONCURRENT_REQUESTS = 50
TIMEOUT = 10


async def worker(queue: asyncio.Queue, session: AsyncSession):
  
    while True:
        domain = await queue.get()

        try:
            
            if not domain.startswith(("http://", "https://")):
                url = f"https://{domain}"
            else:
                url = domain

            try:
                response = await session.get(
                    url,
                    timeout=TIMEOUT,
                    impersonate="chrome110",
                    allow_redirects=True
                )

                print(f"[+] {url:<40} -> [{response.status_code}]")

            except Exception:
                print(f"[-] {url:<40} -> [DOWN / ERROR]")

        finally:
            queue.task_done()


async def main(file_path: str):
    queue = asyncio.Queue(maxsize=1000)

    async with AsyncSession() as session:

        workers = [
            asyncio.create_task(worker(queue, session))
            for _ in range(MAX_CONCURRENT_REQUESTS)
        ]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    domain = line.strip()

                    if domain:
                        await queue.put(domain)

        except FileNotFoundError:
            print(f"[!] File not found: {file_path}")
            return

        await queue.join()

        # Stop workers
        for task in workers:
            task.cancel()

        await asyncio.gather(*workers, return_exceptions=True)


if __name__ == "__main__":

    # Check if the user supplied a file name
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <domains_file>")
        print(f"Example: python {sys.argv[0]} domains.txt")
        print(f"Example: python {sys.argv[0]} targets.txt")
        sys.exit(1)

    target_file = sys.argv[1]

    print(f"[*] Starting probe...")
    print(f"[*] Target File: {target_file}")
    print("-" * 60)

    try:
        asyncio.run(main(target_file))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
