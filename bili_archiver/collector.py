from typing import List
from bili_archiver import recorder
from bili_archiver.api import BiliAPI
from bili_archiver.logger import logger


def collect(
        from_history: bool = False,
        from_self_favorite_folders: bool = False,
        from_user_ids: List[int] = None,
        api: BiliAPI = BiliAPI.from_env()
):
    videos = set()

    if from_history:
        logger.info('collecting videos from history')
        last_view = recorder.get_last_run_time('self_history')
        vs = api.get_history(after=last_view)
        watched = [v for v in vs if v['progress'] > 10 or v['progress'] / v['duration'] > 0.5]
        temp = [v['kid'] for v in watched if not recorder.is_downloaded(v['kid'])]
        logger.info(f'{len(vs)} in history, {len(watched)} watched > 5s, {len(temp)} not downloaded in history')
        videos.update(temp)

    if from_self_favorite_folders:
        logger.info('collecting videos from favorite folders')
        folders = api.get_self_favorite_folders()
        for folder in folders:
            logger.info(f"collecting videos from favorite folder {folder['title']}")
            last_view = recorder.get_last_run_time(f"fld{folder['id']}")
            vs = api.get_videos_of_favorite_folder(
                fav_id=folder['id'],
                after=last_view
            )
            temp = [v['id'] for v in vs if not recorder.is_downloaded(v['id'])]
            logger.info(f"{len(vs)} in folder, {len(temp)} not downloaded in f{folder['title']}")
            videos.update(temp)

    if from_user_ids is not None:
        for user in from_user_ids:
            logger.info('collecting videos from history')
            last_view = recorder.get_last_run_time(f"usr{user}")
            vs = api.get_videos_of_user(
                user_id=user,
                after=last_view
            )
            temp = [v['id'] for v in vs if not recorder.is_downloaded(v['id'])]
            logger.info(f"{len(vs)} collected, {len(temp)} not downloaded in user f{user}")
            videos.update(temp)

    logger.info(f"{len(videos)} collected")

    return videos
