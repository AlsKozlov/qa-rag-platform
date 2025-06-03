from workers.faststream.faststream_main import broker


async def publish_broker_msg(msg: dict,
                             channel: str):
    await broker.connect()
    await broker.publish(
        message=msg,
        channel=channel,
    )
    await broker.close()
