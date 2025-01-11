from typing import TypedDict, NotRequired, Any
from enum import StrEnum


class EmbedFooterDict(TypedDict):
    text: str
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedImageDict(TypedDict):
    url: str
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]


class EmbedThumbnailDict(TypedDict):
    url: str
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]


class EmbedVideoDict(TypedDict):
    url: NotRequired[str]
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]


class EmbedProviderDict(TypedDict):
    name: NotRequired[str]
    url: NotRequired[str]


class EmbedAuthorDict(TypedDict):
    name: str
    url: NotRequired[str]
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedFieldDict(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


class DiscordEmbedDict(TypedDict):
    title: NotRequired[str]
    # https://discord.com/developers/docs/resources/message#embed-object
    # this will always be `rich`
    # type: NotRequired[str]
    description: NotRequired[str]
    url: NotRequired[str]
    timestamp: NotRequired[str]
    color: NotRequired[int]
    footer: NotRequired[EmbedFooterDict]
    image: NotRequired[EmbedImageDict]
    thumbnail: NotRequired[EmbedThumbnailDict]
    video: NotRequired[EmbedVideoDict]
    provider: NotRequired[EmbedProviderDict]
    author: NotRequired[EmbedAuthorDict]
    fields: NotRequired[list[EmbedFieldDict]]


class AllowedMentions(StrEnum):
    roles = "roles"
    users = "users"
    everyone = "everyone"


class AllowedMentionsDict(TypedDict):
    parse: NotRequired[list[AllowedMentions]]
    roles: NotRequired[list[str]]
    users: NotRequired[list[str]]
    replied_user: NotRequired[bool]


class PollDict(TypedDict):
    pass


class DiscordWebhookDict(TypedDict):
    url: str
    id: str
    rate_limit_retry: bool

    allowed_mentions: NotRequired[AllowedMentionsDict]
    attachments: NotRequired[list[dict[str, Any]]]
    avatar_url: NotRequired[str]
    content: NotRequired[str | bytes]
    embeds: NotRequired[list[DiscordEmbedDict]]
    thread_id: NotRequired[str]
    thread_name: NotRequired[str]
    tts: NotRequired[bool]
    username: NotRequired[str]

    # TODO: type the component object
    components: NotRequired[list | None]
    # TODO: type the files object
    files: NotRequired[dict[str, tuple[str | None, bytes | str]]]
    # TODO:
    # payload_json
    # applied_tags: NotRequired[str]
    # flags: NotRequired[int]
    # poll: NotRequired[PollDict]
