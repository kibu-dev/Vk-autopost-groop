def parse_attachments(
    attachments
):

    result = []

    if not attachments:
        return ""

    for item in attachments:

        try:

            item_type = item.get(
                "type"
            )

            if item_type == "photo":

                photo = item["photo"]

                result.append(
                    f"photo{photo['owner_id']}_{photo['id']}"
                )

            elif item_type == "video":

                video = item["video"]

                result.append(
                    f"video{video['owner_id']}_{video['id']}"
                )

            elif item_type == "doc":

                doc = item["doc"]

                result.append(
                    f"doc{doc['owner_id']}_{doc['id']}"
                )

            elif item_type == "audio":

                audio = item["audio"]

                result.append(
                    f"audio{audio['owner_id']}_{audio['id']}"
                )

        except Exception:
            pass

    return ",".join(result)
