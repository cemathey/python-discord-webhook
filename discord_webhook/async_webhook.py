import asyncio
import json
import logging
from contextlib import asynccontextmanager
from functools import partial
from http.client import HTTPException
from . import DiscordWebhook
from typing import AsyncGenerator, Any, Coroutine, Callable, Optional

logger = logging.getLogger(__name__)

try:
    import httpx  # noqa
except ImportError:  # pragma: nocover
    # Async is an optional dependency so don't raise
    # an exception unless the AsyncDiscordWebhook is used.
    pass


class AsyncDiscordWebhook(DiscordWebhook):
    """
    Async version of DiscordWebhook.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            import httpx  # noqa
        except ImportError:  # pragma: nocover
            raise ImportError(
                "You're attempting to use the async version of discord-webhooks but"
                " didn't install it using `pip install discord-webhook[async]`."
            ) from None

    @property
    @asynccontextmanager
    async def http_client(self) -> AsyncGenerator[Optional["httpx.AsyncClient"], None]:
        """
        A property that returns a httpx.AsyncClient instance that is used for a 'with' statement.
        Example:
            async with self.http_client as client:
                client.post(url, data=data)
        It will automatically close the client when the context is exited.
        :return: httpx.AsyncClient
        """
        async with httpx.AsyncClient(mounts=self.proxies) as client:
            # client = httpx.AsyncClient(mounts=self.proxies)
            yield client

    async def api_post_request(  # type: ignore
        self, *, client: Optional["httpx.AsyncClient"] = None
    ) -> "httpx.Response":
        """
        Post the JSON converted webhook data to the specified url.
        :return:
        """

        async def _post_request(client: httpx.AsyncClient):
            if bool(self.files) is False:
                response = await client.post(
                    self.url,
                    json=self.json,
                    params=self._query_params,
                    timeout=self.timeout,
                )
            else:
                self.files["payload_json"] = (
                    None,
                    json.dumps(self.json).encode("utf-8"),
                )
                response = await client.post(
                    self.url,
                    files=self.files,
                    params=self._query_params,
                    timeout=self.timeout,
                )

            return response

        if client is None:
            async with self.http_client as client:
                response = await _post_request(client)
        else:
            response = await _post_request(client)

        return response

    async def handle_rate_limit(  # type: ignore
        self, response, request: Callable[..., Coroutine[None, None, "httpx.Response"]]
    ) -> "httpx.Response":
        """
        Handle the rate limit by resending the webhook until a successful response.
        :param response: Response
        :param request: request function
        :return: Response of the sent webhook
        """
        while response.status_code == 429:
            errors = response.json()
            if not response.headers.get("Via"):
                raise HTTPException(errors)
            wh_sleep = float(errors["retry_after"]) + 0.15
            logger.error(
                "Webhook rate limited: sleeping for {wh_sleep} seconds...".format(
                    wh_sleep=round(wh_sleep, 2)
                )
            )
            await asyncio.sleep(wh_sleep)
            response = await request()
            if response.status_code in [200, 204]:
                break
        return response

    async def execute(  # type: ignore
        self,
        remove_embeds: bool = False,
        *,
        client: Optional["httpx.AsyncClient"] = None,
    ) -> "httpx.Response":
        """
        Execute the sending of the webhook with the given data.
        :param bool remove_embeds: clear the stored embeds after webhook is executed
        :return: Response of the sent webhook
        """
        response = await self.api_post_request(client=client)
        if response.status_code in [200, 204]:
            logger.debug("Webhook executed")
        elif response.status_code == 429 and self.rate_limit_retry:
            response = await self.handle_rate_limit(response, self.api_post_request)
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
        return response

    async def edit(  # type: ignore
        self, *, client: Optional["httpx.AsyncClient"] = None
    ) -> "httpx.Response":
        """
        Edit an already sent webhook with updated data.
        :return: Response of the sent webhook
        """
        assert isinstance(
            self.webhook_id, str
        ), "Webhook ID needs to be set in order to edit the message."
        assert isinstance(
            self.url, str
        ), "Webhook URL needs to be set in order to edit the message."
        assert isinstance(
            self.message_id, str
        ), "Webhook message ID needs to be set in order to edit the message."

        async def _edit(client: "httpx.AsyncClient"):
            url = f"{self.url}/messages/{self.message_id}"
            if bool(self.files) is False:
                patch_kwargs = {
                    "json": self.json,
                    "params": {"wait": True},
                    "timeout": self.timeout,
                }
            else:
                self.files["payload_json"] = (None, json.dumps(self.json))
                patch_kwargs = {"files": self.files, "timeout": self.timeout}
            request = partial(client.patch, url, **patch_kwargs)
            response = await request()
            if response.status_code in [200, 204]:
                logger.debug("Webhook with id {id} edited".format(id=self.webhook_id))
            elif response.status_code == 429 and self.rate_limit_retry:
                response = await self.handle_rate_limit(response, request)
                logger.debug("Webhook edited")
            else:
                logger.error(
                    "Webhook status code {status_code}: {content}".format(
                        status_code=response.status_code,
                        content=response.content.decode("utf-8"),
                    )
                )
            return response

        if client is None:
            async with self.http_client as client:
                response = await _edit(client)
        else:
            response = await _edit(client)

        return response

    async def delete(  # type: ignore
        self, *, client: Optional["httpx.AsyncClient"] = None
    ) -> "httpx.Response":
        """
        Delete the already sent webhook.
        :return: webhook response
        """
        assert isinstance(
            self.webhook_id, str
        ), "Webhook ID needs to be set in order to delete the message."
        assert isinstance(
            self.url, str
        ), "Webhook URL needs to be set in order to delete the message."
        assert isinstance(
            self.message_id, str
        ), "Webhook message ID needs to be set in order to delete the message."
        url = f"{self.url}/messages/{self.message_id}"

        async def _delete(client: "httpx.AsyncClient"):
            response = await client.delete(url, timeout=self.timeout)
            if response.status_code in [200, 204]:
                logger.debug("Webhook deleted")
            else:
                logger.error(
                    "Webhook status code {status_code}: {content}".format(
                        status_code=response.status_code,
                        content=response.content.decode("utf-8"),
                    )
                )
            return response

        if client is None:
            async with self.http_client as client:
                response = await _delete(client)
        else:
            response = await _delete(client)

        return response
