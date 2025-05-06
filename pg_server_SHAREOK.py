from typing import List, Dict
import requests
from json import loads

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SHAREOK")

@mcp.tool()
def records_with_title(title: str) -> List[Dict[str, str]]:
    """ get a list of records that have a specific substring in its title """
    search = f"dc.title:{title}"
    resp = requests.get(f"https://shareok.org/server/api/discover/search/objects?query={search}")

    if resp:
        resp_data = loads(resp.content)
        search_result = resp_data['_embedded']['searchResult']
        records = search_result['_embedded']['objects']

        for record in records:
            yield record


@mcp.tool()
def records_about_subject(subject: str) -> List[Dict[str, str]]:
    """ get a list of records containing the specified subject """
    search = subject
    resp = requests.get(f"https://shareok.org/server/api/discover/search/objects?query={search}")

    if resp:
        resp_data = loads(resp.content)
        search_result = resp_data['_embedded']['searchResult']
        records = search_result['_embedded']['objects']

        for record in records:
            yield record


if __name__ == "__main__":
    mcp.run(transport="stdio")