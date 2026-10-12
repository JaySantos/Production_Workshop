import json
import os

import requests
from dotenv import load_dotenv


def export_storyblok():
    load_dotenv()
    slug_dict = {}
    try:
        result = requests.get(
            "https://api.storyblok.com/v2/cdn/stories",
            params={
                "token": os.environ.get("STORYBLOK_PUBLIC_TOKEN"),
                "version": "published",
                "content_type": "game",
                "resolve_relations": "game.genre,game.studio,game.hwt_producer,external_link.platform",  # noqa: E501
                "per_page": 100,
            },
        )
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException:
        return None
    try:
        if not result.ok:
            print(result.status_code, result.text)
            return None
        json_result = result.json()
        rels_by_uuid = {r["uuid"]: r for r in json_result["rels"]}
        print(rels_by_uuid)
        for story in json_result["stories"]:
            to_summary(story, rels_by_uuid)
            slug_dict[str(story["id"])] = story["full_slug"]
        print(slug_dict)
        with open("game_slugs.json", "w") as f:
            json.dump(slug_dict, f)

    except requests.exceptions.JSONDecodeError:
        return None


def refName(uuid, rels_by_uuid):
    if rels_by_uuid.get(uuid) is None:
        return "Unknown"
    return rels_by_uuid.get(uuid)["content"].get("name", "Unknown")


def clearFolder(folder: str = "games"):
    os.makedirs(folder, exist_ok=True)

    for name in os.listdir(folder):
        os.remove(os.path.join(folder, name))


def save(data: str, filename: str) -> None:
    with open(os.path.join("games", filename), "w", encoding="utf-8") as file:
        file.write(data)


def to_summary(story, rels_by_uuid):
    summary = ""
    summary += f"{story['content'].get('name')}\n"
    summary += f"Genre(s): {', '.join([refName(uuid, rels_by_uuid) for uuid in story['content'].get('genre')]) or None}\n"  # noqa: E501
    summary += f"Studio(s): {', '.join([refName(uuid, rels_by_uuid) for uuid in story['content'].get('studio')]) or None}\n"  # noqa: E501
    summary += f"Producer(s): {', '.join([refName(uuid, rels_by_uuid) for uuid in story['content'].get('hwt_producer')]) or None}\n"  # noqa: E501
    if not story["content"].get("release_year"):
        summary += "Release Date: TBD\n"
    elif not story["content"].get("release_quarter"):
        summary += f"Release Date: {story['content'].get('release_year')}\n"
    else:
        summary += f"Release Date: {story['content'].get('release_quarter')} {story['content'].get('release_year')}\n"  # noqa: E501

    summary += f"Link(s): {
        ', '.join(
            f'{refName(link.get('platform')[0], rels_by_uuid)} - {link.get('url', {}).get('url', 'Unknown')}'
            for link in story['content'].get('social_media')
        )
        or None
    }\n"  # noqa: E501

    summary += f"Store(s): {
        ', '.join(
            f'{refName(link.get('platform')[0], rels_by_uuid)} - {link.get('url', {}).get('url', 'Unknown')}'
            for link in story['content'].get('store')
        )
        or None
    }\n"  # noqa: E501

    summary += f"Description: {story['content'].get('description', '')}\n"
    filename = f"{story.get('id')}"
    save(summary, filename)

    print(summary)


def main(chunk_size=0, chunk_overlap=0, folder=None, embedder=None, vector_store=None):
    clearFolder("games")
    export_storyblok()


if __name__ == "__main__":
    main()
