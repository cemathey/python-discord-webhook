import json
import logging
import time
from datetime import datetime
from functools import partial
from http.client import HTTPException
from typing import (
    Any,
    Callable,
)
import requests
from .webhook_exceptions import ColorNotInRangeException
from .types import (
    EmbedAuthorDict,
    EmbedFieldDict,
    EmbedFooterDict,
    EmbedImageDict,
    EmbedProviderDict,
    EmbedThumbnailDict,
    EmbedVideoDict,
    DiscordEmbedDict,
    DiscordWebhookDict,
    AllowedMentionsDict,
)

logger = logging.getLogger(__name__)


class DiscordEmbed:
    """
    Discord Embed
    """

    author: EmbedAuthorDict | None
    color: int | None
    description: str | None
    fields: list[EmbedFieldDict]
    footer: EmbedFooterDict | None
    image: EmbedImageDict | None
    provider: EmbedProviderDict | None
    thumbnail: EmbedThumbnailDict | None
    timestamp: str | None
    title: str | None
    url: str | None
    video: EmbedVideoDict | None

    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Init Discord Embed
        -----------
        :keyword dict author: information about the author
        :keyword color: color code of the embed as decimal or hexadecimal
        :keyword str description: description of the embed
        :keyword list fields: embed fields as a list of dicts with name and value
        :keyword dict footer: information that will be displayed in the footer
        :keyword dict image: image that will be displayed in the embed
        :keyword dict provider: information about the provider
        :keyword dict thumbnail: thumbnail that will be displayed in the embed
        :keyword str timestamp: timestamp that will be displayed in the embed
        :keyword str title: title of embed
        :keyword str url: add an url to make your embedded title a clickable link
        :keyword dict video: video that will be displayed in the embed
        """
        self.title = title
        self.description = description
        self.url = kwargs.get("url")
        self.footer = kwargs.get("footer")
        self.image = kwargs.get("image")
        self.thumbnail = kwargs.get("thumbnail")
        self.video = kwargs.get("video")
        self.provider = kwargs.get("provider")
        self.author = kwargs.get("author")
        self.fields = kwargs.get("fields", [])
        self.set_color(kwargs.get("color"))  # type: ignore
        if timestamp := kwargs.get("timestamp"):
            self.set_timestamp(timestamp)

    def __len__(self) -> int:
        """Return the total length in characters of the embed

        https://discord.com/developers/docs/resources/channel#embed-limits
        Discord imposes a 6,000 character limit on embeds
        """

        total_length = 0

        if self.fields:
            for field, value in self.fields:
                total_length += len(field) + len(value)

        total_length += len(self.title or "")
        total_length += len(self.description or "")
        total_length += len(self.footer or "")
        total_length += len(self.author or "")

        return total_length

    def as_dict(self) -> DiscordEmbedDict:
        data: DiscordEmbedDict = {}

        if self.title:
            data["title"] = self.title
        if self.description:
            data["description"] = self.description
        if self.url:
            data["url"] = self.url
        if self.timestamp:
            data["timestamp"] = self.timestamp
        if self.color:
            data["color"] = self.color
        if self.footer:
            data["footer"] = self.footer
        if self.image:
            data["image"] = self.image
        if self.thumbnail:
            data["thumbnail"] = self.thumbnail
        if self.description:
            data["description"] = self.description
        if self.video:
            data["video"] = self.video
        if self.provider:
            data["provider"] = self.provider
        if self.author:
            data["author"] = self.author
        if self.fields:
            data["fields"] = self.fields

        return data

    def set_title(self, title: str) -> None:
        """
        Set the title of the embed.
        :param str title: title of embed
        """
        self.title = title

    def set_description(self, description: str) -> None:
        """
        Set the description of the embed.
        :param str description: description of embed
        """
        self.description = description

    def set_url(self, url: str) -> None:
        """
        Set the url of the embed.
        :param str url: url of embed
        """
        self.url = url

    def set_timestamp(self, timestamp: float | int | datetime | None = None) -> None:
        """
        Set timestamp of the embed content.
        :param timestamp: timestamp of embed content
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        elif isinstance(timestamp, float) or isinstance(timestamp, int):
            timestamp = datetime.utcfromtimestamp(timestamp)

        self.timestamp = timestamp.isoformat()

    def set_color(self, color: str | int) -> None:
        """
        Set the color of the embed.
        :param color: color code as decimal(int) or hex(string)
        """
        self.color = int(color, 16) if isinstance(color, str) else color
        if self.color is not None and self.color not in range(16777216):
            raise ColorNotInRangeException(color)

    def set_footer(
        self, text: str, icon_url: str | None = None, proxy_icon_url: str | None = None
    ) -> None:
        """
        Set footer information in the embed.
        :param str text: footer text
        :keyword str icon_url: url of footer icon (only http(s) and attachments)
        :keyword str proxy_icon_url: proxied url of footer icon
        """
        data: EmbedFooterDict = {
            "text": text,
        }

        if icon_url:
            data["icon_url"] = icon_url
        if proxy_icon_url:
            data["proxy_icon_url"] = proxy_icon_url

        self.footer = data

    def set_image(
        self,
        url: str,
        proxy_url: str | None = None,
        height: int | None = None,
        width: int | None = None,
    ) -> None:
        """
        Set the image that will be displayed in the embed.
        :param str url: source url of image (only supports http(s) and attachments)
        :keyword str proxy_url: a proxied url of the image
        :keyword int height: height of image
        :keyword int width: width of image
        """
        data: EmbedImageDict = {
            "url": url,
        }

        if proxy_url:
            data["proxy_url"] = proxy_url
        if height is not None:
            data["height"] = height
        if width is not None:
            data["width"] = width

        self.image = data

    def set_thumbnail(
        self,
        url: str,
        proxy_url: str | None = None,
        height: int | None = None,
        width: int | None = None,
    ) -> None:
        """
        Set the thumbnail that will be displayed in the embed.
        :param str url: source url of thumbnail (only supports http(s) and attachments)
        :keyword str proxy_url: a proxied thumbnail of the image
        :keyword int height: height of thumbnail
        :keyword int width: width of thumbnail
        """
        data: EmbedThumbnailDict = {"url": url}

        if proxy_url:
            data["proxy_url"] = proxy_url
        if height is not None:
            data["height"] = height
        if width is not None:
            data["width"] = width

        self.thumbnail = data

    def set_video(
        self,
        url: str | None = None,
        height: int | None = None,
        width: int | None = None,
    ) -> None:
        """
        Set the video that will be displayed in the embed.
        :keyword str url: source url of video
        :keyword int height: height of video
        :keyword int width: width of video
        """
        data: EmbedVideoDict = {}

        if url:
            data["url"] = url
        if height is not None:
            data["height"] = height
        if width is not None:
            data["width"] = width

        self.video = data

    def set_provider(self, name: str | None = None, url: str | None = None) -> None:
        """
        Set the provider information of the embed.
        :keyword str name: name of provider
        :keyword str url: url of provider
        """
        data: EmbedProviderDict = {}

        if name:
            data["name"] = name
        if url:
            data["url"] = url

        self.provider = data

    def set_author(
        self,
        name: str,
        url: str | None = None,
        icon_url: str | None = None,
        proxy_icon_url: str | None = None,
    ) -> None:
        """
        Set information about the author of the embed.
        :param name: name of author
        :keyword url: url of author
        :keyword icon_url: url of author icon (only supports http(s) and
        attachments)
        :keyword proxy_icon_url: a proxied url of author icon
        """
        data: EmbedAuthorDict = {"name": name}

        if url:
            data["url"] = url
        if icon_url:
            data["icon_url"] = icon_url
        if proxy_icon_url:
            data["proxy_icon_url"] = proxy_icon_url

        self.author = data

    def add_embed_field(self, name: str, value: str, inline: bool = True) -> None:
        """
        Set a field with information for the embed
        :param str name: name of the field
        :param str value: value of the field
        :param bool inline: (optional) whether this field should display inline
        """
        self.fields.append({"name": name, "value": value, "inline": inline})

    def delete_embed_field(self, index: int) -> None:
        """
        Remove a field from the already stored embed fields.
        :param int index: index of field in `self.fields`
        """
        self.fields.pop(index)

    def get_embed_fields(self) -> list[EmbedFieldDict]:
        """
        Get all stored fields of the embed as a list.
        :return: fields of the embed
        """
        return self.fields


class DiscordWebhook:
    """
    Webhook for Discord
    """

    id: str
    url: str

    allowed_mentions: AllowedMentionsDict | None
    attachments: list[dict[str, Any]] | None
    avatar_url: str | None
    components: list | None
    content: str | bytes | None
    embeds: list[DiscordEmbed]
    files: dict[str, tuple[str | None, str | bytes]]
    proxies: dict[str, str] | None
    rate_limit_retry: bool = False
    thread_id: str | None
    thread_name: str | None
    timeout: float | None
    tts: bool | None
    username: str | None
    wait: bool | None

    def __init__(self, url: str, **kwargs) -> None:
        """
        Init Webhook for Discord.
        ---------
        :param str url: your discord webhook url
        :keyword dict allowed_mentions: allowed mentions for the message
        :keyword dict attachments: attachments that should be included
        :keyword str avatar_url: override the default avatar of the webhook
        :keyword str content: the message contents
        :keyword list embeds: list of embedded rich content
        :keyword dict files: to apply file(s) with message
        :keyword str id: webhook id
        :keyword dict proxies: proxies that should be used
        :keyword bool rate_limit_retry: whether the message should be sent again when being rate limited
        :keyword str thread_id: send message to a thread specified by its thread id
        :keyword str thread_name: name of thread to create
        :keyword int timeout: seconds to wait for a response from Discord
        :keyword bool tts: indicates if this is a TTS message
        :keyword str username: override the default username of the webhook
        :keyword bool wait: waits for server confirmation of message send before response (defaults to True)
        """
        self.allowed_mentions = kwargs.get("allowed_mentions", {})
        self.attachments = kwargs.get("attachments", [])
        self.avatar_url = kwargs.get("avatar_url")
        self.content = kwargs.get("content")
        self.embeds = kwargs.get("embeds", [])
        self.files = kwargs.get("files", {})
        self.proxies = kwargs.get("proxies")
        self.rate_limit_retry = kwargs.get("rate_limit_retry", False)
        self.thread_id = kwargs.get("thread_id")
        self.thread_name = kwargs.get("thread_name")
        self.timeout = kwargs.get("timeout")
        self.tts = kwargs.get("tts", False)
        self.url = url
        self.username = kwargs.get("username", False)
        self.wait = kwargs.get("wait", True)
        self.components = kwargs.get('components')

        # Parse the ID from the URL if not explicitly passed
        if kwargs.get("id") is None:
            try:
                chunks = self.url.split("/")
                self.id = chunks[-2]
            except (IndexError, AttributeError):
                raise ValueError(f"`id` was not passed and not parseable from the URL")

    def as_dict(self) -> DiscordWebhookDict:
        data: DiscordWebhookDict = {
            "url": self.url,
            "id": self.id,
            "rate_limit_retry": self.rate_limit_retry,
        }

        if self.allowed_mentions:
            data["allowed_mentions"] = self.allowed_mentions
        if self.attachments:
            data["attachments"] = self.attachments
        if self.avatar_url:
            data["avatar_url"] = self.avatar_url
        if self.content:
            data["content"] = self.content
        if self.embeds:
            data["embeds"] = [embed.as_dict() for embed in self.embeds]
        if self.thread_id:
            data["thread_id"] = self.thread_id
        if self.thread_name:
            data["thread_name"] = self.thread_name
        if self.tts:
            data["tts"] = self.tts
        if self.username:
            data["username"] = self.username
        if self.components:
            data["components"] = self.components
        if self.files:
            data["files"] = self.files

        return data

    def add_embed(self, embed: DiscordEmbed) -> None:
        """
        Add an embedded rich content.
        :param embed: embed object or dict
        """
        self.embeds.append(embed)

    def get_embeds(self) -> list[DiscordEmbed]:
        """
        Get all embeds as a list.
        :return: embeds
        """
        return self.embeds

    def remove_embed(self, index: int) -> None:
        """
        Remove an embed from already added embeds to the webhook.
        :param int index: index of embed
        """
        self.embeds.pop(index)

    def remove_embeds(self) -> None:
        """
        Remove all embeds.
        """
        self.embeds = []

    def add_file(self, file: bytes, filename: str) -> None:
        """
        Add a file to the webhook.
        :param bytes file: file content
        :param str filename: filename
        """
        self.files[f"_{filename}"] = (filename, file)

    def remove_file(self, filename: str) -> None:
        """
        Remove the file by the given filename if it exists.
        :param str filename: filename
        """
        self.files.pop(f"_{filename}", None)
        if self.attachments:
            index = next(
                (
                    i
                    for i, item in enumerate(self.attachments)
                    if item.get("filename") == filename
                ),
                None,
            )
            if index is not None:
                self.attachments.pop(index)

    def remove_files(self, clear_attachments: bool = True) -> None:
        """
        Remove all files and optionally clear the attachments.
        :param bool clear_attachments: Clear the attachments
        """
        self.files = {}
        if clear_attachments:
            self.clear_attachments()

    def clear_attachments(self) -> None:
        """
        Remove all attachments.
        """
        self.attachments = []

    def set_proxies(self, proxies: dict[str, str]) -> None:
        """
        Set proxies that should be used when sending the webhook.
        :param dict proxies: dict of proxies
        """
        self.proxies = proxies

    def set_content(self, content: str) -> None:
        """
        Set the content of the webhook.
        :param str content: content of the webhook
        """
        self.content = content

    @property
    def json(self) -> DiscordWebhookDict:
        """
        Convert data of the webhook to JSON.
        :return: webhook data as json
        """
        data: DiscordWebhookDict = {
            "url": self.url,
            "id": self.id,
            "rate_limit_retry": self.rate_limit_retry,
        }

        if self.allowed_mentions:
            data["allowed_mentions"] = self.allowed_mentions
        if self.attachments:
            data["attachments"] = self.attachments
        if self.avatar_url:
            data["avatar_url"] = self.avatar_url
        if self.content:
            data["content"] = self.content
        if self.embeds:
            data["embeds"] = [embed.as_dict() for embed in self.embeds]
        if self.thread_id:
            data["thread_id"] = self.thread_id
        if self.thread_name:
            data["thread_name"] = self.thread_name
        if self.tts:
            data["tts"] = self.tts
        if self.username:
            data["username"] = self.username
        if self.components:
            data["components"] = self.components
        if self.files:
            data["files"] = self.files

        embeds_empty = not any(data["embeds"]) if "embeds" in data else True
        if embeds_empty and "content" not in data and bool(self.files) is False:
            logger.error("webhook message is empty! set content or embed data")

        return data

    def api_post_request(self) -> "requests.Response":
        """
        Post the JSON converted webhook data to the specified url.
        :return: Response of the sent webhook
        """
        if not self.files:
            return requests.post(
                self.url,
                json=self.json,
                params=self._query_params,
                proxies=self.proxies,
                timeout=self.timeout,
            )

        self.files["payload_json"] = (None, json.dumps(self.json))
        return requests.post(
            self.url,
            files=self.files,
            params=self._query_params,
            proxies=self.proxies,
            timeout=self.timeout,
        )

    def handle_rate_limit(
        self, response, request: Callable[..., requests.Response]
    ) -> requests.Response:
        """
        Handle the rate limit by resending the webhook until a successful response.
        :param response: Response
        :param request: request function
        :return: Response of the sent webhook
        """
        while response.status_code == 429:
            errors = json.loads(response.content.decode("utf-8"))
            if not response.headers.get("Via"):
                raise HTTPException(errors)
            wh_sleep = float(errors["retry_after"]) + 0.15
            logger.error(
                f"Webhook rate limited: sleeping for {wh_sleep:.2f} seconds..."
            )
            time.sleep(wh_sleep)
            response = request()
            if response.status_code in [200, 204]:
                break

        return response

    @property
    def _query_params(self) -> dict:
        """
        Set query parameters for requests.
        :return: Query parameters as dict
        """
        params = {}
        if self.thread_id:
            params["thread_id"] = self.thread_id
        if self.wait:
            params["wait"] = self.wait
        return params

    def execute(self, remove_embeds: bool = False) -> "requests.Response":
        """
        Execute the sending of the webhook with the given data.
        :param bool remove_embeds: clear the stored embeds after webhook is executed
        :return: Response of the sent webhook
        """
        response = self.api_post_request()
        if response.status_code in [200, 204]:
            logger.debug("Webhook executed")
        elif response.status_code == 429 and self.rate_limit_retry:
            response = self.handle_rate_limit(response, self.api_post_request)
            logger.debug("Webhook executed")
        else:
            logger.error(
                "Webhook status code {status_code}: {content}".format(
                    status_code=response.status_code,
                    content=response.content.decode("utf-8"),
                )
            )
        if remove_embeds:
            self.remove_embeds()
        self.remove_files(clear_attachments=False)
        response_content = json.loads(response.content.decode("utf-8"))
        if webhook_id := response_content.get("id"):
            self.id = webhook_id
        if attachments := response_content.get("attachments"):
            self.attachments = attachments
        return response

    def edit(self) -> "requests.Response":
        """
        Edit an already sent webhook with updated data.
        :return: Response of the sent webhook
        """
        assert isinstance(
            self.id, str
        ), "Webhook ID needs to be set in order to edit the webhook."
        assert isinstance(
            self.url, str
        ), "Webhook URL needs to be set in order to edit the webhook."
        url = f"{self.url}/messages/{self.id}"
        if bool(self.files) is False:
            request = partial(
                requests.patch,
                url,
                json=self.json,
                proxies=self.proxies,
                params={"wait": True},
                timeout=self.timeout,
            )
        else:
            self.files["payload_json"] = (None, json.dumps(self.json))
            request = partial(
                requests.patch,
                url,
                files=self.files,
                proxies=self.proxies,
                timeout=self.timeout,
            )
        response = request()
        if response.status_code in [200, 204]:
            logger.debug("Webhook with id {id} edited".format(id=self.id))
        elif response.status_code == 429 and self.rate_limit_retry:
            response = self.handle_rate_limit(response, request)
            logger.debug("Webhook edited")
        else:
            logger.error(
                "Webhook status code {status_code}: {content}".format(
                    status_code=response.status_code,
                    content=response.content.decode("utf-8"),
                )
            )
        return response

    def delete(self) -> "requests.Response":
        """
        Delete the already sent webhook.
        :return: webhook response
        """
        assert isinstance(
            self.id, str
        ), "Webhook ID needs to be set in order to delete the webhook."
        assert isinstance(
            self.url, str
        ), "Webhook URL needs to be set in order to delete the webhook."
        url = f"{self.url}/messages/{self.id}"
        request = partial(
            requests.delete, url, proxies=self.proxies, timeout=self.timeout
        )
        response = request()
        if response.status_code in [200, 204]:
            logger.debug("Webhook deleted")
        elif response.status_code == 429 and self.rate_limit_retry:
            response = self.handle_rate_limit(response, request)
            logger.debug("Webhook edited")
        return response

    @classmethod
    def create_batch(cls, urls: list[str], **kwargs) -> tuple["DiscordWebhook", ...]:
        """
        Create a webhook instance for each specified URL.
        :param list urls: webhook URLs to be used for the instances
        :param kwargs: the same kwargs that are used for an instance of the class
        :return: tuple of webhook instances
        """
        if "url" in kwargs:
            raise TypeError("'url' can't be used as a keyword argument.")
        return tuple([cls(url, **kwargs) for url in urls])
