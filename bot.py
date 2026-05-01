Starting Container
[2026-05-01 17:11:04] [INFO    ] discord.client: logging in using static token
Synced 23 slash commands.
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 851, in start
    await self.connect(reconnect=reconnect)
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 775, in connect
Traceback (most recent call last):
    raise PrivilegedIntentsRequired(exc.shard_id) from None
  File "/app/bot.py", line 2081, in <module>
    bot.run(TOKEN)
    ~~~~~~~^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 933, in run
    asyncio.run(runner())
    ~~~~~~~~~~~^^^^^^^^^^
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/base_events.py", line 725, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 922, in runner
    await self.start(token, reconnect=reconnect)
discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents that have not been explicitly enabled in the developer portal. It is recommended to go to https://discord.com/developers/applications/ and explicitly enable the privileged intents within your application's page. If this is not possible, then consider disabling the privileged intents instead.
[2026-05-01 17:11:07] [INFO    ] discord.client: logging in using static token
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/base_events.py", line 725, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 922, in runner
    await self.start(token, reconnect=reconnect)
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 851, in start
    await self.connect(reconnect=reconnect)
Synced 23 slash commands.
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 775, in connect
Traceback (most recent call last):
  File "/app/bot.py", line 2081, in <module>
    bot.run(TOKEN)
    ~~~~~~~^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 933, in run
    asyncio.run(runner())
    ~~~~~~~~~~~^^^^^^^^^^
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/runners.py", line 118, in run
    raise PrivilegedIntentsRequired(exc.shard_id) from None
discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents that have not been explicitly enabled in the developer portal. It is recommended to go to https://discord.com/developers/applications/ and explicitly enable the privileged intents within your application's page. If this is not possible, then consider disabling the privileged intents instead.
[2026-05-01 17:12:07] [INFO    ] discord.client: logging in using static token
Synced 23 slash commands.
Traceback (most recent call last):
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/runners.py", line 118, in run
  File "/app/bot.py", line 2081, in <module>
    bot.run(TOKEN)
    return self._loop.run_until_complete(task)
    ~~~~~~~^^^^^^^
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 933, in run
    asyncio.run(runner())
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/base_events.py", line 725, in run_until_complete
    ~~~~~~~~~~~^^^^^^^^^^
    return future.result()
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/runners.py", line 195, in run
           ~~~~~~~~~~~~~^^
    return runner.run(main)
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 922, in runner
           ~~~~~~~~~~^^^^^^
    await self.start(token, reconnect=reconnect)
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 851, in start
    await self.connect(reconnect=reconnect)
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 775, in connect
    raise PrivilegedIntentsRequired(exc.shard_id) from None
discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents that have not been explicitly enabled in the developer portal. It is recommended to go to https://discord.com/developers/applications/ and explicitly enable the privileged intents within your application's page. If this is not possible, then consider disabling the privileged intents instead.
[2026-05-01 17:12:10] [INFO    ] discord.client: logging in using static token
           ~~~~~~~~~~~~~^^
    asyncio.run(runner())
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 922, in runner
    await self.start(token, reconnect=reconnect)
    ~~~~~~~~~~~^^^^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 851, in start
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/runners.py", line 195, in run
    await self.connect(reconnect=reconnect)
    return runner.run(main)
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 775, in connect
           ~~~~~~~~~~^^^^^^
Synced 23 slash commands.
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/runners.py", line 118, in run
Traceback (most recent call last):
    return self._loop.run_until_complete(task)
  File "/app/bot.py", line 2081, in <module>
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
    bot.run(TOKEN)
  File "/mise/installs/python/3.13.13/lib/python3.13/asyncio/base_events.py", line 725, in run_until_complete
    ~~~~~~~^^^^^^^
    return future.result()
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 933, in run
    raise PrivilegedIntentsRequired(exc.shard_id) from None
discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents that have not been explicitly enabled in the developer portal. It is recommended to go to https://discord.com/developers/applications/ and explicitly enable the privileged intents within your application's page. If this is not possible, then consider disabling the privileged intents instead.
[2026-05-01 17:13:09] [INFO    ] discord.client: logging in using static token
Synced 23 slash commands.
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 922, in runner
Traceback (most recent call last):
  File "/app/bot.py", line 2081, in <module>
    await self.start(token, reconnect=reconnect)
    bot.run(TOKEN)
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 851, in start
    ~~~~~~~^^^^^^^
    await self.connect(reconnect=reconnect)
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 933, in run
  File "/app/.venv/lib/python3.13/site-packages/discord/client.py", line 775, in connect
    asyncio.run(runner())
    raise PrivilegedIntentsRequired(exc.shard_id) from None
