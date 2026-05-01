import asyncio
import vipertls

async def probe_subdomain(subdomain):

    async with vipertls.AsyncClient(
        impersonate="chrome_145",
        timeout=10.0
    ) as client:
        try:
            r = await client.get(f"https://{subdomain}")

            print(f"[+] {subdomain} - Status: {r.status_code}, Solved by: {r.solved_by}")
        except Exception as e:

            print(f"[-] {subdomain} - Error: {type(e).__name__}")


async def main(wordlist_path):

    with open(wordlist_path, "r") as f:
        subdomains = [line.strip() for line in f if line.strip()]

    tasks = [probe_subdomain(sub) for sub in subdomains]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main("my_wordlist.txt"))
