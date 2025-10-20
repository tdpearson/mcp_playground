from typing import List, Dict, Iterator
import requests
from json import loads

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SHAREOK")

SHAREOK_API_SEARCH_URL = "https://shareok.org/server/api/discover/search/objects"


def collapse_values(value_records: List[Dict]|None, delim="|") -> str:
    """ helper function to collapse metadata with multiple "value" segments into a single string """
    if value_records:
        return f"{delim}".join([r['value'] for r in value_records])


def extract_author(metadata: List[Dict]) -> List[Dict]:
    possible_dc_author_fields = [
        'dc.contributor.author',
        'dc.creator'
    ]
    for author_field in possible_dc_author_fields:
        try:
            return metadata[author_field]
        except KeyError:
            pass
    raise Exception("Author Field not found!")
    

def search_records(query: str) -> Iterator[str]:
    """ get records related to query """
    resp = requests.get(f"{SHAREOK_API_SEARCH_URL}?query={query}")

    resp_data = loads(resp.content)
    search_result = resp_data['_embedded']['searchResult']
    total_pages = search_result['page']['totalPages']

    for page_index in range(total_pages):
        resp_data = loads(resp.content)
        search_result = resp_data['_embedded']['searchResult']
        records = search_result['_embedded']['objects']

        for record in records:
            metadata = record['_embedded']['indexableObject']['metadata']
            author = collapse_values(extract_author(metadata), ";")
            title = collapse_values(metadata['dc.title'], " ")
            subject = collapse_values(metadata['dc.subject'], ";")
            issue_date = collapse_values(metadata['dc.date.issued'], ";")
            abstract = collapse_values(metadata.get('dc.description.abstract'), " ")
            urls = collapse_values(metadata['dc.identifier.uri'], "|")
            yield f"author: {author}\ntitle: {title}\nsubject: {subject}\nissue_date: {issue_date}\nabstract: {abstract}\nurls: {urls}"
        
        # fetch next page
        resp = requests.get(f"{SHAREOK_API_SEARCH_URL}?query={query}&page={page_index}")


@mcp.tool()
def records_with_title(title: str) -> Iterator[str]:
    """ get records that have a specific substring in its title """
    return search_records(f"dc.title:{title}")


@mcp.tool()
def records_about_subject(subject: str) -> Iterator[str]:
    """ get records containing the specified subject """
    return search_records(f"dc.subject:{subject}")


if __name__ == "__main__":
    mcp.run(transport="stdio")